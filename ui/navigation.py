"""Shared Streamlit page registry for role-based navigation."""
import streamlit as st


def _registered_pages():
    from views import (
        admin_dashboard,
        discover,
        feedback,
        my_requests,
        my_skills,
        profile,
        sessions,
        student_home,
    )

    return {
        "home": st.Page(
            student_home.render,
            title="Home",
            url_path="home",
            icon=":material/home:",
            default=True,
        ),
        "discover": st.Page(
            discover.render,
            title="Explore Skills",
            url_path="explore-skills",
            icon=":material/search:",
        ),
        "my_skills": st.Page(
            my_skills.render,
            title="My Skills",
            url_path="my-skills",
            icon=":material/school:",
        ),
        "requests": st.Page(
            my_requests.render,
            title="Learning Requests",
            url_path="learning-requests",
            icon=":material/inbox:",
        ),
        "sessions": st.Page(
            sessions.render,
            title="My Sessions",
            url_path="my-sessions",
            icon=":material/event:",
        ),
        "feedback": st.Page(
            feedback.render,
            title="Feedback",
            url_path="feedback",
            icon=":material/star:",
        ),
        "profile": st.Page(
            profile.render,
            title="My Profile",
            url_path="my-profile",
            icon=":material/person:",
        ),
        "admin": st.Page(
            admin_dashboard.render,
            title="Admin Overview",
            url_path="admin-overview",
            icon=":material/dashboard:",
            default=True,
        ),
    }


def navigation_for_role(role: str):
    pages = _registered_pages()
    if role == "admin":
        return {"Admin Operations": [pages["admin"]]}

    return {
        "Learning Hub": [pages["home"], pages["discover"], pages["my_skills"]],
        "Exchanges & Sessions": [
            pages["requests"],
            pages["sessions"],
            pages["feedback"],
        ],
        "Account": [pages["profile"]],
    }


def page_for(page_key: str):
    return _registered_pages()[page_key]
