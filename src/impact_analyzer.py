from typing import Dict, Any, List

class EngineeringImpactAnalyzer:
    """
    Evaluates detected changes in aviation technical documentation,
    assigns engineering severity, maps downstream maintenance documentation impact,
    and formats items for Human-in-the-Loop engineering sign-off.
    """

    def __init__(self, comparison_data: Dict[str, Any]):
        self.comp_data = comparison_data
        self.meta = comparison_data.get("metadata_diff", {})
        self.param_diffs = comparison_data.get("parameter_diffs", [])
        self.text_diff = comparison_data.get("text_diff", {})

    def generate_impact_report(self) -> List[Dict[str, Any]]:
        """
        Creates structured engineering change impact report.
        """
        report_items = []
        component_id = self.meta.get("component_id", "GEN-001")
        component_name = self.meta.get("component_name", "Aviation Component")
        ata_chapter = self.meta.get("ata_chapter", "ATA 00")

        # 1. Evaluate parameter changes
        for item in self.param_diffs:
            if not item.get("is_changed"):
                continue

            param = item["parameter"]
            prev_val = item["previous_version"]
            upd_val = item["updated_version"]
            delta = item.get("delta", "N/A")

            severity, rationale, downstream_docs = self._assess_parameter_impact(param, prev_val, upd_val, ata_chapter)

            report_items.append({
                "component_id": component_id,
                "component_name": component_name,
                "ata_chapter": ata_chapter,
                "change_description": f"Specification update on '{param}': {prev_val} -> {upd_val} ({delta})",
                "affected_parameter": param,
                "previous_specification": prev_val,
                "updated_specification": upd_val,
                "severity": severity,
                "engineering_rationale": rationale,
                "potential_doc_impact": downstream_docs,
                "review_status": "Pending Engineering Review"
            })

        # 2. Evaluate mandatory accomplishment instructions or text diffs
        for addition in self.text_diff.get("additions", []):
            if any(term in addition.upper() for term in ["MANDATORY", "WARNING", "CALIBRATE", "FATIGUE", "REDUCED", "AIRWORTHINESS"]):
                report_items.append({
                    "component_id": component_id,
                    "component_name": component_name,
                    "ata_chapter": ata_chapter,
                    "change_description": f"New mandatory instructional requirement: {addition[:100]}...",
                    "affected_parameter": "Accomplishment Instruction",
                    "previous_specification": "Standard Line Procedure",
                    "updated_specification": addition[:120],
                    "severity": "CRITICAL",
                    "engineering_rationale": "Safety-critical instructional addition flagged for airworthiness directive cross-reference.",
                    "potential_doc_impact": "AMM Task Cards, Line Maintenance Work Orders, GSE Tooling",
                    "review_status": "Pending Engineering Review"
                })

        return report_items

    def _assess_parameter_impact(self, param: str, prev_val: str, upd_val: str, ata_chapter: str):
        """
        Calculates severity and downstream documentation implications.
        """
        p_upper = param.upper()
        
        # High Severity / Critical parameters
        if "PRESSURE" in p_upper:
            severity = "HIGH"
            rationale = "System pressure modification affects hydraulic line burst margins and relief valve calibration."
            downstream = "AMM 29-10-00 (System Pressurization Check), GSE Rig Tooling Spec, MPD Task Card"
        elif "TORQUE" in p_upper:
            severity = "HIGH"
            rationale = "Fastener torque adjustment impacts structural clamp load and vibration fatigue margins."
            downstream = "AMM Task Maintenance Sign-off, Line Tooling (Calibrated Torque Wrenches)"
        elif "LIFE LIMIT" in p_upper or "INTERVAL" in p_upper or "FLIGHT CYCLES" in p_upper:
            severity = "HIGH"
            rationale = "Maintenance threshold reduction triggers earlier aircraft shop visit and life-limited parts tracking."
            downstream = "AMP (Aircraft Maintenance Programme), Operator Maintenance Planning Document (MPD)"
        elif "PART NUMBER" in p_upper or "P/N" in p_upper:
            severity = "MEDIUM"
            rationale = "Part number supersession requires interchangeability check (Two-way vs One-way interchangeability)."
            downstream = "IPC (Illustrated Parts Catalog), Spares Inventory Warehouse, CMM"
        elif "TEMPERATURE" in p_upper:
            severity = "MEDIUM"
            rationale = "Thermal threshold adjustment requires review of fluid cooling capacity and heat exchanger limits."
            downstream = "AMM Troubleshooting Manual (TSM), Environmental Control System Limits"
        else:
            severity = "LOW"
            rationale = "General specification adjustment."
            downstream = "AMM Reference Sections, IPC Technical Description"

        return severity, rationale, downstream
