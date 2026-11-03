from typing import Dict, List, Any

class SemanticChangeSummarizer:
    """
    Synthesizes complex technical changes, tolerance shifts, and instructional diffs
    into executive engineering rationales, shop-floor technician action items,
    and regulatory compliance assessments.
    """

    @staticmethod
    def generate_executive_rationale(
        meta_diff: Dict[str, Any],
        param_diffs: List[Dict[str, Any]],
        text_diff: Dict[str, Any],
        interchangeability: Dict[str, Any]
    ) -> Dict[str, Any]:
        
        comp_name = meta_diff.get("component_name", "Component")
        comp_id = meta_diff.get("component_id", "HYD-001")
        rev_base = meta_diff.get("revision_base", "Rev 01")
        rev_new = meta_diff.get("revision_rev", "Rev 02")
        ata = meta_diff.get("ata_chapter", "ATA General")

        # Analyze key parameter shifts
        shifted_params = [p for p in param_diffs if p.get("is_changed")]
        pressure_shift = next((p for p in shifted_params if "Pressure" in p.get("parameter", "")), None)
        torque_shift = next((p for p in shifted_params if "Torque" in p.get("parameter", "")), None)
        interval_shift = next((p for p in shifted_params if "Interval" in p.get("parameter", "") or "Limit" in p.get("parameter", "")), None)

        # 1. Executive Summary Narrative
        narrative_points = [
            f"OEM released revision transition from <b>{rev_base}</b> to <b>{rev_new}</b> for <b>{comp_name} ({comp_id})</b> under {ata}.",
        ]

        if pressure_shift:
            narrative_points.append(
                f"Operating system delivery envelope increased from <code>{pressure_shift['previous_version']}</code> to <code>{pressure_shift['updated_version']}</code> "
                f"({pressure_shift['delta']}), requiring line burst pressure verification across all connected hydraulic consumer circuits."
            )

        if torque_shift:
            narrative_points.append(
                f"Structural attachment pre-load specification adjusted from <code>{torque_shift['previous_version']}</code> to <code>{torque_shift['updated_version']}</code> "
                f"to mitigate fastener cyclic fatigue loosening under high vibration profiles."
            )

        if interval_shift:
            narrative_points.append(
                f"Maintenance threshold tightened from <code>{interval_shift['previous_version']}</code> to <code>{interval_shift['updated_version']}</code> "
                f"following OEM fatigue life reassessment and reliability monitoring data."
            )

        # 2. Shop-Floor Maintenance Action List
        shop_floor_actions = [
            "Verify part number stamping on component data plate prior to installation.",
            f"Apply Part Interchangeability Protocol: {interchangeability.get('supply_chain_action', 'Standard stock allocation')}.",
        ]

        if pressure_shift:
            shop_floor_actions.append(
                "MANDATORY GSE CHECK: Recalibrate hydraulic ground service cart pressure relief valve to match the new delivery specification prior to system ground testing."
            )
        if torque_shift:
            shop_floor_actions.append(
                f"TOOLING CHECK: Calibrate line maintenance torque wrench to {torque_shift['updated_version']} with calibrated sign-off on Job Instruction Card (JIC)."
            )

        # Add mandatory text notes if present
        for add_line in text_diff.get("additions", []):
            if "MANDATORY" in add_line.upper() or "WARNING" in add_line.upper():
                shop_floor_actions.append(f"INSTRUCTIONAL DIRECTIVE: {add_line.strip()}")

        # 3. Regulatory Airworthiness Assessment
        has_critical = any(p.get("severity") in ["HIGH", "CRITICAL"] for p in shifted_params) or len(text_diff.get("additions", [])) > 0
        if has_critical:
            regulatory_level = "MANDATORY OPERATOR ACTION (Airworthiness Concurrence Required)"
            regulatory_notes = (
                "Changes alter certified aircraft operating envelope and maintenance intervals. "
                "In accordance with FAA 14 CFR Part 43 / EASA Part 145, an authorized Quality / Technical Services Engineer "
                "must approve revision incorporation and generate an internal Engineering Order (EO) before aircraft release."
            )
        else:
            regulatory_level = "STANDARD REVISION (Routine Incorporation)"
            regulatory_notes = "Minor non-safety-critical updates. Proceed with standard manual document control updates."

        return {
            "executive_brief": narrative_points,
            "shop_floor_actions": shop_floor_actions,
            "regulatory_level": regulatory_level,
            "regulatory_compliance_notes": regulatory_notes
        }
