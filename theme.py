import streamlit as st
import pandas as pd

SHARED_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500;600;700&display=swap');

:root {
    /* Base */
    --bg:           #f4f1eb;
    --bg2:          #ede9e0;
    --surface:      #ffffff;
    --surface2:     #f9f7f3;
    --border:       #ddd8cc;
    --border2:      #c8c1b0;
    --shadow:       rgba(60, 50, 30, 0.08);

    /* Text */
    --text:         #1e1c18;
    --text2:        #4a4538;
    --muted:        #8c8474;
    --muted2:       #b5ae9f;

    /* Accents */
    --navy:         #1e3a5f;
    --navy2:        #2a5298;
    --navy-light:   #e8eef7;

    /* Status - Impersonation (warm red) */
    --imp-bg:       #fdf2f2;
    --imp-border:   #f0b8b8;
    --imp-accent:   #c0392b;
    --imp-text:     #7b1d1d;
    --imp-soft:     #fce8e8;

    /* Status - Same Details (steel blue) */
    --same-bg:      #f0f5fc;
    --same-border:  #aec9f0;
    --same-accent:  #1a5fa8;
    --same-text:    #0d3b6e;
    --same-soft:    #ddeafa;

    /* Status - Sibling/Twin (amber) */
    --sib-bg:       #fdf8ee;
    --sib-border:   #f0d898;
    --sib-accent:   #b45309;
    --sib-text:     #78350f;
    --sib-soft:     #fef0c7;

    /* Match/Correct (sage green) */
    --ok-bg:        #f0f9f4;
    --ok-border:    #a8d9bc;
    --ok-accent:    #166534;
    --ok-text:      #14532d;
    --ok-soft:      #dcfce7;

    /* Mismatch */
    --err-bg:       #fdf2f2;
    --err-accent:   #c0392b;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
}

/* ── OVERALL APP ── */
.stApp {
    background: var(--bg) !important;
    color: var(--text) !important;
}
.main .block-container {
    background: var(--bg) !important;
    padding-top: 2rem !important;
}
#MainMenu, footer, header { visibility: hidden; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: var(--navy) !important;
    border-right: none !important;
}
[data-testid="stSidebarNav"] a {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 1px !important;
    color: rgba(255,255,255,0.55) !important;
    border-radius: 6px !important;
    padding: 8px 14px !important;
    text-transform: uppercase !important;
    transition: all .15s ease !important;
}
[data-testid="stSidebarNav"] a:hover,
[data-testid="stSidebarNav"] a[aria-current] {
    background: rgba(255,255,255,0.12) !important;
    color: #ffffff !important;
}
[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.1) !important;
}

/* ── PAGE TITLE ── */
.page-title {
    font-family: 'DM Sans', sans-serif;
    font-weight: 700;
    font-size: 1.75rem;
    color: var(--navy);
    letter-spacing: -0.5px;
    margin: 0;
    padding: 0;
    border-left: 4px solid var(--navy2);
    padding-left: 14px;
}
.page-sub {
    font-family: 'DM Mono', monospace;
    font-size: 0.67rem;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 1.6rem;
    margin-top: 4px;
    padding-left: 18px;
}

/* ── DIVIDER ── */
.hdiv {
    height: 1px;
    background: var(--border);
    margin: 0.8rem 0 1.4rem;
}

/* ── METRIC CARDS ── */
.mc-row { display:flex; gap:12px; margin:1rem 0 1.6rem; }
.mc {
    flex:1; border-radius:10px; padding:18px 16px 14px;
    text-align:center; border:1px solid;
    background: var(--surface);
    box-shadow: 0 2px 8px var(--shadow);
    transition: transform .15s ease, box-shadow .15s ease;
}
.mc:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px var(--shadow);
}
.mc-total { border-color: var(--border2); border-top: 3px solid var(--navy2); }
.mc-imp   { border-color: var(--imp-border); border-top: 3px solid var(--imp-accent); background: var(--imp-bg); }
.mc-same  { border-color: var(--same-border); border-top: 3px solid var(--same-accent); background: var(--same-bg); }
.mc-sib   { border-color: var(--sib-border); border-top: 3px solid var(--sib-accent); background: var(--sib-bg); }
.mc-new   { border-color: var(--ok-border); border-top: 3px solid var(--ok-accent); background: var(--ok-bg); }

.mc-val {
    font-family: 'DM Mono', monospace;
    font-size: 2.1rem; font-weight: 500; line-height: 1;
}
.mc-total .mc-val { color: var(--navy); }
.mc-imp   .mc-val { color: var(--imp-accent); }
.mc-same  .mc-val { color: var(--same-accent); }
.mc-sib   .mc-val { color: var(--sib-accent); }
.mc-new   .mc-val { color: var(--ok-accent); }
.mc-lbl {
    font-size: 0.6rem; letter-spacing: 2px; text-transform: uppercase;
    margin-top: 7px; color: var(--muted);
    font-family: 'DM Mono', monospace;
}

/* ── COUNT PILL ── */
.cpill {
    display: inline-block;
    background: var(--surface);
    border: 1px solid var(--border2);
    border-radius: 20px;
    padding: 5px 16px;
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    color: var(--muted);
    margin-bottom: .8rem;
    box-shadow: 0 1px 4px var(--shadow);
}

/* ── FORM INPUTS ── */
.stTextInput input {
    background: var(--surface) !important;
    border: 1px solid var(--border2) !important;
    color: var(--text) !important;
    border-radius: 8px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.82rem !important;
    box-shadow: 0 1px 4px var(--shadow) !important;
}
.stTextInput input:focus {
    border-color: var(--navy2) !important;
    box-shadow: 0 0 0 3px rgba(42,82,152,0.12) !important;
}

/* ── BUTTONS ── */
.stFormSubmitButton button {
    background: var(--surface) !important;
    border: 1px solid var(--border2) !important;
    color: var(--text2) !important;
    border-radius: 8px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.5px !important;
    box-shadow: 0 1px 4px var(--shadow) !important;
    transition: all .15s ease !important;
}
.stFormSubmitButton button:hover {
    border-color: var(--navy2) !important;
    color: var(--navy) !important;
    background: var(--navy-light) !important;
}
[data-testid="stDownloadButton"] button {
    background: var(--navy) !important;
    border: none !important;
    color: #ffffff !important;
    border-radius: 8px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem !important;
    padding: 8px 20px !important;
    box-shadow: 0 2px 8px rgba(30,58,95,0.25) !important;
}
[data-testid="stDownloadButton"] button:hover {
    background: var(--navy2) !important;
}

/* ── SELECTS ── */
.stSelectbox > div > div {
    background: var(--surface) !important;
    border: 1px solid var(--border2) !important;
    color: var(--text) !important;
    border-radius: 8px !important;
    box-shadow: 0 1px 4px var(--shadow) !important;
}
div[data-testid="stSelectbox"] label {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.67rem !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
}

/* ── MULTISELECT ── */
.stMultiSelect > div > div {
    background: var(--surface) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
}

/* ── FILE UPLOADER ── */
[data-testid="stFileUploader"] section {
    background: var(--surface) !important;
    border: 1.5px dashed var(--border2) !important;
    border-radius: 10px !important;
}

/* ── DATAFRAME ── */
[data-testid="stDataFrameResizable"] {
    border: 1px solid var(--border2) !important;
    border-radius: 10px !important;
    box-shadow: 0 2px 12px var(--shadow) !important;
    overflow: hidden !important;
}

/* ── ALERTS ── */
[data-testid="stAlert"] {
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* ── SPINNER ── */
[data-testid="stSpinner"] {
    color: var(--navy) !important;
}

/* ── EMPTY STATE ── */
.empty-state { text-align:center; padding:80px 20px; }
.empty-icon  { font-size:3rem; margin-bottom:14px; opacity:.5; }
.empty-txt   {
    font-family: 'DM Mono', monospace;
    font-size: 0.78rem; letter-spacing: 2px;
    color: var(--muted2); text-transform: uppercase;
}

/* ── HOME CARDS ── */
.home-grid {
    display: grid;
    grid-template-columns: repeat(3,1fr);
    gap: 20px;
    margin-top: 2rem;
}
.home-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 30px 26px;
    cursor: pointer;
    transition: transform .2s ease, box-shadow .2s ease;
    text-decoration: none !important;
    display: block;
    box-shadow: 0 2px 12px var(--shadow);
}
.home-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 40px var(--shadow);
}
.home-card.imp  { border-top: 4px solid var(--imp-accent); }
.home-card.same { border-top: 4px solid var(--same-accent); }
.home-card.sib  { border-top: 4px solid var(--sib-accent); }

.card-icon { font-size: 2.2rem; margin-bottom: 14px; }
.card-title {
    font-family: 'DM Sans', sans-serif;
    font-weight: 700; font-size: 1.05rem;
    color: var(--navy); margin-bottom: 8px;
}
.card-desc {
    font-size: 0.84rem; color: var(--text2);
    line-height: 1.6;
}
.card-tag {
    display: inline-block; margin-top: 16px;
    padding: 4px 12px; border-radius: 20px;
    font-family: 'DM Mono', monospace;
    font-size: 0.62rem; letter-spacing: 1px;
    text-transform: uppercase; border: 1px solid;
}
.tag-imp  { background: var(--imp-soft);  color: var(--imp-text);  border-color: var(--imp-border); }
.tag-same { background: var(--same-soft); color: var(--same-text); border-color: var(--same-border); }
.tag-sib  { background: var(--sib-soft);  color: var(--sib-text);  border-color: var(--sib-border); }
</style>
"""


def inject():
    st.markdown(SHARED_CSS, unsafe_allow_html=True)


def page_header(title, subtitle):
    st.markdown(f'<p class="page-title">{title}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="page-sub">{subtitle}</p>', unsafe_allow_html=True)
    st.markdown('<div class="hdiv"></div>', unsafe_allow_html=True)


def metric_cards(cards):
    inner = "".join(
        f'<div class="mc {cls}"><div class="mc-val">{val}</div>'
        f'<div class="mc-lbl">{lbl}</div></div>'
        for cls, val, lbl in cards
    )
    st.markdown(
        f'<div class="mc-row">{inner}</div><div class="hdiv"></div>',
        unsafe_allow_html=True
    )


def count_pill(text):
    st.markdown(f'<div class="cpill">{text}</div>', unsafe_allow_html=True)


def style_table(df, status_col="Status", record_col="Record",
                name_cols=(), father_cols=(), dob_cols=(), dob_match_col="DOB"):
    """
    Light-theme row styler for all report tables.
    """
    styles = pd.DataFrame("", index=df.index, columns=df.columns)

    STATUS_PALETTES = {
        "IMPERSONATION":  ("#fdf2f2", "#c0392b", "#7b1d1d", "#fce8e8"),
        "SAME DETAILS":   ("#f0f5fc", "#1a5fa8", "#0d3b6e", "#ddeafa"),
        "SIBLING / TWIN": ("#fdf8ee", "#b45309", "#78350f", "#fef0c7"),
        "✔ MATCH":        ("#f0f9f4", "#166534", "#14532d", "#dcfce7"),
        "✘ MISMATCH":     ("#fdf2f2", "#c0392b", "#7b1d1d", "#fce8e8"),
    }
    DEFAULT_PAL = ("#f9f7f3", "#4a4538", "#1e1c18", "#ede9e0")

    for idx in df.index:
        status = df.at[idx, status_col] if status_col in df.columns else ""
        record = df.at[idx, record_col] if record_col in df.columns else "NEW"

        bg, accent, text_c, soft = STATUS_PALETTES.get(str(status), DEFAULT_PAL)
        rec_color = "#166534" if record == "NEW" else "#8c8474"
        base = f"background-color:{bg};"

        for col in df.columns:
            if col == status_col:
                styles.at[idx, col] = (
                    f"{base}color:{accent};font-weight:600;"
                    f"font-family:'DM Mono',monospace;font-size:0.78rem;"
                )
            elif col == record_col:
                styles.at[idx, col] = (
                    f"{base}color:{rec_color};font-weight:600;"
                    f"font-family:'DM Mono',monospace;"
                )
            elif col == dob_match_col and dob_match_col in df.columns:
                dv = str(df.at[idx, col])
                dc = "#166534" if ("Same" in dv or "✔" in dv) else "#c0392b"
                styles.at[idx, col] = (
                    f"{base}color:{dc};font-family:'DM Mono',monospace;font-weight:600;"
                )
            elif col in dob_cols:
                styles.at[idx, col] = (
                    f"{base}color:#4a4538;font-family:'DM Mono',monospace;"
                )
            elif col in name_cols:
                styles.at[idx, col] = f"{base}color:{text_c};font-weight:600;"
            elif col in father_cols:
                styles.at[idx, col] = f"{base}color:#6b6358;"
            else:
                styles.at[idx, col] = base

    return styles