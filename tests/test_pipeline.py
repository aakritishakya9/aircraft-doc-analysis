import os
import sys

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.generate_sample_pdfs import generate_all
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

def run_all_tests():
    print("=== STEP 1: GENERATING TEST AVIATION PDFS ===")
    generate_all()
    sample_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "sample_pdfs")
    doc1 = os.path.join(sample_dir, "AMM_29_10_00_Rev01.pdf")
    doc2 = os.path.join(sample_dir, "AMM_29_10_00_Rev02.pdf")
    
    assert os.path.exists(doc1), f"Missing {doc1}"
    assert os.path.exists(doc2), f"Missing {doc2}"
    print("Sample PDFs successfully created.")

    print("\n=== STEP 2: TESTING PYMUPDF EXTRACTION ===")
    ext1 = AviationPDFExtractor(doc1)
    data1 = ext1.extract_all()
    print(f"Extracted Doc 1: Ref={data1['doc_ref']}, Rev={data1['revision']}, Date={data1['pub_date']}, Specs={len(data1['specifications'])}")

    ext2 = AviationPDFExtractor(doc2)
    data2 = ext2.extract_all()
    print(f"Extracted Doc 2: Ref={data2['doc_ref']}, Rev={data2['revision']}, Date={data2['pub_date']}, Specs={len(data2['specifications'])}")

    assert data1['revision'] == "Rev 01", f"Expected Rev 01, got {data1['revision']}"
    assert data2['revision'] == "Rev 02", f"Expected Rev 02, got {data2['revision']}"

    print("\n=== STEP 3: TESTING DOCUMENT COMPARISON & PARAMETER DIFF ===")
    comparator = DocumentComparator(data1, data2)
    comp_results = comparator.compare_all()
    param_diffs = comp_results["parameter_diffs"]
    print(f"Total parameter diffs evaluated: {len(param_diffs)}")
    
    pressure_diff = next((p for p in param_diffs if "Pressure" in p["parameter"]), None)
    assert pressure_diff is not None, "Pressure parameter diff not found!"
    print(f"Pressure diff verified: {pressure_diff['previous_version']} -> {pressure_diff['updated_version']} (Delta: {pressure_diff['delta']})")

    print("\n=== STEP 4: TESTING VISUAL PDF ANNOTATOR ===")
    annot_out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "export", "test_annotated.pdf")
    VisualPDFAnnotator.annotate_document_differences(doc2, param_diffs, annot_out, is_revised_doc=True)
    assert os.path.exists(annot_out), "Annotated PDF not created!"
    print("Visual PDF Annotator created highlighted PDF successfully.")

    print("\n=== STEP 5: TESTING PART INTERCHANGEABILITY & FLEET EFFECTIVITY ===")
    ic_res = FleetEffectivityManager.classify_part_interchangeability("P/N 9400-A", "P/N 9400-B", param_diffs)
    print(f"Interchangeability: {ic_res['interchangeability_class']}")
    assert "Class 2" in ic_res["interchangeability_class"], "Expected Class 2 (One-Way) due to pressure shift!"

    fleet_df = FleetEffectivityManager.evaluate_fleet_impact("Airbus A320-271N MSN 0200 through 0500 equipped with LEAP-1A")
    assert not fleet_df.empty, "Fleet evaluation failed!"
    print(f"Evaluated {len(fleet_df)} fleet tails for effectivity.")

    print("\n=== STEP 6: TESTING SUBSYSTEM KNOWLEDGE GRAPH ===")
    kg = AircraftSystemKnowledgeGraph()
    ripples = kg.trace_ripple_effect("HYD-001")
    assert len(ripples) > 0, "No downstream consumers found in knowledge graph!"
    print(f"Knowledge graph found {len(ripples)} downstream subsystems connected to HYD-001.")
    img_bytes = kg.render_graph_image()
    assert len(img_bytes) > 0, "Failed to render graph image!"
    print("Subsystem knowledge graph image rendered successfully.")

    print("\n=== STEP 7: TESTING SEMANTIC RATIONALE & REGULATORY FEED ===")
    summary = SemanticChangeSummarizer.generate_executive_rationale(
        comp_results["metadata_diff"], param_diffs, comp_results["text_diff"], ic_res
    )
    assert len(summary["executive_brief"]) > 0, "Executive brief empty!"
    print("Semantic engineering rationale generated successfully.")

    ad_df = RegulatoryFeedManager.get_latest_directives()
    assert not ad_df.empty, "Regulatory feed empty!"
    print(f"Regulatory feed verified with {len(ad_df)} Airworthiness Directives.")

    print("\n=== STEP 8: TESTING DATABASE & EXCEL EXPORTER ===")
    db = DatabaseManager()
    impact_items = EngineeringImpactAnalyzer(comp_results).generate_impact_report()
    db.log_engineering_changes(impact_items)
    changes_df = db.get_engineering_changes("HYD-001")
    comps_df = db.get_all_components()
    metrics = db.get_summary_metrics()
    excel_bytes = ExcelEngineeringExporter.generate_excel_report(changes_df, comps_df, metrics)
    assert len(excel_bytes) > 0, "Excel output is empty!"
    print(f"Excel report generated successfully ({len(excel_bytes)} bytes).")

    print("\nALL ENTERPRISE FEATURES AND PIPELINE TESTS PASSED! [SUCCESS]")

if __name__ == "__main__":
    run_all_tests()
