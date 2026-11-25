"""Profile screen: edit student information and account preferences (no SQL)."""
import streamlit as st

from config import DEPARTMENTS
from services.auth import get_user_by_id
from services.profile import update_profile
from ui.theme import avatar_initial


def render():
    user = st.session_state.get("user")
    if not user or user.get("role") != "student":
        st.warning("Please sign in as a student to access this page.")
        return

    st.header("👤 My Student Profile")
    st.markdown('<p class="sb-tagline">Manage your public campus identity, department details, and personal learning bio.</p>', unsafe_allow_html=True)

    # Fetch latest profile data
    latest = get_user_by_id(user["id"])
    if latest:
        st.session_state.user = latest
        user = latest

    initials = avatar_initial(user["name"])

    # Profile Header Card
    with st.container(border=True):
        col_avatar, col_details = st.columns([1, 4])
        with col_avatar:
            st.markdown(
                f"""
                <div style="width: 84px; height: 84px; border-radius: 50%; background: #E6F4F5;
                            color: #1F6F78; border: 3px solid rgba(31, 111, 120, 0.3);
                            display: flex; align-items: center; justify-content: center;
                            font-size: 2rem; font-weight: 800; margin: 0.5rem auto;">
                    {initials}
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col_details:
            st.markdown(f"### **{user['name']}**")
            st.markdown(f"🎓 **Department:** {user['department']}")
            st.caption(f"📧 **University Email:** {user['email']} · **Joined:** {user.get('created_at', '2026')}")
            if user.get("bio"):
                st.write(f'"{user["bio"]}"')

    st.write("")

    # Edit Profile Form
    with st.container(border=True):
        st.subheader("🛠️ Edit Profile Information")
        st.caption("Keep your details current so fellow students know your background.")

        with st.form("form_edit_profile"):
            name = st.text_input("Full Name", value=user["name"])
            dept_idx = DEPARTMENTS.index(user["department"]) if user["department"] in DEPARTMENTS else 0
            department = st.selectbox("Department", DEPARTMENTS, index=dept_idx)
            bio = st.text_area(
                "Student Bio",
                value=user.get("bio", ""),
                placeholder="Mention what you're passionate about, your academic goals, or topics you love exploring...",
            )

            st.write("")
            submitted = st.form_submit_button("💾 Save Profile Changes", use_container_width=True)

            if submitted:
                ok, msg = update_profile(user["id"], name, department, bio)
                if ok:
                    st.toast("Profile updated successfully!", icon="✅")
                    st.success(msg)
                    st.session_state.user["name"] = name
                    st.session_state.user["department"] = department
                    st.session_state.user["bio"] = bio
                    st.rerun()
                else:
                    st.error(msg)
