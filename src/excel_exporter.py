import io
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from typing import Dict, Any

class ExcelEngineeringExporter:
    """
    Exports aerospace change impact assessments and configuration tracking
    into professionally styled Excel workbooks with sign-off audit columns.
    """

    @staticmethod
    def generate_excel_report(changes_df: pd.DataFrame, components_df: pd.DataFrame, metrics: Dict[str, int]) -> bytes:
        output = io.BytesIO()
        wb = openpyxl.Workbook()

        # Styles
        header_fill = PatternFill(start_color="002B49", end_color="002B49", fill_type="solid")
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        
        high_fill = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")
        med_fill = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid")
        low_fill = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
        approved_fill = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid")
        
        thin_border = Border(
            left=Side(style='thin', color='CBD5E1'),
            right=Side(style='thin', color='CBD5E1'),
            top=Side(style='thin', color='CBD5E1'),
            bottom=Side(style='thin', color='CBD5E1')
        )

        # Sheet 1: Executive Summary
        ws_sum = wb.active
        ws_sum.title = "Executive Overview"
        ws_sum.views.sheetView[0].showGridLines = True
        
        # Title Banner
        ws_sum.merge_cells("A1:D1")
        title_cell = ws_sum["A1"]
        title_cell.value = "AIRCRAFT TECHNICAL DOCUMENTATION & CHANGE IMPACT REPORT"
        title_cell.font = Font(name="Calibri", size=14, bold=True, color="002B49")
        title_cell.alignment = Alignment(vertical="center")

        ws_sum["A3"] = "Metric Indicator"
        ws_sum["B3"] = "Value"
        ws_sum["A3"].font = header_font
        ws_sum["A3"].fill = header_fill
        ws_sum["B3"].font = header_font
        ws_sum["B3"].fill = header_fill

        summary_rows = [
            ("Total Documents Processed", metrics.get("total_docs_processed", 0)),
            ("Document Revisions Detected", metrics.get("revisions_detected", 0)),
            ("Engineering Changes Identified", metrics.get("changes_identified", 0)),
            ("Safety / Critical Tolerances Modified", metrics.get("critical_changes", 0)),
            ("Components Affected", metrics.get("components_affected", 0)),
            ("Pending Engineering Reviews", metrics.get("pending_reviews", 0)),
        ]

        for idx, (label, val) in enumerate(summary_rows, start=4):
            ws_sum[f"A{idx}"] = label
            ws_sum[f"B{idx}"] = val
            ws_sum[f"A{idx}"].border = thin_border
            ws_sum[f"B{idx}"].border = thin_border
            ws_sum[f"B{idx}"].alignment = Alignment(horizontal="center")

        ws_sum.column_dimensions["A"].width = 38
        ws_sum.column_dimensions["B"].width = 18

        # Sheet 2: Engineering Change Log
        ws_changes = wb.create_sheet(title="Engineering Changes")
        ws_changes.views.sheetView[0].showGridLines = True

        if not changes_df.empty:
            headers = list(changes_df.columns)
            ws_changes.append(headers)

            for col_idx, cell in enumerate(ws_changes[1], start=1):
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = Alignment(horizontal="center", vertical="center")

            for r_idx, row in enumerate(changes_df.itertuples(index=False), start=2):
                ws_changes.append(list(row))
                for c_idx in range(1, len(headers) + 1):
                    cell = ws_changes.cell(row=r_idx, column=c_idx)
                    cell.border = thin_border
                    
                    # Highlight severity
                    if headers[c_idx - 1].lower() == "severity":
                        val_str = str(cell.value).upper()
                        if "HIGH" in val_str or "CRITICAL" in val_str:
                            cell.fill = high_fill
                        elif "MED" in val_str:
                            cell.fill = med_fill
                        else:
                            cell.fill = low_fill

                    # Highlight review status
                    if "status" in headers[c_idx - 1].lower():
                        val_str = str(cell.value).upper()
                        if "APPROVED" in val_str:
                            cell.fill = approved_fill
                        elif "REJECTED" in val_str:
                            cell.fill = high_fill
                        elif "PENDING" in val_str or "UNDER" in val_str:
                            cell.fill = med_fill

            # Auto-fit column widths
            for col in ws_changes.columns:
                max_len = max(len(str(cell.value or '')) for cell in col)
                col_letter = openpyxl.utils.get_column_letter(col[0].column)
                ws_changes.column_dimensions[col_letter].width = max(max_len + 4, 12)
        else:
            ws_changes["A1"] = "No changes logged yet."

        # Sheet 3: Fleet Component Configuration
        ws_comps = wb.create_sheet(title="Component Configuration")
        ws_comps.views.sheetView[0].showGridLines = True

        if not components_df.empty:
            c_headers = list(components_df.columns)
            ws_comps.append(c_headers)
            for cell in ws_comps[1]:
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = Alignment(horizontal="center")

            for r_idx, row in enumerate(components_df.itertuples(index=False), start=2):
                ws_comps.append(list(row))
                for c_idx in range(1, len(c_headers) + 1):
                    cell = ws_comps.cell(row=r_idx, column=c_idx)
                    cell.border = thin_border

            for col in ws_comps.columns:
                max_len = max(len(str(cell.value or '')) for cell in col)
                col_letter = openpyxl.utils.get_column_letter(col[0].column)
                ws_comps.column_dimensions[col_letter].width = max(max_len + 4, 14)

        wb.save(output)
        return output.getvalue()
