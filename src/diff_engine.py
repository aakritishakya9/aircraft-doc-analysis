import difflib
import re
from typing import Dict, Any, List

class DocumentComparator:
    """
    Compares baseline and revised aerospace technical documents.
    Performs dual-layer comparison:
    1. Structured engineering parameter diff (pressure, torque, life limits, P/Ns)
    2. Text & instruction prose diffing with HTML highlighting
    """

    def __init__(self, doc_baseline: Dict[str, Any], doc_revised: Dict[str, Any]):
        self.doc_base = doc_baseline
        self.doc_rev = doc_revised

    def compare_all(self) -> Dict[str, Any]:
        """
        Executes complete comparison pipeline.
        """
        metadata_diff = self._compare_metadata()
        param_diffs = self._compare_parameters()
        text_diff = self._compare_text_instructions()

        has_critical_changes = any(p.get("is_changed", False) for p in param_diffs)

        return {
            "metadata_diff": metadata_diff,
            "parameter_diffs": param_diffs,
            "text_diff": text_diff,
            "total_param_changes": sum(1 for p in param_diffs if p.get("is_changed")),
            "has_changes": has_critical_changes or metadata_diff.get("revision_changed", False)
        }

    def _compare_metadata(self) -> Dict[str, Any]:
        base_rev = self.doc_base.get("revision", "N/A")
        rev_rev = self.doc_rev.get("revision", "N/A")
        
        base_date = self.doc_base.get("pub_date", "N/A")
        rev_date = self.doc_rev.get("pub_date", "N/A")

        base_ref = self.doc_base.get("doc_ref", "N/A")
        rev_ref = self.doc_rev.get("doc_ref", "N/A")

        return {
            "component_id": self.doc_rev.get("component_id") or self.doc_base.get("component_id", "HYD-001"),
            "component_name": self.doc_rev.get("component_name") or self.doc_base.get("component_name", "Component"),
            "ata_chapter": self.doc_rev.get("ata_chapter") or self.doc_base.get("ata_chapter", "ATA 00"),
            "doc_ref_base": base_ref,
            "doc_ref_rev": rev_ref,
            "revision_base": base_rev,
            "revision_rev": rev_rev,
            "revision_changed": base_rev != rev_rev,
            "pub_date_base": base_date,
            "pub_date_rev": rev_date,
            "date_changed": base_date != rev_date
        }

    def _compare_parameters(self) -> List[Dict[str, Any]]:
        base_specs = self.doc_base.get("specifications", {})
        rev_specs = self.doc_rev.get("specifications", {})

        all_keys = sorted(list(set(base_specs.keys()).union(set(rev_specs.keys()))))
        diff_results = []

        for key in all_keys:
            val_base = base_specs.get(key, {}).get("value", "Not Specified")
            val_rev = rev_specs.get(key, {}).get("value", "Not Specified")

            is_changed = (val_base != val_rev)
            
            # Compute numerical delta if applicable
            delta_str = self._compute_delta(val_base, val_rev)
            
            # Determine change type
            if val_base == "Not Specified":
                change_type = "ADDED"
            elif val_rev == "Not Specified":
                change_type = "REMOVED"
            elif is_changed:
                if "P/N" in val_base or "P/N" in val_rev:
                    change_type = "PART_SUPERSEDED"
                else:
                    change_type = "SPEC_MODIFIED"
            else:
                change_type = "UNCHANGED"

            diff_results.append({
                "parameter": key,
                "previous_version": val_base,
                "updated_version": val_rev,
                "is_changed": is_changed,
                "change_type": change_type,
                "delta": delta_str
            })

        return diff_results

    def _compute_delta(self, val_base: str, val_rev: str) -> str:
        """
        Calculates numerical delta for units like PSI, bar, in-lbs, Flight Hours.
        """
        if val_base == "Not Specified" or val_rev == "Not Specified":
            return "N/A"
            
        # Extract first numbers
        num_base = re.search(r"[-+]?\d*\.?\d+", val_base)
        num_rev = re.search(r"[-+]?\d*\.?\d+", val_rev)

        if num_base and num_rev:
            try:
                f_base = float(num_base.group(0))
                f_rev = float(num_rev.group(0))
                diff = f_rev - f_base
                if diff == 0:
                    return "No Shift (0)"
                unit = re.sub(r"[-+]?\d*\.?\d+", "", val_rev).strip()
                sign = "+" if diff > 0 else ""
                return f"{sign}{diff:g} {unit}".strip()
            except Exception:
                pass
        return "Categorical / Text Change"

    def _compare_text_instructions(self) -> Dict[str, Any]:
        """
        Compares maintenance text and instructions line by line.
        """
        text_base = self.doc_base.get("full_text", "")
        text_rev = self.doc_rev.get("full_text", "")

        lines_base = [line.strip() for line in text_base.splitlines() if line.strip()]
        lines_rev = [line.strip() for line in text_rev.splitlines() if line.strip()]

        differ = difflib.Differ()
        diff_lines = list(differ.compare(lines_base, lines_rev))

        additions = [line[2:] for line in diff_lines if line.startswith("+ ")]
        deletions = [line[2:] for line in diff_lines if line.startswith("- ")]

        # Generate HTML snippet for visual diff
        html_diff = []
        for line in diff_lines:
            if line.startswith("+ "):
                html_diff.append(f"<div style='background-color:#DCFCE7; color:#166534; padding:2px 6px; border-left:3px solid #22C55E; margin:2px 0;'><b>+</b> {line[2:]}</div>")
            elif line.startswith("- "):
                html_diff.append(f"<div style='background-color:#FEE2E2; color:#991B1B; padding:2px 6px; border-left:3px solid #EF4444; margin:2px 0;'><b>-</b> {line[2:]}</div>")
            elif line.startswith("? "):
                continue
            else:
                html_diff.append(f"<div style='color:#64748B; padding:2px 6px; margin:1px 0;'>&nbsp;&nbsp;{line[2:]}</div>")

        return {
            "additions": additions,
            "deletions": deletions,
            "html_diff": "\n".join(html_diff[:120])  # preview first 120 lines
        }
