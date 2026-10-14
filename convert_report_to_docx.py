"""
Script to generate high-fidelity Microsoft Word documents (.docx) from PROJECT_REPORT.md.
Creates:
1. PROJECT_REPORT_with_certificate.docx (Includes official certificate page)
2. PROJECT_REPORT.docx (Standalone project report)

Features:
- Native Word tables with custom borders, cell margins, and shading (Navy header row)
- High-resolution embedded screenshots (category distribution, confusion matrix, metrics, Streamlit app)
- Monospace syntax-styled code boxes for Python scripts (setup_data.py, train_model.py, app.py)
- Running headers and dynamic page numbers in the footer (excluding cover page)
- Elegant typography with custom colors (Navy #1E3A8A, Dark Slate #0F172A, Slate Gray #475569)
"""
import os
import pypdfium2 as pdfium
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))

# Color Palette Constants
COLOR_NAVY = RGBColor(30, 58, 138)       # #1E3A8A (Primary Headings)
COLOR_DARK = RGBColor(15, 23, 42)        # #0F172A (Body / Title Text)
COLOR_MUTED = RGBColor(71, 85, 105)      # #475569 (Subtitles / Captions)
COLOR_LIGHT_MUTED = RGBColor(100, 116, 139) # #64748B
COLOR_BLUE = RGBColor(2, 132, 199)       # #0284C7 (Accents)

HEX_NAVY = "1E3A8A"
HEX_LIGHT_BLUE = "EFF6FF"
HEX_BG_GRAY = "F8FAFC"
HEX_BORDER = "CBD5E1"
HEX_CODE_BG = "F1F5F9"

def set_cell_background(cell, hex_color):
    """Sets background color of a table cell."""
    tcPr = cell._element.get_or_add_tcPr()
    # Remove existing shd if any
    for existing in tcPr.findall(qn('w:shd')):
        tcPr.remove(existing)
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=120, bottom=120, left=160, right=160):
    """Sets cell padding in dxa (1 pt = 20 dxa)."""
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)

def set_table_borders(table, color="CBD5E1", sz="4", val="single"):
    """Applies clean horizontal borders to a table."""
    tblPr = table._element.xpath('w:tblPr')
    if tblPr:
        borders = parse_xml(
            f'<w:tblBorders {nsdecls("w")}>'
            f'<w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
            f'<w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
            f'<w:left w:val="none"/>'
            f'<w:right w:val="none"/>'
            f'<w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
            f'<w:insideV w:val="none"/>'
            f'</w:tblBorders>'
        )
        tblPr[0].append(borders)

def set_card_table_borders(table, color="CBD5E1", sz="6"):
    """Applies an all-around border to a card table."""
    tblPr = table._element.xpath('w:tblPr')
    if tblPr:
        borders = parse_xml(
            f'<w:tblBorders {nsdecls("w")}>'
            f'<w:top w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
            f'<w:bottom w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
            f'<w:left w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
            f'<w:right w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
            f'<w:insideH w:val="single" w:sz="4" w:space="0" w:color="{color}"/>'
            f'<w:insideV w:val="none"/>'
            f'</w:tblBorders>'
        )
        tblPr[0].append(borders)

def add_dynamic_page_number(run):
    """Inserts Word dynamic PAGE field into a run."""
    fldSimple = parse_xml(f'<w:fldSimple {nsdecls("w")} w:instr="PAGE"/>')
    run._r.append(fldSimple)

def add_dynamic_total_pages(run):
    """Inserts Word dynamic NUMPAGES field into a run."""
    fldSimple = parse_xml(f'<w:fldSimple {nsdecls("w")} w:instr="NUMPAGES"/>')
    run._r.append(fldSimple)

def extract_certificate_image():
    """Extracts page 1 of DAUP_Lab Record Certificate Page(novelia).pdf as a high-res PNG."""
    cert_pdf = os.path.join(WORKSPACE_DIR, 'DAUP_Lab Record Certificate Page(novelia).pdf')
    if not os.path.exists(cert_pdf):
        return None
    out_dir = os.path.join(WORKSPACE_DIR, 'outputs_word')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'certificate_page.png')
    pdf = pdfium.PdfDocument(cert_pdf)
    # Page index 1 is the actual certificate
    img = pdf[1].render(scale=3.0).to_pil()
    img.save(out_path)
    return out_path

def add_styled_heading(doc, text, level=1, space_before=14, space_after=6):
    """Adds a custom styled heading with exact point sizing, color, and spacing."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.keep_with_next = True
    
    run = p.add_run(text)
    run.font.name = 'Segoe UI'
    run.bold = True
    
    if level == 1:
        run.font.size = Pt(17)
        run.font.color.rgb = COLOR_DARK
        # Add bottom border to heading 1 paragraph
        pBdr = parse_xml(f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="18" w:space="4" w:color="{HEX_NAVY}"/></w:pBdr>')
        p._p.get_or_add_pPr().append(pBdr)
    elif level == 2:
        run.font.size = Pt(13.5)
        run.font.color.rgb = COLOR_NAVY
        pBdr = parse_xml(f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="8" w:space="3" w:color="93C5FD"/></w:pBdr>')
        p._p.get_or_add_pPr().append(pBdr)
    elif level == 3:
        run.font.size = Pt(11)
        run.font.color.rgb = COLOR_DARK
    return p

def add_body_paragraph(doc, text="", space_after=5, line_spacing=1.15):
    """Adds a clean body paragraph with Segoe UI font."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = line_spacing
    if text:
        run = p.add_run(text)
        run.font.name = 'Segoe UI'
        run.font.size = Pt(10)
        run.font.color.rgb = COLOR_DARK
    return p

def add_bullet_point(doc, lead_in, text, space_after=4):
    """Adds a bullet point with bold lead-in."""
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    
    run1 = p.add_run(lead_in)
    run1.font.name = 'Segoe UI'
    run1.font.size = Pt(10)
    run1.bold = True
    run1.font.color.rgb = COLOR_DARK
    
    run2 = p.add_run(" " + text)
    run2.font.name = 'Segoe UI'
    run2.font.size = Pt(10)
    run2.font.color.rgb = COLOR_DARK
    return p

def add_code_block(doc, code_text):
    """Adds a shaded monospace code box with borders."""
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    
    cell = table.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, "FAFBFC")
    set_cell_margins(cell, top=140, bottom=140, left=180, right=180)
    
    # Border
    tcPr = cell._element.get_or_add_tcPr()
    tcBorders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="6" w:color="{HEX_BORDER}"/>'
        f'<w:left w:val="single" w:sz="18" w:color="{HEX_NAVY}"/>'
        f'<w:bottom w:val="single" w:sz="6" w:color="{HEX_BORDER}"/>'
        f'<w:right w:val="single" w:sz="6" w:color="{HEX_BORDER}"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(tcBorders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.05
    
    run = p.add_run(code_text.strip())
    run.font.name = 'Consolas'
    run.font.size = Pt(8.5)
    run.font.color.rgb = RGBColor(30, 41, 59)
    
    # Spacer paragraph after table
    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(0)
    sp.paragraph_format.space_after = Pt(8)

def build_cover_page(doc):
    """Creates the academic cover page in Word."""
    # Outer Card Table for framing
    frame_table = doc.add_table(rows=1, cols=1)
    frame_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    frame_table.autofit = False
    cell = frame_table.cell(0, 0)
    cell.width = Inches(6.6)
    
    set_cell_background(cell, "FFFFFF")
    set_cell_margins(cell, top=240, bottom=240, left=240, right=240)
    
    tcPr = cell._element.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:top w:val="double" w:sz="18" w:color="{HEX_NAVY}"/>'
        f'<w:bottom w:val="double" w:sz="18" w:color="{HEX_NAVY}"/>'
        f'<w:left w:val="double" w:sz="18" w:color="{HEX_NAVY}"/>'
        f'<w:right w:val="double" w:sz="18" w:color="{HEX_NAVY}"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)
    
    # 1. Department & College Header
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run("DEPARTMENT OF COMPUTER SCIENCE\n")
    r.font.name = 'Segoe UI'
    r.font.size = Pt(11)
    r.bold = True
    r.font.color.rgb = COLOR_NAVY
    
    r2 = p.add_run("RAJAGIRI COLLEGE OF SOCIAL SCIENCES\n")
    r2.font.name = 'Segoe UI'
    r2.font.size = Pt(16)
    r2.bold = True
    r2.font.color.rgb = COLOR_DARK
    
    r3 = p.add_run("(AUTONOMOUS)\n")
    r3.font.name = 'Segoe UI'
    r3.font.size = Pt(10.5)
    r3.bold = True
    r3.font.color.rgb = COLOR_MUTED
    
    r4 = p.add_run("Kalamassery, Kochi – 683 104, Kerala\n\n")
    r4.font.name = 'Segoe UI'
    r4.font.size = Pt(9.5)
    r4.font.color.rgb = COLOR_LIGHT_MUTED
    
    r5 = p.add_run("MASTER OF COMPUTER APPLICATIONS (MCA)\n")
    r5.font.name = 'Segoe UI'
    r5.font.size = Pt(12.5)
    r5.bold = True
    r5.font.color.rgb = COLOR_NAVY
    
    r6 = p.add_run("Academic Batch: 2025 – 2027\n")
    r6.font.name = 'Segoe UI'
    r6.font.size = Pt(9.5)
    r6.bold = True
    r6.font.color.rgb = COLOR_MUTED
    
    # Divider line
    p_div = cell.add_paragraph()
    p_div.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_div.paragraph_format.space_before = Pt(8)
    p_div.paragraph_format.space_after = Pt(10)
    p_divBdr = parse_xml(f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="18" w:space="1" w:color="{HEX_NAVY}"/></w:pBdr>')
    p_div._p.get_or_add_pPr().append(p_divBdr)
    
    # 2. Course & Mini Project Report Badge
    p_course = cell.add_paragraph()
    p_course.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_course.paragraph_format.space_before = Pt(6)
    p_course.paragraph_format.space_after = Pt(2)
    rc = p_course.add_run("MCA306: DATA ANALYTICS USING PYTHON\n")
    rc.font.name = 'Segoe UI'
    rc.font.size = Pt(10.5)
    rc.bold = True
    rc.font.color.rgb = COLOR_BLUE
    
    rb = p_course.add_run("MINI PROJECT REPORT\n\n")
    rb.font.name = 'Segoe UI'
    rb.font.size = Pt(9.5)
    rb.bold = True
    rb.font.color.rgb = COLOR_NAVY
    
    # Title
    rt = p_course.add_run("IT Helpdesk Support Ticket Classifier\n")
    rt.font.name = 'Segoe UI'
    rt.font.size = Pt(20)
    rt.bold = True
    rt.font.color.rgb = COLOR_DARK
    
    rs = p_course.add_run("Automating IT Support Routing & Triage with NLP and Supervised Machine Learning\n")
    rs.font.name = 'Segoe UI'
    rs.font.size = Pt(11)
    rs.font.color.rgb = COLOR_MUTED
    
    # 3. Inner Candidate Metadata Table
    p_spacer = cell.add_paragraph()
    p_spacer.paragraph_format.space_before = Pt(4)
    p_spacer.paragraph_format.space_after = Pt(6)
    
    meta_table = cell.add_table(rows=7, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_table.autofit = False
    set_card_table_borders(meta_table, color="CBD5E1", sz="6")
    
    metadata_rows = [
        ("Candidate Name:", "NOVELIA JOSEPH", True),
        ("Register Number:", "25204046", False),
        ("Roll Number:", "46", False),
        ("Semester / Year:", "Semester III (Third Semester) / 2026", False),
        ("Core Domain:", "Machine Learning & Natural Language Processing (NLP)", False),
        ("Model Architecture:", "Multinomial Logistic Regression + TF-IDF Vectorization", False),
        ("Web Deployment:", "Streamlit Interactive Dashboard", False)
    ]
    
    for idx, (label, val, is_highlight) in enumerate(metadata_rows):
        r_row = meta_table.rows[idx]
        c_lbl = r_row.cells[0]
        c_val = r_row.cells[1]
        
        c_lbl.width = Inches(2.4)
        c_val.width = Inches(3.7)
        
        set_cell_background(c_lbl, HEX_BG_GRAY)
        set_cell_background(c_val, "FFFFFF")
        set_cell_margins(c_lbl, top=70, bottom=70, left=120, right=120)
        set_cell_margins(c_val, top=70, bottom=70, left=120, right=120)
        
        p_l = c_lbl.paragraphs[0]
        p_l.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p_l.paragraph_format.space_before = Pt(0)
        p_l.paragraph_format.space_after = Pt(0)
        r_l = p_l.add_run(label)
        r_l.font.name = 'Segoe UI'
        r_l.font.size = Pt(9.5)
        r_l.bold = True
        r_l.font.color.rgb = COLOR_MUTED
        
        p_v = c_val.paragraphs[0]
        p_v.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p_v.paragraph_format.space_before = Pt(0)
        p_v.paragraph_format.space_after = Pt(0)
        r_v = p_v.add_run(val)
        r_v.font.name = 'Segoe UI'
        r_v.font.size = Pt(9.5)
        if is_highlight:
            r_v.font.size = Pt(10.5)
            r_v.bold = True
            r_v.font.color.rgb = COLOR_NAVY
        else:
            r_v.bold = False
            r_v.font.color.rgb = COLOR_DARK
            
    # Bottom Footer on Cover
    p_foot = cell.add_paragraph()
    p_foot.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_foot.paragraph_format.space_before = Pt(16)
    p_foot.paragraph_format.space_after = Pt(4)
    
    rf1 = p_foot.add_run("Submitted in partial fulfillment of the requirements for continuous evaluation of MCA306\n")
    rf1.font.name = 'Segoe UI'
    rf1.font.size = Pt(8.5)
    rf1.italic = True
    rf1.font.color.rgb = COLOR_LIGHT_MUTED
    
    rf2 = p_foot.add_run("OCTOBER 2026")
    rf2.font.name = 'Segoe UI'
    rf2.font.size = Pt(9.5)
    rf2.bold = True
    rf2.font.color.rgb = COLOR_DARK

def generate_docx(include_certificate=True, filename="PROJECT_REPORT_with_certificate.docx"):
    """Builds the complete Word document report."""
    doc = Document()
    
    # Configure default page setup (A4, 1-inch margins)
    section = doc.sections[0]
    section.page_width = Inches(8.27)
    section.page_height = Inches(11.69)
    section.top_margin = Inches(0.85)
    section.bottom_margin = Inches(0.85)
    section.left_margin = Inches(0.85)
    section.right_margin = Inches(0.85)
    
    # Cover page has different header/footer
    section.different_first_page_header_footer = True
    
    # Setup Running Header & Footer for subsequent pages
    header = section.header
    hp = header.paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    hp.paragraph_format.space_after = Pt(0)
    hr1 = hp.add_run("IT Helpdesk Support Ticket Classifier — Mini Project Report        ")
    hr1.font.name = 'Segoe UI'
    hr1.font.size = Pt(8.5)
    hr1.font.color.rgb = COLOR_LIGHT_MUTED
    
    hr2 = hp.add_run("Novelia Joseph (Reg No: 25204046)")
    hr2.font.name = 'Segoe UI'
    hr2.font.size = Pt(8.5)
    hr2.font.color.rgb = COLOR_LIGHT_MUTED
    
    # Border under header
    hpBdr = parse_xml(f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="6" w:space="3" w:color="{HEX_BORDER}"/></w:pBdr>')
    hp._p.get_or_add_pPr().append(hpBdr)
    
    footer = section.footer
    fp = footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.LEFT
    fp.paragraph_format.space_before = Pt(4)
    fp.paragraph_format.space_after = Pt(0)
    
    fr1 = fp.add_run("Department of Computer Science — Rajagiri College of Social Sciences (Autonomous)")
    fr1.font.name = 'Segoe UI'
    fr1.font.size = Pt(8.5)
    fr1.font.color.rgb = COLOR_LIGHT_MUTED
    
    fr_tab = fp.add_run("                                        Page ")
    fr_tab.font.name = 'Segoe UI'
    fr_tab.font.size = Pt(8.5)
    fr_tab.font.color.rgb = COLOR_LIGHT_MUTED
    add_dynamic_page_number(fr_tab)
    
    fr_of = fp.add_run(" of ")
    fr_of.font.name = 'Segoe UI'
    fr_of.font.size = Pt(8.5)
    fr_of.font.color.rgb = COLOR_LIGHT_MUTED
    add_dynamic_total_pages(fr_of)
    
    # Border above footer
    fpBdr = parse_xml(f'<w:pBdr {nsdecls("w")}><w:top w:val="single" w:sz="6" w:space="3" w:color="{HEX_BORDER}"/></w:pBdr>')
    fp._p.get_or_add_pPr().append(fpBdr)
    
    # ---------------- PAGE 1: COVER PAGE ----------------
    build_cover_page(doc)
    doc.add_page_break()
    
    # ---------------- PAGE 2: OFFICIAL CERTIFICATE (OPTIONAL) ----------------
    if include_certificate:
        cert_img = extract_certificate_image()
        if cert_img and os.path.exists(cert_img):
            p_cert_title = doc.add_paragraph()
            p_cert_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cert_title.paragraph_format.space_before = Pt(0)
            p_cert_title.paragraph_format.space_after = Pt(6)
            
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Pt(0)
            p_img.paragraph_format.space_after = Pt(0)
            run_img = p_img.add_run()
            run_img.add_picture(cert_img, width=Inches(6.3))
            
            doc.add_page_break()
            
    # ---------------- SECTION 1: PROJECT TITLE / TOPIC ----------------
    add_styled_heading(doc, "1. Project Title / Topic", level=1, space_before=0, space_after=8)
    p_title = add_body_paragraph(doc, space_after=8)
    r_bt = p_title.add_run("IT Helpdesk Support Ticket Classifier: Automating IT Support with Machine Learning")
    r_bt.bold = True
    r_bt.font.size = Pt(11)
    r_bt.font.color.rgb = COLOR_NAVY
    
    # Metadata info table
    info_table = doc.add_table(rows=3, cols=2)
    info_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    info_table.autofit = False
    set_card_table_borders(info_table, color="CBD5E1", sz="6")
    
    info_data = [
        ("Candidate Name: Novelia Joseph", "Register Number: 25204046"),
        ("Class Roll Number: 46", "Degree Programme: MCA (2025–2027)"),
        ("Project Domain: Machine Learning & NLP", "Application Framework: Streamlit Web Dashboard")
    ]
    for row_idx, (col1_txt, col2_txt) in enumerate(info_data):
        r_elem = info_table.rows[row_idx]
        c1, c2 = r_elem.cells[0], r_elem.cells[1]
        c1.width = Inches(3.2)
        c2.width = Inches(3.3)
        set_cell_background(c1, HEX_BG_GRAY)
        set_cell_background(c2, HEX_BG_GRAY)
        set_cell_margins(c1, top=60, bottom=60, left=120, right=120)
        set_cell_margins(c2, top=60, bottom=60, left=120, right=120)
        
        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_before = Pt(0)
        p1.paragraph_format.space_after = Pt(0)
        r1 = p1.add_run(col1_txt)
        r1.font.name = 'Segoe UI'
        r1.font.size = Pt(9.5)
        r1.bold = True
        r1.font.color.rgb = COLOR_DARK
        
        p2 = c2.paragraphs[0]
        p2.paragraph_format.space_before = Pt(0)
        p2.paragraph_format.space_after = Pt(0)
        r2 = p2.add_run(col2_txt)
        r2.font.name = 'Segoe UI'
        r2.font.size = Pt(9.5)
        r2.bold = True
        r2.font.color.rgb = COLOR_DARK
        
    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(0)
    p_sp.paragraph_format.space_after = Pt(6)
    
    # ---------------- SECTION 2: OBJECTIVES ----------------
    add_styled_heading(doc, "2. Objectives", level=1, space_before=14, space_after=8)
    add_body_paragraph(doc, "The primary objectives of this machine learning mini project are:")
    
    add_bullet_point(doc, "1. Automate Ticket Triage:", "To design and implement an automated classification system that reads unstructured IT helpdesk support tickets and accurately routes them to the appropriate support category.")
    add_bullet_point(doc, "2. Text Preprocessing & Cleaning:", "To clean raw ticket descriptions by removing noise, extraneous punctuation, and formatting irregularities while preserving domain-specific technical vocabulary and anonymized ticket markers.")
    add_bullet_point(doc, "3. Feature Extraction via NLP:", "To convert unstructured text descriptions into high-dimensional numerical vectors using Term Frequency-Inverse Document Frequency (TF-IDF) with unigram and bigram representation.")
    add_bullet_point(doc, "4. Supervised Classifier Training:", "To train and evaluate a Multinomial Logistic Regression model to classify tickets into 7 distinct operational IT categories.")
    add_bullet_point(doc, "5. Interactive Real-Time Deployment:", "To develop and deploy an intuitive Streamlit web interface that enables support personnel to enter new support tickets and instantly receive the predicted category alongside prediction confidence scores.")
    
    doc.add_page_break()
    
    # ---------------- SECTION 3: DESCRIPTION OF DATASET ----------------
    add_styled_heading(doc, "3. Description of the Dataset", level=1, space_before=0, space_after=8)
    add_bullet_point(doc, "Dataset Name:", "Classification of IT Support Tickets")
    add_bullet_point(doc, "Source of Dataset:", "Zenodo Open-Access Scientific Repository (https://zenodo.org/records/7648117)")
    add_bullet_point(doc, "Number of Records / Rows:", "2,229 tickets")
    add_bullet_point(doc, "Number of Attributes / Columns:", "3 attributes (id, text, category_truth) + 1 generated feature (cleaned_text)")
    add_bullet_point(doc, "Target Variable:", "category_truth (Multi-class with 7 operational categories)")
    
    add_styled_heading(doc, "Dataset Attributes & Data Types", level=3, space_before=10, space_after=4)
    add_bullet_point(doc, "id:", "Categorical / Identifier (String/Object)")
    add_bullet_point(doc, "text:", "Unstructured Raw Ticket Description (String/Object)")
    add_bullet_point(doc, "category_truth:", "Ground Truth Target Variable (String/Object)")
    add_bullet_point(doc, "cleaned_text:", "Preprocessed NLP Feature Space (String/Object)")
    
    add_styled_heading(doc, "Class Distribution Breakdown (2,229 Total Records)", level=3, space_before=10, space_after=6)
    
    dist_table = doc.add_table(rows=8, cols=3)
    dist_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    dist_table.autofit = False
    set_table_borders(dist_table, color="CBD5E1", sz="4")
    
    dist_headers = ["Category Name", "Ticket Volume", "Percentage Share"]
    for c_idx, h_txt in enumerate(dist_headers):
        cell = dist_table.cell(0, c_idx)
        set_cell_background(cell, HEX_NAVY)
        set_cell_margins(cell, top=70, bottom=70, left=100, right=100)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx == 0 else WD_ALIGN_PARAGRAPH.RIGHT
        r = p.add_run(h_txt)
        r.font.name = 'Segoe UI'
        r.font.size = Pt(9)
        r.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        
    dist_rows = [
        ("Support general", "762 tickets", "34.19%"),
        ("Fileservice", "684 tickets", "30.69%"),
        ("Software", "222 tickets", "9.96%"),
        ("O365", "219 tickets", "9.83%"),
        ("Active Directory", "133 tickets", "5.97%"),
        ("Computer-Services", "106 tickets", "4.76%"),
        ("EOL (End of Life)", "103 tickets", "4.62%")
    ]
    
    dist_table.cell(0, 0).width = Inches(2.8)
    dist_table.cell(0, 1).width = Inches(1.8)
    dist_table.cell(0, 2).width = Inches(1.8)
    
    for r_idx, (cat, vol, pct) in enumerate(dist_rows, start=1):
        bg = HEX_BG_GRAY if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate([cat, vol, pct]):
            cell = dist_table.cell(r_idx, c_idx)
            cell.width = dist_table.cell(0, c_idx).width
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=60, bottom=60, left=100, right=100)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx == 0 else WD_ALIGN_PARAGRAPH.RIGHT
            r = p.add_run(val)
            r.font.name = 'Segoe UI'
            r.font.size = Pt(9)
            r.font.color.rgb = COLOR_DARK
            if c_idx == 0:
                r.bold = True
                
    add_styled_heading(doc, "Privacy & Anonymization", level=3, space_before=12, space_after=4)
    add_body_paragraph(doc, "The dataset has been pre-anonymized in full compliance with GDPR guidelines; all Personally Identifiable Information (PII) such as employee names, company identifiers, and location tokens have been sanitized with placeholder tags (e.g., [NAME], [COMPANY], [LOCATION], [TICKET ID]).")
    
    doc.add_page_break()
    
    # ---------------- SECTION 4: SUMMARY OF PROCEDURES ----------------
    add_styled_heading(doc, "4. Summary of Procedures", level=1, space_before=0, space_after=8)
    
    procedures = [
        ("Step 1: Environment Setup & Library Import",
         "The essential data science and machine learning libraries were loaded, including pandas and numpy for data manipulation, re for regular expression text cleaning, scikit-learn for feature extraction (TfidfVectorizer), model training (LogisticRegression), and evaluation metrics (accuracy_score, precision_score, recall_score, f1_score, classification_report, confusion_matrix), matplotlib and seaborn for visualization, joblib for model persistence, and streamlit for frontend deployment."),
        ("Step 2: Dataset Acquisition & Loading",
         "The Zenodo train and test splits (X_train.csv, X_test.csv, y_train.csv, y_test.csv) were downloaded, combined into a unified master dataset of 2,229 records, and saved as helpdesk_tickets.csv in the local data directory. The data was loaded into a Pandas DataFrame, and redundant duplicate index columns were dropped."),
        ("Step 3: Dataset Inspection & Structural Understanding",
         "Exploratory inspections verified column dimensions, data types, and initial sample records. The dataset showed an imbalance, with Support general and Fileservice representing the two highest volume categories (over 64% combined), while technical categories like EOL and Computer-Services represented smaller niche shares."),
        ("Step 4: Missing Value & Duplicate Check",
         "The dataset was verified for null values using .isnull().sum(). Zero missing values were found across the raw records. The duplicate columns generated during concatenation were pruned to ensure a clean feature space."),
        ("Step 5: Text Preprocessing & Cleaning",
         "Natural language text cleaning was implemented via a dedicated clean_text pipeline:\n• Conversion of all text to lowercase to ensure case-insensitivity.\n• Regular expression filtering (re.sub(r'[^\\w\\s]', ' ', text)) to eliminate punctuation, brackets, and extraneous special symbols.\n• Normalization of multiple consecutive whitespaces and trimming leading/trailing spaces.\n• Empty strings resulting from cleaning were filtered out to maintain data integrity."),
        ("Step 6: Stratified Train-Test Splitting",
         "The preprocessed dataset was split into an 80% training set (1,783 tickets) and a 20% test set (446 tickets) using train_test_split. Stratified sampling (stratify=y) with random_state=42 was applied to ensure that all 7 classes remained proportionally represented across both splits."),
        ("Step 7: Feature Extraction via TF-IDF Vectorization",
         "The text descriptions were converted into numerical vector representations using Scikit-Learn's TfidfVectorizer:\n• N-gram Range: Unigrams and bigrams (1, 2) to capture single keywords (e.g., 'password', 'vpn') as well as key phrases (e.g., 'file share', 'license expired').\n• Vocabulary Size: Capped at max_features=5000 to retain the top informative terms and prevent overfitting.\n• Stop Words: Built-in English stop words were eliminated to remove non-informative filler terms.\n• The vectorizer was fitted exclusively on the training corpus (fit_transform) and subsequently used to transform the held-out test corpus (transform)."),
        ("Step 8: Model Training (Multinomial Logistic Regression)",
         "A Multinomial Logistic Regression model was trained on the 5,000 TF-IDF features using LogisticRegression(max_iter=1000). Logistic Regression is well-suited for high-dimensional sparse text vectors due to its convexity, strong calibration, interpretability, and ability to output class posterior probabilities (predict_proba)."),
        ("Step 9: Model Evaluation & Metric Calculation",
         "Predictions were generated on the unseen 446 test samples. Comprehensive multi-class evaluation was performed calculating Overall Accuracy, Weighted Precision, Weighted Recall, Weighted F1-score, and per-class metrics. A confusion matrix was generated and exported as a high-resolution heatmap."),
        ("Step 10: Model Serialization & Web Application Deployment",
         "Both the trained LogisticRegression model and the fitted TfidfVectorizer were serialized to disk (model.pkl and tfidf.pkl) using joblib. A production-ready Streamlit application (app.py) was created, providing an interactive interface where users input real-world ticket descriptions and receive real-time class predictions and confidence percentages.")
    ]
    
    for title, desc in procedures[:5]:
        add_styled_heading(doc, title, level=3, space_before=10, space_after=3)
        add_body_paragraph(doc, desc, space_after=6)
        
    doc.add_page_break()
    
    for title, desc in procedures[5:]:
        add_styled_heading(doc, title, level=3, space_before=10, space_after=3)
        add_body_paragraph(doc, desc, space_after=6)
        
    doc.add_page_break()
    
    # ---------------- SECTION 5: EVALUATION AND RESULTS ----------------
    add_styled_heading(doc, "5. Evaluation and Results", level=1, space_before=0, space_after=8)
    
    add_styled_heading(doc, "5.1 Overall Performance Summary", level=2, space_before=8, space_after=4)
    add_body_paragraph(doc, "The classification model achieved the following performance metrics on the 446 held-out test samples:")
    
    eval_table = doc.add_table(rows=6, cols=3)
    eval_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    eval_table.autofit = False
    set_table_borders(eval_table, color="CBD5E1", sz="4")
    
    eval_headers = ["Metric Name", "Normalized Score", "Percentage"]
    for c_idx, h_txt in enumerate(eval_headers):
        cell = eval_table.cell(0, c_idx)
        set_cell_background(cell, HEX_NAVY)
        set_cell_margins(cell, top=70, bottom=70, left=120, right=120)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx == 0 else WD_ALIGN_PARAGRAPH.RIGHT
        r = p.add_run(h_txt)
        r.font.name = 'Segoe UI'
        r.font.size = Pt(9)
        r.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        
    eval_rows = [
        ("Accuracy", "0.8430", "84.30%"),
        ("Weighted Precision", "0.8654", "86.54%"),
        ("Weighted Recall", "0.8430", "84.30%"),
        ("Weighted F1-Score", "0.8316", "83.16%"),
        ("Macro Average F1", "0.7675", "76.75%")
    ]
    
    eval_table.cell(0, 0).width = Inches(2.6)
    eval_table.cell(0, 1).width = Inches(1.9)
    eval_table.cell(0, 2).width = Inches(1.9)
    
    for r_idx, (m_name, score, pct) in enumerate(eval_rows, start=1):
        bg = HEX_BG_GRAY if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate([m_name, score, pct]):
            cell = eval_table.cell(r_idx, c_idx)
            cell.width = eval_table.cell(0, c_idx).width
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=60, bottom=60, left=120, right=120)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx == 0 else WD_ALIGN_PARAGRAPH.RIGHT
            r = p.add_run(val)
            r.font.name = 'Segoe UI'
            r.font.size = Pt(9)
            r.bold = True
            r.font.color.rgb = COLOR_DARK
            
    add_styled_heading(doc, "5.2 Per-Class Classification Report", level=2, space_before=14, space_after=4)
    
    cls_table = doc.add_table(rows=9, cols=5)
    cls_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cls_table.autofit = False
    set_table_borders(cls_table, color="CBD5E1", sz="4")
    
    cls_headers = ["Category", "Precision", "Recall", "F1-Score", "Support (Test Records)"]
    for c_idx, h_txt in enumerate(cls_headers):
        cell = cls_table.cell(0, c_idx)
        set_cell_background(cell, HEX_NAVY)
        set_cell_margins(cell, top=70, bottom=70, left=80, right=80)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx == 0 else WD_ALIGN_PARAGRAPH.RIGHT
        r = p.add_run(h_txt)
        r.font.name = 'Segoe UI'
        r.font.size = Pt(8.5)
        r.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        
    cls_rows = [
        ("Active Directory", "1.0000", "0.2963", "0.4571", "27"),
        ("Computer-Services", "1.0000", "0.6190", "0.7647", "21"),
        ("EOL (End of Life)", "1.0000", "1.0000", "1.0000", "21"),
        ("Fileservice", "0.9848", "0.9489", "0.9665", "137"),
        ("O365", "0.7179", "0.6364", "0.6747", "44"),
        ("Software", "0.8667", "0.5909", "0.7027", "44"),
        ("Support general", "0.7389", "0.9868", "0.8451", "152"),
        ("Total / Weighted Avg", "0.8654", "0.8430", "0.8316", "446")
    ]
    
    cls_table.cell(0, 0).width = Inches(2.2)
    cls_table.cell(0, 1).width = Inches(1.0)
    cls_table.cell(0, 2).width = Inches(1.0)
    cls_table.cell(0, 3).width = Inches(1.0)
    cls_table.cell(0, 4).width = Inches(1.2)
    
    for r_idx, (cat, prec, rec, f1, sup) in enumerate(cls_rows, start=1):
        is_total = (r_idx == 8)
        bg = HEX_LIGHT_BLUE if is_total else (HEX_BG_GRAY if r_idx % 2 == 1 else "FFFFFF")
        for c_idx, val in enumerate([cat, prec, rec, f1, sup]):
            cell = cls_table.cell(r_idx, c_idx)
            cell.width = cls_table.cell(0, c_idx).width
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=55, bottom=55, left=80, right=80)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx == 0 else WD_ALIGN_PARAGRAPH.RIGHT
            r = p.add_run(val)
            r.font.name = 'Segoe UI'
            r.font.size = Pt(8.5)
            r.bold = is_total or (c_idx == 0)
            r.font.color.rgb = COLOR_DARK
            
    add_styled_heading(doc, "5.3 Interpretation of Results", level=2, space_before=14, space_after=6)
    add_bullet_point(doc, "1. Exceptional Accuracy on Structured Categories:", "The model attained a perfect F1-score of 1.00 (100%) on EOL and 0.97 (97%) on Fileservice, demonstrating that tickets related to hardware retirements and shared folder/drive access possess highly discriminative terminologies.")
    add_bullet_point(doc, "2. High Precision on Technical Categories:", "For technical categories (Active Directory, Computer-Services, and EOL), the model achieved 1.00 (100%) precision, indicating that whenever it predicts these categories, it is almost never wrong (zero false positives).")
    add_bullet_point(doc, "3. General Support Fallback:", "The recall for Support general is 98.68%, showing that general IT queries are reliably captured, although some ambiguous technical requests default into this catch-all category.")
    add_bullet_point(doc, "4. Operational Feasibility:", "With an overall accuracy of 84.30%, the system can automate more than 4 out of every 5 incoming routing decisions, reducing manual triage bottlenecks for IT support desks.")
    
    doc.add_page_break()
    
    # ---------------- SECTION 6: OUTPUT SCREENSHOTS ----------------
    add_styled_heading(doc, "6. Output Screenshots", level=1, space_before=0, space_after=6)
    add_body_paragraph(doc, "This section presents the visual outputs, performance confusion heatmaps, per-class comparison charts, and live interactive Streamlit application screens verifying end-to-end model training, evaluation, and real-time inference.", space_after=14)
    
    screenshots = [
        ("Figure 1: Distribution of IT Support Ticket Categories",
         "IT-Helpdesk-Ticket-Classifier/outputs/category_distribution.png",
         "Figure 1: Distribution of IT Support Ticket Categories in the Dataset (Zenodo 2,229 records).",
         "Horizontal bar chart illustrating the class distribution across the 7 categories: Support general (762), Fileservice (684), Software (222), O365 (219), Active Directory (133), Computer-Services (106), and EOL (103).",
         Inches(5.8)),
        ("Figure 2: Terminal Output of Model Training and Evaluation Pipeline",
         "IT-Helpdesk-Ticket-Classifier/outputs/terminal_training_output.png",
         "Figure 2: Execution Console Output showing Dataset Overview, Preprocessing, TF-IDF Feature Extraction, and Evaluation Metrics.",
         "Detailed console log recording the full lifecycle execution of train_model.py: dataset dimensions (2,229 rows), zero missing values, 80/20 stratified split (1,783 train / 446 test), 5,000 TF-IDF features, 84.30% Accuracy, 86.54% Precision, 84.30% Recall, 83.16% F1-score, and per-class classification report.",
         Inches(5.8)),
        ("Figure 3: Confusion Matrix of the Classification Model",
         "IT-Helpdesk-Ticket-Classifier/outputs/confusion_matrix.png",
         "Figure 3: Confusion Matrix Heatmap of the Logistic Regression Classifier.",
         "Seaborn heatmap illustrating true versus predicted classifications across the 446 test samples. Diagonal elements represent true positives (e.g., 150 correct for Support general, 130 correct for Fileservice, 21 correct for EOL).",
         Inches(5.0)),
        ("Figure 4: Per-Category Precision, Recall, and F1-Score Comparison",
         "IT-Helpdesk-Ticket-Classifier/outputs/per_category_metrics.png",
         "Figure 4: Per-Category Performance Metrics Comparison.",
         "Grouped bar chart comparing Precision, Recall, and F1-Score across all 7 ticket categories, highlighting strong precision across all classes and exceptional balance in Fileservice and EOL.",
         Inches(5.8)),
        ("Figure 5: Interactive Streamlit Web Application Interface",
         "IT-Helpdesk-Ticket-Classifier/outputs/streamlit_app_interface.png",
         "Figure 5: Streamlit Web Application Interface for IT Helpdesk Ticket Classification.",
         "User-facing web application interface showing the application header, descriptive overview, multi-line text input field, and example test ticket prompts.",
         Inches(5.8)),
        ("Figure 6: Real-Time Ticket Classification and Confidence Output",
         "IT-Helpdesk-Ticket-Classifier/outputs/streamlit_app_prediction.png",
         "Figure 6: Real-Time Prediction Output and Model Confidence Score.",
         "Demonstration of live ticket triage in the web dashboard:\n• Input Ticket: \"My computer is not connecting to the office network and intranet.\"\n• Predicted Category: Support general\n• Model Confidence Score: 31.65%",
         Inches(5.8))
    ]
    
    for idx, (fig_title, img_rel_path, caption, desc, img_width) in enumerate(screenshots):
        # Card table for each figure
        card_table = doc.add_table(rows=3, cols=1)
        card_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        card_table.autofit = False
        set_card_table_borders(card_table, color="CBD5E1", sz="6")
        
        # Row 0: Header
        c0 = card_table.cell(0, 0)
        c0.width = Inches(6.5)
        set_cell_background(c0, HEX_BG_GRAY)
        set_cell_margins(c0, top=70, bottom=70, left=120, right=120)
        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_before = Pt(0)
        p0.paragraph_format.space_after = Pt(0)
        r_bdg = p0.add_run("SCREENSHOT VERIFICATION  |  ")
        r_bdg.font.name = 'Segoe UI'
        r_bdg.font.size = Pt(8)
        r_bdg.bold = True
        r_bdg.font.color.rgb = COLOR_NAVY
        r_ttl = p0.add_run(fig_title)
        r_ttl.font.name = 'Segoe UI'
        r_ttl.font.size = Pt(9.5)
        r_ttl.bold = True
        r_ttl.font.color.rgb = COLOR_DARK
        
        # Row 1: Image + Caption
        c1 = card_table.cell(1, 0)
        c1.width = Inches(6.5)
        set_cell_background(c1, "FFFFFF")
        set_cell_margins(c1, top=100, bottom=80, left=100, right=100)
        p1 = c1.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p1.paragraph_format.space_before = Pt(0)
        p1.paragraph_format.space_after = Pt(6)
        
        full_img_path = os.path.join(WORKSPACE_DIR, img_rel_path.replace('/', os.sep))
        if os.path.exists(full_img_path):
            r1_img = p1.add_run()
            r1_img.add_picture(full_img_path, width=img_width)
            
        p_cap = c1.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(4)
        p_cap.paragraph_format.space_after = Pt(0)
        r_cap = p_cap.add_run(caption)
        r_cap.font.name = 'Segoe UI'
        r_cap.font.size = Pt(8.5)
        r_cap.italic = True
        r_cap.font.color.rgb = COLOR_MUTED
        
        # Row 2: Metadata / Description
        c2 = card_table.cell(2, 0)
        c2.width = Inches(6.5)
        set_cell_background(c2, HEX_BG_GRAY)
        set_cell_margins(c2, top=70, bottom=70, left=120, right=120)
        p2 = c2.paragraphs[0]
        p2.paragraph_format.space_before = Pt(0)
        p2.paragraph_format.space_after = Pt(2)
        r_path_lbl = p2.add_run("Asset Path: ")
        r_path_lbl.font.name = 'Segoe UI'
        r_path_lbl.font.size = Pt(8.5)
        r_path_lbl.bold = True
        r_path_lbl.font.color.rgb = COLOR_MUTED
        r_path_val = p2.add_run(img_rel_path)
        r_path_val.font.name = 'Consolas'
        r_path_val.font.size = Pt(8)
        r_path_val.font.color.rgb = COLOR_DARK
        
        p2_desc = c2.add_paragraph()
        p2_desc.paragraph_format.space_before = Pt(3)
        p2_desc.paragraph_format.space_after = Pt(0)
        r_desc_lbl = p2_desc.add_run("Technical Verification: ")
        r_desc_lbl.font.name = 'Segoe UI'
        r_desc_lbl.font.size = Pt(8.5)
        r_desc_lbl.bold = True
        r_desc_lbl.font.color.rgb = COLOR_MUTED
        r_desc_val = p2_desc.add_run(desc)
        r_desc_val.font.name = 'Segoe UI'
        r_desc_val.font.size = Pt(8.5)
        r_desc_val.font.color.rgb = COLOR_DARK
        
        # Page break after each figure except the last
        if idx < len(screenshots) - 1:
            doc.add_page_break()
            
    doc.add_page_break()
    
    # ---------------- SECTION 7: CODE ----------------
    add_styled_heading(doc, "7. Code", level=1, space_before=0, space_after=8)
    
    # 7.1 setup_data.py
    add_styled_heading(doc, "7.1 Dataset Setup Script (setup_data.py)", level=2, space_before=6, space_after=4)
    setup_py_path = os.path.join(WORKSPACE_DIR, 'setup_data.py')
    if os.path.exists(setup_py_path):
        with open(setup_py_path, 'r', encoding='utf-8') as f:
            add_code_block(doc, f.read())
            
    doc.add_page_break()
    
    # 7.2 train_model.py
    add_styled_heading(doc, "7.2 Model Training & Evaluation Script (train_model.py)", level=2, space_before=0, space_after=4)
    train_py_path = os.path.join(WORKSPACE_DIR, 'IT-Helpdesk-Ticket-Classifier/train_model.py')
    if os.path.exists(train_py_path):
        with open(train_py_path, 'r', encoding='utf-8') as f:
            add_code_block(doc, f.read())
            
    doc.add_page_break()
    
    # 7.3 app.py
    add_styled_heading(doc, "7.3 Streamlit Interactive Web Application (app.py)", level=2, space_before=0, space_after=4)
    app_py_path = os.path.join(WORKSPACE_DIR, 'IT-Helpdesk-Ticket-Classifier/app.py')
    if os.path.exists(app_py_path):
        with open(app_py_path, 'r', encoding='utf-8') as f:
            add_code_block(doc, f.read())
            
    doc.add_page_break()
    
    # ---------------- SECTION 8: CONCLUSION ----------------
    add_styled_heading(doc, "8. Conclusion", level=1, space_before=0, space_after=8)
    
    add_bullet_point(doc, "Summary of Major Findings:", "Automated text classification using NLP and Machine Learning provides a robust, scalable mechanism for categorizing IT support tickets. High-volume categories such as Fileservice and standard operational procedures exhibit distinctive lexical markers, enabling the model to classify them with near-perfect reliability (F1-score of 0.97 for Fileservice and 1.00 for EOL).")
    add_bullet_point(doc, "Model Performance:", "The Multinomial Logistic Regression model trained on 5,000 unigram and bigram TF-IDF features attained an overall classification accuracy of 84.30%, with a weighted precision of 86.54%, weighted recall of 84.30%, and weighted F1-score of 83.16% on unseen test tickets.")
    add_bullet_point(doc, "Problem Addressed & Real-World Value:", "Manual triage of IT support tickets is labor-intensive, error-prone, and causes response delays. By implementing this automated triage pipeline and deploying it via an interactive Streamlit web dashboard, tickets can be immediately categorized upon submission, slashing resolution latency, reducing human dispatch overhead, and streamlining ticket routing to specialized IT teams.")
    add_bullet_point(doc, "Future Scope & Enhancements:", "Future iterations can incorporate Transformer-based contextual embeddings (such as RoBERTa or BERT) to better distinguish subtle linguistic boundaries between Support general and Active Directory, as well as integrating the model directly with ticketing APIs such as Jira Service Management or ServiceNow.")
    
    out_file = os.path.join(WORKSPACE_DIR, filename)
    doc.save(out_file)
    print(f"Document saved: {out_file} (Size: {os.path.getsize(out_file):,} bytes)")
    return out_file

def main():
    print("Generating PROJECT_REPORT_with_certificate.docx...")
    generate_docx(include_certificate=True, filename="PROJECT_REPORT_with_certificate.docx")
    
    print("Generating PROJECT_REPORT.docx...")
    generate_docx(include_certificate=False, filename="PROJECT_REPORT.docx")
    
    print("All Word documents generated successfully!")

if __name__ == '__main__':
    main()
