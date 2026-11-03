import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def create_aviation_pdf(filename, title, doc_ref, rev_no, pub_date, ata_chapter, component_id, component_name, specs_data, notes_text):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    doc = SimpleDocTemplate(filename, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'AeroTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=colors.HexColor('#002B49')
    )
    
    meta_style = ParagraphStyle(
        'AeroMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#1E293B')
    )
    
    section_head = ParagraphStyle(
        'AeroSection',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#00558F'),
        spaceBefore=10,
        spaceAfter=5
    )
    
    body_style = ParagraphStyle(
        'AeroBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor('#0F172A')
    )

    story = []

    # Header Banner
    header_data = [
        [Paragraph("<b>AIRBUS TECHNICAL DOCUMENTATION / ENGINEERING CHANGE ORDER</b>", meta_style), 
         Paragraph(f"<b>ATA CHAPTER:</b> {ata_chapter}", meta_style)],
        [Paragraph(f"<b>DOCUMENT REF:</b> {doc_ref}", meta_style), 
         Paragraph(f"<b>REVISION:</b> {rev_no} &nbsp;|&nbsp; <b>DATE:</b> {pub_date}", meta_style)]
    ]
    header_table = Table(header_data, colWidths=[330, 200])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#EBF3F9')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#00558F')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#B8D5E5')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 14))

    # Title
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#00558F'), spaceBefore=2, spaceAfter=10))

    # Section 1: Component & Applicability
    story.append(Paragraph("1. COMPONENT IDENTIFICATION & APPLICABILITY", section_head))
    gen_text = f"""
    <b>Component Identifier:</b> {component_id}<br/>
    <b>Component Nomenclature:</b> {component_name}<br/>
    <b>Aircraft Applicability:</b> Airbus A320-271N / A321-271NX Fleet equipped with CFM LEAP-1A engines.<br/>
    <b>Purpose:</b> Definition of operational limits, installation torques, part supersession, and maintenance thresholds.
    """
    story.append(Paragraph(gen_text, body_style))
    story.append(Spacer(1, 8))

    # Section 2: Technical Specifications Table
    story.append(Paragraph("2. TECHNICAL SPECIFICATIONS & TOLERANCES", section_head))
    
    table_rows = [["Parameter Description", "Engineering Value", "Standard / Remarks"]]
    for row in specs_data:
        table_rows.append([row[0], row[1], row[2]])
    
    specs_table = Table(table_rows, colWidths=[210, 180, 140])
    specs_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#002B49')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('BOTTOMPADDING', (0,0), (-1,0), 5),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F8FAFC')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 8.5),
        ('TOPPADDING', (0,1), (-1,-1), 5),
        ('BOTTOMPADDING', (0,1), (-1,-1), 5),
    ]))
    story.append(specs_table)
    story.append(Spacer(1, 10))

    # Section 3: Maintenance & Accomplishment Instructions
    story.append(Paragraph("3. MAINTENANCE & ACCOMPLISHMENT INSTRUCTIONS", section_head))
    story.append(Paragraph(notes_text, body_style))
    story.append(Spacer(1, 14))

    # Footer note
    footer_text = "<i>CONFIDENTIAL & PROPRIETARY — FOR USE BY CERTIFIED OPERATOR ENGINEERING PERSONNEL ONLY.</i>"
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#94A3B8'), spaceBefore=8, spaceAfter=6))
    story.append(Paragraph(footer_text, ParagraphStyle('Footer', parent=styles['Normal'], fontSize=7.5, textColor=colors.HexColor('#64748B'), alignment=1)))

    doc.build(story)
    print(f"Generated: {filename}")

def generate_all():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sample_dir = os.path.join(base_dir, "sample_pdfs")

    # Document 1: Hydraulic Pump Rev 01
    specs_rev01 = [
        ["Manufacturer Part Number (P/N)", "P/N 9400-A", "Aerospace Standard"],
        ["Rated Operating Delivery Pressure", "3000 PSI", "Continuous Normal"],
        ["Maximum Transient System Pressure", "3400 PSI", "System Safety Limit"],
        ["Case Drain Return Temperature Limit", "105°C", "Thermal Threshold"],
        ["Drive Flange Attachment Bolt Torque", "120 in-lbs", "Installation Specification"],
        ["Inspection & Filter Check Interval", "500 Flight Hours", "Scheduled Line Check"],
        ["Nominal Delivery Flow Rate", "37 GPM", "Rated Flow"]
    ]
    notes_rev01 = """
    Ensure all hydraulic lines are depressurized to 0 PSI prior to commencing removal. Inspect pump casing for signs of hydraulic fluid leakage. 
    Standard elastomeric O-rings (BMS 3-11 Class 4) must be lubricated with Skydrol hydraulic fluid prior to mating.
    Torque attachment bolts evenly in a cross pattern to 120 in-lbs.
    """
    create_aviation_pdf(
        os.path.join(sample_dir, "AMM_29_10_00_Rev01.pdf"),
        "AIRCRAFT MAINTENANCE MANUAL — ENGINE DRIVEN HYDRAULIC PUMP",
        "AMM-29-10-00-820-001",
        "Rev 01",
        "15-JAN-2025",
        "ATA 29",
        "HYD-001",
        "Engine Driven Hydraulic Pump (EDP)",
        specs_rev01,
        notes_rev01
    )

    # Document 1: Hydraulic Pump Rev 02 (Updated)
    specs_rev02 = [
        ["Manufacturer Part Number (P/N)", "P/N 9400-B", "Supersedes P/N 9400-A"],
        ["Rated Operating Delivery Pressure", "3200 PSI", "Continuous Normal (Updated)"],
        ["Maximum Transient System Pressure", "3650 PSI", "System Safety Limit (Updated)"],
        ["Case Drain Return Temperature Limit", "110°C", "Thermal Threshold (Updated)"],
        ["Drive Flange Attachment Bolt Torque", "135 in-lbs", "Installation Specification (Updated)"],
        ["Inspection & Filter Check Interval", "400 Flight Hours", "Scheduled Line Check (Shortened)"],
        ["Nominal Delivery Flow Rate", "37 GPM", "Rated Flow (Unchanged)"]
    ]
    notes_rev02 = """
    Ensure all hydraulic lines are depressurized to 0 PSI prior to commencing removal. Inspect pump casing for signs of hydraulic fluid leakage.
    Standard elastomeric O-rings (BMS 3-11 Class 4) must be lubricated with Skydrol hydraulic fluid prior to mating.
    Torque attachment bolts evenly in a cross pattern to 135 in-lbs.
    MANDATORY ACTION: Due to delivery pressure increase to 3200 PSI, maintenance technicians must calibrate ground test rig relief valves prior to system checkout.
    """
    create_aviation_pdf(
        os.path.join(sample_dir, "AMM_29_10_00_Rev02.pdf"),
        "AIRCRAFT MAINTENANCE MANUAL — ENGINE DRIVEN HYDRAULIC PUMP",
        "AMM-29-10-00-820-001",
        "Rev 02",
        "20-FEB-2026",
        "ATA 29",
        "HYD-001",
        "Engine Driven Hydraulic Pump (EDP)",
        specs_rev02,
        notes_rev02
    )

    # Document 2: Main Landing Gear Actuator Rev 01
    lg_specs_rev01 = [
        ["Actuator Assembly Part Number", "P/N 20145-01", "OEM Standard"],
        ["Seal Operating Pressure Rating", "2800 PSI", "Operating Pressure"],
        ["Lock Nut Torque Limit", "250 ft-lbs", "Assembly Torque"],
        ["Major Overhaul Life Limit", "12000 Flight Cycles", "Life Limit Threshold"]
    ]
    lg_notes_rev01 = """
    Perform visual inspection for chrome plating micro-cracks on piston rod surface.
    Grease pivot bearings with Aeroshell Grease 22 during scheduled C-checks.
    """
    create_aviation_pdf(
        os.path.join(sample_dir, "SB_A320_32_1420_Rev01.pdf"),
        "SERVICE BULLETIN — MAIN LANDING GEAR RETRACTION ACTUATOR",
        "SB-A320-32-1420",
        "Rev 01",
        "10-MAR-2024",
        "ATA 32",
        "LG-002",
        "Main Landing Gear Retraction Actuator",
        lg_specs_rev01,
        lg_notes_rev01
    )

    # Document 2: Main Landing Gear Actuator Rev 02
    lg_specs_rev02 = [
        ["Actuator Assembly Part Number", "P/N 20145-02", "Supersedes P/N 20145-01"],
        ["Seal Operating Pressure Rating", "2950 PSI", "Operating Pressure (Updated)"],
        ["Lock Nut Torque Limit", "275 ft-lbs", "Assembly Torque (Updated)"],
        ["Major Overhaul Life Limit", "10000 Flight Cycles", "Life Limit Threshold (Reduced)"]
    ]
    lg_notes_rev02 = """
    Perform visual inspection for chrome plating micro-cracks on piston rod surface.
    Grease pivot bearings with Aeroshell Grease 22 during scheduled C-checks.
    MANDATORY ACTION: Life limit reduced to 10000 Flight Cycles following fatigue life reassessment by stress engineering.
    """
    create_aviation_pdf(
        os.path.join(sample_dir, "SB_A320_32_1420_Rev02.pdf"),
        "SERVICE BULLETIN — MAIN LANDING GEAR RETRACTION ACTUATOR",
        "SB-A320-32-1420",
        "Rev 02",
        "05-JAN-2026",
        "ATA 32",
        "LG-002",
        "Main Landing Gear Retraction Actuator",
        lg_specs_rev02,
        lg_notes_rev02
    )

if __name__ == "__main__":
    generate_all()
