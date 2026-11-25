"""Explore Skills screen: modern responsive skill discovery directory (no SQL)."""
import streamlit as st

from services.feedback import create_report
from services.requests import create_request
from services.skills import get_categories, get_departments, search_listings
from ui.theme import avatar_initial, section_header


def render():
    user = st.session_state.get("user")
    if not user or user.get("role") != "student":
        st.warning("Please sign in as a student to access this page.")
        return

    st.markdown(section_header("🔍", "Explore Peer Skills", "Connect with verified CHRIST University students to exchange knowledge"), unsafe_allow_html=True)

    # Search & Filter Toolbar
    with st.container(border=True):
        col_search, col_dept, col_cat = st.columns([3, 2, 2])
        with col_search:
            query = st.text_input("🔍 Search skills or topics", placeholder="e.g. Python, Figma, Public Speaking...")
        with col_dept:
            depts = ["All Departments"] + get_departments()
            chosen_dept = st.selectbox("Department", depts)
        with col_cat:
            cats = ["All Categories"] + get_categories()
            chosen_cat = st.selectbox("Category", cats)

    rows = search_listings(
        query=query,
        department=None if chosen_dept == "All Departments" else chosen_dept,
        category=None if chosen_cat == "All Categories" else chosen_cat,
        exclude_user=user["id"],
    )

    # Results counter
    st.markdown(
        f'<div style="margin: 1rem 0 0.75rem 0; font-size: 0.9rem; font-weight: 600; color: #6B7280;">'
        f'Showing <b style="color:#1F6F78;">{len(rows)}</b> available listing{"s" if len(rows) != 1 else ""}</div>',
        unsafe_allow_html=True,
    )

    if not rows:
        st.info("No matching listings found. Try adjusting your search query or clearing filters.")
        return

    # Two-column grid
    for i in range(0, len(rows), 2):
        pair = rows[i : i + 2]
        cols = st.columns(2)
        for col, row in zip(cols, pair):
            with col:
                key = f"{row['skill_id']}_{row['provider_id']}"
                initials = avatar_initial(row["provider"])
                rating_str = f"⭐ {row['avg_rating']} ({row['review_count']} reviews)" if row.get("review_count") else "⭐ New Peer Tutor"

                with st.container(border=True):
                    st.markdown(
                        f"""
                        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.75rem;">
                            <div style="display: flex; align-items: center; gap: 0.75rem;">
                                <div class="sb-avatar-circle">{initials}</div>
                                <div>
                                    <div style="font-weight: 700; font-size: 0.95rem; color: #1F2933;">{row['provider']}</div>
                                    <div style="font-size: 0.78rem; color: #6B7280;">{row['department']}</div>
                                </div>
                            </div>
                            <span class="sb-category-chip">{row['category']}</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    st.markdown(f"### **{row['skill']}**")
                    st.caption(f"{rating_str}")

                    if row.get("bio"):
                        st.markdown(
                            f"""
                            <div style="background: #F7F9FA; border-left: 3px solid #1F6F78; padding: 8px 12px;
                                        border-radius: 6px; font-size: 0.86rem; color: #4B5563; margin: 0.6rem 0;">
                                {row['bio']}
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                    with st.expander("✉️ Request to Learn"):
                        message = st.text_area(
                            "Your message",
                            key=f"msg_{key}",
                            placeholder="e.g. Hi! I need help understanding the basics...",
                            label_visibility="collapsed",
                        )
                        if st.button("✉️ Send Request", key=f"send_{key}", use_container_width=True):
                            ok, text = create_request(user["id"], row["provider_id"], row["skill_id"], message)
                            if ok:
                                st.toast(f"Request sent to {row['provider']}!", icon="✅")
                                st.success(text)
                            else:
                                st.error(text)

                    with st.expander("🚩 Report listing"):
                        report_reason = st.text_input("Reason", key=f"rep_{key}", placeholder="Describe issue...")
                        if st.button("🚩 Submit Report", key=f"btn_rep_{key}", use_container_width=True):
                            rep_ok, rep_msg = create_report(
                                reporter_id=user["id"],
                                target_type="skill_listing",
                                reason=report_reason,
                                target_user_id=row["provider_id"],
                                target_skill_id=row["skill_id"],
                            )
                            if rep_ok:
                                st.toast("Report submitted", icon="⚠️")
                                st.success(rep_msg)
                            else:
                                st.error(rep_msg)
