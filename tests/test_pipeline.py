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
from src.rag_engine import TechnicalManualRAGEngine
from src.ocr_engine import LegacyManualOCREngine
from src.erp_integrator import AirlineERPIntegrator

def run_all_tests():
    sample_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "sample_pdfs")
    doc1 = os.path.join(sample_dir, "AMM_29_10_00_Rev01.pdf")
    doc2 = os.path.join(sample_dir, "AMM_29_10_00_Rev02.pdf")
    
    assert os.path.exists(doc1), f"Missing {doc1}"
    assert os.path.exists(doc2), f"Missing {doc2}"
    print("Sample PDFs verified.")

    print("\n=== STEP 1: TESTING PYMUPDF EXTRACTION ===")
    ext1 = AviationPDFExtractor(doc1)
    data1 = ext1.extract_all()
    ext2 = AviationPDFExtractor(doc2)
    data2 = ext2.extract_all()

    assert data1['revision'] == "Rev 01", f"Expected Rev 01, got {data1['revision']}"
    assert data2['revision'] == "Rev 02", f"Expected Rev 02, got {data2['revision']}"
    print(f"Extraction verified: {data1['doc_ref']} vs {data2['doc_ref']}")

    print("\n=== STEP 2: TESTING DOCUMENT COMPARISON & PARAMETER DIFF ===")
    comparator = DocumentComparator(data1, data2)
    comp_results = comparator.compare_all()
    param_diffs = comp_results["parameter_diffs"]
    pressure_diff = next((p for p in param_diffs if "Pressure" in p["parameter"]), None)
    assert pressure_diff is not None, "Pressure parameter diff not found!"
    print(f"Pressure diff verified: {pressure_diff['previous_version']} -> {pressure_diff['updated_version']} (Delta: {pressure_diff['delta']})")

    print("\n=== STEP 3: TESTING TECHNICAL MANUAL RAG ENGINE ===")
    rag = TechnicalManualRAGEngine()
    rag.index_document(data2["doc_ref"], data2["revision"], data2["full_text"], data2.get("specifications", {}))
    rag_res = rag.query("What is the rated operating delivery pressure?")
    assert len(rag_res["citations"]) > 0, "RAG failed to retrieve relevant chunks!"
    assert rag_res["confidence"] > 0.5, "RAG confidence too low!"
    print(f"RAG query successful (Confidence: {rag_res['confidence']}): {rag_res['answer'][:90]}...")

    print("\n=== STEP 4: TESTING LEGACY OCR PIPELINE ===")
    ocr_res = LegacyManualOCREngine.extract_scanned_pdf(doc1)
    assert ocr_res["is_scanned_ocr"], "OCR flag not set!"
    assert len(ocr_res["specifications"]) > 0, "No OCR specifications extracted!"
    print(f"OCR Pipeline verified: Title={ocr_res['title']}, Specs={len(ocr_res['specifications'])}")

    print("\n=== STEP 5: TESTING AIRLINE ERP / MRO SYNCHRONIZATION ===")
    ic_res = FleetEffectivityManager.classify_part_interchangeability("P/N 9400-A", "P/N 9400-B", param_diffs)
    sample_change = {"component_id": "HYD-001", "parameter_name": "Operating Pressure", "previous_spec": "3000 PSI", "updated_spec": "3200 PSI"}
    eco_payload = AirlineERPIntegrator.generate_eco_payload(sample_change, ic_res, "Capt A. Shakya", "Swiss-AS AMOS")
    assert "eco_header" in eco_payload, "Missing eco_header in payload!"
    assert "cryptographic_checksum" in eco_payload["eco_header"], "Missing checksum in ECO header!"
    disp_res = AirlineERPIntegrator.dispatch_webhook(eco_payload)
    assert disp_res["status_code"] == 200, "Simulated ERP webhook failed!"
    print(f"ERP Integration verified: {disp_res['eco_number']} synced to {disp_res['target_erp']} (TX: {disp_res['transaction_id']})")

    print("\n=== STEP 6: TESTING DATABASE OUTBOX & EXCEL EXPORT ===")
    db = DatabaseManager(":memory:")
    db.log_erp_dispatch(disp_res["eco_number"], disp_res["target_erp"], disp_res["status"], disp_res["transaction_id"], str(eco_payload))
    outbox_df = db.get_erp_dispatches()
    assert not outbox_df.empty, "ERP outbox table empty!"
    print(f"Outbox audit log verified with {len(outbox_df)} records.")

    changes_df = db.get_engineering_changes("HYD-001")
    comps_df = db.get_all_components()
    metrics = db.get_summary_metrics()
    excel_bytes = ExcelEngineeringExporter.generate_excel_report(changes_df, comps_df, metrics)
    assert len(excel_bytes) > 0, "Excel output is empty!"
    print(f"Excel report verified ({len(excel_bytes)} bytes).")

    print("\nALL EXPANDED ROADMAP MODULES PASSED SUCCESSFULLY! [SUCCESS]")

if __name__ == "__main__":
    run_all_tests()
