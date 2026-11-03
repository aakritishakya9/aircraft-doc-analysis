import pymupdf as fitz
import os
from typing import List, Dict, Any, Tuple

class VisualPDFAnnotator:
    """
    Renders visual highlight annotations directly onto PDF pages
    marking changed parameters, revised specifications, and new instructions.
    """

    @staticmethod
    def annotate_document_differences(
        pdf_path_or_bytes: Any,
        diff_items: List[Dict[str, Any]],
        output_path: str,
        is_revised_doc: bool = True
    ) -> str:
        """
        Scans PDF pages for text associated with changes and paints highlight annotations:
        - Amber/Yellow for modified tolerances
        - Green for added requirements/superseded parts
        - Red for deleted/baseline specs
        """
        if isinstance(pdf_path_or_bytes, str):
            doc = fitz.open(pdf_path_or_bytes)
        else:
            doc = fitz.open(stream=pdf_path_or_bytes, filetype="pdf")

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        for item in diff_items:
            # Pick search term depending on whether this is the baseline or revised document
            if is_revised_doc:
                search_term = item.get("updated_version", "")
                if search_term == "Not Specified" or not search_term:
                    search_term = item.get("parameter", "")
            else:
                search_term = item.get("previous_version", "")
                if search_term == "Not Specified" or not search_term:
                    search_term = item.get("parameter", "")

            if not search_term or len(search_term) < 2:
                continue

            # Strip unit prefixes if necessary to maximize hit rate
            clean_term = search_term.strip()

            for page_idx in range(len(doc)):
                page = doc[page_idx]
                rects = page.search_for(clean_term)

                # Fallback to parameter description search if specific value is formatted differently
                if not rects and " " in clean_term:
                    # search first token (e.g. '3200' or 'P/N')
                    first_token = clean_term.split()[0]
                    if len(first_token) >= 3:
                        rects = page.search_for(first_token)

                for r in rects:
                    annot = page.add_highlight_annot(r)
                    if is_revised_doc:
                        if item.get("change_type") == "PART_SUPERSEDED":
                            annot.set_colors(stroke=(0.2, 0.7, 0.2))  # Green
                        elif item.get("severity") in ["HIGH", "CRITICAL"]:
                            annot.set_colors(stroke=(1.0, 0.4, 0.0))  # Orange/Red
                        else:
                            annot.set_colors(stroke=(1.0, 0.8, 0.0))  # Yellow
                    else:
                        annot.set_colors(stroke=(0.9, 0.3, 0.3))      # Red (Baseline)
                    annot.set_info(title="AeroChange Engine", content=f"{item.get('parameter', 'Change')}: {search_term}")
                    annot.update()

        doc.save(output_path)
        doc.close()
        return output_path
