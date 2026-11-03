import pymupdf as fitz
import re
from typing import Dict, Any, Union
import io

class AviationPDFExtractor:
    """
    Extracts aerospace technical document metadata, tables, and prose 
    using PyMuPDF (fitz) with deterministic regex and layout parsing.
    """

    def __init__(self, pdf_source: Union[str, bytes, io.BytesIO]):
        """
        pdf_source: file path (str) or binary stream (bytes / io.BytesIO).
        """
        if isinstance(pdf_source, str):
            self.doc = fitz.open(pdf_source)
            self.source_name = pdf_source
        elif isinstance(pdf_source, (bytes, io.BytesIO)):
            stream = pdf_source if isinstance(pdf_source, io.BytesIO) else io.BytesIO(pdf_source)
            self.doc = fitz.open(stream=stream.getvalue(), filetype="pdf")
            self.source_name = "Uploaded_Document.pdf"
        else:
            raise ValueError("Unsupported PDF source type. Provide a file path or bytes.")

    def extract_all(self) -> Dict[str, Any]:
        """
        Extracts document title, reference, revision, date, ATA chapter, 
        component identifiers, specifications table, and raw text.
        """
        pages_text = []
        full_text = ""
        
        for page_idx in range(len(self.doc)):
            page = self.doc[page_idx]
            text = page.get_text()
            pages_text.append(text)
            full_text += f"\n--- PAGE {page_idx + 1} ---\n" + text

        # Parse Metadata using regex patterns tailored for aerospace standards
        metadata = self._parse_metadata(full_text)
        
        # Parse Technical Specifications
        specs = self._parse_specifications(full_text)
        
        # Parse Structured Sections
        sections = self._parse_sections(full_text)

        return {
            "title": metadata.get("title", "Technical Document"),
            "doc_ref": metadata.get("doc_ref", "UNKNOWN-REF"),
            "revision": metadata.get("revision", "Rev --"),
            "pub_date": metadata.get("pub_date", "UNKNOWN-DATE"),
            "ata_chapter": metadata.get("ata_chapter", "ATA General"),
            "component_id": metadata.get("component_id", "GEN-001"),
            "component_name": metadata.get("component_name", "General Component"),
            "specifications": specs,
            "sections": sections,
            "full_text": full_text.strip(),
            "page_count": len(self.doc)
        }

    def _parse_metadata(self, text: str) -> Dict[str, str]:
        meta = {}

        # Document Ref (e.g. DOCUMENT REF: AMM-29-10-00-820-001 or SB-A320-32-1420)
        doc_ref_match = re.search(r"DOCUMENT REF[:\s]+([A-Z0-9\-_./]+)", text, re.IGNORECASE)
        if doc_ref_match:
            meta["doc_ref"] = doc_ref_match.group(1).strip()
        else:
            ref_fallback = re.search(r"\b(AMM|SB|AD|CMM)[-\s][A-Z0-9\-]+", text)
            meta["doc_ref"] = ref_fallback.group(0).strip() if ref_fallback else "REF-NOT-SPECIFIED"

        # Revision Number (e.g. REVISION: Rev 02 or Rev 01)
        rev_match = re.search(r"REVISION[:\s]+(Rev\s*[0-9A-Z]+|[0-9A-Z]+)", text, re.IGNORECASE)
        if rev_match:
            val = rev_match.group(1).strip()
            meta["revision"] = val if "Rev" in val else f"Rev {val}"
        else:
            rev_fallback = re.search(r"\bRev(?:ision)?\s*([0-9A-Z]+)\b", text, re.IGNORECASE)
            meta["revision"] = f"Rev {rev_fallback.group(1)}" if rev_fallback else "Rev 00"

        # Publication Date (e.g. 15-JAN-2025 or DATE: 20-FEB-2026)
        date_match = re.search(r"DATE[:\s]+(\d{1,2}-[A-Za-z]{3}-\d{4}|\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4})", text, re.IGNORECASE)
        if date_match:
            meta["pub_date"] = date_match.group(1).strip()
        else:
            date_fallback = re.search(r"\b\d{1,2}-[A-Z]{3}-\d{4}\b", text)
            meta["pub_date"] = date_fallback.group(0).strip() if date_fallback else "UNSPECIFIED DATE"

        # ATA Chapter (e.g. ATA CHAPTER: ATA 29 or ATA 32)
        ata_match = re.search(r"ATA\s*(?:CHAPTER)?[:\s]*(ATA\s*\d{2}|\d{2})", text, re.IGNORECASE)
        if ata_match:
            ata_val = ata_match.group(1).strip()
            meta["ata_chapter"] = ata_val if "ATA" in ata_val else f"ATA {ata_val}"
        else:
            meta["ata_chapter"] = "ATA 00 (General)"

        # Component ID (e.g. Component Identifier: HYD-001)
        comp_id_match = re.search(r"Component Identifier[:\s]+([A-Z0-9\-_]+)", text, re.IGNORECASE)
        if comp_id_match:
            meta["component_id"] = comp_id_match.group(1).strip()
        else:
            id_fallback = re.search(r"\b(HYD|LG|FUEL|ENG|ELEC|PNEU|AVION)-\d{3}\b", text)
            meta["component_id"] = id_fallback.group(0) if id_fallback else "COMP-001"

        # Component Name (e.g. Component Nomenclature: Engine Driven Hydraulic Pump)
        comp_name_match = re.search(r"Component Nomenclature[:\s]+([^\n\r]+)", text, re.IGNORECASE)
        if comp_name_match:
            meta["component_name"] = comp_name_match.group(1).strip()
        else:
            meta["component_name"] = "Aviation Component"

        # Title Extraction
        title_match = re.search(r"(AIRCRAFT MAINTENANCE MANUAL[^\n\r]+|SERVICE BULLETIN[^\n\r]+|AIRWORTHINESS DIRECTIVE[^\n\r]+)", text, re.IGNORECASE)
        if title_match:
            meta["title"] = title_match.group(0).strip()
        else:
            meta["title"] = "AIRCRAFT TECHNICAL PUBLICATION"

        return meta

    def _parse_specifications(self, text: str) -> Dict[str, Dict[str, str]]:
        """
        Extracts tabular specifications or key-value parameters.
        """
        specs = {}

        # Look for table rows or parameter listings
        param_patterns = [
            (r"Manufacturer Part Number\s*(?:\(P/N\))?[:\s]*(P/N\s*[A-Z0-9\-]+)", "Manufacturer Part Number (P/N)"),
            (r"Actuator Assembly Part Number[:\s]*(P/N\s*[A-Z0-9\-]+)", "Part Number (P/N)"),
            (r"Rated Operating Delivery Pressure[:\s]*(\d+\s*PSI|\d+\s*bar)", "Rated Operating Delivery Pressure"),
            (r"Maximum Transient System Pressure[:\s]*(\d+\s*PSI|\d+\s*bar)", "Maximum Transient System Pressure"),
            (r"Seal Operating Pressure Rating[:\s]*(\d+\s*PSI|\d+\s*bar)", "Seal Operating Pressure Rating"),
            (r"Case Drain Return Temperature Limit[:\s]*(\d+\s*°C|\d+\s*°F)", "Case Drain Return Temperature Limit"),
            (r"Drive Flange (?:Attachment )?Bolt Torque[:\s]*(\d+\s*in-lbs|\d+\s*Nm)", "Drive Flange Bolt Torque"),
            (r"Lock Nut Torque Limit[:\s]*(\d+\s*ft-lbs|\d+\s*Nm)", "Lock Nut Torque Limit"),
            (r"Inspection & Filter Check Interval[:\s]*(\d+\s*Flight Hours)", "Inspection Interval"),
            (r"Major Overhaul Life Limit[:\s]*(\d+\s*Flight Cycles)", "Major Overhaul Life Limit"),
            (r"Nominal Delivery Flow Rate[:\s]*(\d+\s*GPM)", "Nominal Delivery Flow Rate"),
        ]

        for pattern, label in param_patterns:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                specs[label] = {
                    "value": m.group(1).strip(),
                    "raw": m.group(0).strip()
                }

        # Also search general table rows (e.g., from PDF layout)
        lines = text.splitlines()
        for i, line in enumerate(lines):
            line_str = line.strip()
            # If line has standard parameter indicators
            for unit in ["PSI", "bar", "in-lbs", "ft-lbs", "Nm", "°C", "°F", "Flight Hours", "Flight Cycles", "GPM"]:
                if unit in line_str and len(line_str) < 120:
                    parts = re.split(r"\s{2,}|\t", line_str)
                    if len(parts) >= 2:
                        param_name = parts[0].strip()
                        param_val = parts[1].strip()
                        if param_name and param_name not in specs:
                            specs[param_name] = {"value": param_val, "raw": line_str}

        return specs

    def _parse_sections(self, text: str) -> Dict[str, str]:
        """
        Splits document into logical sections (e.g., Instructions, Applicability).
        """
        sections = {}
        section_splits = re.split(r"\n(?=\d+\.\s+[A-Z\s&]{4,})", text)
        for s in section_splits:
            s_clean = s.strip()
            if not s_clean:
                continue
            first_line = s_clean.splitlines()[0]
            if re.match(r"^\d+\.\s+", first_line):
                sec_title = first_line.strip()
                sec_body = "\n".join(s_clean.splitlines()[1:]).strip()
                sections[sec_title] = sec_body
        return sections
