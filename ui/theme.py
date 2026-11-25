"""UI styling, CSS injection, status badges, and chart themes for SkillBridge."""
from datetime import datetime
from zoneinfo import ZoneInfo
import streamlit as st

STATUS_STYLES = {
    "Pending":   ("#FEF3C7", "#92400E", "#F59E0B"),
    "Accepted":  ("#DBEAFE", "#1E40AF", "#3B82F6"),
    "Awaiting Learner Confirmation": ("#FEF3C7", "#92400E", "#F59E0B"),
    "Completed": ("#DCFCE7", "#166534", "#22C55E"),
    "Rejected":  ("#FEE2E2", "#991B1B", "#EF4444"),
    "Cancelled": ("#F1F5F9", "#475569", "#94A3B8"),
    "Scheduled": ("#DBEAFE", "#1E40AF", "#3B82F6"),
}

ACCENT = "#0F766E"
ACCENT_DARK = "#134E4A"
ACCENT_LIGHT = "#CCFBF1"
ACCENT_SOFT = "#CCFBF1"
NAVY = "#134E4A"
NAVY_LIGHT = "#115E59"
LAVENDER = "#CCFBF1"
PURPLE_GRADIENT = "linear-gradient(135deg, #0F766E 0%, #134E4A 100%)"
ACCENT_SCALE = ["#134E4A", "#0F766E", "#2A968A", "#7DD3C7", "#CCFBF1"]

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Poppins:wght@400;500;600;700;800&display=swap');

:root {
  --sb-primary: #0F766E;
  --sb-primary-dark: #134E4A;
  --sb-primary-light: #5EEAD4;
  --sb-primary-soft: #CCFBF1;
  --sb-primary-gradient: linear-gradient(135deg, #0F766E 0%, #134E4A 100%);
  --sb-hero-gradient: linear-gradient(145deg, #115E59 0%, #134E4A 100%);
  --sb-navy: #134E4A;
  --sb-navy-light: #115E59;
  --sb-lavender: #CCFBF1;
  --sb-bg: #F0FDFA;
  --sb-surface: #FFFFFF;
  --sb-text: #1F2933;
  --sb-text-secondary: #4B5563;
  --sb-text-muted: #6B7280;
  --sb-border: #E5E7EB;
  --sb-border-subtle: #F3F4F6;
  --sb-shadow-xs: 0 1px 3px rgba(31, 41, 51, 0.04);
  --sb-shadow-sm: 0 2px 8px rgba(15, 118, 110, 0.08), 0 1px 3px rgba(31, 41, 51, 0.04);
  --sb-shadow-md: 0 4px 16px rgba(15, 118, 110, 0.11), 0 2px 6px rgba(31, 41, 51, 0.04);
  --sb-shadow-lg: 0 12px 32px rgba(15, 118, 110, 0.15), 0 4px 12px rgba(31, 41, 51, 0.06);
  --sb-shadow-glow: 0 0 28px rgba(15, 118, 110, 0.2);
  --sb-radius-sm: 10px;
  --sb-radius-md: 14px;
  --sb-radius-lg: 18px;
  --sb-radius-xl: 24px;
  --sb-radius-full: 9999px;
}

/* Global Typography & Background */
html, body, [class*="css"] {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
  color: var(--sb-text);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.stApp {
  background: var(--sb-bg);
  color: var(--sb-text);
}

/* Do not leave authenticated navigation visible on public screens after logout. */
.stApp:has(.sb-landing) [data-testid="stSidebar"],
.stApp:has(.sb-split-hero) [data-testid="stSidebar"] {
  display: none !important;
}

.stApp:has(.sb-split-hero) {
  position: relative;
  background:
    radial-gradient(circle at 9% 16%, rgba(15, 118, 110, 0.09) 0 4.5rem, transparent 4.6rem),
    radial-gradient(circle at 92% 78%, rgba(204, 251, 241, 0.8) 0 9rem, transparent 9.1rem),
    radial-gradient(circle at 78% 12%, rgba(17, 94, 89, 0.055) 0 3rem, transparent 3.1rem),
    linear-gradient(125deg, #F0FDFA 0%, #FFFFFF 48%, #CCFBF1 100%) !important;
  background-size: 110% 110%, 110% 110%, 110% 110%, 100% 100%;
  animation: sb-bg-drift 18s ease-in-out infinite alternate;
}

.stApp:has(.sb-split-hero) [data-testid="stAppViewContainer"] {
  position: relative !important;
  min-height: 100vh !important;
  background: transparent !important;
}

.stApp:has(.sb-split-hero) [data-testid="stMain"] {
  position: relative;
  z-index: 1;
  background: transparent !important;
}

.stApp:has(.sb-split-hero) [data-testid="stMainBlockContainer"] {
  background: transparent !important;
}

[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"] {
  background: var(--sb-bg) !important;
}

[data-testid="stMain"],
[data-testid="stMainBlockContainer"] {
  background: var(--sb-bg);
}

[data-testid="stBottom"],
[data-testid="stBottomBlockContainer"] {
  background: var(--sb-bg) !important;
}

[data-testid="stAppViewContainer"] {
  background: var(--sb-bg) !important;
}

.block-container {
  max-width: 1160px;
  padding-top: 1.75rem;
  padding-bottom: 3rem;
}

/* The authentication screen uses the full viewport; other pages keep the
   standard content width and spacing above. */
.block-container:has(.sb-split-hero) {
  box-sizing: border-box;
  width: 100% !important;
  max-width: none !important;
  min-height: 100vh;
  margin: 0 !important;
  padding: clamp(0.75rem, 1.5vh, 1.25rem) clamp(0.75rem, 2vw, 2rem) !important;
}

.block-container:has(.sb-split-hero) [data-testid="stHorizontalBlock"] {
  width: 100%;
  min-height: calc(100vh - 6vh);
  align-items: stretch;
  gap: clamp(1.25rem, 3.5vw, 3.5rem) !important;
}

.block-container:has(.sb-split-hero) [data-testid="stColumn"] > [data-testid="stVerticalBlock"] {
  height: 100%;
  justify-content: center;
}

/* Headings */
h1, h2, h3, h4, h5, h6 {
  font-family: 'Poppins', 'Inter', sans-serif !important;
  font-weight: 700 !important;
  letter-spacing: -0.03em !important;
  color: var(--sb-text) !important;
}
h1 { font-size: 2.1rem !important; margin-bottom: 0.25rem !important; }
h2 { font-size: 1.5rem !important; margin-top: 0.75rem !important; }
h3 { font-size: 1.2rem !important; }

.sb-tagline {
  color: var(--sb-text-muted);
  font-size: 1rem;
  margin-top: -0.35rem;
  margin-bottom: 1.25rem;
  font-weight: 400;
  line-height: 1.5;
}

/* Modern Card Containers */
[data-testid="stVerticalBlockBorderWrapper"] {
  background: var(--sb-surface) !important;
  border: 1px solid var(--sb-border) !important;
  border-radius: var(--sb-radius-lg) !important;
  box-shadow: var(--sb-shadow-sm) !important;
  padding: 1.1rem 1.2rem !important;
  transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1) !important;
  animation: sb-rise 0.35s cubic-bezier(0.16, 1, 0.3, 1) backwards;
}
[data-testid="stVerticalBlockBorderWrapper"]:hover {
  transform: translateY(-3px);
  box-shadow: var(--sb-shadow-md) !important;
  border-color: var(--sb-primary-light) !important;
}

/* Primary and Secondary Buttons */
.stButton > button, .stFormSubmitButton > button {
  font-family: 'Inter', sans-serif !important;
  font-weight: 600 !important;
  font-size: 0.88rem !important;
  border-radius: var(--sb-radius-sm) !important;
  padding: 0.5rem 1.15rem !important;
  letter-spacing: -0.01em !important;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
  border: 1px solid transparent !important;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 6px 20px rgba(15, 118, 110, 0.25) !important;
}
.stButton > button:active, .stFormSubmitButton > button:active {
  transform: translateY(0) !important;
}

/* Metric Cards */
[data-testid="stMetric"] {
  background: var(--sb-surface) !important;
  border: 1px solid var(--sb-border) !important;
  border-radius: var(--sb-radius-md) !important;
  padding: 1rem 1.1rem !important;
  box-shadow: var(--sb-shadow-xs) !important;
  transition: all 0.22s ease !important;
  animation: sb-rise 0.35s ease backwards;
}
[data-testid="stMetric"]:hover {
  border-color: var(--sb-primary-light) !important;
  box-shadow: var(--sb-shadow-sm) !important;
  transform: translateY(-2px);
}
[data-testid="stMetricLabel"] {
  color: var(--sb-text-muted) !important;
  font-size: 0.82rem !important;
  font-weight: 500 !important;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
[data-testid="stMetricValue"] {
  color: var(--sb-text) !important;
  font-weight: 800 !important;
  font-size: 1.9rem !important;
  font-family: 'Poppins', sans-serif !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
  background: #FFFFFF !important;
  border-right: 1px solid var(--sb-border) !important;
}
[data-testid="stSidebar"] * {
  color: var(--sb-text) !important;
}
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
  gap: 0.4rem;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
  color: var(--sb-text) !important;
}
[data-testid="stSidebar"] .stButton > button {
  background: var(--sb-primary-soft) !important;
  color: var(--sb-primary-dark) !important;
  border: 1px solid rgba(15, 118, 110, 0.18) !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
  background: #D7ECEE !important;
  border-color: var(--sb-primary-light) !important;
}

/* Navigation Links in Sidebar */
[data-testid="stSidebar"] a {
  color: var(--sb-text-secondary) !important;
  transition: all 0.15s ease !important;
}
[data-testid="stSidebar"] a:hover {
  color: var(--sb-primary-dark) !important;
}
[data-testid="stSidebar"] [data-testid="stSidebarNavLink"] {
  border-radius: 8px !important;
  padding: 0.4rem 0.75rem !important;
  transition: all 0.15s ease !important;
}
[data-testid="stSidebar"] [data-testid="stSidebarNavLink"]:hover {
  background: var(--sb-primary-soft) !important;
}
[data-testid="stSidebar"] [aria-selected="true"] {
  background: var(--sb-primary-soft) !important;
  border-left: 3px solid var(--sb-primary) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
  gap: 0;
  border-bottom: 2px solid var(--sb-border);
}
.stTabs [data-baseweb="tab"] {
  font-family: 'Inter', sans-serif;
  font-weight: 500;
  font-size: 0.88rem;
  color: var(--sb-text-muted);
  padding: 0.65rem 1.1rem;
  border-bottom: 2px solid transparent;
  transition: all 0.15s ease;
}
.stTabs [data-baseweb="tab"]:hover {
  color: var(--sb-primary);
  background: var(--sb-primary-soft);
  border-radius: 8px 8px 0 0;
}
.stTabs [aria-selected="true"] {
  color: var(--sb-primary) !important;
  font-weight: 600;
  border-bottom-color: var(--sb-primary) !important;
}

/* Text Inputs & Selects */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
  border-radius: var(--sb-radius-sm) !important;
  border-color: var(--sb-border) !important;
  font-family: 'Inter', sans-serif !important;
  transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
  border-color: var(--sb-primary) !important;
  box-shadow: 0 0 0 3px rgba(15, 118, 110, 0.16) !important;
}

/* Keep Streamlit controls, dialogs, tables and expanders on the same palette. */
[data-testid="stExpander"],
[data-testid="stDataFrame"],
[data-testid="stTable"],
[data-testid="stAlert"],
[data-testid="stPopover"],
[data-testid="stDialog"] {
  border-color: var(--sb-border) !important;
}

[data-testid="stExpander"] summary:hover,
[data-testid="stPopover"] button:hover {
  color: var(--sb-primary-dark) !important;
  background: var(--sb-primary-soft) !important;
}

[data-testid="stDataFrame"] *,
[data-testid="stTable"] * {
  color: var(--sb-text) !important;
}

a, [data-testid="stMarkdownContainer"] a {
  color: var(--sb-primary-dark);
}

button[kind="primary"],
[data-testid="stFormSubmitButton"] button,
.stFormSubmitButton > button {
  background: var(--sb-primary) !important;
  border-color: var(--sb-primary) !important;
  color: #FFFFFF !important;
}

button[kind="primary"]:hover,
[data-testid="stFormSubmitButton"] button:hover {
  background: var(--sb-primary-dark) !important;
  border-color: var(--sb-primary-dark) !important;
}

[data-baseweb="select"] > div,
[data-baseweb="input"] > div,
[data-baseweb="textarea"] > div {
  background: #FFFFFF !important;
  border-color: var(--sb-border) !important;
}

[data-baseweb="popover"],
[role="listbox"],
[role="option"] {
  background: #FFFFFF !important;
  color: var(--sb-text) !important;
}

[role="option"]:hover,
[aria-selected="true"][role="option"] {
  background: var(--sb-primary-soft) !important;
}

/* Status Badges */
.sb-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 4px 12px;
  border-radius: var(--sb-radius-full);
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.02em;
  white-space: nowrap;
}

/* Live Notice Dot */
.sb-live {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: #FFFFFF;
  font-size: 0.84rem;
  font-weight: 600;
  background: var(--sb-primary);
  padding: 6px 14px;
  border-radius: var(--sb-radius-full);
  border: none;
}
.sb-live::before {
  content: "";
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #FFFFFF;
  animation: sb-pulse 1.8s infinite;
}

/* Next Session Banner */
.sb-next-banner {
  background: var(--sb-hero-gradient);
  color: #FFFFFF !important;
  border-radius: var(--sb-radius-xl);
  padding: 1.5rem 2rem;
  box-shadow: var(--sb-shadow-lg);
  margin-bottom: 1.5rem;
}

.sb-countdown {
  font-size: 2.2rem;
  font-weight: 800;
  color: #FFFFFF;
  letter-spacing: -0.02em;
  font-variant-numeric: tabular-nums;
  font-family: 'Poppins', sans-serif;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

/* Split-screen Hero */
.sb-split-hero {
  background: linear-gradient(145deg, #115E59 0%, #134E4A 58%, #0E4541 100%);
  border: 1px solid rgba(204, 251, 241, 0.32);
  border-radius: var(--sb-radius-xl);
  padding: clamp(1.5rem, 4vh, 2.75rem) clamp(1.5rem, 3vw, 3rem);
  color: #F0FDFA;
  height: 100%;
  min-height: min(88vh, 900px);
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-shadow: 0 24px 60px rgba(19, 78, 74, 0.24), 0 4px 14px rgba(19, 78, 74, 0.12);
  position: relative;
  overflow: hidden;
  animation: sb-auth-enter 700ms cubic-bezier(0.2, 0.75, 0.25, 1) both;
}
.sb-split-hero::before {
  content: "";
  position: absolute;
  top: -50%;
  right: -30%;
  width: 400px;
  height: 400px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(204, 251, 241, 0.2) 0%, rgba(204, 251, 241, 0) 72%);
  pointer-events: none;
}
.sb-split-hero::after {
  content: "";
  position: absolute;
  bottom: -40%;
  left: -20%;
  width: 300px;
  height: 300px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(15, 118, 110, 0.22) 0%, rgba(15, 118, 110, 0) 72%);
  pointer-events: none;
}

.sb-brand-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(240, 253, 250, 0.96);
  padding: 6px 16px;
  border-radius: var(--sb-radius-full);
  font-size: 0.8rem;
  font-weight: 600;
  color: #134E4A;
  border: 1px solid rgba(204, 251, 241, 0.78);
  width: fit-content;
  margin-bottom: 1.25rem;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.sb-feature-item {
  display: flex;
  align-items: flex-start;
  gap: 0.85rem;
  margin-bottom: 0.75rem;
  padding: 0.75rem 0.85rem;
  border: 1px solid rgba(204, 251, 241, 0.24);
  border-radius: var(--sb-radius-md);
  background: rgba(240, 253, 250, 0.11);
  box-shadow: 0 4px 16px rgba(19, 78, 74, 0.12);
  transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease, background 180ms ease;
}
.sb-feature-item:hover {
  transform: translateY(-3px);
  border-color: rgba(204, 251, 241, 0.54);
  background: rgba(240, 253, 250, 0.19);
  box-shadow: 0 10px 24px rgba(19, 78, 74, 0.2);
}
.sb-feature-icon {
  background: #CCFBF1;
  border-radius: 12px;
  width: 48px;
  height: 48px;
  padding: 9px;
  font-size: 1.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  border: 1px solid rgba(255, 255, 255, 0.76);
  color: #134E4A;
}

.sb-auth-brand {
  color: #FFFFFF;
  font-family: 'Poppins', 'Inter', sans-serif;
  font-size: 3.1rem;
  font-weight: 800;
  letter-spacing: -0.04em;
  margin: 0 0 0.5rem;
  animation: sb-auth-enter 650ms 80ms both;
}

.sb-auth-title {
  color: #134E4A;
  font-family: 'Poppins', 'Inter', sans-serif;
  font-size: 2.1rem;
  font-weight: 800;
  letter-spacing: -0.035em;
  animation: sb-auth-enter 650ms 140ms both;
}

.sb-auth-subtitle {
  color: var(--sb-text-muted);
  font-size: 1rem;
  margin-top: 0.25rem;
  animation: sb-auth-enter 650ms 200ms both;
}

[data-testid="stForm"] {
  background: rgba(255, 255, 255, 0.88) !important;
  border: 1px solid rgba(15, 118, 110, 0.16) !important;
  border-radius: var(--sb-radius-lg) !important;
  box-shadow: 0 18px 48px rgba(19, 78, 74, 0.12), 0 3px 12px rgba(31, 41, 51, 0.04) !important;
  backdrop-filter: blur(14px);
  padding: 1.5rem !important;
  animation: sb-auth-enter 700ms 180ms both;
}

.sb-bridge-art {
  position: absolute;
  top: 3%;
  right: 3%;
  width: clamp(150px, 22vw, 280px);
  opacity: 0.26;
  pointer-events: none;
  animation: sb-drift 7s ease-in-out infinite;
}

.sb-bridge-art svg {
  display: block;
  width: 100%;
  height: auto;
}

.sb-split-hero .sb-brand-pill,
.sb-split-hero .sb-auth-brand,
.sb-split-hero > div:first-child > div:nth-child(3),
.sb-split-hero p,
.sb-split-hero .sb-feature-item,
.sb-split-hero > div:last-child {
  position: relative;
  z-index: 1;
}

.sb-split-hero .sb-feature-item:nth-child(1) { animation: sb-auth-enter 600ms 220ms both; }
.sb-split-hero .sb-feature-item:nth-child(2) { animation: sb-auth-enter 600ms 300ms both; }
.sb-split-hero .sb-feature-item:nth-child(3) { animation: sb-auth-enter 600ms 380ms both; }

.block-container:has(.sb-split-hero) [data-baseweb="tab"] {
  transition: color 160ms ease, background 160ms ease, transform 160ms ease;
}

.block-container:has(.sb-split-hero) [data-baseweb="tab"]:hover {
  color: var(--sb-primary-dark) !important;
  background: var(--sb-primary-soft);
  transform: translateY(-1px);
}

.block-container:has(.sb-split-hero) [data-testid="stForm"] input,
.block-container:has(.sb-split-hero) [data-testid="stForm"] textarea,
.block-container:has(.sb-split-hero) [data-testid="stForm"] [data-baseweb="select"] > div {
  min-height: 3rem;
  border-radius: 12px !important;
  border-color: rgba(15, 118, 110, 0.28) !important;
  background: rgba(255, 255, 255, 0.96) !important;
  transition: border-color 180ms ease, box-shadow 180ms ease, background 180ms ease !important;
}

.block-container:has(.sb-split-hero) [data-testid="stForm"] input:focus,
.block-container:has(.sb-split-hero) [data-testid="stForm"] textarea:focus {
  border-color: #0F766E !important;
  box-shadow: 0 0 0 3px rgba(15, 118, 110, 0.18) !important;
}

.block-container:has(.sb-split-hero) [data-testid="stForm"] label {
  font-size: 1rem !important;
  font-weight: 600 !important;
  color: #134E4A !important;
}

.block-container:has(.sb-split-hero) [data-testid="stForm"] .stFormSubmitButton > button {
  min-height: 3.25rem;
  font-size: 1rem !important;
  font-weight: 700 !important;
  border-radius: 12px !important;
  color: #FFFFFF !important;
  background: linear-gradient(135deg, #0F766E 0%, #134E4A 100%) !important;
  border: 1px solid rgba(19, 78, 74, 0.8) !important;
  box-shadow: 0 8px 20px rgba(19, 78, 74, 0.24);
  transition: transform 180ms ease, box-shadow 180ms ease, filter 180ms ease;
}

.block-container:has(.sb-split-hero) [data-testid="stForm"] .stFormSubmitButton > button:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 26px rgba(19, 78, 74, 0.3);
  filter: brightness(1.06);
}

.block-container:has(.sb-split-hero) [data-testid="stTabContent"] {
  animation: sb-auth-enter 420ms ease both;
}

/* Avatar */
.sb-avatar-circle {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  background: var(--sb-primary-soft);
  color: var(--sb-primary);
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  border: 2px solid rgba(15, 118, 110, 0.2);
  flex-shrink: 0;
}

/* Category Chip */
.sb-category-chip {
  background: var(--sb-primary-soft);
  color: var(--sb-primary-dark);
  padding: 3px 10px;
  border-radius: 8px;
  font-size: 0.74rem;
  font-weight: 600;
  display: inline-block;
}

/* Metric Tile (custom styled, used in dashboards) */
.sb-metric-tile {
  background: var(--sb-surface);
  border: 1px solid var(--sb-border);
  border-radius: var(--sb-radius-md);
  padding: 1.25rem 1.15rem;
  text-align: center;
  transition: all 0.22s ease;
  box-shadow: var(--sb-shadow-xs);
}
.sb-metric-tile:hover {
  transform: translateY(-3px);
  box-shadow: var(--sb-shadow-md);
  border-color: var(--sb-primary-light);
}
.sb-metric-icon {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
}
.sb-metric-value {
  font-family: 'Poppins', sans-serif;
  font-size: 1.85rem;
  font-weight: 800;
  color: var(--sb-text);
  line-height: 1.1;
}
.sb-metric-label {
  font-size: 0.78rem;
  color: var(--sb-text-muted);
  font-weight: 500;
  margin-top: 0.3rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

/* Section Header */
.sb-section-header {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  margin-bottom: 1rem;
  margin-top: 0.5rem;
}
.sb-section-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: var(--sb-primary-soft);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
  flex-shrink: 0;
}
.sb-section-title {
  font-family: 'Poppins', sans-serif;
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--sb-text);
}
.sb-section-subtitle {
  font-size: 0.85rem;
  color: var(--sb-text-muted);
}

/* Divider */
.sb-divider {
  height: 1px;
  background: var(--sb-border);
  margin: 1.5rem 0;
  border: none;
}

/* Animations */
@keyframes sb-rise {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes sb-pulse {
  0%   { box-shadow: 0 0 0 0 rgba(255, 255, 255, 0.5); }
  70%  { box-shadow: 0 0 0 8px rgba(255, 255, 255, 0); }
  100% { box-shadow: 0 0 0 0 rgba(255, 255, 255, 0); }
}
@keyframes sb-float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-4px); }
}
@keyframes sb-auth-enter {
  from { opacity: 0; transform: translateY(14px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes sb-drift {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  50% { transform: translateY(-8px) rotate(1deg); }
}
@keyframes sb-bg-drift {
  from { background-position: 0% 0%, 100% 100%, 70% 0%, 0% 0%; }
  to { background-position: 4% 2%, 96% 98%, 74% 3%, 0% 0%; }
}
@keyframes sb-gradient-shift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

/* Mobile */
@media (max-width: 768px) {
  .block-container { padding: 1rem 0.75rem; }
  h1 { font-size: 1.65rem !important; }
  [data-testid="stMetricValue"] { font-size: 1.4rem !important; }
  .sb-countdown { font-size: 1.5rem; }
  .sb-split-hero { padding: 1.25rem 1rem; margin-bottom: 0; min-height: auto; }
  .sb-auth-brand { font-size: 2rem; }
  .sb-auth-title { font-size: 1.8rem; }
  .sb-bridge-art { width: 150px; opacity: 0.16; }
  .sb-split-hero .sb-brand-pill { margin-bottom: 0.65rem; padding: 4px 11px; font-size: 0.68rem; }
  .sb-split-hero > div:first-child > div:nth-child(3) {
    font-size: 1.15rem !important;
    margin-bottom: 0.75rem !important;
  }
  .sb-split-hero p { display: none; }
  .sb-split-hero > div:first-child > div:last-child {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.45rem;
  }
  .sb-feature-item {
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;
    gap: 0.4rem;
    min-width: 0;
    min-height: 7rem;
    padding: 0.55rem 0.35rem;
    margin-bottom: 0;
  }
  .sb-feature-icon { width: 38px; height: 38px; padding: 7px; }
  .sb-feature-item > div:last-child { width: 100%; }
  .sb-feature-item > div:last-child > div:first-child {
    font-size: 0.72rem !important;
    line-height: 1.2;
    text-align: center;
  }
  .sb-feature-item > div:last-child > div:last-child { display: none; }
  .sb-split-hero > div:last-child {
    margin-top: 0.65rem !important;
    padding-top: 0.55rem !important;
    font-size: 0.68rem !important;
  }
  .sb-metric-value { font-size: 1.5rem; }
  .block-container:has(.sb-split-hero) {
    min-height: 100vh;
    padding: 1rem !important;
  }
  .block-container:has(.sb-split-hero) [data-testid="stHorizontalBlock"] {
    min-height: 0;
    flex-direction: column;
    gap: 1rem !important;
  }
  .block-container:has(.sb-split-hero) [data-testid="stColumn"] > [data-testid="stVerticalBlock"] {
    height: auto;
  }
  .block-container:has(.sb-split-hero) .sb-split-hero {
    min-height: auto;
  }
}

@media (min-width: 769px) and (max-height: 760px) {
  .block-container:has(.sb-split-hero) {
    padding-top: 0.5rem !important;
    padding-bottom: 0.5rem !important;
  }
  .block-container:has(.sb-split-hero) [data-testid="stHorizontalBlock"] {
    min-height: calc(100vh - 1rem);
  }
  .sb-split-hero {
    min-height: auto;
    padding: 1rem 1.5rem;
  }
  .sb-split-hero > div:first-child > .sb-brand-pill {
    margin-bottom: 0.65rem;
    padding: 4px 12px;
    font-size: 0.7rem;
  }
  .sb-auth-brand {
    font-size: 2rem;
    margin-bottom: 0.25rem;
  }
  .sb-split-hero > div:first-child > div:nth-child(3) {
    font-size: 1.1rem !important;
    margin-bottom: 0.75rem !important;
  }
  .sb-split-hero p {
    font-size: 0.9rem !important;
    line-height: 1.45 !important;
    margin-bottom: 1rem !important;
  }
  .sb-feature-item {
    gap: 0.65rem;
    margin-bottom: 0.6rem;
  }
  .sb-feature-icon {
    width: 38px;
    height: 38px;
    padding: 7px;
    font-size: 1rem;
    border-radius: 10px;
  }
  .sb-feature-item {
    padding: 0.4rem 0.55rem;
    margin-bottom: 0.35rem;
  }
  .sb-feature-item > div:last-child > div:first-child {
    font-size: 0.92rem !important;
  }
  .sb-feature-item > div:last-child > div:last-child {
    font-size: 0.82rem !important;
  }
  .sb-split-hero > div:last-child {
    margin-top: 0.75rem !important;
    padding-top: 0.6rem !important;
    font-size: 0.72rem !important;
  }
}

/* Accessibility */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation: none !important;
    transition: none !important;
  }
}

/* Full-viewport authentication layout */
.stApp:has(.sb-split-hero) [data-testid="stHeader"],
.stApp:has(.sb-split-hero) [data-testid="stToolbar"],
.stApp:has(.sb-split-hero) [data-testid="stDecoration"] {
  display: none !important;
}

.stApp:has(.sb-split-hero) [data-testid="stMain"] {
  min-height: 100vh;
  min-height: 100svh;
  padding: 0 !important;
}

.block-container:has(.sb-split-hero) {
  display: flex;
  align-items: stretch;
  min-height: 100vh;
  min-height: 100svh;
  padding: 0 !important;
}

.block-container:has(.sb-split-hero) [data-testid="stHorizontalBlock"] {
  flex: 1 0 auto;
  min-height: 100vh;
  min-height: 100svh;
  align-items: stretch;
  gap: 0 !important;
}

.block-container:has(.sb-split-hero) [data-testid="stColumn"] {
  min-width: 0;
  padding: 0 !important;
}

.block-container:has(.sb-split-hero) [data-testid="stColumn"] > [data-testid="stVerticalBlock"] {
  box-sizing: border-box;
  width: 100%;
  min-height: 100vh;
  min-height: 100svh;
  height: auto;
  justify-content: center;
}

.block-container:has(.sb-split-hero) [data-testid="stColumn"]:first-child > [data-testid="stVerticalBlock"] {
  padding: 0;
}

.block-container:has(.sb-split-hero) [data-testid="stColumn"]:last-child {
  position: relative;
  isolation: isolate;
}

.block-container:has(.sb-split-hero) [data-testid="stColumn"]:last-child::before,
.block-container:has(.sb-split-hero) [data-testid="stColumn"]:last-child::after {
  content: "";
  position: absolute;
  z-index: -1;
  pointer-events: none;
}

.block-container:has(.sb-split-hero) [data-testid="stColumn"]:last-child::before {
  inset: 0;
  background:
    radial-gradient(circle at 82% 19%, rgba(94, 234, 212, 0.28) 0 0.35rem, transparent 0.42rem),
    radial-gradient(circle at 82% 19%, rgba(94, 234, 212, 0.12) 0 4.5rem, transparent 4.6rem),
    radial-gradient(circle at 14% 78%, rgba(15, 118, 110, 0.12) 0 0.45rem, transparent 0.52rem),
    radial-gradient(circle at 14% 78%, rgba(94, 234, 212, 0.12) 0 6rem, transparent 6.1rem),
    linear-gradient(145deg, #F0FDFA 0%, #FFFFFF 52%, #CCFBF1 100%);
  background-size: 110% 110%, 110% 110%, 110% 110%, 110% 110%, 100% 100%;
  animation: sb-bg-drift 20s ease-in-out infinite alternate;
}

.block-container:has(.sb-split-hero) [data-testid="stColumn"]:last-child::after {
  width: min(58%, 390px);
  height: 7rem;
  right: 4%;
  bottom: 3%;
  border-top: 1px solid rgba(15, 118, 110, 0.17);
  border-radius: 50% 50% 0 0;
  transform: rotate(-8deg);
  animation: sb-drift 8s ease-in-out infinite;
}

.block-container:has(.sb-split-hero) [data-testid="stHorizontalBlock"]:has(.sb-split-hero) > [data-testid="stColumn"]:last-child > [data-testid="stVerticalBlock"] {
  position: relative;
  z-index: 1;
  padding: clamp(2rem, 5vh, 4rem) clamp(2rem, 5vw, 5rem);
  gap: 1rem;
}

.sb-split-hero {
  box-sizing: border-box;
  width: 100%;
  min-height: 100vh;
  min-height: 100svh;
  height: auto;
  border: 0;
  border-radius: 0;
  padding: clamp(2rem, 5vh, 4.25rem) clamp(2rem, 4.2vw, 4.5rem);
  box-shadow: none;
  justify-content: space-between;
}

.sb-auth-heading {
  position: relative;
  z-index: 1;
  width: 100%;
  margin: 0 0 0.65rem;
  text-align: center;
}

.sb-auth-title {
  font-size: clamp(2.15rem, 3.2vw, 2.8rem);
  line-height: 1.2;
  white-space: normal;
  overflow: visible;
  overflow-wrap: anywhere;
}

.sb-auth-subtitle {
  font-size: clamp(1.05rem, 1.35vw, 1.2rem);
  line-height: 1.5;
}

.block-container:has(.sb-split-hero) [data-testid="stTabContent"],
.block-container:has(.sb-split-hero) [role="tabpanel"] {
  min-width: 0;
  min-height: 0;
  height: auto;
  overflow: visible;
}

.block-container:has(.sb-split-hero) [data-testid="stForm"] {
  padding: clamp(1.25rem, 2.4vw, 1.75rem) !important;
}

.block-container:has(.sb-split-hero) [data-testid="stForm"] input,
.block-container:has(.sb-split-hero) [data-testid="stForm"] textarea,
.block-container:has(.sb-split-hero) [data-testid="stForm"] [data-baseweb="select"] > div {
  font-size: 1rem !important;
}

.block-container:has(.sb-split-hero) [data-testid="stForm"] label {
  font-size: 1.05rem !important;
}

.block-container:has(.sb-split-hero) [data-baseweb="tab-list"] {
  justify-content: center;
}

.block-container:has(.sb-split-hero) [data-baseweb="tab"] {
  font-size: 1rem;
  padding: 0.75rem 1.15rem;
}

@media (max-width: 768px) {
  .stApp:has(.sb-split-hero) [data-testid="stMain"] {
    min-height: 100vh;
    min-height: 100svh;
  }

  .block-container:has(.sb-split-hero) {
    display: block;
    min-height: 100vh;
    min-height: 100svh;
  }

  .block-container:has(.sb-split-hero) [data-testid="stHorizontalBlock"] {
    min-height: 0;
    flex-direction: column;
  }

  .block-container:has(.sb-split-hero) [data-testid="stColumn"],
  .block-container:has(.sb-split-hero) [data-testid="stColumn"] > [data-testid="stVerticalBlock"] {
    min-height: 0;
  }

  .block-container:has(.sb-split-hero) [data-testid="stColumn"]:first-child > [data-testid="stVerticalBlock"] {
    min-height: 68vh;
    min-height: 68svh;
  }

  .block-container:has(.sb-split-hero) [data-testid="stHorizontalBlock"]:has(.sb-split-hero) > [data-testid="stColumn"]:last-child > [data-testid="stVerticalBlock"] {
    padding: 2rem 1.25rem 2.5rem;
  }

  .sb-split-hero {
    min-height: 68vh;
    min-height: 68svh;
    padding: 1.5rem 1.25rem;
  }

  .sb-auth-title {
    font-size: clamp(2rem, 8vw, 2.4rem);
  }
}

@media (min-width: 769px) and (max-height: 760px) {
  .sb-split-hero {
    padding-top: 1.25rem;
    padding-bottom: 1.25rem;
  }

  .block-container:has(.sb-split-hero) [data-testid="stHorizontalBlock"]:has(.sb-split-hero) > [data-testid="stColumn"]:last-child > [data-testid="stVerticalBlock"] {
    padding-top: 1.25rem;
    padding-bottom: 1.25rem;
  }
}

/* Landing page */
.stApp:has(.sb-landing) {
  color: #F0FDFA;
  background:
    radial-gradient(circle at 8% 18%, rgba(94, 234, 212, 0.12) 0 0.35rem, transparent 0.45rem),
    radial-gradient(circle at 90% 76%, rgba(204, 251, 241, 0.1) 0 0.5rem, transparent 0.62rem),
    linear-gradient(125deg, #063F3B 0%, #064E48 48%, #0F766E 100%) !important;
  background-size: 110% 110%, 110% 110%, 220% 220%;
  animation: sb-gradient-shift 22s ease infinite;
}

.stApp:has(.sb-landing) [data-testid="stHeader"],
.stApp:has(.sb-landing) [data-testid="stToolbar"],
.stApp:has(.sb-landing) [data-testid="stDecoration"] {
  display: none !important;
}

.stApp:has(.sb-landing) [data-testid="stMain"] {
  min-height: 100vh;
  min-height: 100svh;
  padding: 0 !important;
  background: transparent !important;
}

.stApp:has(.sb-landing) [data-testid="stAppViewContainer"],
.stApp:has(.sb-landing) [data-testid="stMainBlockContainer"] {
  background: transparent !important;
}

.block-container:has(.sb-landing) {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-sizing: border-box;
  width: 100% !important;
  max-width: none !important;
  min-height: 100vh;
  min-height: 100svh;
  padding: 0 !important;
  color: #F0FDFA;
}

.sb-landing {
  position: relative;
  display: flex;
  flex: 1 0 auto;
  flex-direction: column;
  justify-content: center;
  box-sizing: border-box;
  width: 100%;
  min-height: calc(100vh - 6rem);
  min-height: calc(100svh - 6rem);
  padding: clamp(2.5rem, 6vh, 5rem) clamp(1.25rem, 6vw, 6rem) 1rem;
  overflow: hidden;
  isolation: isolate;
}

.sb-landing-inner {
  position: relative;
  z-index: 1;
  width: min(100%, 1120px);
  margin: 0 auto;
  text-align: center;
  animation: sb-auth-enter 700ms cubic-bezier(0.2, 0.75, 0.25, 1) both;
}

.sb-landing-brand {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.7rem;
  color: #FFFFFF;
  font-family: 'Poppins', 'Inter', sans-serif;
  font-size: clamp(2rem, 4vw, 3rem);
  font-weight: 800;
  letter-spacing: -0.045em;
}

.sb-landing-logo {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 3.4rem;
  height: 3.4rem;
  border: 1px solid rgba(204, 251, 241, 0.5);
  border-radius: 1.1rem;
  background: rgba(204, 251, 241, 0.14);
  box-shadow: 0 8px 26px rgba(2, 31, 29, 0.18);
  font-size: 1.8rem;
}

.sb-landing-eyebrow {
  width: fit-content;
  margin: 1.4rem auto 0.7rem;
  padding: 0.42rem 0.9rem;
  border: 1px solid rgba(204, 251, 241, 0.24);
  border-radius: 999px;
  background: rgba(204, 251, 241, 0.09);
  color: #CCFBF1;
  font-size: 0.74rem;
  font-weight: 700;
  letter-spacing: 0.12em;
}

.sb-landing-title {
  margin: 0 !important;
  padding: 0 !important;
  color: #FFFFFF !important;
  font-size: clamp(2.25rem, 5vw, 4rem) !important;
  line-height: 1.12 !important;
  letter-spacing: -0.045em !important;
}

.sb-landing-description {
  max-width: 720px;
  margin: 1.1rem auto 0;
  color: rgba(240, 253, 250, 0.82);
  font-size: clamp(1rem, 1.5vw, 1.2rem);
  line-height: 1.7;
}

.sb-landing-bridge {
  width: min(58vw, 510px);
  margin: 0.5rem auto 1.3rem;
  color: rgba(153, 246, 228, 0.5);
  animation: sb-drift 8s ease-in-out infinite;
}

.sb-landing-bridge svg {
  display: block;
  width: 100%;
  height: auto;
  filter: drop-shadow(0 0 16px rgba(94, 234, 212, 0.15));
}

.sb-landing-features {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: clamp(0.8rem, 2vw, 1.35rem);
  margin: 0 auto;
  text-align: left;
}

.sb-landing-feature {
  min-height: 9.5rem;
  padding: clamp(1rem, 2vw, 1.45rem);
  border: 1px solid rgba(204, 251, 241, 0.19);
  border-radius: 1.1rem;
  background: linear-gradient(145deg, rgba(240, 253, 250, 0.13), rgba(240, 253, 250, 0.055));
  box-shadow: 0 12px 32px rgba(2, 31, 29, 0.14);
  backdrop-filter: blur(12px);
  transition: transform 180ms ease, border-color 180ms ease, background 180ms ease, box-shadow 180ms ease;
  animation: sb-auth-enter 650ms both;
}

.sb-landing-feature:nth-child(1) { animation-delay: 180ms; }
.sb-landing-feature:nth-child(2) { animation-delay: 280ms; }
.sb-landing-feature:nth-child(3) { animation-delay: 380ms; }

.sb-landing-feature:hover {
  transform: translateY(-5px);
  border-color: rgba(153, 246, 228, 0.52);
  background: linear-gradient(145deg, rgba(240, 253, 250, 0.19), rgba(240, 253, 250, 0.08));
  box-shadow: 0 18px 38px rgba(2, 31, 29, 0.22);
}

.sb-landing-feature-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.6rem;
  height: 2.6rem;
  margin-bottom: 0.75rem;
  border: 1px solid rgba(204, 251, 241, 0.6);
  border-radius: 0.85rem;
  background: rgba(204, 251, 241, 0.17);
  font-size: 1.25rem;
}

.sb-landing-feature h2 {
  margin: 0 0 0.35rem !important;
  padding: 0 !important;
  color: #FFFFFF !important;
  font-size: clamp(0.98rem, 1.35vw, 1.15rem) !important;
  letter-spacing: -0.02em !important;
}

.sb-landing-feature p {
  margin: 0;
  color: rgba(240, 253, 250, 0.76);
  font-size: 0.9rem;
  line-height: 1.55;
}

.sb-landing-orb {
  position: absolute;
  z-index: 0;
  border-radius: 50%;
  pointer-events: none;
  filter: blur(1px);
  animation: sb-float 7s ease-in-out infinite;
}

.sb-landing-orb-one {
  top: 8%;
  left: 7%;
  width: clamp(5rem, 11vw, 10rem);
  aspect-ratio: 1;
  background: radial-gradient(circle, rgba(94, 234, 212, 0.17), rgba(94, 234, 212, 0));
}

.sb-landing-orb-two {
  right: 5%;
  bottom: 11%;
  width: clamp(8rem, 18vw, 16rem);
  aspect-ratio: 1;
  background: radial-gradient(circle, rgba(204, 251, 241, 0.13), rgba(204, 251, 241, 0));
  animation-delay: -3s;
}

.sb-landing-particle {
  position: absolute;
  z-index: 0;
  width: 0.4rem;
  height: 0.4rem;
  border-radius: 50%;
  background: #99F6E4;
  box-shadow: 0 0 18px rgba(153, 246, 228, 0.85);
  pointer-events: none;
  animation: sb-drift 6s ease-in-out infinite;
}

.sb-landing-particle-one { top: 24%; left: 18%; }
.sb-landing-particle-two { top: 35%; right: 17%; animation-delay: -2s; }
.sb-landing-particle-three { bottom: 16%; left: 28%; animation-delay: -4s; }

.block-container:has(.sb-landing) [data-testid="stHorizontalBlock"] {
  flex: 0 0 auto;
  width: min(100% - 2rem, 430px);
  align-self: center;
  align-items: stretch;
  gap: 1rem !important;
  padding: 0 0 1.5rem;
}

.block-container:has(.sb-landing) [data-testid="stButton"] > button {
  min-height: 3.25rem;
  border: 1px solid rgba(204, 251, 241, 0.65) !important;
  border-radius: 0.9rem !important;
  background: linear-gradient(135deg, #CCFBF1, #99F6E4) !important;
  box-shadow: 0 10px 24px rgba(2, 31, 29, 0.2) !important;
  color: #064E48 !important;
  font-size: 1rem !important;
  font-weight: 800 !important;
  transition: transform 180ms ease, box-shadow 180ms ease, filter 180ms ease !important;
}

.block-container:has(.sb-landing) [data-testid="stButton"] > button:hover {
  transform: translateY(-3px) !important;
  box-shadow: 0 15px 30px rgba(2, 31, 29, 0.28) !important;
  filter: brightness(1.04);
}

@media (max-width: 768px) {
  .sb-landing {
    min-height: calc(100vh - 6rem);
    min-height: calc(100svh - 6rem);
    padding: 2.25rem 1rem 1rem;
  }

  .sb-landing-eyebrow {
    font-size: 0.64rem;
    letter-spacing: 0.08em;
  }

  .sb-landing-description {
    font-size: 0.98rem;
    line-height: 1.55;
  }

  .sb-landing-bridge {
    width: min(78vw, 400px);
    margin: 0.75rem auto;
  }

  .sb-landing-features {
    grid-template-columns: 1fr;
    gap: 0.65rem;
  }

  .sb-landing-feature {
    display: grid;
    grid-template-columns: 2.5rem 1fr;
    column-gap: 0.8rem;
    min-height: auto;
    padding: 0.85rem;
  }

  .sb-landing-feature-icon {
    grid-row: span 2;
    margin: 0;
  }

  .sb-landing-feature p {
    font-size: 0.82rem;
  }

  .block-container:has(.sb-landing) [data-testid="stHorizontalBlock"] {
    width: calc(100% - 2rem);
    max-width: 430px;
    gap: 0.65rem !important;
    padding-bottom: 1rem;
  }

  .block-container:has(.sb-landing) [data-testid="stButton"] > button {
    min-height: 3rem;
    font-size: 0.95rem !important;
  }
}

@media (min-width: 769px) and (max-height: 700px) {
  .sb-landing {
    padding-top: 1rem;
    padding-bottom: 0.25rem;
  }

  .sb-landing-eyebrow {
    margin-top: 0.65rem;
    margin-bottom: 0.4rem;
  }

  .sb-landing-title {
    font-size: clamp(2rem, 4vw, 2.7rem) !important;
  }

  .sb-landing-description {
    margin-top: 0.55rem;
    font-size: 0.98rem;
  }

  .sb-landing-bridge {
    width: min(34vw, 300px);
    margin: 0.15rem auto 0.45rem;
  }

  .sb-landing-feature {
    display: grid;
    grid-template-columns: 2rem minmax(0, 1fr);
    column-gap: 0.6rem;
    min-height: auto;
    padding: 0.7rem;
  }

  .sb-landing-feature-icon {
    grid-row: span 2;
    width: 2rem;
    height: 2rem;
    margin: 0;
  }

  .sb-landing-feature h2 {
    margin: 0 !important;
    font-size: 1.04rem !important;
    line-height: 1.28;
  }

  .sb-landing-feature p {
    margin-top: 0.2rem;
    font-size: 0.9rem;
    line-height: 1.42;
  }
}

@media (prefers-reduced-motion: reduce) {
  .sb-landing,
  .sb-landing-inner,
  .sb-landing-feature,
  .sb-landing-orb,
  .sb-landing-particle,
  .sb-landing-bridge {
    animation: none !important;
  }
}

/* Let the auth page grow with the selected form instead of clipping it. */
.stApp:has(.sb-split-hero),
.stApp:has(.sb-split-hero) [data-testid="stAppViewContainer"],
.stApp:has(.sb-split-hero) [data-testid="stMain"] {
  height: auto !important;
  min-height: 100vh;
  min-height: 100svh;
  overflow: visible !important;
}

.stApp:has(.sb-split-hero) [data-testid="stMainBlockContainer"],
.block-container:has(.sb-split-hero) {
  height: auto !important;
  min-height: 100vh;
  min-height: 100svh;
  flex: 0 0 auto !important;
  gap: 0 !important;
}

.block-container:has(.sb-split-hero) [data-testid="stHorizontalBlock"] {
  height: auto !important;
  flex: 0 0 auto !important;
}

.block-container:has(.sb-split-hero) [data-testid="stColumn"] > [data-testid="stVerticalBlock"] {
  height: auto !important;
  flex: 0 0 auto !important;
}

.block-container:has(.sb-split-hero) [data-testid="stMarkdownContainer"]:has(.sb-split-hero) {
  height: auto !important;
  flex: 0 0 auto !important;
}

.sb-split-hero {
  height: auto !important;
  flex: 0 0 auto !important;
  min-height: 100vh;
  min-height: 100svh;
  overflow: visible;
}

.sb-auth-title {
  line-height: 1.25;
  font-size: clamp(2.5rem, 4vw, 3.25rem);
  letter-spacing: -0.04em;
}

.sb-auth-subtitle {
  font-size: clamp(1.12rem, 1.55vw, 1.3rem);
}

.block-container:has(.sb-split-hero) [data-testid="stForm"] {
  padding: clamp(1.5rem, 3vw, 2rem) !important;
  border: 1px solid rgba(15, 118, 110, 0.2) !important;
  border-radius: 24px !important;
  background: rgba(255, 255, 255, 0.96) !important;
  box-shadow: 0 24px 58px rgba(19, 78, 74, 0.17), 0 5px 16px rgba(31, 41, 51, 0.06) !important;
}

.block-container:has(.sb-split-hero) [data-testid="stForm"] label {
  font-size: 1.15rem !important;
  font-weight: 650 !important;
}

.block-container:has(.sb-split-hero) [data-testid="stForm"] input,
.block-container:has(.sb-split-hero) [data-testid="stForm"] textarea,
.block-container:has(.sb-split-hero) [data-testid="stForm"] [data-baseweb="select"] > div {
  min-height: 3.3rem;
  font-size: 1.1rem !important;
}

.block-container:has(.sb-split-hero) [data-testid="stForm"] .stFormSubmitButton > button {
  min-height: 3.65rem;
  font-size: 1.12rem !important;
  font-weight: 750 !important;
}

.block-container:has(.sb-split-hero) [data-testid="stColumn"]:last-child > [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"]:has([data-testid="stButton"]) {
  width: max-content;
  align-self: flex-start;
}

.block-container:has(.sb-split-hero) [data-testid="stColumn"]:last-child > [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"]:has([data-testid="stButton"]) [data-testid="stButton"] > button {
  min-width: 10.5rem;
  min-height: 3rem;
  width: auto !important;
  padding: 0.65rem 1.1rem !important;
  border: 1px solid rgba(204, 251, 241, 0.35) !important;
  border-radius: 12px !important;
  background: linear-gradient(135deg, #0F766E, #134E4A) !important;
  box-shadow: 0 8px 20px rgba(19, 78, 74, 0.2) !important;
  color: #FFFFFF !important;
  font-size: 1rem !important;
  font-weight: 700 !important;
  transition: transform 180ms ease, box-shadow 180ms ease, filter 180ms ease !important;
}

.block-container:has(.sb-split-hero) [data-testid="stColumn"]:last-child > [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"]:has([data-testid="stButton"]) [data-testid="stButton"] > button:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 26px rgba(19, 78, 74, 0.3) !important;
  filter: brightness(1.08);
}

.sb-landing-feature h2 {
  font-size: clamp(1.1rem, 1.5vw, 1.28rem) !important;
  line-height: 1.3;
}

.sb-landing-feature p {
  font-size: 0.98rem;
  line-height: 1.62;
}

@media (max-width: 768px) {
  .sb-auth-title {
    font-size: clamp(2.25rem, 8vw, 2.8rem);
  }

  .sb-auth-subtitle {
    font-size: 1.12rem;
  }

  .block-container:has(.sb-split-hero) [data-testid="stForm"] label {
    font-size: 1.08rem !important;
  }

  .block-container:has(.sb-split-hero) [data-testid="stForm"] input,
  .block-container:has(.sb-split-hero) [data-testid="stForm"] textarea,
  .block-container:has(.sb-split-hero) [data-testid="stForm"] [data-baseweb="select"] > div {
    font-size: 1rem !important;
  }

  .sb-landing-feature h2 {
    font-size: 1.12rem !important;
  }

  .sb-landing-feature p {
    font-size: 0.92rem;
  }

  .block-container:has(.sb-split-hero) [data-testid="stColumn"]:last-child > [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"]:has([data-testid="stButton"]) {
    width: auto;
    align-self: flex-start;
  }
}

@media (min-width: 769px) and (max-height: 700px) {
  .sb-landing-feature h2 {
    font-size: 1.08rem !important;
  }

  .sb-landing-feature p {
    font-size: 0.94rem;
  }
}

.sb-landing {
  min-height: calc(100vh - 6.25rem);
  min-height: calc(100svh - 6.25rem);
}

.block-container:has(.sb-landing) [data-testid="stButton"] > button {
  min-height: 3.6rem;
  padding: 0.85rem 1.35rem !important;
  font-size: 1.08rem !important;
}

.sb-landing-bridge {
  position: relative;
  isolation: isolate;
  color: rgba(153, 246, 228, 0.78);
  filter: drop-shadow(0 8px 18px rgba(45, 212, 191, 0.14));
  transition: filter 220ms ease;
}

.sb-landing-bridge:hover {
  filter: drop-shadow(0 10px 24px rgba(45, 212, 191, 0.28));
}

.sb-landing-bridge svg {
  overflow: visible;
}

.sb-art-student {
  transform-box: fill-box;
  transform-origin: center;
  animation: sb-student-bob 4.8s ease-in-out infinite;
}

.sb-art-student-peer { animation-delay: -1.6s; }
.sb-art-student-observer { animation-delay: -3.2s; }

.sb-teach-arm {
  transform-box: fill-box;
  transform-origin: left center;
  animation: sb-teach 3.6s ease-in-out infinite;
}

.sb-connection-line {
  stroke-width: 1.7;
  stroke-linecap: round;
  stroke-dasharray: 4 9;
  opacity: 0.34;
  filter: drop-shadow(0 0 3px rgba(103, 232, 249, 0.55));
  animation: sb-connection-flow 8s linear infinite;
}

.sb-connection-line-two { animation-delay: -2s; }
.sb-connection-line-three { animation-delay: -4s; }
.sb-connection-line-four { animation-delay: -6s; }

.sb-art-node {
  fill: #99F6E4;
  filter: drop-shadow(0 0 4px rgba(103, 232, 249, 0.9));
  transform-box: fill-box;
  transform-origin: center;
  animation: sb-node-pulse 3.4s ease-in-out infinite;
}

.sb-art-node-two { animation-delay: -0.55s; }
.sb-art-node-three { animation-delay: -1.1s; }
.sb-art-node-four { animation-delay: -1.65s; }
.sb-art-node-five { animation-delay: -2.2s; }
.sb-art-node-six { animation-delay: -2.75s; }

.sb-art-particle {
  fill: #67E8F9;
  filter: drop-shadow(0 0 5px rgba(103, 232, 249, 0.95));
  transform-box: fill-box;
  transform-origin: center;
  animation: sb-art-particle-drift 4.6s ease-in-out infinite;
}

.sb-art-particle-two { animation-delay: -1.15s; }
.sb-art-particle-three { animation-delay: -2.3s; }
.sb-art-particle-four { animation-delay: -3.45s; }

.sb-landing-feature {
  box-sizing: border-box;
  border-color: rgba(103, 232, 249, 0.24);
  background: linear-gradient(145deg, rgba(45, 212, 191, 0.16), rgba(103, 232, 249, 0.08) 55%, rgba(240, 253, 250, 0.055));
}

.sb-landing-feature:hover {
  border-color: rgba(103, 232, 249, 0.64);
  box-shadow: 0 18px 38px rgba(2, 31, 29, 0.22), 0 0 24px rgba(45, 212, 191, 0.12);
}

.sb-landing-feature-icon {
  color: #CCFBF1;
  background: linear-gradient(145deg, rgba(45, 212, 191, 0.3), rgba(103, 232, 249, 0.2));
  box-shadow: 0 0 20px rgba(45, 212, 191, 0.12);
}

.sb-landing-feature h2 {
  font-size: clamp(1.12rem, 1.6vw, 1.32rem) !important;
}

.sb-landing-feature p {
  font-size: 1rem;
}

.block-container:has(.sb-landing) [data-testid="stButton"] > button {
  min-height: 3.75rem;
  border-radius: 1rem !important;
  font-size: 1.2rem !important;
  letter-spacing: 0.01em !important;
}

.block-container:has(.sb-landing) [data-testid="stButton"] > button p {
  font-size: 1.2rem !important;
}

.block-container:has(.sb-split-hero) [data-baseweb="tab-list"] {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.65rem;
  width: 100%;
  border: 0 !important;
}

.block-container:has(.sb-split-hero) [data-baseweb="tab"] {
  display: flex;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
  width: 100%;
  min-height: 3.5rem;
  padding: 0.8rem 0.65rem;
  border: 1px solid rgba(15, 118, 110, 0.16);
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.68);
  color: #315B5A;
  font-size: 1.08rem;
  font-weight: 700;
  transition: background 180ms ease, color 180ms ease, border-color 180ms ease, transform 180ms ease, box-shadow 180ms ease;
}

.block-container:has(.sb-split-hero) [data-baseweb="tab"]:hover {
  transform: translateY(-2px);
  border-color: rgba(15, 118, 110, 0.42);
  box-shadow: 0 6px 16px rgba(19, 78, 74, 0.1);
}

.block-container:has(.sb-split-hero) [data-baseweb="tab"][aria-selected="true"] {
  border-color: #0F766E !important;
  background: linear-gradient(135deg, #0F766E, #134E4A) !important;
  box-shadow: 0 8px 20px rgba(19, 78, 74, 0.2);
  color: #FFFFFF !important;
}

.block-container:has(.sb-split-hero) [data-baseweb="tab-highlight"] {
  display: none !important;
}

.block-container:has(.sb-split-hero) [role="tablist"] {
  display: grid !important;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.65rem;
  border: 0 !important;
}

.block-container:has(.sb-split-hero) [role="tab"] {
  width: 100%;
  min-height: 3.5rem;
  border: 1px solid rgba(15, 118, 110, 0.28);
  border-radius: 14px;
  background: #E5F8F5;
  color: #315B5A;
  font-size: 1.08rem;
  font-weight: 700;
}

.block-container:has(.sb-split-hero) [role="tab"][aria-selected="true"] {
  background: linear-gradient(135deg, #0F766E, #134E4A) !important;
  color: #FFFFFF !important;
}

.block-container:has(.sb-split-hero) [data-testid="stForm"] .stFormSubmitButton > button {
  min-height: 3.9rem;
  padding: 0.85rem 1.25rem !important;
  font-size: 1.15rem !important;
}

@keyframes sb-teach {
  0%, 100% { transform: rotate(0deg); }
  50% { transform: rotate(-6deg); }
}

@keyframes sb-student-bob {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-4px); }
}

@keyframes sb-connection-flow {
  0% { stroke-dashoffset: 0; opacity: 0.2; }
  50% { opacity: 0.52; }
  100% { stroke-dashoffset: -39; opacity: 0.2; }
}

@keyframes sb-node-pulse {
  0%, 100% { opacity: 0.55; transform: scale(0.82); }
  50% { opacity: 1; transform: scale(1.28); }
}

@keyframes sb-art-particle-drift {
  0%, 100% { opacity: 0.3; transform: translate(0, 0); }
  50% { opacity: 1; transform: translate(0, -7px); }
}

@media (min-width: 769px) {
  .stApp:has(.sb-split-hero),
  .stApp:has(.sb-split-hero) [data-testid="stAppViewContainer"],
  .stApp:has(.sb-split-hero) [data-testid="stMain"] {
    box-sizing: border-box;
    width: 100%;
    height: 100vh !important;
    height: 100svh !important;
    min-height: 100vh !important;
    min-height: 100svh !important;
    max-height: 100vh !important;
    max-height: 100svh !important;
    overflow: hidden !important;
  }

  .stApp:has(.sb-split-hero) [data-testid="stMain"] {
    overflow-y: auto !important;
    overflow-x: hidden !important;
  }

  .stApp:has(.sb-split-hero) [data-testid="stMainBlockContainer"],
  .block-container:has(.sb-split-hero) {
    box-sizing: border-box;
    width: 100% !important;
    height: 100vh !important;
    height: 100svh !important;
    min-height: 100vh !important;
    min-height: 100svh !important;
    max-height: 100vh !important;
    max-height: 100svh !important;
    overflow: hidden !important;
    padding: 0 !important;
  }

  .block-container:has(.sb-split-hero) > [data-testid="stVerticalBlock"] {
    height: 100% !important;
    min-height: 0 !important;
    gap: 0 !important;
  }

  .block-container:has(.sb-split-hero) [data-testid="stHorizontalBlock"] {
    height: 100vh !important;
    height: 100svh !important;
    min-height: 100vh !important;
    min-height: 100svh !important;
    max-height: 100vh !important;
    max-height: 100svh !important;
    margin: 0 !important;
  }

  .block-container:has(.sb-split-hero) [data-testid="stHorizontalBlock"]:has(.sb-split-hero) > [data-testid="stColumn"] > [data-testid="stVerticalBlock"] {
    box-sizing: border-box;
    height: 100vh !important;
    height: 100svh !important;
    min-height: 100vh !important;
    min-height: 100svh !important;
  }

  .block-container:has(.sb-split-hero) [data-testid="stHorizontalBlock"]:not(:has(.sb-split-hero)) {
    height: auto !important;
    min-height: 0 !important;
    flex: 0 1 auto !important;
    gap: 0.6rem !important;
  }

  .block-container:has(.sb-split-hero) [data-testid="stHorizontalBlock"]:not(:has(.sb-split-hero)) [data-testid="stColumn"] > [data-testid="stVerticalBlock"] {
    height: auto !important;
    min-height: 0 !important;
    flex: 1 1 0% !important;
  }

  .sb-split-hero {
    box-sizing: border-box;
    width: 100%;
    height: 100vh !important;
    height: 100svh !important;
    min-height: 100vh !important;
    min-height: 100svh !important;
    overflow: hidden;
  }
}

@media (min-width: 769px) and (max-height: 700px) {
  .sb-split-hero {
    padding: 0.8rem 1.2rem;
  }

  .sb-split-hero > div:first-child > .sb-brand-pill {
    margin-bottom: 0.45rem;
    padding: 3px 10px;
    font-size: 0.62rem;
  }

  .sb-auth-brand {
    margin-bottom: 0.15rem;
    font-size: 1.85rem;
  }

  .sb-split-hero > div:first-child > div:nth-child(3) {
    margin-bottom: 0.5rem !important;
    font-size: 1rem !important;
  }

  .sb-split-hero > div:first-child > p,
  .sb-split-hero .sb-feature-item > div:last-child > div:last-child {
    display: none !important;
  }

  .sb-feature-item {
    gap: 0.55rem;
    margin-bottom: 0.35rem;
    padding: 0.3rem 0.45rem;
  }

  .sb-feature-icon {
    width: 32px;
    height: 32px;
    padding: 5px;
    font-size: 0.95rem;
  }

  .sb-split-hero .sb-feature-item > div:last-child > div:first-child {
    font-size: 0.9rem !important;
  }

  .sb-split-hero > div:last-child {
    margin-top: 0.45rem !important;
    padding-top: 0.4rem !important;
    font-size: 0.62rem !important;
  }

  .block-container:has(.sb-split-hero) [data-testid="stHorizontalBlock"]:has(.sb-split-hero) > [data-testid="stColumn"]:last-child > [data-testid="stVerticalBlock"] {
    padding: 0.5rem 1.1rem;
    gap: 0.4rem;
  }

  .sb-auth-heading {
    margin-bottom: 0.1rem;
  }

  .sb-auth-title {
    font-size: 2.45rem;
  }

  .sb-auth-subtitle {
    margin-top: 0.1rem;
    font-size: 1rem;
  }

  .block-container:has(.sb-split-hero) [data-baseweb="tab-list"] {
    gap: 0.4rem;
  }

  .block-container:has(.sb-split-hero) [data-baseweb="tab"] {
    min-height: 2.85rem;
    padding: 0.5rem;
    font-size: 0.98rem;
  }

  .block-container:has(.sb-split-hero) [role="tab"] {
    min-height: 2.85rem;
    padding: 0.5rem;
    font-size: 0.98rem;
  }

  .block-container:has(.sb-split-hero) [data-testid="stForm"] {
    padding: 0.8rem !important;
  }

  .block-container:has(.sb-split-hero) [data-testid="stForm"] [data-testid="stVerticalBlock"] {
    gap: 0.35rem !important;
  }

  .block-container:has(.sb-split-hero) [data-testid="stForm"] label {
    font-size: 1rem !important;
  }

  .block-container:has(.sb-split-hero) [data-testid="stForm"] input,
  .block-container:has(.sb-split-hero) [data-testid="stForm"] [data-baseweb="select"] > div {
    min-height: 2.55rem;
    font-size: 0.98rem !important;
  }

  .block-container:has(.sb-split-hero) [data-testid="stForm"] .stFormSubmitButton > button {
    min-height: 3rem;
    padding: 0.55rem 1rem !important;
    font-size: 1rem !important;
  }

  .block-container:has(.sb-split-hero) [data-testid="stExpander"] summary {
    min-height: 2.25rem;
    padding-top: 0.35rem;
    padding-bottom: 0.35rem;
  }

  .block-container:has(.sb-split-hero) [data-testid="stColumn"]:last-child > [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"]:has([data-testid="stButton"]) [data-testid="stButton"] > button {
    min-height: 2.6rem;
    padding: 0.45rem 0.9rem !important;
  }
}

@media (max-width: 768px) {
  .sb-landing {
    min-height: calc(100vh - 6.5rem);
    min-height: calc(100svh - 6.5rem);
  }

  .block-container:has(.sb-landing) [data-testid="stButton"] > button {
    min-height: 3.4rem;
    padding: 0.7rem 0.9rem !important;
    font-size: 1.1rem !important;
  }

  .block-container:has(.sb-landing) [data-testid="stButton"] > button p {
    font-size: 1.1rem !important;
  }

  .block-container:has(.sb-split-hero) [data-baseweb="tab"] {
    min-height: 3.25rem;
    font-size: 1rem;
  }
}

@media (min-width: 769px) and (max-height: 700px) {
  .sb-landing-bridge {
    width: min(30vw, 260px);
    margin: 0.1rem auto 0.3rem;
  }

  .block-container:has(.sb-split-hero) [data-testid="stHorizontalBlock"]:has(.sb-split-hero) > [data-testid="stColumn"]:last-child > [data-testid="stVerticalBlock"] {
    justify-content: flex-start;
    padding: 0.35rem 1.1rem;
    gap: 0.25rem;
  }

  .sb-auth-heading {
    margin-bottom: 0;
  }

  .sb-auth-title {
    font-size: 2.3rem;
    line-height: 1.18;
  }

  .sb-auth-subtitle {
    font-size: 0.95rem;
  }

  .block-container:has(.sb-split-hero) [data-testid="stForm"] {
    padding: 0.55rem !important;
  }

  .block-container:has(.sb-split-hero) [data-testid="stForm"] [data-testid="stVerticalBlock"] {
    gap: 0.25rem !important;
  }

  .block-container:has(.sb-split-hero) [data-testid="stForm"] label {
    font-size: 0.98rem !important;
  }

  .block-container:has(.sb-split-hero) [data-testid="stForm"] input,
  .block-container:has(.sb-split-hero) [data-testid="stForm"] [data-baseweb="select"] > div {
    min-height: 2.35rem;
    font-size: 0.95rem !important;
  }

  .block-container:has(.sb-split-hero) [data-testid="stForm"] [data-testid="stSelectbox"],
  .block-container:has(.sb-split-hero) [data-testid="stForm"] [data-baseweb="select"] {
    width: 100% !important;
  }

  .block-container:has(.sb-split-hero) [data-testid="stForm"] .stFormSubmitButton > button {
    min-height: 2.75rem;
    font-size: 0.98rem !important;
  }

  .block-container:has(.sb-split-hero) [role="tab"] {
    min-height: 2.65rem;
    padding: 0.35rem;
    font-size: 0.94rem;
  }

  .block-container:has(.sb-split-hero) [data-testid="stExpander"] summary {
    min-height: 1.9rem;
  }

  .block-container:has(.sb-split-hero) [data-testid="stColumn"]:last-child > [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"]:has([data-testid="stButton"]) [data-testid="stButton"] > button {
    min-height: 2.4rem;
    padding: 0.35rem 0.8rem !important;
  }
}

@media (min-width: 769px) {
  .stApp:has(.sb-landing),
  .stApp:has(.sb-landing) [data-testid="stAppViewContainer"],
  .stApp:has(.sb-landing) [data-testid="stMain"] {
    box-sizing: border-box;
    height: 100vh !important;
    height: 100svh !important;
    min-height: 100vh !important;
    min-height: 100svh !important;
    max-height: 100vh !important;
    max-height: 100svh !important;
    overflow: hidden !important;
  }

  .stApp:has(.sb-landing) [data-testid="stMainBlockContainer"],
  .block-container:has(.sb-landing) {
    box-sizing: border-box;
    height: 100vh !important;
    height: 100svh !important;
    min-height: 100vh !important;
    min-height: 100svh !important;
    max-height: 100vh !important;
    max-height: 100svh !important;
    overflow: hidden !important;
    padding: 0 !important;
  }

  .block-container:has(.sb-landing) > [data-testid="stVerticalBlock"] {
    height: 100% !important;
    min-height: 0 !important;
    gap: 0 !important;
  }

  .block-container:has(.sb-landing) > [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"]:has(.sb-landing) {
    flex: 0 0 auto !important;
    min-height: calc(100vh - 6rem) !important;
    min-height: calc(100svh - 6rem) !important;
  }

  .block-container:has(.sb-landing) [data-testid="stHorizontalBlock"] {
    flex: 0 0 auto;
  }
}

@media (max-width: 768px) {
  .block-container:has(.sb-split-hero) [data-testid="stHorizontalBlock"]:has(.sb-split-hero) {
    flex-direction: column !important;
  }

  .block-container:has(.sb-split-hero) [data-testid="stColumn"] {
    flex: 1 1 100% !important;
    width: 100% !important;
  }

  .block-container:has(.sb-split-hero) [data-testid="stColumn"] > [data-testid="stVerticalBlock"] {
    width: 100% !important;
    justify-content: flex-start !important;
  }

  .block-container:has(.sb-split-hero) [data-testid="stColumn"]:first-child > [data-testid="stVerticalBlock"] {
    min-height: 0 !important;
  }

  .sb-split-hero {
    width: 100%;
  }

  .sb-split-hero::before {
    width: min(80vw, 300px);
    height: min(80vw, 300px);
    right: 0;
  }
}

.sb-split-hero .sb-brand-pill {
  font-size: 0.88rem !important;
}

.sb-split-hero .sb-auth-brand {
  font-size: clamp(2.15rem, 3.5vw, 3.3rem) !important;
}

.sb-split-hero > div:first-child > div:nth-child(3) {
  font-size: clamp(1.2rem, 2vw, 1.55rem) !important;
}

.sb-split-hero > div:first-child > p {
  font-size: 1.15rem !important;
}

.sb-split-hero .sb-feature-item > div:last-child > div:first-child {
  font-size: 1.05rem !important;
}

.sb-split-hero .sb-feature-item > div:last-child > div:last-child {
  font-size: 1rem !important;
}

.sb-split-hero > div:last-child {
  font-size: 0.9rem !important;
}

.block-container:has(.sb-split-hero) .sb-auth-title {
  font-size: clamp(2.65rem, 4vw, 3.5rem) !important;
}

.block-container:has(.sb-split-hero) .sb-auth-subtitle {
  font-size: clamp(1.2rem, 1.7vw, 1.4rem) !important;
}

.block-container:has(.sb-split-hero) [role="tab"],
.block-container:has(.sb-split-hero) [role="tab"] p,
.block-container:has(.sb-split-hero) [data-baseweb="tab"],
.block-container:has(.sb-split-hero) [data-baseweb="tab"] p {
  font-size: 1.18rem !important;
}

.block-container:has(.sb-split-hero) [data-testid="stForm"] label {
  font-size: 1.2rem !important;
}

.block-container:has(.sb-split-hero) [data-testid="stForm"] input,
.block-container:has(.sb-split-hero) [data-testid="stForm"] input::placeholder,
.block-container:has(.sb-split-hero) [data-testid="stForm"] textarea,
.block-container:has(.sb-split-hero) [data-testid="stForm"] [data-baseweb="select"] > div {
  font-size: 1.2rem !important;
}

.block-container:has(.sb-split-hero) [data-testid="stForm"] .stFormSubmitButton > button,
.block-container:has(.sb-split-hero) [data-testid="stForm"] .stFormSubmitButton > button p {
  font-size: 1.2rem !important;
}

.block-container:has(.sb-split-hero) [data-testid="stButton"] > button,
.block-container:has(.sb-split-hero) [data-testid="stButton"] > button p {
  font-size: 1.18rem !important;
}

.block-container:has(.sb-split-hero) [data-testid="stColumn"]:last-child > [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"]:has([data-testid="stButton"]) [data-testid="stButton"] > button,
.block-container:has(.sb-split-hero) [data-testid="stColumn"]:last-child > [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"]:has([data-testid="stButton"]) [data-testid="stButton"] > button p {
  font-size: 1.18rem !important;
}

.block-container:has(.sb-split-hero) [data-testid="stCaptionContainer"],
.block-container:has(.sb-split-hero) [data-testid="stCaptionContainer"] p {
  font-size: 1.05rem !important;
}

.block-container:has(.sb-split-hero) [data-testid="stExpander"] summary,
.block-container:has(.sb-split-hero) [data-testid="stExpander"] summary p,
.block-container:has(.sb-split-hero) [data-testid="stAlert"] {
  font-size: 1.1rem !important;
}

.stApp:has(.sb-split-hero) [role="option"] {
  font-size: 1.1rem !important;
}

/* Full-width, readable workspace for authenticated student and admin pages. */
.stApp:not(:has(.sb-split-hero)):not(:has(.sb-landing)) [data-testid="stMain"] {
  min-height: calc(100vh - 3.5rem);
}

.stApp:not(:has(.sb-split-hero)):not(:has(.sb-landing)) .block-container {
  box-sizing: border-box;
  width: 100% !important;
  max-width: none !important;
  min-height: calc(100vh - 3.5rem);
  margin: 0 !important;
  padding: clamp(1.1rem, 2vh, 1.75rem) clamp(1rem, 3vw, 3rem) 1.75rem !important;
}

.stApp:not(:has(.sb-split-hero)):not(:has(.sb-landing)) [data-testid="stMain"] h1 {
  font-size: clamp(2rem, 2.6vw, 2.5rem) !important;
}

.stApp:not(:has(.sb-split-hero)):not(:has(.sb-landing)) [data-testid="stMain"] h2 {
  font-size: clamp(1.6rem, 2.1vw, 1.95rem) !important;
}

.stApp:not(:has(.sb-split-hero)):not(:has(.sb-landing)) [data-testid="stMain"] h3 {
  font-size: clamp(1.3rem, 1.65vw, 1.55rem) !important;
}

.stApp:not(:has(.sb-split-hero)):not(:has(.sb-landing)) [data-testid="stMarkdownContainer"] p,
.stApp:not(:has(.sb-split-hero)):not(:has(.sb-landing)) [data-testid="stMarkdownContainer"] li,
.stApp:not(:has(.sb-split-hero)):not(:has(.sb-landing)) [data-testid="stCaptionContainer"] p,
.stApp:not(:has(.sb-split-hero)):not(:has(.sb-landing)) [data-testid="stAlert"],
.stApp:not(:has(.sb-split-hero)):not(:has(.sb-landing)) [data-testid="stWidgetLabel"],
.stApp:not(:has(.sb-split-hero)):not(:has(.sb-landing)) [data-testid="stWidgetLabel"] p {
  font-size: 1.02rem !important;
  line-height: 1.5;
}

.stApp:not(:has(.sb-split-hero)):not(:has(.sb-landing)) [data-testid="stMarkdownContainer"] [style*="font-size: 0."],
.stApp:not(:has(.sb-split-hero)):not(:has(.sb-landing)) [data-testid="stMarkdownContainer"] [style*="font-size:0."] {
  font-size: 1rem !important;
  line-height: 1.45 !important;
}

.stApp:not(:has(.sb-split-hero)):not(:has(.sb-landing)) .sb-section-title {
  font-size: 1.4rem !important;
}

.stApp:not(:has(.sb-split-hero)):not(:has(.sb-landing)) .sb-section-subtitle {
  font-size: 1rem !important;
}

.stApp:not(:has(.sb-split-hero)):not(:has(.sb-landing)) .sb-metric-value {
  font-size: 2rem !important;
}

.stApp:not(:has(.sb-split-hero)):not(:has(.sb-landing)) .sb-metric-label,
.stApp:not(:has(.sb-split-hero)):not(:has(.sb-landing)) .sb-badge {
  font-size: 0.98rem !important;
}

.stApp:not(:has(.sb-split-hero)):not(:has(.sb-landing)) [data-testid="stMetricLabel"] {
  font-size: 1rem !important;
}

.stApp:not(:has(.sb-split-hero)):not(:has(.sb-landing)) [data-testid="stMetricValue"] {
  font-size: 2rem !important;
}

.stApp:not(:has(.sb-split-hero)):not(:has(.sb-landing)) [data-testid="stMain"] input,
.stApp:not(:has(.sb-split-hero)):not(:has(.sb-landing)) [data-testid="stMain"] textarea,
.stApp:not(:has(.sb-split-hero)):not(:has(.sb-landing)) [data-testid="stMain"] [data-baseweb="select"] {
  font-size: 1rem !important;
}

.stApp:not(:has(.sb-split-hero)):not(:has(.sb-landing)) [data-testid="stMain"] [data-testid="stRadio"] label,
.stApp:not(:has(.sb-split-hero)):not(:has(.sb-landing)) [data-testid="stMain"] [data-testid="stCheckbox"] label,
.stApp:not(:has(.sb-split-hero)):not(:has(.sb-landing)) [data-testid="stMain"] [role="option"] {
  font-size: 1rem !important;
}

.stApp:not(:has(.sb-split-hero)):not(:has(.sb-landing)) [data-testid="stMain"] [data-testid="stButton"] > button,
.stApp:not(:has(.sb-split-hero)):not(:has(.sb-landing)) [data-testid="stMain"] [data-testid="stFormSubmitButton"] > button {
  min-height: 3rem;
  padding: 0.65rem 1rem !important;
  font-size: 1rem !important;
}

.stApp:not(:has(.sb-split-hero)):not(:has(.sb-landing)) [data-testid="stMain"] [data-testid="stButton"] > button p,
.stApp:not(:has(.sb-split-hero)):not(:has(.sb-landing)) [data-testid="stMain"] [data-testid="stFormSubmitButton"] > button p {
  font-size: 1rem !important;
}

.stApp:not(:has(.sb-split-hero)):not(:has(.sb-landing)) [data-testid="stMain"] .stTabs [data-baseweb="tab"] {
  min-height: 3rem;
  padding: 0.7rem 1rem;
  font-size: 1rem !important;
}

.stApp:not(:has(.sb-split-hero)):not(:has(.sb-landing)) [data-testid="stMain"] .stTabs [data-baseweb="tab"] p {
  font-size: 1rem !important;
}

.stApp:not(:has(.sb-split-hero)):not(:has(.sb-landing)) [data-testid="stDataFrame"] *,
.stApp:not(:has(.sb-split-hero)):not(:has(.sb-landing)) [data-testid="stTable"] * {
  font-size: 0.98rem !important;
}

.stApp:not(:has(.sb-split-hero)):not(:has(.sb-landing)) [data-testid="stSidebar"] [data-testid="stSidebarNavLink"] {
  min-height: 2.8rem;
  padding: 0.55rem 0.8rem !important;
}

.stApp:not(:has(.sb-split-hero)):not(:has(.sb-landing)) [data-testid="stSidebar"] [data-testid="stSidebarNavLink"],
.stApp:not(:has(.sb-split-hero)):not(:has(.sb-landing)) [data-testid="stSidebar"] [data-testid="stSidebarNavLink"] p {
  font-size: 1rem !important;
}

@media (max-width: 900px) {
  .stApp:not(:has(.sb-split-hero)):not(:has(.sb-landing)) [data-testid="stMain"] [data-testid="stHorizontalBlock"] {
    flex-wrap: wrap;
    gap: 0.85rem !important;
  }

  .stApp:not(:has(.sb-split-hero)):not(:has(.sb-landing)) [data-testid="stMain"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
    min-width: min(100%, 20rem);
  }
}

@media (max-width: 640px) {
  .stApp:not(:has(.sb-split-hero)):not(:has(.sb-landing)) .block-container {
    padding: 1rem 0.85rem 1.5rem !important;
  }

  .stApp:not(:has(.sb-split-hero)):not(:has(.sb-landing)) [data-testid="stMain"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
    min-width: 100%;
  }

  .stApp:not(:has(.sb-split-hero)):not(:has(.sb-landing)) [data-testid="stMain"] .stTabs [data-baseweb="tab"] {
    padding: 0.6rem 0.65rem;
    font-size: 0.95rem !important;
  }
}

@media (prefers-reduced-motion: reduce) {
  .sb-teach-arm,
  .sb-art-student,
  .sb-connection-line,
  .sb-art-node,
  .sb-art-particle {
    animation: none !important;
  }

  .sb-landing-bridge {
    transition: none !important;
  }
}

</style>
"""


def inject_css():
    """Inject custom CSS for modern SaaS layout, typography, and widgets."""
    st.markdown(CSS, unsafe_allow_html=True)


def status_badge(status: str) -> str:
    """Return a clean modern HTML pill badge for a request or session status."""
    status_labels = {
        "awaiting_confirmation": "Awaiting Learner Confirmation",
    }
    title_status = status_labels.get(
        (status or "").lower(),
        (status or "").replace("_", " ").title(),
    )
    style = STATUS_STYLES.get(title_status, ("#F1F5F9", "#475569", "#94A3B8"))
    bg, fg, border = style
    return f'<span class="sb-badge" style="background:{bg};color:{fg};border:1px solid {border}30;">● {title_status}</span>'


def avatar_initial(name: str) -> str:
    """Return 1-2 letter uppercase initials for user display."""
    if not name:
        return "U"
    parts = name.strip().split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[1][0]).upper()
    return name[:2].upper()


def metric_tile(icon: str, value, label: str) -> str:
    """Return HTML for a styled dashboard metric tile."""
    return f'''
    <div class="sb-metric-tile">
        <div class="sb-metric-icon">{icon}</div>
        <div class="sb-metric-value">{value}</div>
        <div class="sb-metric-label">{label}</div>
    </div>
    '''


def section_header(icon: str, title: str, subtitle: str = "") -> str:
    """Return HTML for a styled section header with icon."""
    sub_html = f'<div class="sb-section-subtitle">{subtitle}</div>' if subtitle else ""
    return f'''
    <div class="sb-section-header">
        <div class="sb-section-icon">{icon}</div>
        <div>
            <div class="sb-section-title">{title}</div>
            {sub_html}
        </div>
    </div>
    '''


def style_fig(fig, title: str):
    """Apply unified styling and typography to Plotly figures."""
    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>",
            x=0.01,
            font=dict(family="Inter, Poppins, sans-serif", size=15, color="#1F2933"),
        ),
        template="plotly_white",
        font=dict(family="Inter, sans-serif", color="#4B5563", size=12),
        margin=dict(l=15, r=15, t=48, b=15),
        height=320,
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


IST = ZoneInfo("Asia/Kolkata")


@st.fragment(run_every=1)
def countdown(start_text: str):
    """Real-time live countdown updating every second in Asia/Kolkata (IST)."""
    start = datetime.strptime(start_text, "%Y-%m-%d %H:%M")
    now = datetime.now(IST).replace(tzinfo=None)
    remaining = start - now
    if remaining.total_seconds() <= 0:
        st.markdown('<div class="sb-countdown">Session in progress</div>', unsafe_allow_html=True)
        return
    hours, rem = divmod(int(remaining.total_seconds()), 3600)
    minutes, seconds = divmod(rem, 60)
    st.markdown(
        f'<div class="sb-countdown">{hours:02d}:{minutes:02d}:{seconds:02d}</div>',
        unsafe_allow_html=True,
    )
