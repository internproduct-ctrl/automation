import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from theme import inject, page_header

st.set_page_config(
    page_title="Automation Hub",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject()

# ── SIDEBAR LOGO ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:20px 8px 28px;">
        <div style="font-family:'IBM Plex Mono',monospace;font-weight:600;
                    font-size:1.1rem;color:#c9d6e8;letter-spacing:-0.5px;">
            ⚡ AUTOMATION HUB
        </div>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.62rem;
                    letter-spacing:2px;color:#3d5070;margin-top:4px;text-transform:uppercase;">
            Report Intelligence Suite
        </div>
    </div>
    """, unsafe_allow_html=True)

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