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
    
    # Check pressure shift: 3000 PSI -> 3200 PSI (+200 PSI)
    pressure_diff = next((p for p in param_diffs if "Pressure" in p["parameter"]), None)
    assert pressure_diff is not None, "Pressure parameter diff not found!"
    print(f"Pressure diff verified: {pressure_diff['previous_version']} -> {pressure_diff['updated_version']} (Delta: {pressure_diff['delta']})")

    print("\n=== STEP 4: TESTING ENGINEERING IMPACT ANALYSIS ===")
    analyzer = EngineeringImpactAnalyzer(comp_results)
    impact_items = analyzer.generate_impact_report()
    print(f"Generated {len(impact_items)} engineering impact items.")
    assert len(impact_items) > 0, "No impact items generated!"

    high_sev_items = [i for i in impact_items if i['severity'] in ['HIGH', 'CRITICAL']]
    print(f"High severity safety items flagged: {len(high_sev_items)}")
    assert len(high_sev_items) > 0, "High severity items should be flagged!"

    print("\n=== STEP 5: TESTING DATABASE OPERATIONS ===")
    db = DatabaseManager()
    db.log_document_revision(data2["doc_ref"], data2["revision"], data2["pub_date"], data2["component_id"])
    db.log_engineering_changes(impact_items)
    db.update_component_status("HYD-001", "Rev 02", "Under Review")
    
    changes_df = db.get_engineering_changes("HYD-001")
    assert not changes_df.empty, "Failed to retrieve engineering changes from database!"
    print(f"Retrieved {len(changes_df)} database change records for HYD-001.")

    metrics = db.get_summary_metrics()
    print(f"Metrics: {metrics}")

    print("\n=== STEP 6: TESTING EXCEL EXPORTER ===")
    comps_df = db.get_all_components()
    excel_bytes = ExcelEngineeringExporter.generate_excel_report(changes_df, comps_df, metrics)
    assert len(excel_bytes) > 0, "Excel output is empty!"
    print(f"Excel report generated successfully ({len(excel_bytes)} bytes).")

    print("\nALL AUTOMATED TESTS PASSED SUCCESSFULLY! [SUCCESS]")

if __name__ == "__main__":
    run_all_tests()
