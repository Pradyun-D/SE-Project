from __future__ import annotations

from typing import Any

import requests
import streamlit as st
import json
from datetime import datetime
from pathlib import Path
from urllib.parse import quote


st.set_page_config(
    page_title="Regulatory SRS Studio",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    /* Force Light Color Scheme at browser/root level */
    :root {
        color-scheme: light !important;
        --primary-color: #2563eb;
        --background-color: #f8fafc;
        --secondary-background-color: #ffffff;
        --text-color: #0f172a;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #0f172a !important;
    }

    /* Keep the document browser available in the sidebar. */
    [data-testid="stHeader"] {
        background: transparent !important;
    }

    /* Main canvas background & layout */
    .stApp, [data-testid="stAppViewContainer"] {
        background-color: #f8fafc !important;
        color: #0f172a !important;
    }
    .block-container {
        max-width: 1120px !important;
        padding-top: 2rem !important;
        padding-bottom: 4rem !important;
    }

    /* Dark slate text on ALL labels, sliders, toggles, headings, and markdown */
    .stApp p, .stApp li, .stApp span, .stApp label,
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
    [data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] span,
    [data-testid="stSlider"] label, [data-testid="stSlider"] p, [data-testid="stSlider"] div,
    [data-testid="stCheckbox"] label, [data-testid="stCheckbox"] p,
    [data-testid="stExpander"] summary, [data-testid="stExpander"] summary p, [data-testid="stExpander"] summary svg,
    [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p,
    [data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li {
        color: #0f172a !important;
    }

    /* Slider value bubble & min/max ticks */
    [data-testid="stSliderTickBarMin"],
    [data-testid="stSliderTickBarMax"],
    [data-testid="stThumbValue"] {
        color: #334155 !important;
        background: transparent !important;
    }

    /* Inputs, Textareas & Selectboxes */
    .stApp input,
    .stApp textarea,
    [data-baseweb="select"] > div,
    [data-baseweb="input"] > div {
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 10px !important;
        color: #0f172a !important;
        -webkit-text-fill-color: #0f172a !important;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);
    }

    /* Dropdown popover menu (rendered in a portal outside .stApp) */
    [data-baseweb="popover"],
    [data-baseweb="popover"] ul,
    [data-baseweb="menu"],
    [role="listbox"],
    [role="option"] {
        background-color: #ffffff !important;
        color: #0f172a !important;
    }
    [role="option"]:hover, [aria-selected="true"][role="option"] {
        background-color: #eff6ff !important;
        color: #1d4ed8 !important;
    }

    .stApp textarea:focus, .stApp input:focus {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12) !important;
    }
    .stApp input::placeholder, .stApp textarea::placeholder {
        color: #94a3b8 !important;
        -webkit-text-fill-color: #94a3b8 !important;
        opacity: 1 !important;
    }

    /* Expander header & body background */
    [data-testid="stExpander"] {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
    }

    /* Hero Banner */
    .stApp .hero-card {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 55%, #0f766e 100%) !important;
        border-radius: 16px;
        padding: 2rem 2.25rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    .stApp .hero-card .hero-badge {
        display: inline-block;
        background: rgba(45, 212, 191, 0.15) !important;
        color: #5eead4 !important;
        -webkit-text-fill-color: #5eead4 !important;
        border: 1px solid rgba(45, 212, 191, 0.3);
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        padding: 0.25rem 0.7rem;
        border-radius: 999px;
        margin-bottom: 0.75rem;
    }
    .stApp .hero-card .hero-title {
        margin: 0 0 0.45rem 0;
        font-size: 1.9rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        line-height: 1.2;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }
    .stApp .hero-card p {
        margin: 0;
        font-size: 0.98rem;
        color: #e2e8f0 !important;
        -webkit-text-fill-color: #e2e8f0 !important;
        max-width: 680px;
        line-height: 1.5;
    }

    /* Containers & Cards */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 14px !important;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
    }

    /* Metrics */
    div[data-testid="stMetric"] {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        padding: 1rem 1.25rem;
        border-radius: 12px;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);
    }
    div[data-testid="stMetric"] label, div[data-testid="stMetric"] label p {
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        color: #64748b !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-size: 1.65rem !important;
        font-weight: 700 !important;
        color: #0f172a !important;
    }

    /* Primary Button */
    button[kind="primary"] {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.6rem 1.25rem !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25) !important;
        transition: all 0.15s ease;
    }
    button[kind="primary"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(37, 99, 235, 0.35) !important;
    }
    button[kind="primary"] p, button[kind="primary"] span {
        background: transparent !important;
        font-weight: 600 !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }

    /* Secondary Buttons */
    button[kind="secondary"] {
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 10px !important;
    }
    button[kind="secondary"] p, button[kind="secondary"] span {
        background: transparent !important;
        color: #1e293b !important;
        font-weight: 500 !important;
    }
    button[kind="secondary"]:hover {
        background-color: #f1f5f9 !important;
        border-color: #94a3b8 !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        border-bottom: 1px solid #e2e8f0;
        padding-bottom: 0.25rem;
    }
    .stTabs [data-baseweb="tab"], .stTabs [data-baseweb="tab"] p {
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        color: #64748b !important;
    }
    .stTabs [aria-selected="true"], .stTabs [aria-selected="true"] p {
        background-color: #eff6ff !important;
        color: #1d4ed8 !important;
        font-weight: 600 !important;
    }

    /* Custom Badges for Requirements */
    .pill-row {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
        margin-bottom: 0.75rem;
    }
    .pill {
        font-size: 0.75rem;
        font-weight: 600;
        padding: 0.2rem 0.65rem;
        border-radius: 6px;
        background: #f1f5f9;
        color: #334155 !important;
        border: 1px solid #e2e8f0;
    }
    .pill-high {
        background: #fef2f2 !important;
        color: #b91c1c !important;
        border-color: #fecaca !important;
    }
    .pill-med {
        background: #fffbeb !important;
        color: #b45309 !important;
        border-color: #fde68a !important;
    }
    .pill-low {
        background: #f0fdf4 !important;
        color: #15803d !important;
        border-color: #bbf7d0 !important;
    }
    code, pre {
        font-family: 'JetBrains Mono', monospace !important;
        color: #0f172a !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def api_url() -> str:
    return st.session_state.get("api_base_url", "http://127.0.0.1:8000").strip().rstrip("/")


HISTORY_PATH = Path(__file__).resolve().parent / "responses" / "ui_history.json"


def load_history() -> list[dict[str, Any]]:
    try:
        return json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []


def save_history(requirement: str, result: dict[str, Any]) -> None:
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    history = load_history()
    history.insert(0, {"created_at": datetime.now().astimezone().isoformat(), "requirement": requirement, "result": result})
    HISTORY_PATH.write_text(json.dumps(history[:50], ensure_ascii=False, indent=2), encoding="utf-8")


def select_document(name: str) -> None:
    st.session_state["selected_doc"] = name


def show_error(error: Exception) -> None:
    if isinstance(error, requests.HTTPError) and error.response is not None:
        try:
            detail = error.response.json().get("detail", error.response.text)
        except ValueError:
            detail = error.response.text
        st.error(f"Backend returned HTTP {error.response.status_code}: {detail}")
    elif isinstance(error, requests.ConnectionError):
        st.error("Could not connect to the backend. Start the FastAPI server and verify its URL.")
    elif isinstance(error, requests.Timeout):
        st.error("Request timed out. Model generation can take several minutes; check the backend and notebook.")
    else:
        st.error(f"Request failed: {error}")


def pretty_key(value: str) -> str:
    return value.replace("_", " ").strip().title()


def priority_pill_class(priority: str) -> str:
    p = str(priority).lower()
    if any(k in p for k in ("high", "must", "critical", "p0", "p1")):
        return "pill pill-high"
    if any(k in p for k in ("med", "should", "p2")):
        return "pill pill-med"
    if any(k in p for k in ("low", "could", "nice", "p3")):
        return "pill pill-low"
    return "pill"


def render_details(result: dict[str, Any]) -> None:
    requirements = result.get("extracted_requirements") or []
    quality = result.get("quality_check") or {}
    recommendation = result.get("sdlc_recommendation") or {}
    factors = result.get("sdlc_factors") or {}
    sources = result.get("sources") or []

    overview, req_tab, quality_tab, sdlc_tab, sources_tab, files_tab = st.tabs(
        [
            "📄 SRS Document",
            f"📋 Requirements ({len(requirements)})",
            "✅ Quality Review",
            "⚙️ SDLC Strategy",
            f"📚 Sources ({len(sources)})",
            "💾 Output Logs",
        ]
    )

    with overview:
        with st.container(border=True):
            top_left, top_right = st.columns([3, 1])
            top_left.markdown("#### Generated Software Requirements Specification")
            top_right.download_button(
                "⬇ Download .md",
                data=result.get("response", ""),
                file_name="generated_srs.md",
                mime="text/markdown",
                use_container_width=True,
            )
            st.divider()
            st.markdown(result.get("response") or "_No SRS text was returned._")

    with req_tab:
        if not requirements:
            st.info("No structured requirements were returned.")
        for index, item in enumerate(requirements, start=1):
            if not isinstance(item, dict):
                st.write(item)
                continue
            req_id = item.get("req_id", f"REQ-{index:03d}")
            title = item.get("title") or req_id
            category = item.get("category", "General")
            priority = item.get("priority", "Unspecified")

            with st.expander(f"**{req_id}** — {title}", expanded=(index <= 2)):
                st.markdown(
                    f"""
                    <div class="pill-row">
                        <span class="pill">Category: {category}</span>
                        <span class="{priority_pill_class(priority)}">Priority: {priority}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.write(item.get("description", ""))
                extra_keys = [
                    k for k in item.keys() if k not in {"req_id", "title", "description", "category", "priority"}
                ]
                if extra_keys:
                    st.divider()
                    for key in extra_keys:
                        st.markdown(f"**{pretty_key(key)}:** {item[key]}")

    with quality_tab:
        if not quality:
            st.info("No quality review was returned.")
        else:
            complete = quality.get("is_complete")
            q_cols = st.columns(2 if "ambiguity_score" in quality else 1)
            q_cols[0].metric("Completeness Status", "Complete" if complete else "Gaps Detected")
            if "ambiguity_score" in quality:
                q_cols[1].metric("Ambiguity Score", quality["ambiguity_score"])

            remaining = {k: v for k, v in quality.items() if k not in {"is_complete", "ambiguity_score"}}
            if remaining:
                with st.container(border=True):
                    for key, value in remaining.items():
                        st.markdown(f"**{pretty_key(key)}**")
                        st.write(value)

    with sdlc_tab:
        if not recommendation and not factors:
            st.info("No SDLC recommendation was returned.")
        else:
            with st.container(border=True):
                for key, value in recommendation.items():
                    st.markdown(f"**{pretty_key(key)}**")
                    st.write(value)
                if factors:
                    st.divider()
                    st.markdown("**Decision Factors**")
                    st.json(factors, expanded=True)

    with sources_tab:
        if not sources:
            st.info("No source metadata was returned. RAG may be disabled or no regulatory passages matched.")
        for index, source in enumerate(sources, start=1):
            with st.expander(f"Regulatory Reference #{index}", expanded=(index == 1)):
                st.json(source, expanded=True)

    with files_tab:
        with st.container(border=True):
            st.markdown("#### Backend Artifact Locations")
            st.caption("Intermediate stream logs and final outputs saved on the host running FastAPI.")
            st.code(
                f"Stream log : {result.get('stream_file') or 'Not provided'}\n"
                f"Response   : {result.get('response_file') or 'Not provided'}",
                language="text",
            )


# --- Header ---
st.markdown(
    """
    <div class="hero-card">
        <div class="hero-badge">Account Aggregator Compliance Engine</div>
        <div class="hero-title">Regulatory SRS Studio</div>
        <p>Transform high-level product requirements into structured, audit-ready Software Requirements Specifications grounded in Account Aggregator regulatory frameworks.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("### Saved outputs")
    saved_runs = load_history()
    if saved_runs:
        run_labels = [
            f"{item.get('created_at', '')[:16].replace('T', ' ')} · {item.get('requirement', '')[:55]}"
            for item in saved_runs
        ]
        selected_run = st.selectbox("Reopen a complete run", run_labels, key="saved_run_picker")
        if st.button("Open complete run", use_container_width=True):
            run = saved_runs[run_labels.index(selected_run)]
            st.session_state["last_result"] = run["result"]
            st.session_state["last_requirement"] = run.get("requirement", "")
            st.session_state["opened_saved_output"] = None
            st.rerun()
    else:
        st.caption("Completed SRS, requirements, quality review, SDLC analysis, and sources will be saved here.")

    try:
        saved_response = requests.get(f"{api_url()}/responses", timeout=10)
        saved_response.raise_for_status()
        saved_outputs = saved_response.json()
    except requests.RequestException:
        saved_outputs = []
    if saved_outputs:
        response_names = [item["name"] for item in saved_outputs]
        chosen_response = st.selectbox("Open a previous output", response_names)
        if st.button("Show saved output", use_container_width=True):
            try:
                saved = requests.get(f"{api_url()}/responses/{quote(chosen_response)}", timeout=10)
                saved.raise_for_status()
                st.session_state["opened_saved_output"] = saved.json()
            except requests.RequestException as error:
                show_error(error)
    else:
        st.caption("Generated Markdown files in backend/responses will appear here.")

if st.session_state.get("opened_saved_output"):
    old_output = st.session_state["opened_saved_output"]
    if st.button("← Back to generator"):
        st.session_state["opened_saved_output"] = None
        st.rerun()
    with st.container(border=True):
        st.markdown(f"### {old_output['name']}")
        st.markdown(old_output["content"])
    st.stop()

viewing_result = bool(st.session_state.get("last_result"))
if viewing_result:
    if st.button("← New requirement"):
        st.session_state["last_result"] = None
        st.rerun()

# --- Main Input Card ---
with st.container(border=True):
    st.markdown("#### Product Requirement Specification")
    requirement = st.text_area(
        "Minimal requirement",
        label_visibility="collapsed",
        placeholder="Describe your feature (e.g., Users can link savings accounts and fetch statements using PAN and DOB, with consent management and audit logging)...",
        height=140,
        max_chars=12000,
    )

    col_scale, col_rag, col_action = st.columns([1.2, 1.5, 1.3], vertical_alignment="bottom")
    scale = col_scale.selectbox("Organization scale", ["Small", "Medium", "Large"], index=1)
    use_rag = col_rag.toggle("Ground with AA Regulatory PDFs", value=True)
    submitted = col_action.button("Generate SRS →", type="primary", use_container_width=True)

# --- Compact Backend & Model Controls (Replaces Sidebar) ---
with st.expander("⚙️ Backend Connection & Model Parameters", expanded=False):
    conn_col1, conn_col2, conn_col3 = st.columns([2.5, 1, 1], vertical_alignment="bottom")
    conn_col1.text_input("FastAPI Endpoint URL", value="http://127.0.0.1:8000", key="api_base_url")
    if conn_col2.button("Ping API", use_container_width=True):
        try:
            response = requests.get(f"{api_url()}/health", timeout=10)
            response.raise_for_status()
            st.toast("Backend is online", icon="✅")
        except requests.RequestException as error:
            show_error(error)
    if conn_col3.button("Ingest PDFs", use_container_width=True):
        try:
            with st.spinner("Indexing regulatory PDFs..."):
                response = requests.post(f"{api_url()}/ingest", timeout=3600)
                response.raise_for_status()
            data = response.json()
            st.success(f"Indexed {data.get('documents', 0)} documents ({data.get('chunks', 0)} chunks).")
        except requests.RequestException as error:
            show_error(error)

    st.divider()
    p_left, p_mid, p_right = st.columns(3)
    max_new_tokens = p_left.slider("Max New Tokens", 256, 8192, 2048, 256)
    temperature = p_mid.slider("Temperature", 0.0, 2.0, 0.3, 0.05)
    top_p = p_right.slider("Top-p", 0.05, 1.0, 0.95, 0.05)

# --- Execution ---
if not viewing_result and submitted:
    if not requirement.strip():
        st.warning("Please enter a product requirement before generating.")
    else:
        payload = {
            "minimal_requirement": requirement.strip(),
            "scale": scale,
            "use_rag": use_rag,
            "human_approved": False,
            "max_new_tokens": max_new_tokens,
            "temperature": temperature,
            "top_p": top_p,
        }
        try:
            with st.expander("Live model stream", expanded=True):
                progress_area = st.empty()
                stream_area = st.empty()
            streamed_text = ""
            result = None
            with st.spinner("Synthesizing regulatory context and generating SRS..."):
                with requests.post(
                    f"{api_url()}/generate/stream",
                    json=payload,
                    timeout=(30, 3600),
                    stream=True,
                ) as response:
                    response.raise_for_status()
                    event_name = "message"
                    for line in response.iter_lines(decode_unicode=True):
                        if not line:
                            event_name = "message"
                            continue
                        if line.startswith("event:"):
                            event_name = line[6:].strip()
                        elif line.startswith("data:"):
                            data = json.loads(line[5:].strip())
                            if event_name == "progress":
                                progress_area.info(data)
                            elif event_name == "token":
                                streamed_text += data
                                stream_area.markdown(streamed_text)
                            elif event_name == "result":
                                result = data
                            elif event_name == "error":
                                raise RuntimeError(data)
            if result is None:
                raise RuntimeError("The backend stream ended before returning the completed SRS.")
            st.session_state["last_result"] = result
            st.session_state["last_requirement"] = requirement.strip()
            save_history(requirement.strip(), result)
        except (requests.RequestException, RuntimeError, ValueError) as error:
            show_error(error)

# --- Results Dashboard ---
result = st.session_state.get("last_result")
if result:
    output_col, info_col = st.columns([2, 1], gap="large")
    with output_col:
        st.markdown("### Generated Output")
        st.caption(f"**Input prompt:** {st.session_state.get('last_requirement', '')}")

    with info_col:
        st.markdown("### Run details")
        st.metric("Extracted requirements", len(result.get("extracted_requirements") or []))
        st.metric("Regulatory citations", len(result.get("sources") or []))
        st.metric("Quality audit", "Passed" if (result.get("quality_check") or {}).get("is_complete") else "Needs review")
        with st.expander("Sources"):
            st.json(result.get("sources") or [], expanded=False)

    with output_col:
      
        metric_cols = st.columns(3)
        metric_cols[0].metric("Requirements", len(result.get("extracted_requirements") or []))
        metric_cols[1].metric("Sources", len(result.get("sources") or []))
        metric_cols[2].metric("Quality", "Passed" if (result.get("quality_check") or {}).get("is_complete") else "Review")

    stage_names = ["Requirements", "Quality Review", "SDLC Strategy", "Final SRS"]
    stage = st.session_state.get("review_stage", 0)
    st.progress((stage + 1) / len(stage_names), text=f"Stage {stage + 1} of {len(stage_names)} · {stage_names[stage]}")
    stage_cols = st.columns([1, 5, 1])
    if stage_cols[0].button("← Back", disabled=stage == 0, use_container_width=True):
        st.session_state["review_stage"] = max(0, stage - 1)
        st.rerun()
    stage_cols[2].button("Next →", disabled=stage == len(stage_names) - 1, use_container_width=True, on_click=lambda: st.session_state.update(review_stage=min(3, st.session_state.get("review_stage", 0) + 1)))
    if stage == 0:
        st.subheader("Extracted requirements")
        st.json(result.get("extracted_requirements") or [], expanded=True)
        with st.expander("Retrieved regulatory sources"):
            st.json(result.get("sources") or [], expanded=False)
    elif stage == 1:
        st.subheader("Quality review")
        st.json(result.get("quality_check") or {}, expanded=True)
    elif stage == 2:
        st.subheader("SDLC recommendation")
        st.json({"recommendation": result.get("sdlc_recommendation"), "decision_factors": result.get("sdlc_factors")}, expanded=True)
    else:
        st.subheader("Generated SRS")
        render_details(result)
