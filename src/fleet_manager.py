import pandas as pd
import re
from typing import Dict, List, Any, Tuple

class FleetEffectivityManager:
    """
    Manages aircraft fleet effectivity by Manufacturer Serial Number (MSN)
    and evaluates OEM Part Number Interchangeability classes (Class 1 vs Class 2 vs Class 3).
    """

    # Pre-defined Airline Operator Fleet
    DEFAULT_FLEET = [
        {"tail_number": "N201AA", "msn": 240, "aircraft_model": "A320-271N", "engine_type": "CFM LEAP-1A", "total_hours": 14200, "total_cycles": 6200, "base_hub": "DFW"},
        {"tail_number": "N202AA", "msn": 310, "aircraft_model": "A320-271N", "engine_type": "CFM LEAP-1A", "total_hours": 11800, "total_cycles": 5100, "base_hub": "ORD"},
        {"tail_number": "N203AA", "msn": 495, "aircraft_model": "A321-271NX", "engine_type": "CFM LEAP-1A", "total_hours": 8500, "total_cycles": 3700, "base_hub": "CLT"},
        {"tail_number": "N204AA", "msn": 612, "aircraft_model": "A320-271N", "engine_type": "CFM LEAP-1A", "total_hours": 6200, "total_cycles": 2650, "base_hub": "MIA"},
        {"tail_number": "N205AA", "msn": 820, "aircraft_model": "A321-271NX", "engine_type": "CFM LEAP-1A", "total_hours": 3100, "total_cycles": 1400, "base_hub": "PHX"},
    ]

    @staticmethod
    def get_fleet_dataframe() -> pd.DataFrame:
        return pd.DataFrame(FleetEffectivityManager.DEFAULT_FLEET)

    @staticmethod
    def evaluate_fleet_impact(applicability_text: str, fleet_df: pd.DataFrame = None) -> pd.DataFrame:
        """
        Cross-references document applicability against airline fleet tail numbers.
        Extracts MSN ranges (e.g. 'MSN 0200 through 0500' or default A320 fleet)
        """
        if fleet_df is None:
            fleet_df = FleetEffectivityManager.get_fleet_dataframe()

        # Parse MSN range if present in text
        msn_range_match = re.search(r"MSN\s*(\d+)\s*(?:through|to|-)\s*(\d+)", applicability_text, re.IGNORECASE)
        
        results = []
        for _, row in fleet_df.iterrows():
            tail = row["tail_number"]
            msn = int(row["msn"])
            model = row["aircraft_model"]

            if msn_range_match:
                min_msn = int(msn_range_match.group(1))
                max_msn = int(msn_range_match.group(2))
                is_affected = (min_msn <= msn <= max_msn)
                scope_reason = f"MSN {msn} is within SB effectivity window ({min_msn}-{max_msn})" if is_affected else f"MSN {msn} outside effectivity window ({min_msn}-{max_msn})"
            else:
                # Default to model applicability check
                is_affected = ("A320" in applicability_text or "A321" in applicability_text or "LEAP-1A" in applicability_text)
                scope_reason = f"Aircraft model {model} matches document applicability definition" if is_affected else "Model outside applicability criteria"

            impact_status = "AFFECTED - Action Required" if is_affected else "EXEMPT - Out of Scope"
            urgency = "High (Priority Line Maintenance)" if (is_affected and row["total_hours"] > 10000) else ("Medium" if is_affected else "None")

            results.append({
                "Tail Number": tail,
                "MSN": msn,
                "Model": model,
                "Base Hub": row["base_hub"],
                "Flight Hours": row["total_hours"],
                "Fleet Impact Status": impact_status,
                "Urgency Level": urgency,
                "Applicability Rationale": scope_reason
            })

        return pd.DataFrame(results)

    @staticmethod
    def classify_part_interchangeability(prev_pn: str, new_pn: str, param_shifts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Applies OEM aerospace interchangeability rules:
        Class 1 (Two-Way): Fully interchangeable in both directions.
        Class 2 (One-Way): New P/N can replace Old P/N, but Old CANNOT replace New.
        Class 3 (Non-Interchangeable): Incompatible without physical modification.
        """
        # If delivery pressure or torque increased, it's typically One-Way (Class 2)
        has_pressure_increase = any("Pressure" in p.get("parameter", "") and "+" in p.get("delta", "") for p in param_shifts)
        has_critical_shift = any(p.get("is_changed") and p.get("severity") in ["HIGH", "CRITICAL"] for p in param_shifts)

        if has_pressure_increase or has_critical_shift:
            ic_class = "Class 2 (One-Way Interchangeable)"
            impact_desc = "New P/N can replace Old P/N. Old P/N CANNOT be installed on modified aircraft due to higher operating tolerances."
            warehouse_action = "QUARANTINE / RE-ALLOCATE OLD STOCK: Existing stock of previous P/N must not be installed on aircraft operating under Rev 02 baseline."
            airworthiness_risk = "HIGH: Reverse installation will cause component overpressure or premature fatigue failure."
        elif prev_pn != new_pn and prev_pn != "Not Specified":
            ic_class = "Class 1 (Two-Way Interchangeable)"
            impact_desc = "Both old and new P/N are mutually interchangeable. No aircraft configuration split."
            warehouse_action = "USE UNTIL EXHAUSTED: Normal stock attrition allowed for previous P/N."
            airworthiness_risk = "LOW: Form, fit, and function are fully equivalent."
        else:
            ic_class = "Class 0 (No Part Number Change)"
            impact_desc = "Component part number unchanged across revisions."
            warehouse_action = "Standard warehouse storage."
            airworthiness_risk = "NONE"

        return {
            "previous_part_number": prev_pn,
            "updated_part_number": new_pn,
            "interchangeability_class": ic_class,
            "engineering_definition": impact_desc,
            "supply_chain_action": warehouse_action,
            "airworthiness_risk_level": airworthiness_risk
        }
