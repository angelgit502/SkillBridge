"""Feedback & Ratings screen: submit reviews for completed sessions and view peer feedback (no SQL)."""
import streamlit as st

from services.feedback import (
    get_feedback_given,
    get_feedback_received,
    get_unreviewed_sessions,
    submit_feedback,
)
from ui.theme import avatar_initial


def render():
    user = st.session_state.get("user")
    if not user or user.get("role") != "student":
        st.warning("Please sign in as a student to access this page.")
        return

    st.header("⭐ Feedback & Peer Ratings")
    st.markdown('<p class="sb-tagline">Rate your learning sessions, submit constructive reviews, and build campus credibility.</p>', unsafe_allow_html=True)

    tab_submit, tab_given, tab_received = st.tabs([
        "⭐ Submit Session Review",
        "📤 Feedback You Gave",
        "📥 Feedback You Received",
    ], key="feedback_tabs", on_change="rerun")

    with tab_submit:
        st.subheader("📝 Review Completed Sessions")
        st.caption("You can submit a 1 to 5 star rating and comment for completed sessions you attended as a learner.")

        unreviewed = get_unreviewed_sessions(user["id"])
        if not unreviewed:
            st.info("You have no pending completed sessions waiting for feedback. Great job keeping up!")
        else:
            options = {
                f"{u['skill']} taught by {u['provider']} ({u['start_time']})": u
                for u in unreviewed
            }
            choice = st.selectbox("Select completed session to review", list(options.keys()))
            selected_sess = options[choice]

            with st.container(border=True):
                st.markdown(f"### Review for: **{selected_sess['skill']}**")
                st.caption(f"Instructor: **{selected_sess['provider']}** · Scheduled: {selected_sess['start_time']}")

                with st.form("form_submit_feedback"):
                    rating = st.slider("Session Rating", min_value=1, max_value=5, value=5, help="1 (Poor) to 5 (Excellent)")
                    st.write(f"Rating: {'⭐' * rating} ({rating}/5)")
                    comment = st.text_area(
                        "Session Feedback & Highlights",
                        placeholder="Share what went well, how clear the explanations were, and tips for future learners...",
                    )
                    submitted = st.form_submit_button("⭐ Submit Peer Review", use_container_width=True)

                    if submitted:
                        ok, msg = submit_feedback(
                            session_id=selected_sess["id"],
                            learner_id=user["id"],
                            rating=rating,
                            comment=comment,
                        )
                        if ok:
                            st.toast("Thank you! Review recorded.", icon="🌟")
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)

    with tab_given:
        st.subheader("📤 Reviews You've Submitted")
        st.caption("Past feedback you provided to your student tutors.")

        given = get_feedback_given(user["id"])
        if not given:
            st.info("You haven't submitted any feedback yet.")
        else:
            for f in given:
                with st.container(border=True):
                    initials = avatar_initial(f["provider"])
                    c_av, c_txt = st.columns([0.8, 6.2])
                    with c_av:
                        st.markdown(f'<div class="sb-avatar-circle">{initials}</div>', unsafe_allow_html=True)
                    with c_txt:
                        st.markdown(f"**{f['skill']}** taught by **{f['provider']}**")
                        st.caption(f"Submitted on: {f['created_at']} · {'⭐' * f['rating']} ({f['rating']}/5)")
                        if f["comment"]:
                            st.markdown(
                                f"""
                                <div style="background: #F8FAFC; border-left: 3px solid #1F6F78; padding: 6px 12px;
                                            border-radius: 4px; font-size: 0.9rem; color: #334155; margin-top: 6px;">
                                    "{f['comment']}"
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

    with tab_received:
        st.subheader("📥 Feedback from Your Learners")
        st.caption("Reviews submitted by peers who took sessions taught by you.")

        received = get_feedback_received(user["id"])
        if not received:
            st.info("You haven't received any feedback yet. Complete teaching sessions to earn campus reviews!")
        else:
            avg_rcvd = sum(r["rating"] for r in received) / len(received)
            st.metric(label="Overall Teaching Rating", value=f"{avg_rcvd:.1f} / 5.0 ⭐", delta=f"{len(received)} total reviews")
            st.write("")

            for f in received:
                with st.container(border=True):
                    initials = avatar_initial(f["learner"])
                    c_av, c_txt = st.columns([0.8, 6.2])
                    with c_av:
                        st.markdown(f'<div class="sb-avatar-circle">{initials}</div>', unsafe_allow_html=True)
                    with c_txt:
                        st.markdown(f"**{f['skill']}** learned by **{f['learner']}**")
                        st.caption(f"Received on: {f['created_at']} · {'⭐' * f['rating']} ({f['rating']}/5)")
                        if f["comment"]:
                            st.markdown(
                                f"""
                                <div style="background: #F7F9FA; border-left: 3px solid #67A6AC; padding: 6px 12px;
                                            border-radius: 4px; font-size: 0.9rem; color: #334155; margin-top: 6px;">
                                    "{f['comment']}"
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
