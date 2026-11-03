import pandas as pd
from datetime import datetime
from typing import List, Dict, Any

class RegulatoryFeedManager:
    """
    Simulates and ingests regulatory safety publications (FAA Airworthiness Directives & EASA SBs)
    and cross-references them against active fleet components and manuals.
    """

    MOCK_REGULATORY_DIRECTIVES = [
        {
            "ad_number": "FAA-AD-2025-22-09",
            "issuing_authority": "Federal Aviation Administration (FAA)",
            "effective_date": "2025-11-15",
            "subject": "Engine Driven Hydraulic Pump Pressure Pulse Fatigue Cracking",
            "target_ata": "ATA 29",
            "affected_component": "HYD-001",
            "mandated_action": "Mandatory inspection of EDP case drain and incorporation of delivery pressure relief check per Airbus AMM 29-10-00 Rev 02.",
            "compliance_window": "Within 500 flight hours or 60 calendar days",
            "severity": "CRITICAL"
        },
        {
            "ad_number": "EASA-AD-2026-0014",
            "issuing_authority": "European Union Aviation Safety Agency (EASA)",
            "effective_date": "2026-01-20",
            "subject": "Main Landing Gear Retraction Actuator End-Cap Retention Ring",
            "target_ata": "ATA 32",
            "affected_component": "LG-002",
            "mandated_action": "Life cycle threshold reduction to 10000 Flight Cycles and torque limit verification per SB A320-32-1420 Rev 02.",
            "compliance_window": "At next scheduled C-Check or before exceeding 10000 cycles",
            "severity": "CRITICAL"
        },
        {
            "ad_number": "FAA-AD-2024-18-02",
            "issuing_authority": "Federal Aviation Administration (FAA)",
            "effective_date": "2024-09-01",
            "subject": "Main Tank Fuel Boost Pump Electrical Wiring Conduit Inspection",
            "target_ata": "ATA 28",
            "affected_component": "FUEL-003",
            "mandated_action": "Repetitive resistance check every 1200 flight hours.",
            "compliance_window": "Repetitive Maintenance",
            "severity": "HIGH"
        }
    ]

    @staticmethod
    def get_latest_directives() -> pd.DataFrame:
        return pd.DataFrame(RegulatoryFeedManager.MOCK_REGULATORY_DIRECTIVES)

    @staticmethod
    def check_component_regulatory_status(component_id: str) -> List[Dict[str, Any]]:
        matches = [d for d in RegulatoryFeedManager.MOCK_REGULATORY_DIRECTIVES if d["affected_component"] == component_id]
        return matches
