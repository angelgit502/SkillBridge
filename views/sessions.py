"""Sessions screen: schedule time slots, book accepted requests, live countdown & session history (no SQL)."""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import streamlit as st

from services.requests import fetch_requests
from services.sessions import (
    book_slot_for_request,
    change_session_status,
    delete_slot,
    get_next_session,
    get_provider_available_slots,
    get_user_sessions,
    publish_slot,
)
from ui.theme import countdown, section_header, status_badge

IST = ZoneInfo("Asia/Kolkata")


def render():
    user = st.session_state.get("user")
    if not user or user.get("role") != "student":
        st.warning("Please sign in as a student to access this page.")
        return

    st.markdown(section_header("📅", "My Learning Sessions", "Manage peer sessions, publish hours, and book requests"), unsafe_allow_html=True)

    # Next session banner
    next_sess = get_next_session(user["id"])
    if next_sess:
        with st.container(border=True):
            other_role = "Learner" if user["id"] == next_sess["provider_id"] else "Peer Tutor"
            other_name = next_sess["learner"] if user["id"] == next_sess["provider_id"] else next_sess["provider"]
            other_dept = next_sess["learner_dept"] if user["id"] == next_sess["provider_id"] else next_sess["provider_dept"]

            st.markdown(
                '<span style="background: #E6F4F5; color: #1F6F78; padding: 4px 14px; border-radius: 999px; font-size: 0.74rem; font-weight: 700; text-transform: uppercase;">Next Session</span>',
                unsafe_allow_html=True,
            )
            col_info, col_timer = st.columns([2.5, 1.5])
            with col_info:
                st.markdown(f"### 📅 **{next_sess['skill']}** ({next_sess['category']})")
                st.write(f"{other_role}: **{other_name}** ({other_dept})")
                st.markdown(f"🕒 **{next_sess['start_time']}** to **{next_sess['end_time']}** (IST)")
            with col_timer:
                st.caption("Time remaining:")
                countdown(next_sess["start_time"])
    else:
        st.info("No upcoming sessions scheduled.")

    st.write("")

    tab_upcoming, tab_booking, tab_slots, tab_history = st.tabs([
        "📅 Scheduled", "⚡ Book a Session", "🕒 Publish Slots", "📜 History",
    ], key="sessions_tabs", on_change="rerun")

    all_sessions = get_user_sessions(user["id"])
    scheduled_sessions = [s for s in all_sessions if s["status"] == "scheduled"]
    completed_sessions = [s for s in all_sessions if s["status"] == "completed"]
    cancelled_sessions = [s for s in all_sessions if s["status"] == "cancelled"]

    with tab_upcoming:
        if not scheduled_sessions:
            st.info("No active scheduled sessions. Book one from the '⚡ Book a Session' tab.")
        else:
            for sess in scheduled_sessions:
                with st.container(border=True):
                    is_tutor = user["id"] == sess["provider_id"]
                    partner = sess["learner"] if is_tutor else sess["provider"]
                    partner_dept = sess["learner_dept"] if is_tutor else sess["provider_dept"]
                    partner_label = "Learner" if is_tutor else "Instructor"

                    c1, c2 = st.columns([3.5, 1.5])
                    with c1:
                        st.markdown(f"### **{sess['skill']}** ({sess['category']})")
                        st.write(f"👥 **{partner_label}:** {partner} · {partner_dept}")
                        st.markdown(f"🕒 `{sess['start_time']}` to `{sess['end_time']}`")
                    with c2:
                        visible_status = (
                            "awaiting_confirmation"
                            if sess["request_status"] == "awaiting_confirmation"
                            else sess["status"]
                        )
                        st.markdown(
                            f'<div style="text-align: right;">{status_badge(visible_status)}</div>',
                            unsafe_allow_html=True,
                        )
                        st.write("")
                        if sess["request_status"] == "awaiting_confirmation":
                            st.caption("See Learning Requests to confirm completion or report an issue.")
                        elif sess["request_status"] == "accepted":
                            if st.button("✖️ Cancel", key=f"btn_canc_{sess['id']}", use_container_width=True):
                                ok, msg = change_session_status(sess["id"], user["id"], "cancelled")
                                if ok:
                                    st.toast("Session cancelled", icon="🚫")
                                    st.rerun()
                                else:
                                    st.error(msg)

    with tab_booking:
        st.caption("Select an accepted request and pick a provider's time slot.")

        sent_accepted = [
            r for r in fetch_requests(user["id"], as_provider=False)
            if r["status"] == "accepted"
        ]

        if not sent_accepted:
            st.info("No accepted requests waiting to be scheduled. Explore skills and send requests first!")
        else:
            req_map = {
                f"{r['skill']} with {r['provider']} (#{r['id']})": r
                for r in sent_accepted
            }
            chosen_label = st.selectbox("Select accepted request", list(req_map.keys()))
            selected_req = req_map[chosen_label]

            prov_slots = get_provider_available_slots(
                selected_req["provider_id"], future_only=True
            )
            if not prov_slots:
                st.warning(f"{selected_req['provider']} has no open slots yet.")
            else:
                slot_map = {
                    f"📅 {s['start_time']} to {s['end_time']} (IST)": s["id"]
                    for s in prov_slots
                }
                chosen_slot_str = st.selectbox("Select time slot", list(slot_map.keys()))
                chosen_slot_id = slot_map[chosen_slot_str]

                if st.button("✅ Confirm & Book Session", use_container_width=True, key="btn_confirm_booking"):
                    ok_book, msg_book = book_slot_for_request(
                        request_id=selected_req["id"],
                        slot_id=chosen_slot_id,
                        learner_id=user["id"],
                    )
                    if ok_book:
                        st.toast("Session booked!", icon="🎉")
                        st.success(msg_book)
                        st.rerun()
                    else:
                        st.error(msg_book)

    with tab_slots:
        st.caption("Offer dates/times when you are free to teach.")

        now_ist = datetime.now(IST)
        default_start = (now_ist + timedelta(days=1)).strftime("%Y-%m-%d 14:00")
        default_end = (now_ist + timedelta(days=1)).strftime("%Y-%m-%d 15:00")

        with st.form("form_publish_slot"):
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                start_val = st.text_input("Start Time (YYYY-MM-DD HH:MM)", value=default_start)
            with col_t2:
                end_val = st.text_input("End Time (YYYY-MM-DD HH:MM)", value=default_end)
            btn_publish = st.form_submit_button("📤 Publish Slot", use_container_width=True)
            if btn_publish:
                ok_pub, msg_pub = publish_slot(user["id"], start_val, end_val)
                if ok_pub:
                    st.toast("Slot published!", icon="✅")
                    st.success(msg_pub)
                    st.rerun()
                else:
                    st.error(msg_pub)

        my_slots = get_provider_available_slots(user["id"])
        st.write("")
        st.markdown(f"**Your Unbooked Slots ({len(my_slots)})**")
        if not my_slots:
            st.caption("No unbooked slots.")
        else:
            for s in my_slots:
                with st.container(border=True):
                    cs1, cs2 = st.columns([4, 1])
                    with cs1:
                        st.write(f"🕐 **{s['start_time']}** to **{s['end_time']}** (IST)")
                    with cs2:
                        if st.button("🗑️ Delete", key=f"del_slot_{s['id']}", use_container_width=True):
                            del_ok, del_msg = delete_slot(s["id"], user["id"])
                            if del_ok:
                                st.toast("Slot deleted", icon="🗑️")
                                st.rerun()
                            else:
                                st.error(del_msg)

    with tab_history:
        sub_comp, sub_canc = st.tabs(
            ["✅ Completed", "✖️ Cancelled"],
            key="session_history_tabs",
            on_change="rerun",
        )
        with sub_comp:
            if not completed_sessions:
                st.info("No completed sessions yet.")
            else:
                for cs in completed_sessions:
                    with st.container(border=True):
                        is_tutor = user["id"] == cs["provider_id"]
                        partner = cs["learner"] if is_tutor else cs["provider"]
                        partner_label = "Learner" if is_tutor else "Instructor"
                        c1, c2 = st.columns([4, 1])
                        with c1:
                            st.markdown(f"**{cs['skill']}** ({cs['category']})")
                            st.caption(f"{partner_label}: {partner} · {cs['start_time']}")
                        with c2:
                            st.markdown(status_badge("Completed"), unsafe_allow_html=True)

        with sub_canc:
            if not cancelled_sessions:
                st.info("No cancelled sessions.")
            else:
                for cns in cancelled_sessions:
                    with st.container(border=True):
                        is_tutor = user["id"] == cns["provider_id"]
                        partner = cns["learner"] if is_tutor else cns["provider"]
                        partner_label = "Learner" if is_tutor else "Instructor"
                        c1, c2 = st.columns([4, 1])
                        with c1:
                            st.markdown(f"**{cns['skill']}** ({cns['category']})")
                            st.caption(f"{partner_label}: {partner} · {cns['start_time']}")
                        with c2:
                            st.markdown(status_badge("Cancelled"), unsafe_allow_html=True)
