"""Learning Requests screen: manage incoming peer requests and outgoing learning goals (no SQL)."""
import streamlit as st

from services.feedback import report_request_issue
from services.requests import change_status, fetch_requests
from ui.theme import avatar_initial, section_header, status_badge


def available_actions(status, is_provider):
    """Return available buttons based on request status and actor role."""
    if status == "pending":
        if is_provider:
            return [("✅ Accept", "accepted"), ("🚫 Reject", "rejected"), ("✖️ Cancel", "cancelled")]
        return [("✖️ Cancel", "cancelled")]
    if status == "accepted":
        if is_provider:
            return [("✅ Mark Completed", "awaiting_confirmation"), ("✖️ Cancel", "cancelled")]
        return [("✖️ Cancel", "cancelled")]
    if status == "awaiting_confirmation" and not is_provider:
        return [("✅ Confirm Completion", "completed")]
    return []


def render():
    user = st.session_state.get("user")
    if not user or user.get("role") != "student":
        st.warning("Please sign in as a student to access this page.")
        return

    st.markdown(section_header("📬", "Learning Requests", "Track incoming and outgoing peer skill requests"), unsafe_allow_html=True)

    incoming_tab, sent_tab = st.tabs(
        ["📥 Received Requests", "📤 Sent Requests"],
        key="requests_tabs",
        on_change="rerun",
    )

    with incoming_tab:
        render_request_list(
            requests=fetch_requests(user["id"], as_provider=True),
            user_id=user["id"],
            is_provider=True,
            empty_msg="No incoming requests yet. When students request your skills, they'll appear here.",
        )

    with sent_tab:
        render_request_list(
            requests=fetch_requests(user["id"], as_provider=False),
            user_id=user["id"],
            is_provider=False,
            empty_msg="You haven't sent any learning requests yet. Explore skills to send your first!",
        )


def render_request_list(requests, user_id, is_provider, empty_msg):
    if not requests:
        st.info(empty_msg)
        return

    # Filter
    filter_opts = [
        "All", "Pending", "Accepted", "Awaiting Learner Confirmation",
        "Completed", "Rejected", "Cancelled",
    ]
    chosen_filter = st.segmented_control(
        "Filter by status",
        filter_opts,
        default="All",
        key=f"seg_{'prov' if is_provider else 'learn'}",
        label_visibility="collapsed",
    )

    filtered_reqs = requests
    if chosen_filter and chosen_filter != "All":
        selected_status = (
            "awaiting_confirmation"
            if chosen_filter == "Awaiting Learner Confirmation"
            else chosen_filter.lower()
        )
        filtered_reqs = [r for r in requests if r["status"] == selected_status]

    if not filtered_reqs:
        st.info(f"No {chosen_filter.lower()} requests found.")
        return

    for r in filtered_reqs:
        with st.container(border=True):
            other_name = r["learner"] if is_provider else r["provider"]
            other_dept = r["learner_dept"] if is_provider else r["provider_dept"]
            other_role = "Learner" if is_provider else "Peer Tutor"
            initials = avatar_initial(other_name)

            col_meta, col_badge = st.columns([3.8, 1.2])
            with col_meta:
                st.markdown(
                    f"""
                    <div style="display: flex; align-items: center; gap: 0.85rem; margin-bottom: 0.35rem;">
                        <div class="sb-avatar-circle">{initials}</div>
                        <div>
                            <div style="font-weight: 700; font-size: 1rem; color: #1F2933;">
                                {r['skill']} <span style="font-size: 0.78rem; font-weight: 500; color: #6B7280;">({r['category']})</span>
                            </div>
                            <div style="font-size: 0.82rem; color: #6B7280;">
                                {other_role}: <b>{other_name}</b> · {other_dept}
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.caption(f"Requested on: {r['created_at']}")
            with col_badge:
                st.markdown(
                    f'<div style="text-align: right;">{status_badge(r["status"])}</div>',
                    unsafe_allow_html=True,
                )

            if r.get("message"):
                st.markdown(
                    f"""
                    <div style="background: #F7F9FA; border: 1px solid #E5E7EB; padding: 10px 14px;
                                border-radius: 10px; font-size: 0.88rem; color: #4B5563; margin: 0.6rem 0;">
                        <b>Message:</b> "{r['message']}"
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            actions = available_actions(r["status"], is_provider)
            if actions:
                st.write("")
                btn_cols = st.columns(len(actions))
                for col, (label, new_status) in zip(btn_cols, actions):
                    key = f"{label}_{r['id']}_{is_provider}"
                    if col.button(label, key=key, use_container_width=True):
                        ok, text = change_status(r["id"], user_id, new_status)
                        if ok:
                            if new_status == "awaiting_confirmation":
                                st.toast("Waiting for learner confirmation.", icon="✅")
                            else:
                                st.toast(f"Request marked as {new_status}!", icon="✅")
                            st.rerun()
                        else:
                            st.error(text)

            if r["status"] == "awaiting_confirmation" and not is_provider:
                if r["issue_reported"]:
                    st.info("An issue has been reported for this request.")
                else:
                    with st.expander("🚩 Report Issue"):
                        with st.form(f"form_issue_{r['id']}"):
                            reason = st.text_area(
                                "Describe the issue",
                                key=f"issue_reason_{r['id']}",
                            )
                            submitted = st.form_submit_button(
                                "🚩 Submit Issue Report",
                                use_container_width=True,
                            )
                            if submitted:
                                ok, text = report_request_issue(
                                    request_id=r["id"],
                                    learner_id=user_id,
                                    reason=reason,
                                )
                                if ok:
                                    st.toast(text, icon="⚠️")
                                    st.rerun()
                                else:
                                    st.error(text)
