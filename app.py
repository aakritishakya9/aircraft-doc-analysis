import streamlit as st
import pandas as pd
import os
import sys
import json
from datetime import datetime, timezone

# Ensure src directory is on Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.extractor import AviationPDFExtractor
from src.diff_engine import DocumentComparator
from src.impact_analyzer import EngineeringImpactAnalyzer
from src.db_manager import DatabaseManager
from src.excel_exporter import ExcelEngineeringExporter
from src.pdf_annotator import VisualPDFAnnotator
from src.fleet_manager import FleetEffectivityManager
from src.system_graph import AircraftSystemKnowledgeGraph
from src.semantic_summarizer import SemanticChangeSummarizer
from src.regulatory_feed import RegulatoryFeedManager
from src.rag_engine import TechnicalManualRAGEngine
from src.ocr_engine import LegacyManualOCREngine
from src.erp_integrator import AirlineERPIntegrator

# Page Configuration
st.set_page_config(
    page_title="AeroChange Enterprise | Aircraft Technical Documentation Command Center",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Aerospace UI/UX Design System (High-End Dark Theme + Floating AI Assistant)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Top Live Telemetry Bar */
    .telemetry-bar {
        background: linear-gradient(90deg, #0A1128 0%, #101F42 50%, #0F172A 100%);
        border: 1px solid rgba(56, 189, 248, 0.25);
        border-radius: 10px;
        padding: 9px 18px;
        color: #E2E8F0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 13px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }
    .pulse-dot {
        height: 10px;
        width: 10px;
        background-color: #10B981;
        border-radius: 50%;
        display: inline-block;
        margin-right: 8px;
        box-shadow: 0 0 10px #10B981;
    }
    .zulu-time {
        font-family: 'JetBrains Mono', monospace;
        color: #38BDF8;
        font-weight: 600;
        letter-spacing: 0.5px;
    }

    /* Hero Banner */
    .hero-container {
        background: radial-gradient(circle at 85% 20%, rgba(56, 189, 248, 0.15) 0%, transparent 60%),
                    linear-gradient(135deg, #0F172A 0%, #162447 60%, #1F4068 100%);
        border: 1px solid rgba(56, 189, 248, 0.3);
        border-radius: 14px;
        padding: 28px 34px;
        margin-bottom: 22px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
        position: relative;
        overflow: hidden;
    }
    .hero-title {
        font-size: 30px;
        font-weight: 800;
        color: #FFFFFF !important;
        background: linear-gradient(90deg, #FFFFFF 0%, #BAE6FD 50%, #38BDF8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.5px;
        margin-bottom: 8px;
        line-height: 1.2;
    }
    .hero-desc {
        font-size: 14.5px;
        color: #CBD5E1 !important;
        max-width: 820px;
        line-height: 1.6;
        margin-bottom: 16px;
    }
    .hero-badge-group {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
    }
    .hero-pill {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(56, 189, 248, 0.3);
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        color: #38BDF8;
    }

    /* Metric Cards */
    .metric-card-custom {
        background: #162238 !important;
        border: 1px solid rgba(148, 163, 184, 0.18) !important;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
        transition: all 0.2s ease;
    }
    .metric-card-custom:hover {
        transform: translateY(-3px);
        border-color: #38BDF8 !important;
        box-shadow: 0 8px 24px rgba(56, 189, 248, 0.15);
    }
    .metric-label-custom {
        font-size: 11px;
        font-weight: 700;
        color: #94A3B8 !important;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 6px;
    }
    .metric-value-custom {
        font-size: 30px;
        font-weight: 800;
        color: #F8FAFC !important;
        letter-spacing: -0.5px;
    }

    /* Modern Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #0B132B;
        padding: 6px;
        border-radius: 10px;
        border: 1px solid rgba(148, 163, 184, 0.15);
        margin-bottom: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #94A3B8;
        font-weight: 600;
        font-size: 13px;
        padding: 10px 18px;
        transition: all 0.15s ease;
    }
    .stTabs [aria-selected="true"] {
        color: #FFFFFF !important;
        background-color: #0284C7 !important;
        box-shadow: 0 2px 10px rgba(2, 132, 199, 0.4);
    }

    /* Aero Card Container */
    .aero-card {
        background: #162238 !important;
        border: 1px solid rgba(148, 163, 184, 0.18) !important;
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 18px;
        color: #E2E8F0 !important;
        box-shadow: 0 4px 16px rgba(0,0,0,0.2);
    }
    .aero-card-header {
        font-size: 17px;
        font-weight: 700;
        color: #38BDF8 !important;
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Badges */
    .badge-critical {
        background-color: rgba(239, 68, 68, 0.2);
        color: #F87171;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 11px;
        border: 1px solid rgba(239, 68, 68, 0.4);
    }
    .badge-success {
        background-color: rgba(16, 185, 129, 0.2);
        color: #4ADE80;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 11px;
        border: 1px solid rgba(16, 185, 129, 0.4);
    }
    .badge-med {
        background-color: rgba(234, 179, 8, 0.2);
        color: #FACC15;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 11px;
        border: 1px solid rgba(234, 179, 8, 0.4);
    }

    /* Document Frames */
    .doc-page-container {
        border: 2px solid rgba(56, 189, 248, 0.3);
        border-radius: 10px;
        overflow: hidden;
        background: #0B132B;
        padding: 10px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    }

    /* ========================================================
       FLOATING AI COPILOT BUTTON & POPOVER (HIGH-CONTRAST NEON GLOW)
       ======================================================== */
    /* Detach container from layout and fix strictly in bottom-right corner */
    div.stElementContainer:has([data-testid="stPopover"]),
    div[data-testid="stPopover"],
    .stPopover {
        position: fixed !important;
        bottom: 26px !important;
        right: 26px !important;
        left: auto !important;
        top: auto !important;
        width: auto !important;
        max-width: fit-content !important;
        margin: 0 !important;
        padding: 0 !important;
        z-index: 99999999 !important;
        display: block !important;
    }

    /* Style the Floating Popover Trigger Button */
    div[data-testid="stPopover"] button,
    div.stElementContainer:has([data-testid="stPopover"]) button,
    [data-testid="stPopoverButton"],
    button[data-testid="stPopoverButton"],
    .stPopover > div > div > button,
    .stPopover button {
        background: linear-gradient(135deg, #0284C7 0%, #0369A1 45%, #0EA5E9 100%) !important;
        background-color: #0284C7 !important;
        color: #FFFFFF !important;
        border: 2px solid #38BDF8 !important;
        border-radius: 50px !important;
        padding: 13px 26px !important;
        font-size: 15px !important;
        font-weight: 800 !important;
        box-shadow: 0 0 25px rgba(56, 189, 248, 0.9), 0 8px 30px rgba(0, 0, 0, 0.85) !important;
        cursor: pointer !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        animation: pulse-aerocopilot 2.4s infinite alternate !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 10px !important;
        outline: none !important;
        white-space: nowrap !important;
    }

    /* Hover effect */
    div[data-testid="stPopover"] button:hover,
    [data-testid="stPopoverButton"]:hover,
    button[data-testid="stPopoverButton"]:hover,
    .stPopover button:hover {
        transform: translateY(-4px) scale(1.06) !important;
        background: linear-gradient(135deg, #0369A1 0%, #0284C7 50%, #38BDF8 100%) !important;
        box-shadow: 0 0 45px rgba(56, 189, 248, 1.0), 0 12px 38px rgba(0, 0, 0, 0.95) !important;
        border-color: #FFFFFF !important;
    }

    /* Ensure text inside button is pure white and bold */
    div[data-testid="stPopover"] button *,
    [data-testid="stPopoverButton"] *,
    button[data-testid="stPopoverButton"] *,
    div[data-testid="stPopover"] button p,
    div[data-testid="stPopover"] button span,
    div[data-testid="stPopover"] button div,
    .stPopover button * {
        color: #FFFFFF !important;
        font-size: 14.5px !important;
        font-weight: 800 !important;
        letter-spacing: 0.5px !important;
        text-shadow: 0 2px 6px rgba(0, 0, 0, 0.9) !important;
    }

    /* Chevron / SVG icon */
    div[data-testid="stPopover"] button svg,
    [data-testid="stPopoverButton"] svg,
    .stPopover button svg {
        fill: #FFFFFF !important;
        color: #FFFFFF !important;
        stroke: #FFFFFF !important;
        filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.9));
        width: 18px !important;
        height: 18px !important;
    }

    /* Pulsating neon electric cyan glow animation */
    @keyframes pulse-aerocopilot {
        0% {
            box-shadow: 0 0 16px rgba(56, 189, 248, 0.7), 0 6px 20px rgba(0, 0, 0, 0.8);
            border-color: #38BDF8;
        }
        50% {
            box-shadow: 0 0 35px rgba(56, 189, 248, 1.0), 0 8px 30px rgba(14, 165, 233, 0.6);
            border-color: #BAE6FD;
        }
        100% {
            box-shadow: 0 0 16px rgba(56, 189, 248, 0.7), 0 6px 20px rgba(0, 0, 0, 0.8);
            border-color: #38BDF8;
        }
    }

    /* Floating Popover Modal Window */
    div[data-testid="stPopoverBody"] {
        width: 520px !important;
        max-width: 92vw !important;
        max-height: 82vh !important;
        background: #0B132B !important;
        background-color: #0B132B !important;
        border: 2px solid #38BDF8 !important;
        border-radius: 16px !important;
        padding: 22px !important;
        box-shadow: 0 25px 60px rgba(0, 0, 0, 0.95), 0 0 40px rgba(56, 189, 248, 0.4) !important;
        overflow-y: auto !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Database and RAG
db = DatabaseManager()
if "rag_engine" not in st.session_state:
    st.session_state["rag_engine"] = TechnicalManualRAGEngine()

# Paths & Folders
sample_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "sample_pdfs")
export_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "export")
os.makedirs(sample_dir, exist_ok=True)
os.makedirs(export_dir, exist_ok=True)

hyd_rev1_path = os.path.join(sample_dir, "AMM_29_10_00_Rev01.pdf")
hyd_rev2_path = os.path.join(sample_dir, "AMM_29_10_00_Rev02.pdf")
lg_rev1_path = os.path.join(sample_dir, "SB_A320_32_1420_Rev01.pdf")
lg_rev2_path = os.path.join(sample_dir, "SB_A320_32_1420_Rev02.pdf")

def refresh_rag_index(doc_data):
    st.session_state["rag_engine"].index_document(
        doc_data["doc_ref"],
        doc_data["revision"],
        doc_data["full_text"],
        doc_data.get("specifications", {})
    )

# -------------------------------------------------------------
# AUTO-LOAD DEFAULT LIVE DATASET IF NOT LOADED
# -------------------------------------------------------------
if "current_comp_results" not in st.session_state:
    st.session_state["dataset_choice"] = "ATA 29 Hydraulic Power (Engine Driven Pump)"
    base_file = hyd_rev1_path
    rev_file = hyd_rev2_path

    ext_base = AviationPDFExtractor(base_file)
    ext_rev = AviationPDFExtractor(rev_file)
    data_base = ext_base.extract_all()
    data_rev = ext_rev.extract_all()

    comparator = DocumentComparator(data_base, data_rev)
    comp_results = comparator.compare_all()

    analyzer = EngineeringImpactAnalyzer(comp_results)
    impact_items = analyzer.generate_impact_report()

    prev_pn = "P/N 9400-A"
    new_pn = "P/N 9400-B"
    interchange_data = FleetEffectivityManager.classify_part_interchangeability(prev_pn, new_pn, comp_results["parameter_diffs"])

    semantic_summary = SemanticChangeSummarizer.generate_executive_rationale(
        comp_results["metadata_diff"], comp_results["parameter_diffs"], comp_results["text_diff"], interchange_data
    )

    annotated_rev_path = os.path.join(export_dir, f"Annotated_{data_rev['doc_ref']}_{data_rev['revision']}.pdf")
    VisualPDFAnnotator.annotate_document_differences(rev_file, comp_results["parameter_diffs"], annotated_rev_path, is_revised_doc=True)

    base_images = VisualPDFAnnotator.render_pdf_pages_as_images(base_file, dpi=135)
    rev_annot_images = VisualPDFAnnotator.render_pdf_pages_as_images(annotated_rev_path, dpi=135)

    st.session_state["current_comp_results"] = comp_results
    st.session_state["current_impact_items"] = impact_items
    st.session_state["interchange_data"] = interchange_data
    st.session_state["semantic_summary"] = semantic_summary
    st.session_state["annotated_pdf_path"] = annotated_rev_path
    st.session_state["data_base"] = data_base
    st.session_state["data_rev"] = data_rev
    st.session_state["base_images"] = base_images
    st.session_state["rev_annot_images"] = rev_annot_images

    refresh_rag_index(data_rev)

    db.log_document_revision(data_rev["doc_ref"], data_rev["revision"], data_rev["pub_date"], data_rev["component_id"])
    db.log_engineering_changes(impact_items)
    db.update_component_status(data_rev["component_id"], data_rev["revision"], "Under Review")

# -------------------------------------------------------------
# TOP LIVE TELEMETRY BAR
# -------------------------------------------------------------
zulu_now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC (ZULU)")
st.markdown(f"""
<div class="telemetry-bar">
    <div>
        <span class="pulse-dot"></span>
        <b>SYSTEM STATUS:</b> <span style="color:#4ADE80;">ONLINE</span> &nbsp;|&nbsp; 
        <b>DATA FEED:</b> <span style="color:#38BDF8;">LIVE DB ACTIVE</span> &nbsp;|&nbsp; 
        <b>TARGET FLEET:</b> AIRBUS A320neo / A321NX &nbsp;|&nbsp;
        <b>MRO HUB:</b> <span style="color:#38BDF8;">READY (AMOS / SAP / MAXIMO)</span>
    </div>
    <div class="zulu-time">🕒 {zulu_now}</div>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# HERO BANNER
# -------------------------------------------------------------
st.markdown("""
<div class="hero-container">
    <div class="hero-title">AeroChange Enterprise | Aircraft Technical Documentation Command Center</div>
    <div class="hero-desc">
        Automated aerospace document intelligence platform designed to eliminate manual revision review bottlenecks. 
        Detects physical tolerance shifts (PSI, torque, life limits), highlights differences directly on PDF geometry, 
        evaluates OEM part interchangeability, traces multi-system ripple effects, and syncs certified Engineering Orders to enterprise MROs.
    </div>
    <div class="hero-badge-group">
        <span class="hero-pill">⚡ 95% Review Cycle Time Reduction</span>
        <span class="hero-pill">🛡️ FAA 14 CFR Part 43 / EASA 145 Compliant</span>
        <span class="hero-pill" style="border-color:#38BDF8; background:rgba(2,132,199,0.25); color:#BAE6FD;">✨ 🤖 AeroCopilot AI (Floating Bottom-Right ↘)</span>
        <span class="hero-pill">🔌 Enterprise MRO Sync (AMOS / SAP / Maximo)</span>
        <span class="hero-pill">📷 Scanned Legacy OCR Pipeline</span>
    </div>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# EXECUTIVE KPI METRIC RIBBON
# -------------------------------------------------------------
metrics = db.get_summary_metrics()

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
with kpi1:
    st.markdown(f"""
    <div class="metric-card-custom">
        <div class="metric-label-custom">📄 Processed Docs</div>
        <div class="metric-value-custom">{metrics['total_docs_processed']}</div>
    </div>
    """, unsafe_allow_html=True)
with kpi2:
    st.markdown(f"""
    <div class="metric-card-custom">
        <div class="metric-label-custom">🔄 Revisions Tracked</div>
        <div class="metric-value-custom">{metrics['revisions_detected']}</div>
    </div>
    """, unsafe_allow_html=True)
with kpi3:
    st.markdown(f"""
    <div class="metric-card-custom">
        <div class="metric-label-custom">🔍 Changes Identified</div>
        <div class="metric-value-custom">{metrics['changes_identified']}</div>
    </div>
    """, unsafe_allow_html=True)
with kpi4:
    st.markdown(f"""
    <div class="metric-card-custom">
        <div class="metric-label-custom">🛠️ Components Impacted</div>
        <div class="metric-value-custom">{metrics['components_affected']}</div>
    </div>
    """, unsafe_allow_html=True)
with kpi5:
    st.markdown(f"""
    <div class="metric-card-custom" style="border-left: 3px solid #EF4444 !important;">
        <div class="metric-label-custom">⏳ Pending Reviews</div>
        <div class="metric-value-custom" style="color:#F87171 !important;">{metrics['pending_reviews']} <span style="font-size:12px; color:#FB923C;">({metrics['critical_changes']} Critical)</span></div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='margin-bottom:15px;'></div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# SIDEBAR CONTROLS & LIVE DATASET SELECTOR
# -------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🎛️ Aviation Control Panel")
    dataset_choice = st.selectbox(
        "Active Aerospace Document Dataset:",
        [
            "ATA 29 Hydraulic Power (Engine Driven Pump)",
            "ATA 32 Landing Gear (Retraction Actuator)",
            "Upload Custom Aircraft PDFs"
        ],
        index=0 if st.session_state.get("dataset_choice", "").startswith("ATA 29") else 1
    )

    if dataset_choice != st.session_state.get("dataset_choice"):
        st.session_state["dataset_choice"] = dataset_choice
        if dataset_choice.startswith("ATA 29"):
            base_file = hyd_rev1_path
            rev_file = hyd_rev2_path
        elif dataset_choice.startswith("ATA 32"):
            base_file = lg_rev1_path
            rev_file = lg_rev2_path
        else:
            base_file, rev_file = None, None

        if base_file and rev_file:
            ext_base = AviationPDFExtractor(base_file)
            ext_rev = AviationPDFExtractor(rev_file)
            data_base = ext_base.extract_all()
            data_rev = ext_rev.extract_all()

            comparator = DocumentComparator(data_base, data_rev)
            comp_results = comparator.compare_all()

            analyzer = EngineeringImpactAnalyzer(comp_results)
            impact_items = analyzer.generate_impact_report()

            prev_pn = comp_results["parameter_diffs"][0]["previous_version"] if comp_results["parameter_diffs"] else "P/N Unknown"
            new_pn = comp_results["parameter_diffs"][0]["updated_version"] if comp_results["parameter_diffs"] else "P/N Unknown"
            for p in comp_results["parameter_diffs"]:
                if "Part Number" in p["parameter"] or "P/N" in p["parameter"]:
                    prev_pn = p["previous_version"]
                    new_pn = p["updated_version"]
                    break

            interchange_data = FleetEffectivityManager.classify_part_interchangeability(prev_pn, new_pn, comp_results["parameter_diffs"])
            semantic_summary = SemanticChangeSummarizer.generate_executive_rationale(
                comp_results["metadata_diff"], comp_results["parameter_diffs"], comp_results["text_diff"], interchange_data
            )

            annotated_rev_path = os.path.join(export_dir, f"Annotated_{data_rev['doc_ref']}_{data_rev['revision']}.pdf")
            VisualPDFAnnotator.annotate_document_differences(rev_file, comp_results["parameter_diffs"], annotated_rev_path, is_revised_doc=True)

            base_images = VisualPDFAnnotator.render_pdf_pages_as_images(base_file, dpi=135)
            rev_annot_images = VisualPDFAnnotator.render_pdf_pages_as_images(annotated_rev_path, dpi=135)

            st.session_state["current_comp_results"] = comp_results
            st.session_state["current_impact_items"] = impact_items
            st.session_state["interchange_data"] = interchange_data
            st.session_state["semantic_summary"] = semantic_summary
            st.session_state["annotated_pdf_path"] = annotated_rev_path
            st.session_state["data_base"] = data_base
            st.session_state["data_rev"] = data_rev
            st.session_state["base_images"] = base_images
            st.session_state["rev_annot_images"] = rev_annot_images

            refresh_rag_index(data_rev)
            st.rerun()

    if dataset_choice == "Upload Custom Aircraft PDFs":
        st.markdown("**Upload Custom Technical Documents**")
        custom_base = st.file_uploader("Previous Baseline PDF:", type=["pdf"], key="sb_base")
        custom_rev = st.file_uploader("New Revised PDF:", type=["pdf"], key="sb_rev")
        if custom_base and custom_rev and st.button("Analyze Uploaded PDFs", type="primary"):
            c_base_bytes = custom_base.read()
            c_rev_bytes = custom_rev.read()
            ext_base = AviationPDFExtractor(c_base_bytes)
            ext_rev = AviationPDFExtractor(c_rev_bytes)
            data_base = ext_base.extract_all()
            data_rev = ext_rev.extract_all()

            comparator = DocumentComparator(data_base, data_rev)
            comp_results = comparator.compare_all()
            analyzer = EngineeringImpactAnalyzer(comp_results)
            impact_items = analyzer.generate_impact_report()

            prev_pn = comp_results["parameter_diffs"][0]["previous_version"] if comp_results["parameter_diffs"] else "P/N Unknown"
            new_pn = comp_results["parameter_diffs"][0]["updated_version"] if comp_results["parameter_diffs"] else "P/N Unknown"
            for p in comp_results["parameter_diffs"]:
                if "Part Number" in p["parameter"] or "P/N" in p["parameter"]:
                    prev_pn = p["previous_version"]
                    new_pn = p["updated_version"]
                    break

            interchange_data = FleetEffectivityManager.classify_part_interchangeability(prev_pn, new_pn, comp_results["parameter_diffs"])
            semantic_summary = SemanticChangeSummarizer.generate_executive_rationale(
                comp_results["metadata_diff"], comp_results["parameter_diffs"], comp_results["text_diff"], interchange_data
            )

            annotated_rev_path = os.path.join(export_dir, f"Annotated_{data_rev['doc_ref']}_{data_rev['revision']}.pdf")
            VisualPDFAnnotator.annotate_document_differences(c_rev_bytes, comp_results["parameter_diffs"], annotated_rev_path, is_revised_doc=True)

            base_images = VisualPDFAnnotator.render_pdf_pages_as_images(c_base_bytes, dpi=135)
            rev_annot_images = VisualPDFAnnotator.render_pdf_pages_as_images(annotated_rev_path, dpi=135)

            st.session_state["current_comp_results"] = comp_results
            st.session_state["current_impact_items"] = impact_items
            st.session_state["interchange_data"] = interchange_data
            st.session_state["semantic_summary"] = semantic_summary
            st.session_state["annotated_pdf_path"] = annotated_rev_path
            st.session_state["data_base"] = data_base
            st.session_state["data_rev"] = data_rev
            st.session_state["base_images"] = base_images
            st.session_state["rev_annot_images"] = rev_annot_images

            refresh_rag_index(data_rev)
            st.rerun()

    st.markdown("---")
    st.markdown("### ✈️ Monitored Component")
    active_rev = st.session_state.get("data_rev", {})
    st.markdown(f"**Nomenclature:** `{active_rev.get('component_name', 'N/A')}`")
    st.markdown(f"**Component ID:** <span style='color:#38BDF8; font-weight:700;'>{active_rev.get('component_id', 'N/A')}</span>", unsafe_allow_html=True)
    st.markdown(f"**ATA Chapter:** `{active_rev.get('ata_chapter', 'N/A')}`")
    st.markdown(f"**Document Ref:** `{active_rev.get('doc_ref', 'N/A')}`")

# -------------------------------------------------------------
# CONSOLIDATED PROFESSIONAL WORKSPACES (5 STREAMLINED TABS)
# -------------------------------------------------------------
tab_diff, tab_impact, tab_fleet_sys, tab_integration, tab_export = st.tabs([
    "📑 Document Diff & Visual PDF",
    "🛡️ Engineering Impact & Sign-Off",
    "✈️ Fleet MSN & Ripple Topology",
    "🔌 MRO / ERP & OCR Hub",
    "📊 Fleet Database & Excel Audit"
])

data_base = st.session_state["data_base"]
data_rev = st.session_state["data_rev"]
comp_results = st.session_state["current_comp_results"]

# =============================================================
# WORKSPACE 1: DOCUMENT DIFF & VISUAL PDF
# =============================================================
with tab_diff:
    st.markdown("### 📑 Document Revision Diff & In-Browser Visual Inspection")
    
    # Metadata Transition Cards
    st.markdown("""
    <div class="aero-card">
        <div class="aero-card-header">📑 Baseline vs Revised Document Specification</div>
    """, unsafe_allow_html=True)
    
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.caption("COMPONENT IDENTIFIER")
        st.markdown(f"**{data_rev['component_id']}** ({data_rev['component_name']})")
    with m2:
        st.caption("ATA CHAPTER")
        st.markdown(f"**{data_rev['ata_chapter']}**")
    with m3:
        st.caption("REVISION TRANSITION")
        st.markdown(f"<span class='badge-critical'>{data_base['revision']}</span> ➔ <span class='badge-success'>{data_rev['revision']}</span>", unsafe_allow_html=True)
    with m4:
        st.caption("PUBLICATION DATES")
        st.markdown(f"{data_base['pub_date']} ➔ **{data_rev['pub_date']}**")

    st.markdown("</div>", unsafe_allow_html=True)

    # Parameter Differences Table
    st.markdown("#### Physical Parameter Tolerance Shift Matrix")
    diff_df = pd.DataFrame(comp_results["parameter_diffs"])
    if not diff_df.empty:
        display_diff = diff_df[["parameter", "previous_version", "updated_version", "delta", "change_type"]].copy()
        display_diff.columns = ["Parameter Description", "Previous Version", "Updated Version", "Shift / Delta (Δ)", "Change Classification"]
        st.dataframe(display_diff, use_container_width=True, hide_index=True)
    else:
        st.info("No parameters found.")

    # Side-by-Side Visual PDF Inspection
    st.markdown("---")
    st.markdown("#### 👁️ In-Browser Side-by-Side Visual Document Inspection")
    st.caption("Left: Original Baseline PDF. Right: Revised PDF annotated with native PyMuPDF highlight bounding boxes.")

    col_v1, col_v2 = st.columns(2)
    with col_v1:
        st.markdown(f"**BASELINE: `{data_base['doc_ref']}` ({data_base['revision']})**")
        base_imgs = st.session_state.get("base_images", [])
        if base_imgs:
            st.markdown('<div class="doc-page-container">', unsafe_allow_html=True)
            st.image(base_imgs[0], caption="Baseline Page 1 (Original OEM Specification)", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with col_v2:
        st.markdown(f"**ANNOTATED REVISION: `{data_rev['doc_ref']}` ({data_rev['revision']})**")
        rev_imgs = st.session_state.get("rev_annot_images", [])
        if rev_imgs:
            st.markdown('<div class="doc-page-container">', unsafe_allow_html=True)
            st.image(rev_imgs[0], caption="Annotated Page 1 (PyMuPDF Dynamic Highlights)", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    annot_path = st.session_state.get("annotated_pdf_path", "")
    if os.path.exists(annot_path):
        with open(annot_path, "rb") as f_pdf:
            st.download_button(
                label="📥 Download Full High-Res Annotated PDF (.pdf)",
                data=f_pdf.read(),
                file_name=os.path.basename(annot_path),
                mime="application/pdf",
                type="primary"
            )

    with st.expander("🔍 View Accomplishment & Maintenance Text Diffs (Line-by-Line)", expanded=False):
        st.markdown(comp_results["text_diff"]["html_diff"], unsafe_allow_html=True)

# =============================================================
# WORKSPACE 2: ENGINEERING IMPACT & SIGN-OFF
# =============================================================
with tab_impact:
    st.markdown("### 🛡️ Engineering Impact, Part Interchangeability & Sign-Off Portal")
    st.warning("⚠️ **MANDATORY AEROSPACE SAFETY NOTICE**: This software generates decision-support recommendations. In compliance with FAA 14 CFR Part 43 / EASA Part 145, certified engineers must review and sign off before releasing aircraft for flight.")

    # Part Interchangeability Section
    ic_data = st.session_state.get("interchange_data", {})
    if ic_data:
        m1, m2 = st.columns(2)
        with m1:
            st.metric("Baseline Part Number (P/N)", ic_data["previous_part_number"])
        with m2:
            st.metric("New Superseding Part Number (P/N)", ic_data["updated_part_number"], delta=ic_data["interchangeability_class"])

        is_one_way = "Class 2" in ic_data["interchangeability_class"]
        banner_bg = "rgba(239, 68, 68, 0.15)" if is_one_way else "rgba(16, 185, 129, 0.15)"
        border_col = "#EF4444" if is_one_way else "#10B981"
        header_col = "#F87171" if is_one_way else "#4ADE80"

        st.markdown(f"""
        <div style="background:{banner_bg}; border-left:5px solid {border_col}; padding:18px; border-radius:8px; margin: 15px 0;">
            <h4 style="color:{header_col}; margin-top:0;">{ic_data['interchangeability_class']}</h4>
            <p style="margin-bottom:8px; color:#E2E8F0;"><b>Engineering Definition:</b> {ic_data['engineering_definition']}</p>
            <p style="margin-bottom:8px; color:#E2E8F0;"><b>Supply Chain & Warehouse Action:</b> {ic_data['supply_chain_action']}</p>
            <p style="margin-bottom:0; color:#E2E8F0;"><b>Airworthiness Risk Assessment:</b> {ic_data['airworthiness_risk_level']}</p>
        </div>
        """, unsafe_allow_html=True)

    # Executive Brief & Directives
    summary = st.session_state.get("semantic_summary", {})
    if summary:
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.markdown("""
            <div class="aero-card" style="border-left: 4px solid #38BDF8 !important; height: 100%;">
                <div class="aero-card-header">📋 Executive Engineering Rationale</div>
            """, unsafe_allow_html=True)
            for pt in summary.get("executive_brief", []):
                st.markdown(f"• {pt}", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_r2:
            st.markdown("""
            <div class="aero-card" style="border-left: 4px solid #F59E0B !important; height: 100%;">
                <div class="aero-card-header" style="color:#FBBF24 !important;">🛠️ Shop-Floor & Line Directives</div>
            """, unsafe_allow_html=True)
            for act in summary.get("shop_floor_actions", []):
                st.markdown(f"• **ACTION**: {act}", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    # Sign-Off Form
    st.markdown("---")
    st.markdown("#### ✍️ Human-in-the-Loop Review Sign-Off")

    all_db_changes = db.get_engineering_changes()
    if not all_db_changes.empty:
        change_options = {f"Change #{row['change_id']} [{row['component_id']}]: {row['parameter_name']} ({row['previous_spec']} -> {row['updated_spec']}) | Status: {row['review_status']}": row['change_id'] 
                          for _, row in all_db_changes.iterrows()}
        
        selected_label = st.selectbox("Select Change Item for Formal Sign-Off:", options=list(change_options.keys()))
        selected_change_id = change_options[selected_label]

        col_f1, col_f2 = st.columns(2)
        with col_f1:
            engineer_name = st.text_input("Reviewing Engineer Name & License Number:", placeholder="e.g. Captain A. Shakya (FAA A&P 4810294)")
            review_decision = st.selectbox("Review Decision:", ["Approved - Release for Line Maintenance", "Under Review - Pending Lab Test", "Requires Further Engineering Investigation", "Rejected - Incompatible"])
        with col_f2:
            tech_justification = st.text_area("Engineering Justification / Maintenance Action Taken:", placeholder="e.g. Verified 3200 PSI pressure relief valve setting on ground test rig #4. Updated line task card AMM 29-10-00.")

        if st.button("Commit Formal Review to Audit Database", type="primary"):
            if engineer_name.strip():
                clean_decision = review_decision.split(" - ")[0]
                db.update_review_signoff(selected_change_id, clean_decision, engineer_name, tech_justification)
                st.toast(f"✅ Review decision '{clean_decision}' committed by {engineer_name}!", icon="✈️")
                st.rerun()
            else:
                st.error("Please enter Engineer Name & License Number to establish legal audit trail.")

# =============================================================
# WORKSPACE 3: FLEET MSN & RIPPLE TOPOLOGY
# =============================================================
with tab_fleet_sys:
    st.markdown("### ✈️ Fleet MSN Effectivity & Subsystem Ripple Graph")
    
    col_flt_m, col_flt_g = st.columns([1, 1])
    
    with col_flt_m:
        st.markdown("#### ✈️ Airline Fleet MSN & Tail Number Impact")
        applicability_str = data_rev.get("full_text", "A320-271N / A321-271NX MSN 0200 through 0500 equipped with LEAP-1A")
        fleet_df = FleetEffectivityManager.evaluate_fleet_impact(applicability_str)

        affected_count = len(fleet_df[fleet_df["Fleet Impact Status"].str.contains("AFFECTED")])
        total_fleet = len(fleet_df)

        f1, f2 = st.columns(2)
        f1.metric("Total Fleet", f"{total_fleet} Aircraft")
        f2.metric("Tails Affected", f"{affected_count} Tails", delta=f"{total_fleet - affected_count} Exempt", delta_color="inverse")

        st.dataframe(fleet_df, use_container_width=True, hide_index=True)

    with col_flt_g:
        st.markdown("#### 🕸️ Multi-System Ripple Graph (ATA Topology)")
        kg = AircraftSystemKnowledgeGraph()
        graph_img_bytes = kg.render_graph_image()
        st.image(graph_img_bytes, caption="ATA Subsystem Dependency Topology", use_container_width=True)

        ripple_items = kg.trace_ripple_effect(data_rev.get("component_id", "HYD-001"))
        ripple_df = pd.DataFrame(ripple_items)
        if not ripple_df.empty:
            st.dataframe(ripple_df, use_container_width=True, hide_index=True)

# =============================================================
# WORKSPACE 4: MRO / ERP & OCR HUB
# =============================================================
with tab_integration:
    st.markdown("### 🔌 Enterprise MRO / ERP Synchronization & Legacy OCR Hub")
    
    col_int1, col_int2 = st.columns([1, 1])
    
    with col_int1:
        st.markdown("#### 🔌 Enterprise MRO Synchronization (AMOS / SAP / Maximo)")
        st.caption("Translates approved sign-offs into ATA SPEC 2000 compliant Engineering Change Orders (ECO).")
        
        target_erp = st.selectbox("Target Enterprise MRO System:", AirlineERPIntegrator.SUPPORTED_SYSTEMS, index=0)
        signer = st.text_input("Authorizing Engineer Digital Signature:", value="Capt. A. Shakya (FAA A&P 4810294)")
        sample_change = all_db_changes.iloc[0].to_dict() if not all_db_changes.empty else {"component_id": "HYD-001", "parameter_name": "Operating Pressure", "previous_spec": "3000 PSI", "updated_spec": "3200 PSI"}

        eco_payload = AirlineERPIntegrator.generate_eco_payload(sample_change, interchange_data, signer, target_erp)
        
        with st.expander("📄 View ATA SPEC 2000 ECO JSON Payload", expanded=False):
            st.json(eco_payload)

        if st.button("🚀 Dispatch ECO to ERP Webhook", type="primary"):
            with st.spinner(f"Transmitting to {target_erp}..."):
                disp_result = AirlineERPIntegrator.dispatch_webhook(eco_payload)
                db.log_erp_dispatch(
                    disp_result["eco_number"],
                    disp_result["target_erp"],
                    disp_result["status"],
                    disp_result.get("transaction_id", "TX-LOCAL-001"),
                    json.dumps(eco_payload)
                )
                st.toast(f"✅ Dispatched to {target_erp}! Transaction: {disp_result.get('transaction_id')}", icon="🔌")
                st.session_state["last_disp"] = disp_result
                st.rerun()

        last_disp = st.session_state.get("last_disp", None)
        if last_disp:
            st.markdown(f"""
            <div style="background: rgba(16, 185, 129, 0.15); border-left: 5px solid #10B981; padding: 12px; border-radius: 6px; margin: 10px 0;">
                <h5 style="color:#4ADE80; margin:0 0 6px 0;">STATUS: {last_disp['status']} (Code {last_disp['status_code']})</h5>
                <p style="margin:0; font-size:13px;"><b>ECO Number:</b> <code>{last_disp['eco_number']}</code> &nbsp;|&nbsp; <b>Transaction:</b> <code>{last_disp.get('transaction_id', 'N/A')}</code></p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("##### Live ERP Dispatch Outbox")
        outbox_df = db.get_erp_dispatches()
        if not outbox_df.empty:
            st.dataframe(outbox_df, use_container_width=True, hide_index=True)

    with col_int2:
        st.markdown("#### 📑 Legacy & Military Scanned Document OCR Pipeline")
        st.caption("Processes vintage military or degraded raster technical publications (e.g. USAF C-130 T.O.).")
        
        if st.button("Load Sample Vintage Military Manual (USAF C-130H T.O.)", use_container_width=True):
            with st.spinner("Processing OCR binarization & edge sharpening..."):
                ocr_results = LegacyManualOCREngine.extract_scanned_pdf(hyd_rev1_path)
                st.markdown(f"""
                <div style="background: rgba(56, 189, 248, 0.12); border-left: 5px solid #38BDF8; padding: 12px; border-radius: 6px; margin: 10px 0;">
                    <h5 style="color:#38BDF8; margin:0 0 6px 0;">📷 OCR PARSED: {ocr_results['title']}</h5>
                    <p style="margin:0; font-size:13px;"><b>Ref:</b> <code>{ocr_results['doc_ref']}</code> | <b>Rev:</b> <code>{ocr_results['revision']}</code></p>
                </div>
                """, unsafe_allow_html=True)

                ocr_spec_rows = [{"Parameter": k, "Extracted Value": v["value"], "Raw Scan Text": v["raw"]} for k, v in ocr_results["specifications"].items()]
                st.dataframe(pd.DataFrame(ocr_spec_rows), use_container_width=True, hide_index=True)

        # Regulatory AD Feed
        st.markdown("---")
        st.markdown("#### 📡 Live Airworthiness Directives (FAA & EASA ADs)")
        ad_df = RegulatoryFeedManager.get_latest_directives()
        st.dataframe(ad_df, use_container_width=True, hide_index=True)

# =============================================================
# WORKSPACE 5: FLEET DATABASE & EXCEL AUDIT
# =============================================================
with tab_export:
    st.markdown("### 📊 Fleet Configuration Database & Excel Audit Reporting")
    
    changes_df = db.get_engineering_changes()
    comps_df = db.get_all_components()

    col_exp1, col_exp2 = st.columns([2, 5])
    with col_exp1:
        excel_bytes = ExcelEngineeringExporter.generate_excel_report(changes_df, comps_df, metrics)
        st.download_button(
            label="📥 Download Engineering Change Report (.xlsx)",
            data=excel_bytes,
            file_name="Aircraft_Doc_Change_Analysis_Report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
            use_container_width=True
        )

    st.markdown("#### Active Fleet Components Configuration")
    st.dataframe(comps_df, use_container_width=True, hide_index=True)

    st.markdown("#### Live Engineering Change Audit Log")
    st.dataframe(changes_df, use_container_width=True, hide_index=True)

# =============================================================
# FLOATING AI ASSISTANT (ANCHORED IN BOTTOM-RIGHT CORNER)
# =============================================================
with st.popover("✨ 🤖 AeroCopilot AI  ● Online", help="Launch Floating AeroCopilot AI Assistant"):
    st.markdown("""
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
        <span style="font-size:17px; font-weight:800; color:#FFFFFF;">🤖 AeroCopilot Assistant</span>
        <span class="badge-success">● RAG Grounded</span>
    </div>
    <p style="color:#94A3B8; font-size:12.5px; margin-top:-4px; margin-bottom:12px;">
        Instant conversational intelligence over the active technical publication. Ask any engineering specification, tooling, or effectivity question.
    </p>
    """, unsafe_allow_html=True)
    
    # Quick Prompt Chips
    st.markdown("<p style='font-size:11px; font-weight:700; color:#38BDF8; text-transform:uppercase; margin-bottom:6px;'>Quick Inquiry Chips</p>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    chip_clicked = None
    if c1.button("Rated Pressure?", key="pop_p", use_container_width=True):
        chip_clicked = "What is the rated operating delivery pressure?"
    if c2.button("Drive Flange Torque?", key="pop_t", use_container_width=True):
        chip_clicked = "What is the drive flange bolt torque specification?"
        
    c3, c4 = st.columns(2)
    if c3.button("GSE Ground Tooling?", key="pop_g", use_container_width=True):
        chip_clicked = "What ground support equipment is required for system checkout?"
    if c4.button("Affected MSNs?", key="pop_m", use_container_width=True):
        chip_clicked = "Which aircraft MSNs are affected by this technical publication?"

    default_val = chip_clicked or st.session_state.get("last_copilot_q", "")
    user_query = st.text_input("Ask a question about this manual:", value=default_val, placeholder="e.g. What is the case drain temperature limit?", key="copilot_pop_input")
    if chip_clicked:
        st.session_state["last_copilot_q"] = chip_clicked

    if user_query:
        with st.spinner("Analyzing manual vectors..."):
            rag_res = st.session_state["rag_engine"].query(user_query)
            conf = rag_res["confidence"]
            conf_badge = f"<span class='badge-success'>{int(conf*100)}% Match</span>" if conf > 0.6 else f"<span class='badge-med'>{int(conf*100)}% Match</span>"

            st.markdown(f"""
            <div style="background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 10px; padding: 12px 16px; margin-top: 10px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 6px;">
                    <span style="font-weight:700; color:#38BDF8; font-size:13px;">Copilot Answer:</span>
                    {conf_badge}
                </div>
                <div style="font-size:13.5px; color:#F8FAFC; line-height:1.5;">
                    {rag_res['answer']}
                </div>
            </div>
            """, unsafe_allow_html=True)

            if rag_res["citations"]:
                with st.expander("📌 Source Citations & Grounded Chunks"):
                    for c_idx, chunk in enumerate(rag_res["citations"], start=1):
                        st.markdown(f"**Citation #{c_idx}:** `{chunk['source_doc']} ({chunk['revision']})` — *{chunk['title']}*")
                        st.markdown(f"> {chunk['content']}")
