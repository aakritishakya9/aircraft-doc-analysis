import streamlit as st
import pandas as pd
import os
import sys

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
    page_title="AeroChange Enterprise | Aircraft Technical Change Analysis System",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Aviation Styling
st.markdown("""
<style>
    .main-title {
        font-size: 26px;
        font-weight: 700;
        color: #002B49;
        margin-bottom: 2px;
    }
    .sub-title {
        font-size: 14px;
        color: #475569;
        margin-bottom: 18px;
    }
    .badge-critical {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 700;
        font-size: 12px;
        border: 1px solid #FCA5A5;
    }
    .badge-med {
        background-color: #FEF3C7;
        color: #92400E;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 12px;
        border: 1px solid #FCD34D;
    }
    .badge-low {
        background-color: #F1F5F9;
        color: #334155;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 12px;
        border: 1px solid #CBD5E1;
    }
    .badge-approved {
        background-color: #DCFCE7;
        color: #166534;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 12px;
        border: 1px solid #86EFAC;
    }
    .card-box {
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 14px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
</style>
""", unsafe_allow_html=True)

# Initialize Database
db = DatabaseManager()

# Header
col_logo, col_heading = st.columns([1, 11])
with col_logo:
    st.markdown("# ✈️")
with col_heading:
    st.markdown('<div class="main-title">Aircraft Technical Documentation & Engineering Change Impact Analysis System</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Automated PDF Parsing, Parameter Tolerance Diffing, Part Interchangeability, Subsystem Ripple Effects & Fleet MSN Mapping</div>', unsafe_allow_html=True)

# Executive KPI Ribbon
metrics = db.get_summary_metrics()
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.metric(label="📄 Total Docs Processed", value=metrics["total_docs_processed"])
with c2:
    st.metric(label="🔄 Revisions Detected", value=metrics["revisions_detected"])
with c3:
    st.metric(label="🔍 Changes Identified", value=metrics["changes_identified"])
with c4:
    st.metric(label="🛠️ Components Affected", value=metrics["components_affected"])
with c5:
    st.metric(label="⏳ Pending Reviews", value=metrics["pending_reviews"], delta=f"{metrics['critical_changes']} Critical", delta_color="inverse")

st.markdown("---")

# Navigation Tabs
tab_compare, tab_semantic, tab_interchange, tab_fleet, tab_graph, tab_regulatory, tab_export = st.tabs([
    "📑 Document Comparison & Visual PDF",
    "🧠 Engineering Rationale & Review",
    "🔄 Part Interchangeability",
    "✈️ Fleet MSN Effectivity",
    "🕸️ Subsystem Ripple Graph",
    "📡 Regulatory Feeds (FAA/EASA)",
    "📥 Configuration & Excel Export"
])

sample_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "sample_pdfs")

# -------------------------------------------------------------
# TAB 1: Document Comparison & Visual PDF Annotator
# -------------------------------------------------------------
with tab_compare:
    st.subheader("1. Ingest & Compare Technical Documentation")
    
    with st.expander("📂 Quick-Load Sample Aerospace Technical Publications", expanded=True):
        col_load1, col_load2, col_info = st.columns([2, 2, 3])
        load_hyd = col_load1.button("Load ATA 29 Hydraulic Pump (Rev 01 vs Rev 02)", use_container_width=True)
        load_lg = col_load2.button("Load ATA 32 Landing Gear Actuator (Rev 01 vs Rev 02)", use_container_width=True)
        col_info.info("Select a pre-verified Airbus AMM/SB pair or upload custom PDFs below.")

    col_up1, col_up2 = st.columns(2)
    with col_up1:
        st.markdown("**Baseline Technical Document (Previous Version)**")
        file_base = st.file_uploader("Upload Previous PDF (e.g. Rev 01)", type=["pdf"], key="file_base")
    with col_up2:
        st.markdown("**Updated Technical Document (New Version)**")
        file_rev = st.file_uploader("Upload New PDF (e.g. Rev 02)", type=["pdf"], key="file_rev")

    # Determine files to process
    base_source, rev_source = None, None
    hyd_rev1_path = os.path.join(sample_dir, "AMM_29_10_00_Rev01.pdf")
    hyd_rev2_path = os.path.join(sample_dir, "AMM_29_10_00_Rev02.pdf")
    lg_rev1_path = os.path.join(sample_dir, "SB_A320_32_1420_Rev01.pdf")
    lg_rev2_path = os.path.join(sample_dir, "SB_A320_32_1420_Rev02.pdf")

    if load_hyd and os.path.exists(hyd_rev1_path) and os.path.exists(hyd_rev2_path):
        base_source = hyd_rev1_path
        rev_source = hyd_rev2_path
        st.session_state["active_dataset"] = "Hydraulic Pump"
    elif load_lg and os.path.exists(lg_rev1_path) and os.path.exists(lg_rev2_path):
        base_source = lg_rev1_path
        rev_source = lg_rev2_path
        st.session_state["active_dataset"] = "Landing Gear"
    elif file_base and file_rev:
        base_source = file_base.read()
        rev_source = file_rev.read()
        st.session_state["active_dataset"] = "Custom Upload"
    elif "last_base" in st.session_state and "last_rev" in st.session_state:
        base_source = st.session_state["last_base"]
        rev_source = st.session_state["last_rev"]

    if base_source and rev_source:
        st.session_state["last_base"] = base_source
        st.session_state["last_rev"] = rev_source

        # Extract data with PyMuPDF
        with st.spinner("Extracting PDF structures and engineering tolerances..."):
            ext_base = AviationPDFExtractor(base_source)
            ext_rev = AviationPDFExtractor(rev_source)

            data_base = ext_base.extract_all()
            data_rev = ext_rev.extract_all()

            # Compare Documents
            comparator = DocumentComparator(data_base, data_rev)
            comp_results = comparator.compare_all()

            # Analyze Impact
            analyzer = EngineeringImpactAnalyzer(comp_results)
            impact_items = analyzer.generate_impact_report()
            
            # Evaluate Part Interchangeability
            prev_pn = comp_results["parameter_diffs"][0]["previous_version"] if comp_results["parameter_diffs"] else "P/N Unknown"
            new_pn = comp_results["parameter_diffs"][0]["updated_version"] if comp_results["parameter_diffs"] else "P/N Unknown"
            for p in comp_results["parameter_diffs"]:
                if "Part Number" in p["parameter"] or "P/N" in p["parameter"]:
                    prev_pn = p["previous_version"]
                    new_pn = p["updated_version"]
                    break

            interchange_data = FleetEffectivityManager.classify_part_interchangeability(prev_pn, new_pn, comp_results["parameter_diffs"])
            
            # Generate Semantic Summaries
            semantic_summary = SemanticChangeSummarizer.generate_executive_rationale(
                comp_results["metadata_diff"],
                comp_results["parameter_diffs"],
                comp_results["text_diff"],
                interchange_data
            )

            # Generate Visual Annotated PDF
            export_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "export")
            annotated_rev_path = os.path.join(export_dir, f"Annotated_{data_rev['doc_ref']}_{data_rev['revision']}.pdf")
            VisualPDFAnnotator.annotate_document_differences(rev_source, comp_results["parameter_diffs"], annotated_rev_path, is_revised_doc=True)

            # Save in session state
            st.session_state["current_impact_items"] = impact_items
            st.session_state["current_comp_results"] = comp_results
            st.session_state["interchange_data"] = interchange_data
            st.session_state["semantic_summary"] = semantic_summary
            st.session_state["annotated_pdf_path"] = annotated_rev_path
            st.session_state["data_rev"] = data_rev
            st.session_state["data_base"] = data_base

        # Log to Database if not already logged
        if st.session_state.get("logged_doc") != data_rev["doc_ref"] + data_rev["revision"]:
            db.log_document_revision(data_rev["doc_ref"], data_rev["revision"], data_rev["pub_date"], data_rev["component_id"])
            db.log_engineering_changes(impact_items)
            db.update_component_status(data_rev["component_id"], data_rev["revision"], "Under Review")
            st.session_state["logged_doc"] = data_rev["doc_ref"] + data_rev["revision"]

        st.success(f"Successfully processed **{data_base['doc_ref']} ({data_base['revision']})** vs **{data_rev['doc_ref']} ({data_rev['revision']})**")

        # Metadata Comparison Cards
        st.markdown("#### Document Metadata & Revision Transition")
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        m_col1.metric("Component ID", data_rev["component_id"], data_rev["component_name"])
        m_col2.metric("ATA Chapter", data_rev["ata_chapter"])
        m_col3.metric("Revision Transition", f"{data_base['revision']} ➔ {data_rev['revision']}")
        m_col4.metric("Document Date Shift", f"{data_base['pub_date']} ➔ {data_rev['pub_date']}")

        # Visual PDF Highlight Banner & Download
        st.markdown("#### 🖍️ Visual PDF Inspection (PyMuPDF Annotation Engine)")
        st.info("PyMuPDF has directly annotated the revised PDF with color-coded highlight boxes indicating parameter shifts and new mandatory instructions.")
        
        with open(annotated_rev_path, "rb") as f_pdf:
            pdf_bytes = f_pdf.read()

        col_dl_pdf, col_stat = st.columns([2, 5])
        with col_dl_pdf:
            st.download_button(
                label="📥 Download Annotated PDF with Highlight Boxes",
                data=pdf_bytes,
                file_name=os.path.basename(annotated_rev_path),
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )
        col_stat.caption(f"Annotated file saved to: `{annotated_rev_path}`")

        # Parameter Comparison Table
        st.markdown("#### Parameter Specification Shift Matrix")
        diff_df = pd.DataFrame(comp_results["parameter_diffs"])
        if not diff_df.empty:
            display_diff_df = diff_df[["parameter", "previous_version", "updated_version", "delta", "change_type"]]
            display_diff_df.columns = ["Parameter", "Previous Version", "Updated Version", "Shift / Delta", "Change Classification"]
            st.dataframe(display_diff_df, use_container_width=True, hide_index=True)
        else:
            st.info("No parameters detected in tables.")

        # Text diff viewer
        with st.expander("🔍 View Textual & Accomplishment Instruction Diffs"):
            st.markdown(comp_results["text_diff"]["html_diff"], unsafe_allow_html=True)
    else:
        st.info("Please select a sample dataset above or upload two technical PDF documents to start comparison.")

# -------------------------------------------------------------
# TAB 2: AI Engineering Rationale & Sign-Off Portal
# -------------------------------------------------------------
with tab_semantic:
    st.subheader("2. AI Engineering Rationale & Sign-Off Portal")
    
    st.warning("⚠️ **MANDATORY AEROSPACE SAFETY NOTICE**: This software assists in decision support and does not independently certify aircraft airworthiness. Certified aviation engineers must complete sign-off.")

    summary = st.session_state.get("semantic_summary", None)
    if summary:
        # Executive Narrative Box
        with st.container():
            st.markdown("""
            <div class="card-box">
                <h4 style="color:#002B49; margin-top:0;">📋 Executive Engineering Brief</h4>
            """, unsafe_allow_html=True)
            for pt in summary["executive_brief"]:
                st.markdown(f"• {pt}", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # Shop Floor Directives Box
        with st.container():
            st.markdown("""
            <div class="card-box" style="border-left: 4px solid #0284C7;">
                <h4 style="color:#0284C7; margin-top:0;">🛠️ Line Maintenance & Shop-Floor Directives</h4>
            """, unsafe_allow_html=True)
            for act in summary["shop_floor_actions"]:
                st.markdown(f"• **ACTION**: {act}", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # Airworthiness Compliance Statement
        with st.container():
            st.markdown(f"""
            <div class="card-box" style="border-left: 4px solid #DC2626;">
                <h4 style="color:#DC2626; margin-top:0;">⚖️ Regulatory Airworthiness Assessment: {summary['regulatory_level']}</h4>
                <p style="color:#334155; margin-bottom:0;">{summary['regulatory_compliance_notes']}</p>
            </div>
            """, unsafe_allow_html=True)

        # Sign-off section
        st.markdown("---")
        st.markdown("#### ✍️ Engineer Review & Sign-Off Portal")
        all_db_changes = db.get_engineering_changes()
        if not all_db_changes.empty:
            change_options = {f"ID #{row['change_id']}: [{row['component_id']}] {row['parameter_name']} ({row['previous_spec']} -> {row['updated_spec']})": row['change_id'] 
                              for _, row in all_db_changes.iterrows()}
            
            selected_label = st.selectbox("Select Change Item to Sign-Off:", options=list(change_options.keys()))
            selected_change_id = change_options[selected_label]

            col_form1, col_form2 = st.columns(2)
            with col_form1:
                engineer_name = st.text_input("Engineer Name / License ID:", placeholder="e.g. John Doe (FAA A&P 429103)")
                signoff_status = st.selectbox("Review Decision:", ["Approved", "Under Review", "Requires Further Engineering Investigation", "Rejected"])
            with col_form2:
                review_comments = st.text_area("Technical Justification / Maintenance Actions:", placeholder="e.g. Concur with 3200 PSI shift. Updated hydraulic ground cart cal specs in AMM Task 29-10-00.")

            if st.button("Submit Engineering Review Sign-Off", type="primary"):
                if engineer_name.strip():
                    db.update_review_signoff(selected_change_id, signoff_status, engineer_name, review_comments)
                    st.success(f"Review decision '{signoff_status}' recorded for Change #{selected_change_id} by {engineer_name}.")
                    st.rerun()
                else:
                    st.error("Please enter your Engineer Name or License ID.")
    else:
        st.info("Ingest documents in Tab 1 to generate engineering rationales.")

# -------------------------------------------------------------
# TAB 3: Part Interchangeability Engine
# -------------------------------------------------------------
with tab_interchange:
    st.subheader("3. Aerospace Part Interchangeability Analysis")
    st.markdown("Evaluates OEM interchangeability classification rules (Class 1 Two-Way vs Class 2 One-Way vs Class 3 Non-Interchangeable).")

    ic_data = st.session_state.get("interchange_data", None)
    if ic_data:
        col_ic1, col_ic2 = st.columns([1, 1])
        with col_ic1:
            st.metric("Baseline Part Number", ic_data["previous_part_number"])
        with col_ic2:
            st.metric("Updated Superseding Part Number", ic_data["updated_part_number"], delta=ic_data["interchangeability_class"])

        is_one_way = "Class 2" in ic_data["interchangeability_class"]
        banner_color = "#FEF2F2" if is_one_way else "#F0FDF4"
        border_color = "#EF4444" if is_one_way else "#22C55E"
        text_color = "#991B1B" if is_one_way else "#166534"

        st.markdown(f"""
        <div style="background:{banner_color}; border-left:5px solid {border_color}; padding:14px; border-radius:6px; margin: 15px 0;">
            <h4 style="color:{text_color}; margin-top:0;">{ic_data['interchangeability_class']}</h4>
            <p><b>Engineering Definition:</b> {ic_data['engineering_definition']}</p>
            <p><b>Supply Chain & Warehouse Action:</b> {ic_data['supply_chain_action']}</p>
            <p><b>Airworthiness Risk:</b> {ic_data['airworthiness_risk_level']}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Ingest documents in Tab 1 to evaluate part number supersessions.")

# -------------------------------------------------------------
# TAB 4: Fleet MSN Effectivity Mapping
# -------------------------------------------------------------
with tab_fleet:
    st.subheader("4. Aircraft Fleet MSN & Tail Number Effectivity")
    st.markdown("Determines which aircraft in your fleet are **affected** by this revision based on Manufacturer Serial Numbers (MSN) and Engine types.")

    applicability_str = st.session_state.get("data_rev", {}).get("full_text", "A320-271N / A321-271NX MSN 0200 through 0500 equipped with LEAP-1A")
    
    fleet_impact_df = FleetEffectivityManager.evaluate_fleet_impact(applicability_str)
    
    affected_count = len(fleet_impact_df[fleet_impact_df["Fleet Impact Status"].str.contains("AFFECTED")])
    total_fleet = len(fleet_impact_df)

    f_col1, f_col2, f_col3 = st.columns(3)
    f_col1.metric("Total Fleet Size", total_fleet)
    f_col2.metric("Aircraft Tails Affected", affected_count, delta=f"{total_fleet - affected_count} Exempt", delta_color="inverse")
    f_col3.metric("Fleet Readiness Status", "Action Plan Required" if affected_count > 0 else "Compliant")

    st.markdown("#### Aircraft Tail Number Impact Roster")
    st.dataframe(fleet_impact_df, use_container_width=True, hide_index=True)

# -------------------------------------------------------------
# TAB 5: Subsystem Ripple Graph
# -------------------------------------------------------------
with tab_graph:
    st.subheader("5. Multi-System Ripple Effect (Knowledge Graph)")
    st.markdown("Visualizes upstream hydraulic/power sources and all connected downstream consumer subsystems.")

    kg = AircraftSystemKnowledgeGraph()
    ripple_items = kg.trace_ripple_effect("HYD-001")

    col_g_img, col_g_tbl = st.columns([3, 2])
    with col_g_img:
        graph_img_bytes = kg.render_graph_image()
        st.image(graph_img_bytes, caption="Subsystem Dependency Topology", use_container_width=True)

    with col_g_tbl:
        st.markdown("#### Downstream Circuit Impact Analysis")
        ripple_df = pd.DataFrame(ripple_items)
        if not ripple_df.empty:
            st.dataframe(ripple_df, use_container_width=True, hide_index=True)

# -------------------------------------------------------------
# TAB 6: Regulatory Feeds (FAA & EASA)
# -------------------------------------------------------------
with tab_regulatory:
    st.subheader("6. Live Airworthiness Directives Feed (FAA / EASA)")
    st.markdown("Cross-references regulatory safety bulletins against monitored aircraft components.")

    ad_df = RegulatoryFeedManager.get_latest_directives()
    st.dataframe(ad_df, use_container_width=True, hide_index=True)

# -------------------------------------------------------------
# TAB 7: Configuration Database & Excel Export
# -------------------------------------------------------------
with tab_export:
    st.subheader("7. Configuration Database & Excel Reporting")
    st.markdown("Comprehensive export of engineering changes, fleet statuses, and audit records.")

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

    st.markdown("#### Engineering Changes Audit Log")
    st.dataframe(changes_df, use_container_width=True, hide_index=True)
