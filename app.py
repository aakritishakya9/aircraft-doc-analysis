import streamlit as st
import pandas as pd
import os
import sys
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

# Page Configuration
st.set_page_config(
    page_title="AeroChange | Aerospace Engineering Change Impact Command Center",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern Aerospace Command Center CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Top Status Bar */
    .telemetry-bar {
        background: linear-gradient(90deg, #0A192F 0%, #0F2A4A 100%);
        border: 1px solid #1E3A8A;
        border-radius: 8px;
        padding: 8px 16px;
        color: #E2E8F0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 13px;
        margin-bottom: 16px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.15);
    }
    .pulse-dot {
        height: 9px;
        width: 9px;
        background-color: #10B981;
        border-radius: 50%;
        display: inline-block;
        margin-right: 6px;
        box-shadow: 0 0 8px #10B981;
    }
    .zulu-time {
        font-family: 'JetBrains Mono', monospace;
        color: #38BDF8;
        font-weight: 600;
    }

    /* Titles */
    .main-title {
        font-size: 26px;
        font-weight: 800;
        color: #0A2540;
        letter-spacing: -0.5px;
        margin-bottom: 2px;
    }
    .sub-title {
        font-size: 14px;
        color: #475569;
        margin-bottom: 14px;
    }

    /* Metric Cards */
    .metric-card-custom {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 14px 18px;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .metric-card-custom:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
        border-color: #CBD5E1;
    }
    .metric-label-custom {
        font-size: 12px;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }
    .metric-value-custom {
        font-size: 26px;
        font-weight: 800;
        color: #0F172A;
    }

    /* Badges */
    .badge-critical {
        background-color: #FEF2F2;
        color: #DC2626;
        padding: 4px 10px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 11px;
        border: 1px solid #FECACA;
        display: inline-block;
    }
    .badge-high {
        background-color: #FFF7ED;
        color: #EA580C;
        padding: 4px 10px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 11px;
        border: 1px solid #FFEDD5;
        display: inline-block;
    }
    .badge-med {
        background-color: #FEFCE8;
        color: #CA8A04;
        padding: 4px 10px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 11px;
        border: 1px solid #FEF08A;
        display: inline-block;
    }
    .badge-success {
        background-color: #F0FDF4;
        color: #16A34A;
        padding: 4px 10px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 11px;
        border: 1px solid #BBF7D0;
        display: inline-block;
    }

    /* Content Cards */
    .aero-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 18px 20px;
        margin-bottom: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }
    .aero-card-header {
        font-size: 16px;
        font-weight: 700;
        color: #002B49;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Visual Document Viewer Frames */
    .doc-page-container {
        border: 2px solid #CBD5E1;
        border-radius: 8px;
        overflow: hidden;
        background: #F8FAFC;
        padding: 8px;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.04);
    }
</style>
""", unsafe_allow_html=True)

# Initialize Database
db = DatabaseManager()

# Top Live Telemetry Status Ribbon
zulu_now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC (ZULU)")
st.markdown(f"""
<div class="telemetry-bar">
    <div>
        <span class="pulse-dot"></span>
        <b>SYSTEM STATUS:</b> ONLINE &nbsp;|&nbsp; 
        <b>DATA FEED:</b> LIVE DATABASE SYNC &nbsp;|&nbsp; 
        <b>TARGET FLEET:</b> AIRBUS A320neo / A321NX
    </div>
    <div class="zulu-time">🕒 {zulu_now}</div>
</div>
""", unsafe_allow_html=True)

# Header Section
col_logo, col_heading = st.columns([1, 11])
with col_logo:
    st.markdown("# ✈️")
with col_heading:
    st.markdown('<div class="main-title">Aircraft Technical Documentation & Engineering Change Impact Analysis System</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Live Automated PDF Extraction, Tolerance Shift Diffing, Component Configuration, and Human-in-the-Loop Sign-Off</div>', unsafe_allow_html=True)

# Sample Documents Directory
sample_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "sample_pdfs")
export_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "export")
os.makedirs(sample_dir, exist_ok=True)
os.makedirs(export_dir, exist_ok=True)

# Ensure sample PDFs exist
hyd_rev1_path = os.path.join(sample_dir, "AMM_29_10_00_Rev01.pdf")
hyd_rev2_path = os.path.join(sample_dir, "AMM_29_10_00_Rev02.pdf")
lg_rev1_path = os.path.join(sample_dir, "SB_A320_32_1420_Rev01.pdf")
lg_rev2_path = os.path.join(sample_dir, "SB_A320_32_1420_Rev02.pdf")

if not (os.path.exists(hyd_rev1_path) and os.path.exists(hyd_rev2_path)):
    from data.generate_sample_pdfs import generate_all
    generate_all()

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

    # Part Interchangeability
    prev_pn = "P/N 9400-A"
    new_pn = "P/N 9400-B"
    interchange_data = FleetEffectivityManager.classify_part_interchangeability(prev_pn, new_pn, comp_results["parameter_diffs"])

    # Semantic Summary
    semantic_summary = SemanticChangeSummarizer.generate_executive_rationale(
        comp_results["metadata_diff"], comp_results["parameter_diffs"], comp_results["text_diff"], interchange_data
    )

    # Annotated PDF
    annotated_rev_path = os.path.join(export_dir, f"Annotated_{data_rev['doc_ref']}_{data_rev['revision']}.pdf")
    VisualPDFAnnotator.annotate_document_differences(rev_file, comp_results["parameter_diffs"], annotated_rev_path, is_revised_doc=True)

    # Convert to images for instant in-browser viewing
    base_images = VisualPDFAnnotator.render_pdf_pages_as_images(base_file, dpi=135)
    rev_annot_images = VisualPDFAnnotator.render_pdf_pages_as_images(annotated_rev_path, dpi=135)

    # Store in session state
    st.session_state["current_comp_results"] = comp_results
    st.session_state["current_impact_items"] = impact_items
    st.session_state["interchange_data"] = interchange_data
    st.session_state["semantic_summary"] = semantic_summary
    st.session_state["annotated_pdf_path"] = annotated_rev_path
    st.session_state["data_base"] = data_base
    st.session_state["data_rev"] = data_rev
    st.session_state["base_images"] = base_images
    st.session_state["rev_annot_images"] = rev_annot_images

    # Seed in Database
    db.log_document_revision(data_rev["doc_ref"], data_rev["revision"], data_rev["pub_date"], data_rev["component_id"])
    db.log_engineering_changes(impact_items)
    db.update_component_status(data_rev["component_id"], data_rev["revision"], "Under Review")

# -------------------------------------------------------------
# LIVE EXECUTIVE KPI METRIC RIBBON
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
    <div class="metric-card-custom" style="border-left: 3px solid #EF4444;">
        <div class="metric-label-custom">⏳ Pending Reviews</div>
        <div class="metric-value-custom" style="color:#DC2626;">{metrics['pending_reviews']} <span style="font-size:12px; color:#EF4444;">({metrics['critical_changes']} Critical)</span></div>
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
            st.rerun()

    st.markdown("---")
    st.markdown("### ✈️ Active Monitored Component")
    active_rev = st.session_state.get("data_rev", {})
    st.write(f"**Nomenclature:** {active_rev.get('component_name', 'N/A')}")
    st.write(f"**Component ID:** `{active_rev.get('component_id', 'N/A')}`")
    st.write(f"**ATA Chapter:** {active_rev.get('ata_chapter', 'N/A')}")
    st.write(f"**Document Ref:** `{active_rev.get('doc_ref', 'N/A')}`")

# -------------------------------------------------------------
# MAIN COMMAND CENTER TABS
# -------------------------------------------------------------
tab_diff, tab_visual, tab_rationale, tab_interchange, tab_fleet, tab_graph, tab_regulatory, tab_export = st.tabs([
    "📊 Parameter Shift Matrix",
    "👁️ Side-by-Side Visual PDF",
    "🧠 Engineering Rationale & Sign-Off",
    "🔄 Part Interchangeability",
    "✈️ Fleet MSN Effectivity",
    "🕸️ Subsystem Ripple Graph",
    "📡 Regulatory Feeds (FAA/EASA)",
    "📥 Configuration & Excel Export"
])

# -------------------------------------------------------------
# TAB 1: PARAMETER SHIFT MATRIX
# -------------------------------------------------------------
with tab_diff:
    st.subheader("1. Technical Document Specification Diff & Tolerance Analysis")
    
    data_base = st.session_state["data_base"]
    data_rev = st.session_state["data_rev"]
    comp_results = st.session_state["current_comp_results"]

    # Metadata Transition Cards
    st.markdown("""
    <div class="aero-card">
        <div class="aero-card-header">📑 Document Revision & Identification Shift</div>
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
    st.markdown("#### Detected Parameter Shifts & Tolerance Changes")
    diff_df = pd.DataFrame(comp_results["parameter_diffs"])
    if not diff_df.empty:
        display_diff = diff_df[["parameter", "previous_version", "updated_version", "delta", "change_type"]].copy()
        display_diff.columns = ["Parameter Description", "Previous Version", "Updated Version", "Shift / Delta (Δ)", "Change Classification"]
        st.dataframe(display_diff, use_container_width=True, hide_index=True)
    else:
        st.info("No parameters found.")

    # Text Diff Accordion
    with st.expander("🔍 View Accomplishment & Maintenance Text Diffs (Line-by-Line)", expanded=False):
        st.markdown(comp_results["text_diff"]["html_diff"], unsafe_allow_html=True)

# -------------------------------------------------------------
# TAB 2: SIDE-BY-SIDE VISUAL PDF VIEWER
# -------------------------------------------------------------
with tab_visual:
    st.subheader("2. Side-by-Side Visual Document Inspection")
    st.markdown("Direct visual rendering of the baseline PDF versus the revised PDF with **native PyMuPDF highlight bounding boxes**.")

    col_v1, col_v2 = st.columns(2)
    with col_v1:
        st.markdown(f"**BASELINE DOCUMENT: `{data_base['doc_ref']}` ({data_base['revision']})**")
        base_imgs = st.session_state.get("base_images", [])
        if base_imgs:
            st.markdown('<div class="doc-page-container">', unsafe_allow_html=True)
            st.image(base_imgs[0], caption="Baseline Page 1 (Original)", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with col_v2:
        st.markdown(f"**ANNOTATED REVISED DOCUMENT: `{data_rev['doc_ref']}` ({data_rev['revision']})**")
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
                mime="application/pdf"
            )

# -------------------------------------------------------------
# TAB 3: ENGINEERING RATIONALE & SIGN-OFF
# -------------------------------------------------------------
with tab_rationale:
    st.subheader("3. AI Engineering Rationale & Mandatory Sign-Off Portal")
    
    st.warning("⚠️ **MANDATORY AEROSPACE SAFETY NOTICE**: This software generates decision-support recommendations. In compliance with FAA 14 CFR Part 43 / EASA Part 145, certified engineers must review and sign off before releasing aircraft for flight.")

    summary = st.session_state.get("semantic_summary", {})
    if summary:
        # Executive Brief
        st.markdown("""
        <div class="aero-card" style="border-left: 4px solid #002B49;">
            <div class="aero-card-header">📋 Executive Engineering Rationale</div>
        """, unsafe_allow_html=True)
        for pt in summary.get("executive_brief", []):
            st.markdown(f"• {pt}", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Shop-Floor Actions
        st.markdown("""
        <div class="aero-card" style="border-left: 4px solid #0284C7;">
            <div class="aero-card-header">🛠️ Shop-Floor & Line Technician Action Directives</div>
        """, unsafe_allow_html=True)
        for act in summary.get("shop_floor_actions", []):
            st.markdown(f"• **ACTION ITEM**: {act}", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Airworthiness statement
        reg_level = summary.get('regulatory_level', 'STANDARD REVISION')
        st.markdown(f"""
        <div class="aero-card" style="border-left: 4px solid #DC2626;">
            <div class="aero-card-header" style="color:#DC2626;">⚖️ Airworthiness Regulatory Assessment: {reg_level}</div>
            <p style="color:#334155; margin-bottom:0;">{summary.get('regulatory_compliance_notes', '')}</p>
        </div>
        """, unsafe_allow_html=True)

    # Interactive Sign-Off Form
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

# -------------------------------------------------------------
# TAB 4: PART INTERCHANGEABILITY
# -------------------------------------------------------------
with tab_interchange:
    st.subheader("4. Aerospace Part Number Supersession & Interchangeability")
    st.markdown("Enforces OEM aerospace interchangeability standards (Class 1 Two-Way vs Class 2 One-Way vs Class 3 Non-Interchangeable).")

    ic_data = st.session_state.get("interchange_data", {})
    if ic_data:
        m1, m2 = st.columns(2)
        with m1:
            st.metric("Baseline Part Number (P/N)", ic_data["previous_part_number"])
        with m2:
            st.metric("New Superseding Part Number (P/N)", ic_data["updated_part_number"], delta=ic_data["interchangeability_class"])

        is_one_way = "Class 2" in ic_data["interchangeability_class"]
        banner_bg = "#FEF2F2" if is_one_way else "#F0FDF4"
        border_col = "#EF4444" if is_one_way else "#22C55E"
        header_col = "#991B1B" if is_one_way else "#166534"

        st.markdown(f"""
        <div style="background:{banner_bg}; border-left:5px solid {border_col}; padding:18px; border-radius:8px; margin: 15px 0;">
            <h4 style="color:{header_col}; margin-top:0;">{ic_data['interchangeability_class']}</h4>
            <p style="margin-bottom:8px;"><b>Engineering Definition:</b> {ic_data['engineering_definition']}</p>
            <p style="margin-bottom:8px;"><b>Supply Chain & Warehouse Action:</b> {ic_data['supply_chain_action']}</p>
            <p style="margin-bottom:0;"><b>Airworthiness Risk Assessment:</b> {ic_data['airworthiness_risk_level']}</p>
        </div>
        """, unsafe_allow_html=True)

# -------------------------------------------------------------
# TAB 5: FLEET MSN EFFECTIVITY
# -------------------------------------------------------------
with tab_fleet:
    st.subheader("5. Airline Fleet MSN & Tail Number Impact Evaluation")
    st.markdown("Cross-references document applicability definitions against actual aircraft tail numbers in your airline's fleet.")

    applicability_str = data_rev.get("full_text", "A320-271N / A321-271NX MSN 0200 through 0500 equipped with LEAP-1A")
    fleet_df = FleetEffectivityManager.evaluate_fleet_impact(applicability_str)

    affected_count = len(fleet_df[fleet_df["Fleet Impact Status"].str.contains("AFFECTED")])
    total_fleet = len(fleet_df)

    f1, f2, f3 = st.columns(3)
    f1.metric("Total Monitored Fleet", f"{total_fleet} Aircraft")
    f2.metric("Aircraft Tails Affected", f"{affected_count} Tails", delta=f"{total_fleet - affected_count} Exempt", delta_color="inverse")
    f3.metric("Fleet Readiness Status", "Action Plan Required" if affected_count > 0 else "Compliant")

    st.markdown("#### Live Aircraft Tail Number Impact Roster")
    st.dataframe(fleet_df, use_container_width=True, hide_index=True)

# -------------------------------------------------------------
# TAB 6: SUBSYSTEM RIPPLE GRAPH
# -------------------------------------------------------------
with tab_graph:
    st.subheader("6. Multi-System Ripple Effect (Knowledge Graph)")
    st.markdown("Visualizes topological relationships between the upstream power source (ATA 29) and downstream consumer circuits.")

    kg = AircraftSystemKnowledgeGraph()
    ripple_items = kg.trace_ripple_effect(data_rev.get("component_id", "HYD-001"))

    col_g_img, col_g_tbl = st.columns([3, 2])
    with col_g_img:
        graph_img_bytes = kg.render_graph_image()
        st.image(graph_img_bytes, caption="Topological Ripple Topology", use_container_width=True)

    with col_g_tbl:
        st.markdown("#### Downstream Circuit Consumers")
        ripple_df = pd.DataFrame(ripple_items)
        if not ripple_df.empty:
            st.dataframe(ripple_df, use_container_width=True, hide_index=True)

# -------------------------------------------------------------
# TAB 7: REGULATORY FEEDS
# -------------------------------------------------------------
with tab_regulatory:
    st.subheader("7. Live Regulatory Feeds (FAA & EASA Airworthiness Directives)")
    st.markdown("Real-time monitoring of legally binding Airworthiness Directives matching fleet components.")

    ad_df = RegulatoryFeedManager.get_latest_directives()
    st.dataframe(ad_df, use_container_width=True, hide_index=True)

# -------------------------------------------------------------
# TAB 8: EXCEL EXPORT & DATABASE
# -------------------------------------------------------------
with tab_export:
    st.subheader("8. Configuration Database & Excel Audit Reporting")
    
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

    st.markdown("#### Live Fleet Components Configuration Table")
    st.dataframe(comps_df, use_container_width=True, hide_index=True)

    st.markdown("#### Live Engineering Change Audit Log")
    st.dataframe(changes_df, use_container_width=True, hide_index=True)
