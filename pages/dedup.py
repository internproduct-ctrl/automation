import re
import hashlib
import requests
import pandas as pd
import streamlit as st
from bs4 import BeautifulSoup

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from theme import inject, page_header, metric_cards, style_table

st.set_page_config(page_title="Dedup Analyser", layout="wide")
inject()

page_header("DEDUP ANALYSER", "Biometric Cross-Match Intelligence")

# ── SESSION STATE ──────────────────────
for key, default in [
    ("seen_keys", set()),
    ("refresh_count", 0),
    ("last_df", None),
    ("duplicate_df", None),
    ("duplicate_count", 0),
    ("input_url", ""),
    ("raw_total", 0)
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── HELPERS ────────────────────────────
def clean(text):
    return re.sub(r'[^a-z0-9 ]', '', str(text).lower().strip())

def get_status(curr, prev):
    name_same = clean(curr["name"]) == clean(prev["name"])
    father_same = clean(curr["fname"]) == clean(prev["fname"])
    dob_same = curr["dob"] == prev["dob"] and curr["dob"] != ""

    if name_same and father_same and dob_same:
        return "SAME DETAILS"
    if not father_same:
        return "IMPERSONATION"
    if father_same and dob_same:
        return "TWIN"
    return "SIBLING"

DOB_RE = re.compile(r'\d{4}-\d{2}-\d{2}')

def parse_p_text(text):
    parts = [p.strip() for p in text.strip().split(",")]
    dob_idx = next((i for i, p in enumerate(parts) if DOB_RE.match(p[:10])), None)
    if dob_idx is None or dob_idx < 3:
        return None
    return {
        "roll": parts[dob_idx - 3].strip(),
        "name": parts[dob_idx - 2].strip().upper(),
        "fname": parts[dob_idx - 1].strip().upper(),
        "dob": parts[dob_idx].strip()[:10],
    }

def make_key(row):
    raw = "|".join([row["Curr Roll"], row["Prev Roll"]])
    return hashlib.md5(raw.encode()).hexdigest()

# ── FETCH ──────────────────────────────
def fetch_and_tag(url):
    html = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).text
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.find_all("tr")

    results = []

    for row in rows[1:]:
        p_tags = row.find_all("p")
        tds = row.find_all("td")
        app_to_app = 0.0

        try:
            nums = []

            for td in tds:
                vals = re.findall(r'\d+\.\d+', td.get_text(" ", strip=True))
                nums.extend([float(x) for x in vals])

                if len(nums) >= 2:
                    app_to_app = nums[-2]

        except:
            pass
        records = [parse_p_text(p.get_text(" ", strip=True)) for p in p_tags]
        records = [r for r in records if r]

        if len(records) < 2:
            continue

        curr = records[0]

        for prev in records[1:]:
            if prev["roll"] == curr["roll"]:
                continue

            father_same = clean(curr["fname"]) == clean(prev["fname"])
            dob_same = curr["dob"] == prev["dob"] and curr["dob"] != ""

            status = get_status(curr, prev)

            record = {
                "Curr Roll": curr["roll"],
                "Prev Roll": prev["roll"],

                "Curr Name": curr["name"],
                "Curr Father": curr["fname"],
                "Curr DOB": curr["dob"],

                "Prev Name": prev["name"],
                "Prev Father": prev["fname"],
                "Prev DOB": prev["dob"],

                "Father Match": "✔ Same" if father_same else "✘ Diff",
                "DOB Match": "✔ Same" if dob_same else "✘ Diff",
                "App Score": round(app_to_app, 2),

                "Status": status
            }

            record["_key"] = make_key(record)
            results.append(record)

    if not results:
        return pd.DataFrame(), 0

    df = pd.DataFrame(results)

    # ── REMOVE DUPLICATES ───────────────
    df["pair_key"] = df.apply(
        lambda x: tuple(sorted([x["Curr Roll"], x["Prev Roll"]])),
        axis=1
    )

    duplicate_df = df[df.duplicated("pair_key", keep="first")]
    clean_df = df.drop_duplicates("pair_key", keep="first")

    st.session_state.duplicate_df = duplicate_df.drop(columns="pair_key")
    st.session_state.duplicate_count = len(duplicate_df)

    df = clean_df.drop(columns="pair_key")

    # ── RECORD STATUS ───────────────────
    is_first = st.session_state.refresh_count == 0
    df["Record"] = "NEW" if is_first else df["_key"].apply(
        lambda k: "OLD" if k in st.session_state.seen_keys else "NEW"
    )

    st.session_state.seen_keys.update(df["_key"])
    df = df.drop(columns="_key")

    return df, len(results)

# ── INPUT ──────────────────────────────
url = st.text_input("Enter Report URL", value=st.session_state.input_url)

c1, c2 = st.columns(2)
with c1:
    load = st.button("▶ LOAD", use_container_width=True)
with c2:
    refresh = st.button("🔄 REFRESH", use_container_width=True)

if load or refresh:
    if url:
        st.session_state.input_url = url
        with st.spinner("Fetching..."):
            df, raw_total = fetch_and_tag(url)
            st.session_state.last_df = df
            st.session_state.raw_total = raw_total
            st.session_state.refresh_count += 1

# ── DISPLAY ────────────────────────────
df = st.session_state.last_df

if df is not None and not df.empty:

    raw_total = st.session_state.raw_total
    dup = st.session_state.duplicate_count

    imp = (df["Status"] == "IMPERSONATION").sum()
    same = (df["Status"] == "SAME DETAILS").sum()
    twin = (df["Status"] == "TWIN").sum()
    sib = (df["Status"] == "SIBLING").sum()

    new_count = (df["Record"] == "NEW").sum()
    old_count = (df["Record"] == "OLD").sum()

    metric_cards([
        ("mc-total", raw_total, "Total"),
        ("mc-imp", imp, "Impersonation"),
        ("mc-same", same, "Same"),
        ("mc-sib", twin, "Twin"),
        ("mc-new", sib, "Sibling"),
        ("mc-imp", dup, "Duplicates"),
        ("mc-new", new_count, "New Records"),
        ("mc-total", old_count, "Old Records"),
    ])

    # ── FILTERS ─────────────────────────
    f1, f2, f3, f4, f5 = st.columns(5)

    with f1:
        sel_status = st.selectbox("STATUS", ["ALL", "SAME DETAILS", "TWIN", "SIBLING", "IMPERSONATION"])

    with f2:
        sel_father = st.selectbox("FATHER MATCH", ["ALL", "✔ Same", "✘ Diff"])

    with f3:
        sel_dob = st.selectbox("DOB MATCH", ["ALL", "✔ Same", "✘ Diff"])

    with f4:
        sel_record = st.selectbox("RECORD", ["ALL", "NEW", "OLD"])
    with f5:
        min_app = st.number_input(
            "MIN APP SCORE",
            min_value=0.0,
            max_value=1.0,
            value=0.0,
            step=0.01
        )

    filt = df.copy()

    if sel_status != "ALL":
        filt = filt[filt["Status"] == sel_status]

    if sel_father != "ALL":
        filt = filt[filt["Father Match"] == sel_father]

    if sel_dob != "ALL":
        filt = filt[filt["DOB Match"] == sel_dob]

    if sel_record != "ALL":
        filt = filt[filt["Record"] == sel_record]
    filt = filt[filt["App Score"] >= min_app]

    # ✅ NEW FEATURE: SHOW COUNT
    filtered_count = len(filt)
    total_count = len(df)

    st.markdown(
        f'<div class="cpill">Showing {filtered_count} of {total_count} records</div>',
        unsafe_allow_html=True
    )

    display_df = filt.drop(columns=[
        "DOB Match",
        "Father Match",
        "Curr Roll",
        "Prev Roll"
    ])

    tab1, tab2 = st.tabs(["Main Report", "Duplicates"])

    with tab1:
        st.dataframe(
            display_df.style
            .format({
                "App Score": "{:.2f}"
                })
            .apply(
                style_table,
                axis=None,
                name_cols=["Curr Name", "Prev Name"],
                father_cols=["Curr Father", "Prev Father"],
                dob_cols=["Curr DOB", "Prev DOB"]
            ),
            use_container_width=True
        )

    with tab2:
        dup_df = st.session_state.duplicate_df
        if dup_df is not None and not dup_df.empty:
            st.dataframe(
                dup_df.drop(columns=["DOB Match", "Father Match", "Curr Roll", "Prev Roll"]),
                use_container_width=True
            )
        else:
            st.info("No duplicates found")

else:
    st.info("Enter URL and click LOAD")