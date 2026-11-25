"""Admin Dashboard: professional campus analytics, moderation, student & skill management (no SQL)."""
import plotly.express as px
import pandas as pd
import streamlit as st

from services.admin import get_all_students, open_reports, resolve_report, toggle_user_active
from services.analytics import (
    load_feedback,
    load_ratings,
    load_requests,
    load_sessions_analytics,
    load_skills_summary,
    load_students,
)
from services.skills import add_or_get_skill
from ui.theme import ACCENT, status_badge, style_fig


@st.fragment(run_every=15)
def live_dashboard(dept: str):
    """Metrics and charts that refresh automatically every 15 seconds."""
    requests_df = load_requests(dept)
    students_df = load_students(dept)
    sessions_df = load_sessions_analytics(dept)
    skills_df = load_skills_summary()

    completed_sessions_count = int((sessions_df["status"] == "completed").sum()) if not sessions_df.empty else 0
    pending_requests_count = int((requests_df["status"] == "pending").sum()) if not requests_df.empty else 0
    accepted_requests_count = int((requests_df["status"] == "accepted").sum()) if not requests_df.empty else 0

    # 4 Key Metrics Row
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Registered Students", len(students_df), help="Active students enrolled in SkillBridge")
    c2.metric("Pending Requests", pending_requests_count, help="Requests waiting for provider action")
    c3.metric("Learning Requests", len(requests_df), help="Total requests submitted")
    c4.metric("Accepted / Completed", f"{accepted_requests_count} / {completed_sessions_count}", help="Accepted requests and completed sessions")

    st.write("")

    # Charts Row 1: Top Requested Skills & Requests by Status
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        if requests_df.empty:
            st.info("No request data for this department.")
        else:
            top_skills = (
                requests_df.groupby("skill")
                .size()
                .reset_index(name="requests")
                .sort_values("requests", ascending=False)
                .head(10)
            )
            fig_bar = px.bar(top_skills, x="requests", y="skill", orientation="h")
            fig_bar.update_traces(marker_color=ACCENT)
            fig_bar.update_yaxes(categoryorder="total ascending", title=None)
            fig_bar.update_xaxes(title="Requests")
            st.plotly_chart(style_fig(fig_bar, "Most Requested Skills (Top 10)"), use_container_width=True)

    with col_chart2:
        if requests_df.empty:
            st.info("No status data for this department.")
        else:
            status_counts = requests_df["status"].str.capitalize().value_counts().reset_index()
            status_counts.columns = ["status", "count"]
            fig_pie = px.pie(
                status_counts,
                names="status",
                values="count",
                hole=0.55,
                color="status",
                color_discrete_map={
                    "Pending": "#F59E0B",
                    "Accepted": "#3B82F6",
                    "Completed": "#22C55E",
                    "Rejected": "#EF4444",
                    "Cancelled": "#94A3B8",
                },
            )
            st.plotly_chart(style_fig(fig_pie, "Requests by Status Flow"), use_container_width=True)

    # Charts Row 2: Department-wise Participation (full width)
    all_students = load_students("All")
    if not all_students.empty:
        dept_counts = (
            all_students.groupby("department")
            .size()
            .reset_index(name="students")
            .sort_values("students", ascending=False)
        )
        fig_dept = px.bar(dept_counts, x="department", y="students")
        fig_dept.update_traces(marker_color=ACCENT)
        fig_dept.update_xaxes(title="Department")
        fig_dept.update_yaxes(title="Students Enrolled")
        st.plotly_chart(
            style_fig(fig_dept, "Student Participation by Academic Department"),
            use_container_width=True,
        )

    if not sessions_df.empty:
        session_dates = sessions_df.assign(
            date=pd.to_datetime(sessions_df["created_at"], errors="coerce").dt.date
        ).dropna(subset=["date"])
        if not session_dates.empty:
            sessions_over_time = session_dates.groupby("date").size().reset_index(name="sessions")
            fig_sessions = px.area(sessions_over_time, x="date", y="sessions")
            fig_sessions.update_traces(line_color=ACCENT, fillcolor="rgba(31, 111, 120, 0.12)")
            st.plotly_chart(
                style_fig(fig_sessions, "Sessions Over Time"),
                use_container_width=True,
            )


def render_ratings(dept: str):
    st.subheader("⭐ Provider Ratings & Teaching Performance")
    ratings_df = load_ratings(dept)
    if ratings_df.empty:
        st.info("No ratings recorded yet.")
        return

    summary = (
        ratings_df.groupby(["provider", "provider_dept"])["rating"]
        .agg(["mean", "count"])
        .reset_index()
    )
    summary.columns = ["Provider", "Department", "Average Rating", "Total Reviews"]
    summary["Average Rating"] = summary["Average Rating"].round(2)
    st.dataframe(
        summary.sort_values("Average Rating", ascending=False),
        hide_index=True,
        use_container_width=True,
    )


def render_students(actor_id: int):
    st.subheader("👥 Student Accounts & Verification")
    st.caption("Monitor registered campus users and manage access privileges.")

    students = get_all_students()
    if not students:
        st.info("No students registered.")
        return

    search_user = st.text_input("Filter by student name or email", placeholder="Type name or email...", key="txt_search_stud")
    filtered_students = [
        s for s in students
        if not search_user or search_user.lower() in s["name"].lower() or search_user.lower() in s["email"].lower()
    ]

    for s in filtered_students:
        with st.container(border=True):
            col_info, col_action = st.columns([4, 1.2])
            with col_info:
                active_str = "🟢 Active" if s["is_active"] else "🔴 Deactivated"
                st.markdown(f"**{s['name']}** — {active_str}")
                st.caption(f"📧 {s['email']} · 🎓 {s['department']} · Joined: {s['created_at']}")
                if s.get("bio"):
                    st.write(f'"{s["bio"]}"')
            with col_action:
                btn_label = "⏸️ Deactivate" if s["is_active"] else "▶️ Reactivate"
                target_state = 0 if s["is_active"] else 1
                if st.button(btn_label, key=f"tog_stud_{s['id']}", use_container_width=True):
                    ok, msg = toggle_user_active(actor_id, s["id"], target_state)
                    if ok:
                        st.toast(msg, icon="👤")
                        st.rerun()
                    else:
                        st.error(msg)


def render_skills(actor_id: int):
    st.subheader("💡 Campus Skill Catalog")
    st.caption("View popular skills offered across the university and add official offerings.")

    skills_df = load_skills_summary()
    st.dataframe(skills_df, hide_index=True, use_container_width=True)

    with st.expander("➕ Add Official Skill to Catalog"):
        with st.form("form_admin_add_skill"):
            col_n, col_c = st.columns(2)
            with col_n:
                s_name = st.text_input("Skill Name", placeholder="e.g. Prompt Engineering")
            with col_c:
                s_cat = st.selectbox(
                    "Category",
                    ["Programming", "Design", "Soft Skills", "Productivity", "Music", "Data", "Languages", "Academics", "Other"]
                )
            btn_add = st.form_submit_button("➕ Add Skill to Catalog", use_container_width=True)
            if btn_add:
                s_id, msg = add_or_get_skill(s_name, s_cat, actor_id=actor_id)
                if s_id:
                    st.toast("Skill added to platform catalog!", icon="✅")
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)


def render_monitoring(dept: str):
    st.subheader("📊 Platform Activity Monitoring")
    st.caption("Audit learning requests and scheduled sessions.")

    sub_req, sub_sess = st.tabs(
        ["📬 Learning Requests", "📅 Session Records"],
        key="admin_monitor_tabs",
        on_change="rerun",
    )
    with sub_req:
        reqs_df = load_requests(dept)
        if reqs_df.empty:
            st.info("No requests found.")
        else:
            st.dataframe(reqs_df, hide_index=True, use_container_width=True)

    with sub_sess:
        sess_df = load_sessions_analytics(dept)
        if sess_df.empty:
            st.info("No sessions found.")
        else:
            st.dataframe(sess_df, hide_index=True, use_container_width=True)


def render_feedback(dept: str):
    st.subheader("⭐ Feedback Monitoring")
    feedback_df = load_feedback(dept)
    if feedback_df.empty:
        st.info("No learner feedback has been submitted.")
        return
    st.metric("Average Provider Rating", f"{feedback_df['rating'].mean():.1f} / 5")
    st.dataframe(
        feedback_df[["provider", "provider_dept", "learner", "skill", "rating", "comment", "created_at"]],
        hide_index=True,
        use_container_width=True,
    )


def render_reports(actor_id: int):
    st.subheader("🚩 Content Moderation Queue")
    st.caption("Review flagged student listings and inappropriate content reports.")

    reports = open_reports()
    if not reports:
        st.success("🎉 All clear! There are no open reports in the queue.")
        return

    for rp in reports:
        with st.container(border=True):
            st.markdown(
                f"### Flagged {rp['target_type'].replace('_', ' ').title()}: **{rp['target']}**"
            )
            st.markdown(f"**Reported by:** `{rp['reporter']}` · **Submitted:** {rp['created_at']}")
            if rp["request_id"] is not None:
                st.caption(
                    f"Related learning request #{rp['request_id']} · {rp['request_skill']}"
                )
            st.markdown(
                f"""
                <div style="background: #FEE2E2; border-left: 3px solid #EF4444; padding: 10px 14px;
                            border-radius: 6px; font-size: 0.92rem; color: #991B1B; margin: 0.75rem 0;">
                    <b>Reason:</b> "{rp['reason']}"
                </div>
                """,
                unsafe_allow_html=True,
            )

            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ Resolve Report", key=f"res_{rp['id']}", use_container_width=True):
                    ok, msg = resolve_report(rp["id"], actor_id=actor_id)
                    if ok:
                        st.toast(msg, icon="✅")
                        st.rerun()
                    else:
                        st.error(msg)
            with c2:
                if rp["target_user_id"] is not None:
                    if st.button("⚠️ Resolve & Deactivate User", key=f"res_deact_{rp['id']}", use_container_width=True):
                        ok, msg = resolve_report(
                            rp["id"],
                            actor_id=actor_id,
                            deactivate_user_id=rp["target_user_id"],
                        )
                        if ok:
                            st.toast(msg, icon="⚠️")
                            st.rerun()
                        else:
                            st.error(msg)


def render():
    user = st.session_state.get("user")
    if not user or user.get("role") != "admin":
        st.warning("Please sign in as an administrator to access this dashboard.")
        return

    st.header("📊 Admin Operations Center")
    st.markdown('<p class="sb-tagline">Campus-wide metrics, moderation, skill inventory, and student monitoring.</p>', unsafe_allow_html=True)

    # Department Filter Bar
    all_students = load_students("All")
    departments = ["All Departments"] + sorted(all_students["department"].unique().tolist())
    chosen_dept_raw = st.selectbox("Filter dashboard by department", departments)
    dept = "All" if chosen_dept_raw == "All Departments" else chosen_dept_raw

    # Tabbed Admin Sections
    tab_overview, tab_students, tab_skills, tab_mon, tab_feedback, tab_reports = st.tabs([
        "📊 Admin Overview",
        "👥 Student Management",
        "💡 Skill Management",
        "📋 Monitoring",
        "⭐ Feedback",
        "🚩 Moderation Queue",
    ], key="admin_tabs", on_change="rerun")

    with tab_overview:
        live_dashboard(dept)
        st.markdown("---")
        render_ratings(dept)

    with tab_students:
        render_students(user["id"])

    with tab_skills:
        render_skills(user["id"])

    with tab_mon:
        render_monitoring(dept)

    with tab_feedback:
        render_feedback(dept)

    with tab_reports:
        render_reports(user["id"])
