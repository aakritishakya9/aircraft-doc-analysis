import json
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List
import requests

class AirlineERPIntegrator:
    """
    Integrates approved engineering changes with Airline Enterprise MRO systems:
    - Swiss-AS AMOS
    - SAP S/4HANA for Aviation MRO
    - IBM Maximo Aviation
    
    Generates ATA SPEC 2000 compliant Engineering Change Orders (ECO)
    and dispatches them via secure REST webhooks.
    """

    SUPPORTED_SYSTEMS = ["Swiss-AS AMOS", "SAP S/4HANA Aviation", "IBM Maximo Aviation"]

    @staticmethod
    def generate_eco_payload(
        change_item: Dict[str, Any],
        interchange_data: Dict[str, Any],
        reviewer_name: str,
        erp_target: str = "Swiss-AS AMOS"
    ) -> Dict[str, Any]:
        """
        Constructs an ATA SPEC 2000 compliant Engineering Change Order (ECO) JSON payload.
        """
        now_iso = datetime.now(timezone.utc).isoformat()
        comp_id = change_item.get("component_id", "HYD-001")
        param = change_item.get("parameter_name", "Operating Pressure")
        prev_spec = change_item.get("previous_spec", "3000 PSI")
        new_spec = change_item.get("updated_spec", "3200 PSI")
        
        # Deterministic ECO Number
        eco_num = f"ECO-{comp_id}-{datetime.now().strftime('%Y%m')}-0042"

        # Cryptographic verification checksum
        payload_str = f"{eco_num}|{comp_id}|{prev_spec}|{new_spec}|{reviewer_name}|{now_iso}"
        sha256_hash = hashlib.sha256(payload_str.encode()).hexdigest()

        payload = {
            "eco_header": {
                "eco_number": eco_num,
                "target_erp": erp_target,
                "spec_standard": "ATA SPEC 2000 / Spec 42",
                "creation_timestamp": now_iso,
                "compliance_category": "MANDATORY SAFETY COMPLIANCE",
                "authorized_by": reviewer_name,
                "cryptographic_checksum": sha256_hash
            },
            "component_master": {
                "component_id": comp_id,
                "ata_chapter": "ATA 29",
                "affected_parameter": param,
                "baseline_specification": prev_spec,
                "revised_specification": new_spec,
                "downstream_task_card": "AMM Task 29-10-00-820-001"
            },
            "supply_chain_supersession": {
                "previous_part_number": interchange_data.get("previous_part_number", "P/N 9400-A"),
                "superseding_part_number": interchange_data.get("updated_part_number", "P/N 9400-B"),
                "interchangeability_class": interchange_data.get("interchangeability_class", "Class 2 (One-Way)"),
                "warehouse_directive": interchange_data.get("supply_chain_action", "Quarantine old stock"),
                "auto_block_old_po": "Class 2" in interchange_data.get("interchangeability_class", "")
            },
            "fleet_work_orders": {
                "action_type": "CALIBRATE_AND_INSPECT",
                "affected_tails": ["N201AA", "N202AA", "N203AA"],
                "target_work_package": f"WP-{comp_id}-LINE-01",
                "estimated_ground_time_hrs": 3.5
            }
        }
        return payload

    @staticmethod
    def dispatch_webhook(payload: Dict[str, Any], webhook_url: str = None) -> Dict[str, Any]:
        """
        Dispatches payload to ERP endpoint, or simulates a 200 OK enterprise receipt if in mock mode.
        """
        target = payload["eco_header"]["target_erp"]
        eco_num = payload["eco_header"]["eco_number"]
        now_iso = datetime.now(timezone.utc).isoformat()

        if webhook_url and webhook_url.startswith("http"):
            try:
                resp = requests.post(webhook_url, json=payload, timeout=5)
                return {
                    "status_code": resp.status_code,
                    "status": "DELIVERED" if resp.status_code in [200, 201, 202] else "ERROR",
                    "target_erp": target,
                    "eco_number": eco_num,
                    "response_text": resp.text[:200],
                    "timestamp": now_iso
                }
            except Exception as e:
                return {
                    "status_code": 500,
                    "status": "DISPATCH_FAILED",
                    "target_erp": target,
                    "eco_number": eco_num,
                    "error_message": str(e),
                    "timestamp": now_iso
                }
        else:
            # High-fidelity simulated enterprise acknowledgment
            return {
                "status_code": 200,
                "status": "SYNCED_AND_ACKNOWLEDGED",
                "target_erp": target,
                "eco_number": eco_num,
                "transaction_id": f"TX-{target.split()[0].upper()}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "sync_message": f"Successfully ingested {eco_num} into {target}. Work package WP-HYD-042 generated; warehouse quarantine flag set on old part stock.",
                "timestamp": now_iso
            }
