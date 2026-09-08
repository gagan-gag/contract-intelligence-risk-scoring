"""Script to generate realistic Indian commercial contracts in PDF and DOCX formats with Rupee values."""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable


OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "sample_contracts")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def create_pdf_msa_high_risk():
    """Create a high-risk Master Services Agreement in PDF with INR values."""
    pdf_path = os.path.join(OUTPUT_DIR, "Master_Services_Agreement_HighRisk.pdf")
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45,
    )
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'ContractTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0f172a'),
        alignment=1, # Center
        spaceAfter=15,
    )
    h2_style = ParagraphStyle(
        'ContractH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#1e40af'),
        spaceBefore=10,
        spaceAfter=5,
    )
    body_style = ParagraphStyle(
        'ContractBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155'),
        spaceAfter=8,
    )

    story = []
    story.append(Paragraph("MASTER SERVICES AGREEMENT", title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2563eb'), spaceAfter=15))
    
    story.append(Paragraph("This Master Services Agreement ('Agreement') is entered into as of <b>October 15, 2026</b> by and between <b>Tata Consultancy Solutions Pvt Ltd</b> ('Customer'), having its registered office in <b>Bengaluru</b>, Karnataka, and <b>Apex Cloud Technologies Ltd</b> ('Vendor').", body_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph("1. Scope of Services & Commercial Value", h2_style))
    story.append(Paragraph("Vendor agrees to provide enterprise cloud infrastructure management, data pipeline security, and AI workflow deployment. Total contract remuneration is fixed at <b>INR 1,50,00,000</b> (Rupees 1.5 Crores) payable in quarterly tranches of <b>Rs. 37,50,000</b>.", body_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("2. Term & Automatic Renewal (High Risk)", h2_style))
    story.append(Paragraph("This Agreement shall remain in effect for an initial period of two (2) years. This Agreement includes automatic renewal for successive twelve (12) month periods unless either party delivers written notice of non-renewal at least <b>90 days</b> prior to expiration. Failure to provide timely notice results in unconditional lock-in for the renewal term.", body_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("3. Indemnification & Unlimited Liability (High Risk Triggers)", h2_style))
    story.append(Paragraph("Vendor shall fully defend, indemnify, and hold harmless Customer, its directors, officers, and affiliates from and against any and all claims, liabilities, losses, damages, penalties, and expenses. The parties expressly agree to <b>unlimited liability</b> regarding all indemnification obligations, intellectual property infringement, and data breach claims without any financial cap.", body_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("4. Termination for Convenience", h2_style))
    story.append(Paragraph("Customer may terminate without notice in case of performance variance, or terminate for convenience upon thirty (30) days prior written notice subject to payment of early termination liquidated damages of <b>Rs. 25,00,000</b>.", body_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("5. Governing Law & Jurisdiction", h2_style))
    story.append(Paragraph("This Agreement shall be governed by and construed in accordance with the substantive laws of India. The courts of <b>Bengaluru</b>, Karnataka shall have exclusive jurisdiction over any dispute arising hereunder.", body_style))
    
    doc.build(story)
    print(f"Created: {pdf_path}")


def create_docx_software_license_medium_risk():
    """Create a medium-risk Software License Agreement in DOCX with INR values."""
    docx_path = os.path.join(OUTPUT_DIR, "Software_License_Agreement_MediumRisk.docx")
    doc = docx.Document()

    # Title
    title = doc.add_heading("ENTERPRISE SOFTWARE LICENSE AGREEMENT", level=1)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_run = title.runs[0]
    title_run.font.color.rgb = RGBColor(15, 23, 42)
    title_run.font.size = Pt(16)

    doc.add_paragraph(
        "This Enterprise Software License Agreement ('Agreement') is made effective on November 01, 2026, by and between "
        "Infosys Global Technologies Ltd ('Licensor'), located in Mumbai, Maharashtra, and Reliance Retail Enterprises Ltd ('Licensee')."
    )

    doc.add_heading("1. Grant of License and Fees", level=2)
    doc.add_paragraph(
        "Licensor grants Licensee a non-exclusive, non-transferable enterprise license to use the Core Engine suite. "
        "The annual license fee is ₹45,00,000 (Rupees 45 Lakhs) plus applicable GST, with an upfront setup charge of Rs. 5,00,000."
    )

    doc.add_heading("2. Limitation of Liability (Medium Risk)", level=2)
    doc.add_paragraph(
        "Except for breach of confidentiality obligations, the aggregate liability of Licensor arising under or in connection with "
        "this Agreement shall be strictly capped at the total fees paid by Licensee in the six (6) months preceding the event, "
        "not to exceed INR 22,50,000."
    )

    doc.add_heading("3. Termination & Notice", level=2)
    doc.add_paragraph(
        "Either party may terminate this agreement upon 30 days written notice of termination for material breach. "
        "Licensor reserves the right to terminate without notice in the event of unauthorized reverse engineering or unpaid invoices exceeding 60 days."
    )

    doc.add_heading("4. Confidentiality & Non-Disclosure", level=2)
    doc.add_paragraph(
        "Both parties agree to hold confidential information in strict confidence for a period of three (3) years from disclosure. "
        "Liquidated damages for willful disclosure shall be ₹15,00,000 per violation."
    )

    doc.add_heading("5. Governing Law", level=2)
    doc.add_paragraph(
        "This Agreement shall be governed by the laws of India, with exclusive dispute resolution jurisdiction submitted to the courts in Mumbai, Maharashtra."
    )

    doc.save(docx_path)
    print(f"Created: {docx_path}")


def create_pdf_nda_low_risk():
    """Create a standard low-risk Non-Disclosure Agreement in PDF with INR values."""
    pdf_path = os.path.join(OUTPUT_DIR, "Non_Disclosure_Agreement_LowRisk.pdf")
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50,
    )
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'NDATitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=colors.HexColor('#0f172a'),
        alignment=1,
        spaceAfter=12,
    )
    h2_style = ParagraphStyle(
        'NDAH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#0f766e'),
        spaceBefore=8,
        spaceAfter=4,
    )
    body_style = ParagraphStyle(
        'NDABody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#334155'),
        spaceAfter=6,
    )

    story = []
    story.append(Paragraph("MUTUAL NON-DISCLOSURE AGREEMENT", title_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0d9488'), spaceAfter=12))

    story.append(Paragraph("This Mutual Non-Disclosure Agreement is executed on <b>December 10, 2026</b> between <b>Wipro Digital Solutions Pvt Ltd</b> and <b>Zaalima AI Research Labs LLP</b>, having operations in <b>New Delhi</b>, India.", body_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("1. Purpose & Protection", h2_style))
    story.append(Paragraph("The parties wish to explore a potential strategic technology collaboration. Each party agrees to protect disclosed confidential information with standard reasonable care.", body_style))

    story.append(Paragraph("2. Term & Mutual Covenants (Low Risk)", h2_style))
    story.append(Paragraph("The non-disclosure obligations shall survive for a fixed term of three (3) years. No automatic renewal applies. Standard mutual exclusions apply for public domain information and independently developed technology.", body_style))

    story.append(Paragraph("3. Remedies & Liquidated Damages", h2_style))
    story.append(Paragraph("Breach of confidentiality shall entitle the non-breaching party to seek injunctive relief and provable damages, with liquidated damages capped at <b>₹10,00,000</b> (Rupees 10 Lakhs).", body_style))

    story.append(Paragraph("4. Governing Jurisdiction", h2_style))
    story.append(Paragraph("This agreement is governed by the laws of India and subject to the jurisdiction of the High Court of Delhi in <b>New Delhi</b>.", body_style))

    doc.build(story)
    print(f"Created: {pdf_path}")


def create_docx_vendor_supply_high_risk():
    """Create a high-risk Vendor Supply Agreement in DOCX with INR values."""
    docx_path = os.path.join(OUTPUT_DIR, "Vendor_Supply_Agreement_HighRisk.docx")
    doc = docx.Document()

    title = doc.add_heading("EXCLUSIVE VENDOR SUPPLY & PROCUREMENT AGREEMENT", level=1)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_run = title.runs[0]
    title_run.font.color.rgb = RGBColor(185, 28, 28)
    title_run.font.size = Pt(15)

    doc.add_paragraph(
        "This Exclusive Supply Agreement is entered into on January 05, 2027 by and between "
        "Mahindra Logistics Solutions Ltd ('Buyer'), located in Chennai, Tamil Nadu, and Bharat Industrial Components Pvt Ltd ('Supplier')."
    )

    doc.add_heading("1. Supply Obligation and Total Value", level=2)
    doc.add_paragraph(
        "Supplier agrees to manufacture and deliver specialized industrial hardware. "
        "The total annual procurement value is committed at ₹85,00,000 (Rupees 85 Lakhs), subject to a 10% advance guarantee of Rs. 8,50,000."
    )

    doc.add_heading("2. Auto-Renewal & Lock-In (High Risk)", level=2)
    doc.add_paragraph(
        "This Agreement contains an auto-renewal provision extending the term automatically by twelve (12) months each anniversary "
        "unless cancelled in writing at least ninety (90) days in advance."
    )

    doc.add_heading("3. Unlimited Liability & Indemnification (High Risk)", level=2)
    doc.add_paragraph(
        "Supplier shall unconditionally indemnify and hold harmless Buyer against all direct and consequential losses resulting from supply delay. "
        "The contract specifies unlimited liability for any equipment failure or operational stoppage."
    )

    doc.add_heading("4. Jurisdiction", level=2)
    doc.add_paragraph(
        "The courts in Chennai, Tamil Nadu shall have exclusive jurisdiction over any dispute."
    )

    doc.save(docx_path)
    print(f"Created: {docx_path}")


if __name__ == "__main__":
    create_pdf_msa_high_risk()
    create_docx_software_license_medium_risk()
    create_pdf_nda_low_risk()
    create_docx_vendor_supply_high_risk()
    print("All sample contract datasets generated successfully in examples/sample_contracts/!")
