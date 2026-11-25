"""SkillBridge application entry point."""
import streamlit as st

from config import DEPARTMENTS
from db.seed import ADMIN_EMAIL, ADMIN_PASSWORD, DEMO_PASSWORD, STUDENTS, seed_if_empty
from services.auth import get_user_by_id, login, register
from services.requests import count_incoming_pending
from ui.navigation import navigation_for_role, page_for
from ui.theme import avatar_initial, inject_css, metric_tile

# st.set_page_config must be the very first Streamlit call
st.set_page_config(
    page_title="🌉 SkillBridge",
    page_icon="🌉",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()

@st.fragment(run_every=10)
def pending_notice(user_id: int):
    """Sidebar notice for incoming requests. Refreshes every 10 seconds."""
    count = count_incoming_pending(user_id)
    if count:
        st.markdown(
            f'<div class="sb-live">{count} new request{"s" if count != 1 else ""} waiting</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div style="font-size:0.82rem;color:#9B9CB8;padding:4px 0;">● All caught up</div>',
            unsafe_allow_html=True,
        )


def landing_screen():
    st.markdown(
        """
        <main class="sb-landing">
            <div class="sb-landing-orb sb-landing-orb-one" aria-hidden="true"></div>
            <div class="sb-landing-orb sb-landing-orb-two" aria-hidden="true"></div>
            <div class="sb-landing-particle sb-landing-particle-one" aria-hidden="true"></div>
            <div class="sb-landing-particle sb-landing-particle-two" aria-hidden="true"></div>
            <div class="sb-landing-particle sb-landing-particle-three" aria-hidden="true"></div>
            <div class="sb-landing-inner">
                <div class="sb-landing-brand">
                    <span class="sb-landing-logo" aria-hidden="true">🌉</span>
                    <span>SkillBridge</span>
                </div>
                <div class="sb-landing-eyebrow">CHRIST UNIVERSITY · CAMPUS EXCHANGE</div>
                <h1 class="sb-landing-title">Learn. Teach. Connect. Grow.</h1>
                <p class="sb-landing-description">
                    Your campus is full of people who know what you want to learn.
                    Share what you know, discover a new skill, and build connections
                    that make learning better.
                </p>
                <div class="sb-landing-bridge" aria-hidden="true">
                    <svg viewBox="0 0 640 190" role="presentation">
                        <defs>
                            <linearGradient id="sb-art-bridge" x1="0" x2="1">
                                <stop offset="0" stop-color="#2DD4BF"/>
                                <stop offset="0.5" stop-color="#67E8F9"/>
                                <stop offset="1" stop-color="#99F6E4"/>
                            </linearGradient>
                            <linearGradient id="sb-art-shirt-a" x1="0" x2="1">
                                <stop offset="0" stop-color="#2DD4BF"/>
                                <stop offset="1" stop-color="#0EA5A4"/>
                            </linearGradient>
                            <linearGradient id="sb-art-shirt-b" x1="0" x2="1">
                                <stop offset="0" stop-color="#67E8F9"/>
                                <stop offset="1" stop-color="#3B82F6"/>
                            </linearGradient>
                            <filter id="sb-art-glow" x="-40%" y="-40%" width="180%" height="180%">
                                <feGaussianBlur stdDeviation="7" result="blur"/>
                                <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
                            </filter>
                        </defs>
                        <g class="sb-bridge-connections" fill="none" stroke="#67E8F9">
                            <path class="sb-connection-line sb-connection-line-one" d="M104 72 C128 40 155 34 181 49"/>
                            <path class="sb-connection-line sb-connection-line-two" d="M454 49 C482 30 514 42 540 72"/>
                            <path class="sb-connection-line sb-connection-line-three" d="M105 128 C124 103 144 99 161 108"/>
                            <path class="sb-connection-line sb-connection-line-four" d="M480 136 C506 126 528 118 548 102"/>
                        </g>
                        <g class="sb-art-nodes">
                            <circle class="sb-art-node sb-art-node-one" cx="104" cy="72" r="3"/>
                            <circle class="sb-art-node sb-art-node-two" cx="181" cy="49" r="3"/>
                            <circle class="sb-art-node sb-art-node-three" cx="454" cy="49" r="3"/>
                            <circle class="sb-art-node sb-art-node-four" cx="540" cy="72" r="3"/>
                            <circle class="sb-art-node sb-art-node-five" cx="105" cy="128" r="3"/>
                            <circle class="sb-art-node sb-art-node-six" cx="548" cy="102" r="3"/>
                        </g>
                        <g class="sb-art-particles">
                            <circle class="sb-art-particle sb-art-particle-one" cx="133" cy="48" r="2.5"/>
                            <circle class="sb-art-particle sb-art-particle-two" cx="260" cy="43" r="2.5"/>
                            <circle class="sb-art-particle sb-art-particle-three" cx="389" cy="42" r="2.5"/>
                            <circle class="sb-art-particle sb-art-particle-four" cx="516" cy="117" r="2.5"/>
                        </g>
                        <ellipse cx="320" cy="166" rx="222" ry="15" fill="#2DD4BF" opacity=".12"/>
                        <path d="M36 160 Q320 8 604 160" fill="none" stroke="url(#sb-art-bridge)" stroke-width="3" opacity=".56"/>
                        <path d="M36 161 H604" fill="none" stroke="url(#sb-art-bridge)" stroke-width="3" opacity=".65"/>
                        <path d="M92 143 V103 M174 116 V67 M466 116 V67 M548 143 V103"
                              fill="none" stroke="#99F6E4" stroke-width="2" opacity=".5"/>
                        <circle cx="92" cy="99" r="4" fill="#99F6E4"/>
                        <circle cx="174" cy="63" r="4" fill="#67E8F9"/>
                        <circle cx="466" cy="63" r="4" fill="#67E8F9"/>
                        <circle cx="548" cy="99" r="4" fill="#99F6E4"/>
                        <rect x="268" y="130" width="157" height="8" rx="4" fill="#99F6E4" opacity=".7"/>
                        <path d="M292 138 L284 157 M402 138 L410 157" stroke="#5EEAD4" stroke-width="4" stroke-linecap="round"/>
                        <path d="M311 128 V91 Q311 85 317 85 H378 Q384 85 384 91 V128 Z"
                              fill="#083F49" stroke="#67E8F9" stroke-width="3"/>
                        <rect x="320" y="94" width="55" height="27" rx="3" fill="#CCFBF1" opacity=".94"/>
                        <path d="M327 103 H345 M327 109 H355 M327 115 H340" stroke="#0F766E" stroke-width="2" stroke-linecap="round"/>
                        <path d="M307 129 H388 L397 135 H299 Z" fill="url(#sb-art-bridge)"/>
                        <g class="sb-art-student sb-art-student-teacher">
                            <g class="sb-teach-arm">
                                <path d="M257 111 Q281 103 305 116" fill="none" stroke="#F3C9A6" stroke-width="8" stroke-linecap="round"/>
                                <circle cx="306" cy="116" r="5" fill="#F3C9A6"/>
                            </g>
                            <circle cx="232" cy="70" r="17" fill="#F3C9A6"/>
                            <path d="M215 68 Q216 48 235 51 Q248 53 250 68 Q239 63 228 66 Q220 69 215 68" fill="#183B47"/>
                            <path d="M199 127 Q201 91 231 90 Q258 91 264 127 Z" fill="url(#sb-art-shirt-a)"/>
                            <path d="M208 109 Q226 118 251 108" fill="none" stroke="#99F6E4" stroke-width="3" opacity=".8"/>
                        </g>
                        <g class="sb-art-student sb-art-student-peer">
                            <circle cx="447" cy="76" r="16" fill="#D9A982"/>
                            <path d="M431 75 Q432 56 449 58 Q462 60 464 76 Q450 68 431 75" fill="#2B3446"/>
                            <path d="M420 131 Q420 98 447 96 Q474 98 480 131 Z" fill="url(#sb-art-shirt-b)"/>
                            <path d="M421 109 Q407 112 391 119" fill="none" stroke="#D9A982" stroke-width="7" stroke-linecap="round"/>
                            <rect x="477" y="106" width="37" height="28" rx="4" fill="#F0FDFA" stroke="#99F6E4" stroke-width="2"/>
                            <path d="M485 114 H506 M485 120 H501 M485 126 H504" stroke="#0F766E" stroke-width="2" stroke-linecap="round"/>
                        </g>
                        <g class="sb-art-student sb-art-student-observer">
                            <circle cx="164" cy="112" r="12" fill="#F3C9A6"/>
                            <path d="M152 112 Q153 97 165 98 Q176 99 177 112 Q163 106 152 112" fill="#26354B"/>
                            <path d="M145 145 Q146 122 165 121 Q184 122 187 145 Z" fill="#818CF8" opacity=".9"/>
                        </g>
                        <circle cx="232" cy="70" r="27" fill="#5EEAD4" opacity=".12" filter="url(#sb-art-glow)"/>
                    </svg>
                </div>
                <div class="sb-landing-features">
                    <article class="sb-landing-feature">
                        <span class="sb-landing-feature-icon" aria-hidden="true">🎓</span>
                        <h2>Verified Campus Community</h2>
                        <p>A trusted learning network built for CHRIST University students.</p>
                    </article>
                    <article class="sb-landing-feature">
                        <span class="sb-landing-feature-icon" aria-hidden="true">🔄</span>
                        <h2>Every Student Teaches &amp; Learns</h2>
                        <p>Trade your strengths and curiosity through peer-to-peer learning.</p>
                    </article>
                    <article class="sb-landing-feature">
                        <span class="sb-landing-feature-icon" aria-hidden="true">🤝</span>
                        <h2>One-to-One Learning Sessions</h2>
                        <p>Meet, practice together, and turn new skills into real progress.</p>
                    </article>
                </div>
            </div>
        </main>
        """,
        unsafe_allow_html=True,
    )

    _, started_col, _ = st.columns([1, 2, 1])
    with started_col:
        if st.button(
            "Get Started",
            key="landing_get_started",
            type="primary",
            use_container_width=True,
        ):
            st.session_state.auth_page = "login"
            st.rerun()


def auth_screen():
    col_hero, col_card = st.columns([1, 1], gap=None)

    with col_hero:
        st.markdown(
            """
            <div class="sb-split-hero">
                <div style="position:relative;z-index:1;">
                    <div class="sb-brand-pill">CHRIST UNIVERSITY · CAMPUS EXCHANGE</div>
                    <div class="sb-auth-brand">🌉 SkillBridge</div>
                    <div style="font-size: 1.45rem; font-weight: 700; color: #CCFBF1; margin-bottom: 1.25rem; font-family: 'Poppins', sans-serif;">
                        Learn. Teach. Connect. Grow.
                    </div>
                    <p style="font-size: 1.08rem; color: rgba(240, 253, 250, 0.88); line-height: 1.65; margin-bottom: 1.75rem;">
                        SkillBridge is CHRIST University's peer-to-peer knowledge network. Share the skills you excel at,
                        learn what you're curious about, and build real-world campus connections.
                    </p>
                    <div>
                        <div class="sb-feature-item">
                            <div class="sb-feature-icon">🎓</div>
                            <div>
                                <div style="font-weight: 700; font-size: 1rem; color: #FFFFFF;">Verified Campus Community</div>
                                <div style="font-size: 0.93rem; color: rgba(240, 253, 250, 0.82);">Exclusive to authenticated students with university emails.</div>
                            </div>
                        </div>
                        <div class="sb-feature-item">
                            <div class="sb-feature-icon">🔄</div>
                            <div>
                                <div style="font-weight: 700; font-size: 1rem; color: #FFFFFF;">Every Student Teaches & Learns</div>
                                <div style="font-size: 0.93rem; color: rgba(240, 253, 250, 0.82);">No corporate barriers. Learn Python, Figma, Excel, or Guitar directly from peers.</div>
                            </div>
                        </div>
                        <div class="sb-feature-item">
                            <div class="sb-feature-icon">📅</div>
                            <div>
                                <div style="font-weight: 700; font-size: 1rem; color: #FFFFFF;">1-on-1 Sessions & Live Countdown</div>
                                <div style="font-size: 0.93rem; color: rgba(240, 253, 250, 0.82);">Publish open slots, book accepted requests, and track upcoming sessions in IST.</div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="sb-bridge-art" aria-hidden="true">
                    <svg viewBox="0 0 320 170" role="presentation">
                        <path d="M18 132 Q160 26 302 132" fill="none" stroke="#CCFBF1" stroke-width="5" stroke-linecap="round"/>
                        <path d="M18 132 H302" fill="none" stroke="#CCFBF1" stroke-width="5" stroke-linecap="round"/>
                        <path d="M68 113 Q105 69 142 113 M178 113 Q215 69 252 113" fill="none" stroke="#5EEAD4" stroke-width="4" stroke-linecap="round"/>
                        <path d="M86 102 V58 M234 102 V58" fill="none" stroke="#5EEAD4" stroke-width="4" stroke-linecap="round"/>
                        <circle cx="86" cy="48" r="7" fill="#CCFBF1"/>
                        <circle cx="234" cy="48" r="7" fill="#CCFBF1"/>
                        <circle cx="160" cy="127" r="6" fill="#5EEAD4"/>
                    </svg>
                </div>
                <div style="margin-top: 1.5rem; padding-top: 1.25rem; border-top: 1px solid rgba(204, 251, 241, 0.24); font-size: 0.8rem; color: rgba(240, 253, 250, 0.7); position:relative;z-index:1;">
                    🔒 Powered by salted PBKDF2-SHA256 encryption · Built for CHRIST University students
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_card:
        if st.button("← Back to Home", key="back_to_home"):
            st.session_state.auth_page = "home"
            st.rerun()

        st.markdown(
            """
            <div class="sb-auth-heading">
                <div class="sb-auth-title">Welcome Back</div>
                <div class="sb-auth-subtitle">Sign in or create your student account</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        tab_login, tab_register = st.tabs(
            ["🔐 Log In", "✨ Create Account"],
            key="auth_tabs",
            on_change="rerun",
        )

        with tab_login:
            with st.form("login_form"):
                email = st.text_input(
                    "University Email",
                    placeholder="name@christuniversity.in",
                )
                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Enter your password",
                )
                submitted = st.form_submit_button("🔐 Sign In to SkillBridge", use_container_width=True)
                if submitted:
                    user, msg = login(email, password)
                    if user:
                        st.session_state.user = user
                        st.toast(f"Welcome back, {user['name']}!", icon="👋")
                        st.rerun()
                    else:
                        st.error(msg)

            st.markdown(
                f"""
                <div style="margin-top: 0.5rem; padding: 0.85rem 1rem; border: 1px solid #CDE7E8; border-radius: 12px; background: #F4FBFB;">
                    <div style="font-size: 0.95rem; font-weight: 700; color: #1F6F78; margin-bottom: 0.55rem;">Demo Accounts</div>
                    <div style="display: grid; gap: 0.45rem; font-size: 0.86rem; color: #455A64;">
                        <div><strong>Administrator</strong><br>{ADMIN_EMAIL} &nbsp; / &nbsp; {ADMIN_PASSWORD}</div>
                        <div><strong>Student</strong><br>{STUDENTS[0][1]} &nbsp; / &nbsp; {DEMO_PASSWORD}</div>
                        <div>All demo students use: <strong>{DEMO_PASSWORD}</strong></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with tab_register:
            with st.form("register_form"):
                name_col, department_col = st.columns([1.1, 1])
                with name_col:
                    name = st.text_input("Full Name", placeholder="Your name")
                with department_col:
                    department = st.selectbox("Department", DEPARTMENTS)

                reg_email = st.text_input(
                    "University Email",
                    placeholder="name@christuniversity.in",
                )

                password_col, confirm_col = st.columns([1, 1])
                with password_col:
                    reg_password = st.text_input(
                        "Create Password",
                        type="password",
                        placeholder="Min. 8 characters",
                    )
                st.caption("🔒 Minimum 8 characters. Stored as salted PBKDF2-SHA256 hash.")
                with confirm_col:
                    confirm = st.text_input(
                        "Confirm Password",
                        type="password",
                        placeholder="Re-enter",
                    )
                reg_submitted = st.form_submit_button("✨ Create Student Account", use_container_width=True)
                if reg_submitted:
                    ok, text = register(name, reg_email, department, reg_password, confirm)
                    if ok:
                        st.toast("Account created successfully! 🎉", icon="✅")
                        st.success(f"{text} Please switch to the 'Log In' tab to sign in.")
                    else:
                        st.error(text)

def main():
    if "user" not in st.session_state or not st.session_state.user:
        if st.session_state.get("auth_page", "home") == "login":
            seed_if_empty()
            auth_screen()
        else:
            landing_screen()
        return

    user = get_user_by_id(st.session_state.user["id"])
    if not user or not user["is_active"]:
        st.session_state.clear()
        st.warning("Your account is deactivated. Please contact an administrator.")
        return
    st.session_state.user = user

    nav = st.navigation(navigation_for_role(user["role"]))

    # Dark sidebar with user info
    with st.sidebar:
        initials = avatar_initial(user["name"])
        role_label = "Student" if user["role"] == "student" else "Administrator"
        role_color = "#0F766E" if user["role"] == "student" else "#E74C3C"

        st.markdown(
            f"""
            <div style="background: rgba(204, 251, 241, 0.45); border: 1px solid rgba(15, 118, 110, 0.18);
                        border-radius: 14px; padding: 14px 16px; margin-bottom: 1rem;
                        display: flex; align-items: center; gap: 12px;">
                <div style="width: 42px; height: 42px; border-radius: 50%; background: rgba(204, 251, 241, 0.8);
                            border: 2px solid rgba(15, 118, 110, 0.28); display: flex; align-items: center;
                            justify-content: center; font-size: 1rem; font-weight: 800; color: #134E4A !important;
                            flex-shrink: 0;">{initials}</div>
                <div style="overflow: hidden;">
                    <div style="font-weight: 700; font-size: 0.92rem; color: #FFFFFF !important;
                                text-overflow: ellipsis; white-space: nowrap; overflow: hidden;">
                        {user['name']}
                    </div>
                    <div style="font-size: 0.76rem; color: #9B9CB8 !important;">
                        <span style="display:inline-block;width:7px;height:7px;border-radius:50%;background:{role_color};margin-right:5px;"></span>
                        {role_label} · {user.get('department', 'CHRIST University')}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if user["role"] == "student":
            pending_notice(user["id"])
            st.write("")
        else:
            st.page_link(
                page_for("admin"),
                label="Admin Overview",
                icon=":material/dashboard:",
                use_container_width=True,
            )

        if st.button("🚪 Log Out", use_container_width=True, help="Sign out of your SkillBridge session"):
            st.session_state.clear()
            st.switch_page(page_for("home" if user["role"] == "student" else "admin"))

    nav.run()


main()
