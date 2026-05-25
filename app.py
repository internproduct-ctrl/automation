import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from theme import inject, page_header, theme_selector

st.set_page_config(
    page_title="Automation Hub",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)
inject()

# ── TOP BAR ────────────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns([1, 6, 1])
with c1:
    st.markdown("""
    <div style="font-family:'IBM Plex Mono',monospace;font-weight:600;
                font-size:1rem;color:var(--navy);letter-spacing:-0.5px;
                padding-top:4px;">
        ⚡ AUTOMATION HUB
    </div>
    """, unsafe_allow_html=True)
with c3:
    theme_selector()
st.markdown("<hr style='margin:0 0 0 0;opacity:0.3;'>", unsafe_allow_html=True)

# ── HERO ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding:40px 0 10px;">
    <div style="font-family:'IBM Plex Mono',monospace;font-weight:600;font-size:2.2rem;
                letter-spacing:-1px;
                background:linear-gradient(90deg,#60a5fa 0%,#a78bfa 55%,#f472b6 100%);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                margin-bottom:8px;">
        AUTOMATION HUB
    </div>
    <div style="font-family:'IBM Plex Mono',monospace;font-size:0.72rem;letter-spacing:3px;
                text-transform:uppercase;color:#3d5070;margin-bottom:32px;">
        Select a report to begin analysis
    </div>
</div>
""", unsafe_allow_html=True)

# ── CARDS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="home-grid">

  <a class="home-card imp" href="/dedup" target="_self">
    <div class="card-icon">🔍</div>
    <div class="card-title">DEDUP ANALYSER</div>
  </a>

  <a class="home-card same" href="/pre_dedup" target="_self">
    <div class="card-icon">📊</div>
    <div class="card-title">PRE-DEDUP</div>
  </a>

  <a class="home-card sib" href="/prev_report" target="_self">
    <div class="card-icon">📋</div>
    <div class="card-title">PREV REPORT</div>
  </a>

</div>
""", unsafe_allow_html=True)

# ── DIVIDER + FOOTER ──────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-top:60px;height:1px;
            background:linear-gradient(90deg,transparent,#1a2035,transparent);"></div>
<div style="margin-top:16px;font-family:'IBM Plex Mono',monospace;font-size:0.65rem;
            letter-spacing:2px;text-transform:uppercase;color:#1a2035;text-align:center;">
    Automation Hub · Report Intelligence Suite
</div>
""", unsafe_allow_html=True)