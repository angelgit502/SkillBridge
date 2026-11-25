"""My Skills screen: manage teaching and learning skill portfolios (no SQL)."""
import streamlit as st

from services.profile import (
    add_user_skill,
    get_user_skills,
    remove_user_skill,
    toggle_skill_hidden,
)
from services.skills import add_or_get_skill, get_all_skills
from ui.theme import section_header


def render():
    user = st.session_state.get("user")
    if not user or user.get("role") != "student":
        st.warning("Please sign in as a student to access this page.")
        return

    st.markdown(section_header("🎓", "My Skills Portfolio", "Manage what you teach and what you want to learn"), unsafe_allow_html=True)

    tab_teach, tab_learn, tab_add = st.tabs(
        ["📚 Skills I Teach", "🎯 Skills I Want to Learn", "➕ Add New Skill"],
        key="my_skills_tabs",
        on_change="rerun",
    )

    with tab_teach:
        teach_skills = get_user_skills(user["id"], kind="teach")
        if not teach_skills:
            st.info("You haven't added any teaching skills yet. Switch to '➕ Add New Skill' to get started!")
        else:
            for ts in teach_skills:
                with st.container(border=True):
                    c_info, c_actions = st.columns([3, 2])
                    with c_info:
                        st.markdown(f"### **{ts['name']}**")
                        st.markdown(f'<span class="sb-category-chip">{ts["category"]}</span>', unsafe_allow_html=True)
                        status_str = "🔴 Hidden from Discover" if ts["is_hidden"] else "🟢 Visible in Discover"
                        st.caption(f"Status: {status_str}")
                    with c_actions:
                        is_hidden = bool(ts["is_hidden"])
                        hide_btn_text = "👁️ Show in Discover" if is_hidden else "🙈 Hide listing"
                        if st.button(hide_btn_text, key=f"hide_{ts['skill_id']}", use_container_width=True):
                            ok, text = toggle_skill_hidden(user["id"], ts["skill_id"], not is_hidden)
                            if ok:
                                st.toast(text, icon="👁️")
                                st.rerun()
                            else:
                                st.error(text)
                        if st.button("🗑️ Remove Skill", key=f"rem_teach_{ts['skill_id']}", use_container_width=True):
                            ok, text = remove_user_skill(user["id"], ts["skill_id"], "teach")
                            if ok:
                                st.toast(text, icon="🗑️")
                                st.rerun()
                            else:
                                st.error(text)

    with tab_learn:
        learn_skills = get_user_skills(user["id"], kind="learn")
        if not learn_skills:
            st.info("No learning goals yet. Add skills you wish to explore!")
        else:
            for ls in learn_skills:
                with st.container(border=True):
                    c_info, c_action = st.columns([3, 1.5])
                    with c_info:
                        st.markdown(f"### **{ls['name']}**")
                        st.markdown(f'<span class="sb-category-chip">{ls["category"]}</span>', unsafe_allow_html=True)
                    with c_action:
                        if st.button("🗑️ Remove Goal", key=f"rem_learn_{ls['skill_id']}", use_container_width=True):
                            ok, text = remove_user_skill(user["id"], ls["skill_id"], "learn")
                            if ok:
                                st.toast(text, icon="🗑️")
                                st.rerun()
                            else:
                                st.error(text)

    with tab_add:
        col_type, col_sel = st.columns([1, 2])
        with col_type:
            kind_choice = st.radio("I want to:", ["Teach this skill", "Learn this skill"], key="radio_kind")
            kind_val = "teach" if "Teach" in kind_choice else "learn"

        with col_sel:
            all_skills = get_all_skills()
            skill_map = {f"{s['name']} ({s['category']})": s["id"] for s in all_skills}
            chosen_skill = st.selectbox(
                "Select a skill from catalog",
                ["-- Choose existing skill --", "-- Create a new custom skill --"] + list(skill_map.keys()),
                key="sel_add_skill",
            )

            if chosen_skill == "-- Create a new custom skill --":
                new_name = st.text_input("New Skill Name", placeholder="e.g. Kotlin, UI Design", key="txt_new_skill")
                new_cat = st.selectbox(
                    "Category",
                    ["Programming", "Design", "Soft Skills", "Productivity", "Music", "Data", "Languages", "Academics", "Other"],
                    key="sel_new_cat",
                )
                if st.button("➕ Create & Add", key="btn_create_skill", use_container_width=True):
                    skill_id, msg = add_or_get_skill(new_name, new_cat, actor_id=user["id"])
                    if skill_id:
                        ok, text = add_user_skill(user["id"], skill_id, kind_val)
                        if ok:
                            st.toast(text, icon="✅")
                            st.rerun()
                        else:
                            st.error(text)
                    else:
                        st.error(msg)
            elif chosen_skill != "-- Choose existing skill --":
                if st.button(f"➕ Add to {kind_val.title()} List", key="btn_add_existing", use_container_width=True):
                    ok, text = add_user_skill(user["id"], skill_map[chosen_skill], kind_val)
                    if ok:
                        st.toast(text, icon="✅")
                        st.rerun()
                    else:
                        st.error(text)
