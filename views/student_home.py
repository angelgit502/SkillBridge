"""Student Home Dashboard: personalized overview, metrics, next session countdown & popular skills (no SQL)."""
import streamlit as st

from services.profile import get_user_skills
from services.requests import count_incoming_pending, fetch_requests
from services.sessions import get_next_session, get_user_sessions
from services.skills import get_popular_skills
from ui.navigation import page_for
from ui.theme import avatar_initial, countdown, metric_tile, section_header, status_badge


def render():
    user = st.session_state.get("user")
    if not user or user.get("role") != "student":
        st.warning("Please sign in as a student to access this page.")
        return

    # 1. Hero Welcome Banner
    initials = avatar_initial(user["name"])
    bio_snippet = f'"{user["bio"]}"' if user.get("bio") else "Welcome to your SkillBridge learning hub."

    st.markdown(
        f"""
        <div style="background: linear-gradient(145deg, #1F6F78 0%, #185B63 100%);
                    border-radius: 20px; padding: 2rem 2.25rem; color: #FFFFFF;
                    box-shadow: 0 12px 32px rgba(31, 111, 120, 0.2); margin-bottom: 1.75rem;
                    position: relative; overflow: hidden;">
            <div style="position:absolute;top:-60px;right:-40px;width:200px;height:200px;border-radius:50%;background:rgba(165,203,205,0.12);"></div>
            <div style="position: relative; z-index: 1; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 1rem;">
                <div style="display: flex; align-items: center; gap: 1.15rem;">
                    <div style="width: 56px; height: 56px; border-radius: 50%; background: rgba(255, 255, 255, 0.15);
                                border: 2px solid rgba(255, 255, 255, 0.25); display: flex; align-items: center;
                                justify-content: center; font-size: 1.4rem; font-weight: 800; color: #FFFFFF;">
                        {initials}
                    </div>
                    <div>
                        <div style="font-size: 0.8rem; font-weight: 600; text-transform: uppercase;
                                    letter-spacing: 0.08em; color: rgba(230, 244, 245, 0.9); margin-bottom: 2px;">
                            CHRIST University · {user.get('department', 'Student')}
                        </div>
                        <h2 style="color: #FFFFFF !important; margin: 0; font-size: 1.75rem; font-weight: 800; font-family: 'Poppins', sans-serif !important;">
                            Welcome back, {user['name'].split()[0]}! 👋
                        </h2>
                        <div style="font-size: 0.9rem; color: rgba(255,255,255,0.75); margin-top: 4px;">
                            {bio_snippet}
                        </div>
                    </div>
                </div>
                <div style="background: rgba(255, 255, 255, 0.08); backdrop-filter: blur(12px);
                            border: 1px solid rgba(255, 255, 255, 0.12); border-radius: 14px;
                            padding: 0.65rem 1.1rem; text-align: center;">
                    <span style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: rgba(230,244,245,0.9); font-weight: 600;">Status</span>
                    <div style="font-size: 0.92rem; font-weight: 700; color: #FFFFFF; display: flex; align-items: center; gap: 6px; justify-content: center;">
                        <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #2ECC71;"></span> Active Student
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 2. Key Metrics Row (custom tiles)
    teach_skills = get_user_skills(user["id"], "teach")
    learn_skills = get_user_skills(user["id"], "learn")
    pending_count = count_incoming_pending(user["id"])
    all_sessions = get_user_sessions(user["id"])
    scheduled_sessions = [s for s in all_sessions if s["status"] == "scheduled"]

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(metric_tile("📚", len(teach_skills), "Skills Offered"), unsafe_allow_html=True)
    with m2:
        st.markdown(metric_tile("🎯", len(learn_skills), "Skills Wanted"), unsafe_allow_html=True)
    with m3:
        st.markdown(metric_tile("📬", pending_count, "Pending Requests"), unsafe_allow_html=True)
    with m4:
        st.markdown(metric_tile("📅", len(scheduled_sessions), "Upcoming Sessions"), unsafe_allow_html=True)

    st.write("")

    # 3. Next Upcoming Session Card
    next_sess = get_next_session(user["id"])
    if next_sess:
        with st.container(border=True):
            other_role = "Learner" if user["id"] == next_sess["provider_id"] else "Instructor"
            other_name = next_sess["learner"] if user["id"] == next_sess["provider_id"] else next_sess["provider"]
            other_dept = next_sess["learner_dept"] if user["id"] == next_sess["provider_id"] else next_sess["provider_dept"]

            col_sess_info, col_sess_timer = st.columns([2.2, 1.3])
            with col_sess_info:
                st.markdown(
                    '<span style="background: #E6F4F5; color: #1F6F78; padding: 3px 12px; border-radius: 999px; font-size: 0.74rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.03em;">Next Up</span>',
                    unsafe_allow_html=True,
                )
                st.markdown(f"### 📅 **{next_sess['skill']}** ({next_sess['category']})")
                st.caption(f"{other_role}: **{other_name}** ({other_dept})")
                st.write(f"🕐 **{next_sess['start_time']}** to **{next_sess['end_time']}** (IST)")
            with col_sess_timer:
                st.caption("Live countdown:")
                countdown(next_sess["start_time"])

    # 4. Quick Actions
    st.markdown(section_header("⚡", "Quick Actions", "Jump to common tasks"), unsafe_allow_html=True)
    qa1, qa2, qa3, qa4 = st.columns(4)
    with qa1:
        if st.button("🔍 Explore Skills", use_container_width=True):
            st.switch_page(page_for("discover"))
    with qa2:
        if st.button("📬 View Requests", use_container_width=True):
            st.switch_page(page_for("requests"))
    with qa3:
        if st.button("📅 Sessions", use_container_width=True):
            st.switch_page(page_for("sessions"))
    with qa4:
        if st.button("👤 Profile", use_container_width=True):
            st.switch_page(page_for("profile"))

    st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)

    # 5. Popular Skills & Recent Requests
    col_left, col_right = st.columns([1.1, 1])

    with col_left:
        st.markdown(section_header("🔥", "Popular Skills", "Most requested on campus"), unsafe_allow_html=True)

        popular = get_popular_skills(limit=5)
        if not popular:
            st.info("No skills data available yet.")
        else:
            for idx, item in enumerate(popular):
                with st.container(border=True):
                    c_title, c_stats = st.columns([2.5, 1.5])
                    with c_title:
                        st.markdown(f"**{item['name']}**")
                        st.markdown(f'<span class="sb-category-chip">{item["category"]}</span>', unsafe_allow_html=True)
                    with c_stats:
                        st.markdown(
                            f"""
                            <div style="text-align: right; font-size: 0.82rem; color: #6B7280;">
                                <div><b style="color:#1F6F78;">{item['request_count']}</b> requests</div>
                                <div><b style="color:#1F6F78;">{item['teacher_count']}</b> peers teaching</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

    with col_right:
        st.markdown(section_header("📥", "Recent Requests", "Latest updates on your exchanges"), unsafe_allow_html=True)

        incoming = fetch_requests(user["id"], as_provider=True)
        sent = fetch_requests(user["id"], as_provider=False)
        recent = (incoming + sent)[:4]

        if not recent:
            st.info("No recent requests. Try exploring skills!")
        else:
            for req in recent:
                with st.container(border=True):
                    is_prov = req["provider_id"] == user["id"]
                    partner = req["learner"] if is_prov else req["provider"]
                    role_tag = "From" if is_prov else "To"

                    c_head, c_bdg = st.columns([3, 1.2])
                    with c_head:
                        st.markdown(f"**{req['skill']}** ({role_tag} {partner})")
                        st.caption(f"{req['created_at']}")
                    with c_bdg:
                        st.markdown(status_badge(req["status"]), unsafe_allow_html=True)
