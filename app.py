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

# Page Configuration
st.set_page_config(
    page_title="AeroChange | Aircraft Tech Doc Impact Analysis",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Aviation CSS
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
    .metric-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 12px 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .badge-high {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 12px;
    }
    .badge-med {
        background-color: #FEF3C7;
        color: #92400E;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 12px;
    }
    .badge-low {
        background-color: #E2E8F0;
        color: #334155;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 12px;
    }
    .badge-approved {
        background-color: #DCFCE7;
        color: #166534;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 12px;
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
    st.markdown('<div class="sub-title">Automated PDF Extraction, Parameter Tolerance Shift Analysis, and Downstream Maintenance Impact Tracking</div>', unsafe_allow_html=True)

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
tab_compare, tab_impact, tab_config, tab_export = st.tabs([
    "📑 Document Ingestion & Comparison",
    "⚠️ Engineering Change Impact Analysis",
    "🗄️ Component Configuration Tracking",
    "📥 Reports & Excel Export"
])

# Paths for sample data
sample_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "sample_pdfs")

# -------------------------------------------------------------
# TAB 1: Document Ingestion & Comparison
# -------------------------------------------------------------
with tab_compare:
    st.subheader("1. Ingest & Compare Technical Documentation")
    
    # Quick loader for sample documents
    with st.expander("📂 Quick-Load Sample Aerospace Technical Publications", expanded=True):
        col_load1, col_load2, col_info = st.columns([2, 2, 3])
        load_hyd = col_load1.button("Load ATA 29 Hydraulic Pump (Rev 01 vs Rev 02)", use_container_width=True)
        load_lg = col_load2.button("Load ATA 32 Landing Gear Actuator (Rev 01 vs Rev 02)", use_container_width=True)
        col_info.info("Quick-load verified synthetic Airbus AMM / Service Bulletins or upload your own PDFs below.")

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
            st.session_state["current_impact_items"] = impact_items
            st.session_state["current_comp_results"] = comp_results

        # Log to Database if not already logged
        if st.session_state.get("logged_doc") != data_rev["doc_ref"] + data_rev["revision"]:
            db.log_document_revision(data_rev["doc_ref"], data_rev["revision"], data_rev["pub_date"], data_rev["component_id"])
            db.log_engineering_changes(impact_items)
            db.update_component_status(data_rev["component_id"], data_rev["revision"], "Under Review")
            st.session_state["logged_doc"] = data_rev["doc_ref"] + data_rev["revision"]

        st.success(f"Successfully processed and compared **{data_base['doc_ref']} ({data_base['revision']})** vs **{data_rev['doc_ref']} ({data_rev['revision']})**")

        # Feature 1 & 2 Display: Metadata Comparison
        st.markdown("#### Document Metadata & Revision Shift")
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        m_col1.metric("Component ID", data_rev["component_id"], data_rev["component_name"])
        m_col2.metric("ATA Chapter", data_rev["ata_chapter"])
        m_col3.metric("Revision Transition", f"{data_base['revision']} ➔ {data_rev['revision']}")
        m_col4.metric("Document Date Shift", f"{data_base['pub_date']} ➔ {data_rev['pub_date']}")

        # Feature 2 Display: Parameter Comparison Table
        st.markdown("#### Parameter Specification Shift Matrix")
        diff_df = pd.DataFrame(comp_results["parameter_diffs"])
        
        # Color formatting helper
        def style_diff(row):
            if row["change_type"] in ["SPEC_MODIFIED", "PART_SUPERSEDED"]:
                return ["background-color: #FEF3C7"] * len(row)
            elif row["change_type"] == "ADDED":
                return ["background-color: #DCFCE7"] * len(row)
            elif row["change_type"] == "REMOVED":
                return ["background-color: #FEE2E2"] * len(row)
            return [""] * len(row)

        if not diff_df.empty:
            display_diff_df = diff_df[["parameter", "previous_version", "updated_version", "delta", "change_type"]]
            display_diff_df.columns = ["Parameter", "Previous Version", "Updated Version", "Shift / Delta", "Change Classification"]
            st.dataframe(display_diff_df, use_container_width=True, hide_index=True)
        else:
            st.info("No numerical parameters detected in tables.")

        # Text & Instructional Diff
        with st.expander("🔍 View Textual & Accomplishment Instruction Diffs"):
            st.markdown(comp_results["text_diff"]["html_diff"], unsafe_allow_html=True)
    else:
        st.info("Please select a sample dataset above or upload two technical PDF documents to start comparison.")

# -------------------------------------------------------------
# TAB 2: Engineering Change Impact Analysis & Sign-Off
# -------------------------------------------------------------
with tab_impact:
    st.subheader("2. Engineering Change Impact & Review Portal")
    
    # Human-in-the-Loop Safety Callout
    st.warning("⚠️ **MANDATORY AEROSPACE SAFETY NOTICE**: This software flags changes for engineering review. Certified aviation engineers must review and sign off before updating live aircraft maintenance records or issuing Engineering Orders.")

    impact_items = st.session_state.get("current_impact_items", [])
    if impact_items:
        impact_df = pd.DataFrame(impact_items)
        
        st.markdown("#### Structured Impact Report")
        for idx, row in impact_df.iterrows():
            badge_class = "badge-high" if row["severity"] in ["HIGH", "CRITICAL"] else ("badge-med" if row["severity"] == "MEDIUM" else "badge-low")
            
            with st.container():
                st.markdown(f"""
                <div style="border: 1px solid #CBD5E1; border-radius: 8px; padding: 12px; margin-bottom: 12px; background: white;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-size:16px; font-weight:700; color:#002B49;">{row['affected_parameter']}</span>
                        <span class="{badge_class}">{row['severity']} SEVERITY</span>
                    </div>
                    <p style="margin: 6px 0; color:#334155;"><b>Change Description:</b> {row['change_description']}</p>
                    <p style="margin: 4px 0; font-size:13px; color:#475569;"><b>Previous Spec:</b> <code>{row['previous_specification']}</code> &nbsp;|&nbsp; <b>Updated Spec:</b> <code>{row['updated_specification']}</code></p>
                    <p style="margin: 4px 0; font-size:13px; color:#1E293B;"><b>Engineering Rationale:</b> {row['engineering_rationale']}</p>
                    <p style="margin: 4px 0; font-size:13px; color:#0369A1;"><b>Potential Documentation Impact:</b> {row['potential_doc_impact']}</p>
                </div>
                """, unsafe_allow_html=True)

        # Engineering Review Sign-Off Form
        st.markdown("---")
        st.markdown("#### ✍️ Engineer Review & Sign-Off")
        
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

            if st.button("Submit Engineering Review", type="primary"):
                if engineer_name.strip():
                    db.update_review_signoff(selected_change_id, signoff_status, engineer_name, review_comments)
                    st.success(f"Review decision '{signoff_status}' recorded for Change #{selected_change_id} by {engineer_name}.")
                    st.rerun()
                else:
                    st.error("Please enter your Engineer Name or License ID to establish an audit trail.")
    else:
        st.info("No active change impact analysis loaded. Ingest two documents in Tab 1 to generate impact items.")

# -------------------------------------------------------------
# TAB 3: Component Configuration Tracking
# -------------------------------------------------------------
with tab_config:
    st.subheader("3. Component Fleet Configuration Tracking")
    st.markdown("Systematic tracking of component baselines, active revisions, and regulatory compliance status.")

    comps_df = db.get_all_components()
    
    col_filter1, col_filter2 = st.columns(2)
    with col_filter1:
        status_filter = st.multiselect("Filter by Configuration Status:", 
                                       options=comps_df["status"].unique().tolist(), 
                                       default=comps_df["status"].unique().tolist())
    with col_filter2:
        ata_filter = st.multiselect("Filter by ATA Chapter:", 
                                    options=comps_df["ata_chapter"].unique().tolist(), 
                                    default=comps_df["ata_chapter"].unique().tolist())

    filtered_comps = comps_df[
        (comps_df["status"].isin(status_filter)) & 
        (comps_df["ata_chapter"].isin(ata_filter))
    ]

    st.dataframe(filtered_comps, use_container_width=True, hide_index=True)

    with st.expander("➕ Register or Update Fleet Component Configuration"):
        c_add1, c_add2, c_add3, c_add4 = st.columns(4)
        new_comp_id = c_add1.text_input("Component ID", "APU-006")
        new_rev = c_add2.text_input("Document Revision", "Rev 01")
        new_status = c_add3.selectbox("Status", ["Updated", "Under Review", "Compliant", "Superseded"])
        if c_add4.button("Save Component", use_container_width=True):
            db.update_component_status(new_comp_id, new_rev, new_status)
            st.success(f"Component {new_comp_id} saved successfully!")
            st.rerun()

# -------------------------------------------------------------
# TAB 4: Reports & Excel Export
# -------------------------------------------------------------
with tab_export:
    st.subheader("4. Engineering Audit Reports & Excel Export")
    st.markdown("Export comprehensive engineering change logs and configuration status with sign-offs.")

    changes_df = db.get_engineering_changes()
    comps_df = db.get_all_components()

    col_btn1, col_btn2 = st.columns([2, 5])
    with col_btn1:
        excel_bytes = ExcelEngineeringExporter.generate_excel_report(changes_df, comps_df, metrics)
        st.download_button(
            label="📥 Download Engineering Change Report (.xlsx)",
            data=excel_bytes,
            file_name="Aircraft_Doc_Change_Analysis_Report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
            use_container_width=True
        )

    st.markdown("#### Live Engineering Change Audit Log")
    if not changes_df.empty:
        st.dataframe(changes_df, use_container_width=True, hide_index=True)
    else:
        st.info("No engineering changes logged yet.")
