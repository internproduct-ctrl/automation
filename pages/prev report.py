# app.py
# Install: pip install streamlit beautifulsoup4 pandas requests rapidfuzz

import re
import hashlib
import requests
import pandas as pd
import streamlit as st
from bs4 import BeautifulSoup
from rapidfuzz import fuzz
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from theme import inject, page_header, metric_cards, count_pill

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Duplicate Detection System",
    layout="wide",
    initial_sidebar_state="collapsed",
)
inject()

# ── SESSION STATE INIT ────────────────────────────────────────────────────────
if "seen_keys"      not in st.session_state:
    st.session_state.seen_keys      = set()    # all keys ever seen across all refreshes
if "refresh_count"  not in st.session_state:
    st.session_state.refresh_count  = 0
if "last_df"        not in st.session_state:
    st.session_state.last_df        = None     # cached df from last fetch
if "url_submitted"  not in st.session_state:
    st.session_state.url_submitted  = False
if "input_url"      not in st.session_state:
    st.session_state.input_url      = ""

# ── HELPERS ───────────────────────────────────────────────────────────────────
def clean(text):
    return re.sub(r'[^a-z0-9 ]', '', text.lower().strip())

def similarity_score(a, b):
    if not a or not b:
        return 0
    return max(fuzz.ratio(a, b), fuzz.partial_ratio(a, b), fuzz.token_sort_ratio(a, b))

def extract_bio_scores(text):

    nums = re.findall(r'\d+\.\d+', str(text))

    return [float(x) for x in nums]

def classify(score):
    if score >= 90:   return "VERY_HIGH"
    elif score >= 75: return "HIGH"
    elif score >= 40: return "LOW"
    else:             return "DIFF"

def name_exact_match(a, b, score):
    tokens_a, tokens_b = set(a.split()), set(b.split())
    if tokens_a.issubset(tokens_b) or tokens_b.issubset(tokens_a):
        return True
    if fuzz.ratio(a.replace(" ", ""), b.replace(" ", "")) >= 90:
        return True
    if score >= 90 and abs(len(a) - len(b)) <= 3:
        return True
    return False

INVALID_KEYWORDS = [
    "bank", "board", "university", "college", "school",
    "department", "institute", "commission", "authority", "office"
]
def is_non_person(name):
    return any(word in name for word in INVALID_KEYWORDS)

def make_record_key(row: dict) -> str:
    """Stable unique hash for a record — used to track old vs new across refreshes."""
    raw = "|".join([
        str(row.get("Current Name",   "")),
        str(row.get("Current Father", "")),
        str(row.get("Current DOB",    "")),
        str(row.get("Prev Name",      "")),
        str(row.get("Prev Father",    "")),
        str(row.get("Prev DOB",       "")),
    ])
    return hashlib.md5(raw.encode()).hexdigest()

def get_current(text):
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    name, father, dob = "", "", ""
    if lines:
        parts = lines[0].split("-")
        if len(parts) > 1:
            name = clean(parts[1])
    parts = re.split(r'Father\s*:\s*', text, flags=re.IGNORECASE)
    if len(parts) > 1:
        father = clean(re.split(r'\|\||DOB', parts[1])[0])
    dob_match = re.search(r'DOB\s*:\s*(\d{4}-\d{2}-\d{2})', text)
    if dob_match:
        dob = dob_match.group(1)
    return {"name": name, "father": father, "dob": dob}

def get_prev(block):

    lines = [l.strip() for l in block.split("\n") if l.strip()]

    if not lines:
        return None

    first = lines[0]
    parts = first.split("-")

    if len(parts) < 4:
        return None

    name = clean(parts[2])

    score_match = re.search(
        r'(True|False)-([\d\.]+)-([\d\.]+)',
        first
    )

    if not score_match:
        return None

    face_score  = float(score_match.group(2))
    cross_score = float(score_match.group(3))

    father = ""
    dob = ""

    # Search all lines from bottom
    for line in reversed(lines):

        dob_match = re.search(r'(\d{4}-\d{2}-\d{2})', line)

        if dob_match:
            dob = dob_match.group(1)

            possible_father = clean(
                line.replace(dob, "")
            ).strip()

            if len(possible_father.split()) >= 2:
                father = possible_father

            break

    return {
        "name": name,
        "father": father,
        "dob": dob,
        "score": face_score,
        "cross_score": cross_score
    }

def get_status(curr, prev, current_text):

    if "duplicate" in current_text.lower():
        return "IGNORED (Duplicate)"

    if prev["score"] < 0.5:
        return "IGNORED (Low Score)"

    if prev["cross_score"] < 0.67:
        return "IGNORED (Low Cross Score)"

    if is_non_person(prev["name"]):
        return "INVALID DATA (Non-person in Prev)"

    if is_non_person(curr["name"]):
        return "INVALID DATA (Non-person in Current)"

    name_score   = similarity_score(curr["name"], prev["name"])
    father_score = similarity_score(curr["father"], prev["father"])

    name_type   = classify(name_score)
    father_type = classify(father_score)

    dob_curr = curr["dob"]
    dob_prev = prev["dob"]


    dob_same    = (dob_curr == dob_prev and dob_curr != "")
    dob_missing = (dob_curr == "" or dob_prev == "")
    dob_diff    = (not dob_same and not dob_missing)

    # -------------------------
    # IMPERSONATION
    # -------------------------
    if name_score < 25 and father_score < 25:
        return "IMPERSONATION"

    if father_type == "DIFF":
        return "IMPERSONATION"

    if father_type == "LOW" and name_type == "VERY_HIGH" and dob_diff:
        return "IMPERSONATION"

    if father_type == "LOW" and name_type in ["LOW", "DIFF"] and (dob_missing or dob_diff):
        return "IMPERSONATION"

    # -------------------------
    # NAME MATCH
    # -------------------------
    name_exact = name_exact_match(curr["name"], prev["name"], name_score)

    # SAME PERSON
    if father_type in ["VERY_HIGH", "HIGH"] and name_exact:
        return "SAME DETAILS"

    # TWIN
    if father_type in ["VERY_HIGH", "HIGH"] and dob_same:
        if name_type in ["VERY_HIGH", "HIGH"]:
            return "SIBLING/TWIN"

    # SIBLING
    if father_type in ["VERY_HIGH", "HIGH"]:
        return "SIBLING/TWIN"

    return "IMPERSONATION"
# ── FETCH & TAG ───────────────────────────────────────────────────────────────
def fetch_and_tag(url: str) -> tuple[pd.DataFrame, str | None]:

    try:
        html = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=15
        ).text

        soup = BeautifulSoup(html, "html.parser")
        rows = soup.find_all("tr")

        results = []

        for row in rows[1:]:

            cols = row.find_all("td")

            if len(cols) < 5:
                continue

            current_text = cols[2].get_text("\n", strip=True)
            prev_text    = cols[3].get_text("\n", strip=True)

            # REAL BIO SCORE COLUMN
            bio_score_text = cols[4].get_text(" ", strip=True)

            bio_scores = extract_bio_scores(bio_score_text)

            curr = get_current(current_text)

            prev_blocks = re.findall(
                r'([a-zA-Z]+\d+-\d+-.*?)(?=[a-zA-Z]+\d+-\d+-|$)',
                prev_text,
                re.DOTALL
            )

            for idx, block in enumerate(prev_blocks):

                prev = get_prev(block)

                if not prev:
                    continue

                # MAP BIO SCORE CORRECTLY
                current_bio_score = 0.0

                if idx < len(bio_scores):
                    current_bio_score = bio_scores[idx]

                status = get_status(curr, prev, current_text)

                record = {
                    "Current Name":   curr["name"],
                    "Current Father": curr["father"],
                    "Current DOB":    curr["dob"],

                    "Prev Name":      prev["name"],
                    "Prev Father":    prev["father"],
                    "Prev DOB":       prev["dob"],

                    "Face Score":     round(prev["score"], 2),
                    "Cross Score":    round(prev["cross_score"], 2),

                    "Bio Score":      round(current_bio_score, 2),

                    "Status":         status,
                }

                record["_key"] = make_record_key(record)

                results.append(record)

        if not results:
            return pd.DataFrame(), None

        df = pd.DataFrame(results)

        # NEW / OLD TAGGING
        if st.session_state.refresh_count == 0:
            df["Record Status"] = "🟢 NEW"
        else:
            df["Record Status"] = df["_key"].apply(
                lambda k:
                    "⚪ OLD"
                    if k in st.session_state.seen_keys
                    else "🟢 NEW"
            )

        st.session_state.seen_keys.update(df["_key"].tolist())

        df = df.drop(columns=["_key"])

        df.index += 1

        return df, None

    except Exception as e:
        return pd.DataFrame(), str(e)
# ════════════════════════════════════════════════════════════════════════════
# UI
# ════════════════════════════════════════════════════════════════════════════

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("## 🔍 DUPLICATE DETECTION SYSTEM")
st.markdown("---")

# ── URL INPUT FORM ────────────────────────────────────────────────────────────
with st.form("url_form"):
    url_input = st.text_input(
        "HTML REPORT URL",
        value=st.session_state.input_url,
        placeholder="https://example.com/report.html",
        help="Paste the URL of the HTML report to analyse"
    )
    col_submit, col_refresh, col_reset = st.columns([2, 2, 3])
    with col_submit:
        submitted = st.form_submit_button("▶ LOAD / REFRESH", use_container_width=True)
    with col_refresh:
        reset_btn = st.form_submit_button("↺ RESET HISTORY", use_container_width=True)

# Handle reset
if reset_btn:
    st.session_state.seen_keys     = set()
    st.session_state.refresh_count = 0
    st.session_state.last_df       = None
    st.info("History cleared. Load the URL to start fresh.")

# Handle load / refresh
if submitted and url_input.strip():
    st.session_state.input_url     = url_input.strip()
    st.session_state.url_submitted = True

    with st.spinner("Fetching data from URL..."):
        df, error = fetch_and_tag(st.session_state.input_url)

    if error:
        st.error(f"Error fetching data: {error}")
    elif df.empty:
        st.warning("No records found at that URL.")
    else:
        st.session_state.last_df       = df
        st.session_state.refresh_count += 1

elif not url_input.strip() and submitted:
    st.warning("Please enter a valid URL.")

# ── DISPLAY ───────────────────────────────────────────────────────────────────
df = st.session_state.last_df

if df is not None and not df.empty:

    rc = st.session_state.refresh_count
    new_count = (df["Record Status"] == "🟢 NEW").sum()
    old_count = (df["Record Status"] == "⚪ OLD").sum()

    # ── REFRESH INFO BAR ──────────────────────────────────────────────────────
    count_pill(f"REFRESH #{rc}  ·  🟢 {new_count} NEW  ·  ⚪ {old_count} OLD")

    # ── METRICS ───────────────────────────────────────────────────────────────
    total         = len(df)
    impersonation = (df["Status"] == "IMPERSONATION").sum()
    same_details  = (df["Status"] == "SAME DETAILS").sum()
    ignored       = df["Status"].str.startswith("IGNORED").sum()
    invalid       = df["Status"].str.startswith("INVALID").sum()

    metric_cards([
        ("mc-total", total, "Total"),
        ("mc-imp", impersonation, "Impersonation"),
        ("mc-same", same_details, "Same Details"),
        ("mc-sib", invalid, "Invalid"),
        ("mc-imp", ignored, "Ignored"),
    ])

    # ── FILTERS ───────────────────────────────────────────────────────────────
    f1, f2, f3, f4, f5, f6 = st.columns([2,2,2,1.5,1.5,1.5])

    with f1:
        status_options  = ["ALL"] + sorted(df["Status"].unique().tolist())
        selected_status = st.selectbox("STATUS FILTER", status_options)

    with f2:
        selected_father = st.selectbox("FATHER NAME FILTER", ["ALL", "SAME", "DIFFERENT"])

    with f3:
        selected_record = st.selectbox("RECORD STATUS", ["ALL", "🟢 NEW", "⚪ OLD"])
    with f5:
        min_bio = st.number_input(
            "MIN BIO SCORE",
            min_value=0.0,
            max_value=1.0,
            value=0.0,
            step=0.01
    )

    with f6:
        min_cross = st.number_input(
            "MIN CROSS SCORE",
            min_value=0.0,
            max_value=1.0,
            value=0.0,
            step=0.01
    )

    # Apply filters
    filtered = df.copy()
    if selected_status != "ALL":
        filtered = filtered[filtered["Status"] == selected_status]
    if selected_father != "ALL":
        filtered = filtered[filtered["Father Match"] == selected_father]
    if selected_record != "ALL":
        filtered = filtered[filtered["Record Status"] == selected_record]
    filtered = filtered[filtered["Bio Score"] >= min_bio]
    filtered = filtered[filtered["Cross Score"] >= min_cross]

    with f4:
        count_pill(f"Showing {len(filtered)} of {total} records")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── COLOR MAP ─────────────────────────────────────────────────────────────
    STATUS_COLORS = {
        "IMPERSONATION":                        "#ef4444",
        "SAME DETAILS":                         "#3b82f6",
        "SIBLING":                              "#8b5cf6",
        "TWIN":                                 "#f59e0b",
        "INVALID DATA (No Similarity)":         "#f97316",
        "INVALID DATA (Non-person in Prev)":    "#f97316",
        "INVALID DATA (Non-person in Current)": "#f97316",
        "IGNORED (Duplicate)":                  "#6b7280",
        "IGNORED (Low Score)":                  "#6b7280",
        "IGNORED (Low Cross Score)":            "#6b7280",
    }

    def style_row(row):
        # NEW records get a green left border; OLD get a grey left border
        is_new    = row.get("Record Status") == "🟢 NEW"
        indicator = "#22c55e" if is_new else "#475569"
        status_bg = STATUS_COLORS.get(row["Status"], "#1e2130") + "22"
        return [
            f"background-color:{status_bg}; border-left:3px solid {indicator}"
            if i == 0 else f"background-color:{status_bg}"
            for i in range(len(row))
        ]

    # ── TABLE ─────────────────────────────────────────────────────────────────
    if filtered.empty:
        st.info("No records match the selected filters.")
    else:
        styled = (
            filtered.style
            .apply(style_row, axis=1)
            .format({"Face Score": "{:.2f}", "Cross Score": "{:.2f}","Bio Score":"{:.2f}"})
            .set_properties(**{
                "font-family": "IBM Plex Mono, monospace",
                "font-size":   "12px",
            })
        )
        st.dataframe(styled, use_container_width=True, height=600)

elif not st.session_state.url_submitted:
    st.markdown(
        '<div style="text-align:center;padding:60px;color:#475569;'
        'font-family:IBM Plex Mono,monospace;font-size:13px;">'
        'Enter a URL above and click LOAD to begin analysis.</div>',
        unsafe_allow_html=True
    )