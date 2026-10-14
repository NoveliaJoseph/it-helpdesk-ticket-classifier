"""
Comprehensive generator for PROJECT_REPORT.pdf and PROJECT_REPORT_with_certificate.pdf
Features:
- High-fidelity typography and layout designed for academic project submission
- Embeds all 6 project output screenshots in full native resolution via Base64 data URIs
- Pygments syntax highlighting for all Python scripts (setup_data.py, train_model.py, app.py)
- Standalone single-page Cover Page without running headers/footers
- Running headers and footers with page numbering on all content pages
- Zero awkward page breaks; each figure, table, and section formatted cleanly
- Standalone PROJECT_REPORT.pdf + Combined PROJECT_REPORT_with_certificate.pdf
"""
import os
import re
import base64
import pypdf
import markdown
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
from playwright.sync_api import sync_playwright

WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_image_base64(rel_path):
    """Reads an image from disk and encodes it as a base64 data URI."""
    full_path = os.path.join(WORKSPACE_DIR, rel_path.replace('/', os.sep))
    if not os.path.exists(full_path):
        print(f"Warning: Image not found at {full_path}")
        return ""
    with open(full_path, "rb") as f:
        data = f.read()
    ext = os.path.splitext(full_path)[1].lower().replace('.', '')
    if ext == 'jpg':
        ext = 'jpeg'
    encoded = base64.b64encode(data).decode('utf-8')
    return f"data:image/{ext};base64,{encoded}"

def highlight_code_blocks(md_text):
    """Replaces python code blocks with Pygments syntax highlighted HTML."""
    formatter = HtmlFormatter(style='friendly', noclasses=True, font_size='7.8pt', lineos=False)
    
    def replace_code(match):
        code = match.group(1).strip()
        highlighted = highlight(code, PythonLexer(), formatter)
        return f"\n<div class='code-block-wrapper'>{highlighted}</div>\n"
        
    pattern = r'```python\r?\n(.*?)```'
    return re.sub(pattern, replace_code, md_text, flags=re.DOTALL)

def process_figures_and_images(md_text):
    """
    Transforms markdown figure structures in Section 6 into dedicated,
    clean figure cards with optimal pagination.
    Figure 1 appears on the Section 6 intro page, while Figures 2-6
    each have a dedicated page.
    """
    figure_pattern = re.compile(
        r'### (Figure (\d+):[^\n]+)\r?\n+'
        r'!\[([^\]]*)\]\((IT-Helpdesk-Ticket-Classifier/outputs/[^\)]+)\)\r?\n+'
        r'\* \*\*Caption:\*\* ([^\n]+)\r?\n+'
        r'\* \*\*File Location:\*\* `([^`]+)`\r?\n+'
        r'\* \*\*Description:\*\* ([^\n]+(?:\r?\n(?:\s+-\s+[^\n]+))*)(?=\r?\n\r?\n---|\r?\n\r?\n##|\Z)',
        re.MULTILINE
    )

    def figure_replacer(match):
        full_fig_title = match.group(1).strip()
        fig_num = int(match.group(2))
        alt_text = match.group(3).strip()
        img_rel_path = match.group(4).strip()
        caption = match.group(5).strip()
        file_loc = match.group(6).strip()
        desc = match.group(7).strip()
        
        # Format description list items cleanly
        formatted_desc_lines = []
        for line in desc.splitlines():
            line_str = line.strip()
            if line_str.startswith('- ') or line_str.startswith('* '):
                formatted_desc_lines.append(f"<li class='desc-bullet'>{line_str[2:]}</li>")
            else:
                formatted_desc_lines.append(f"<p class='desc-p'>{line_str}</p>")
        desc_html = "".join(formatted_desc_lines)
        
        b64_img = get_image_base64(img_rel_path)
        
        # Figure 1 stays with Section 6 heading; Figures 2-6 start on fresh pages
        page_break_class = "figure-break" if fig_num > 1 else "figure-first"
        
        return f"""
<div class="figure-page-wrapper {page_break_class}">
    <div class="figure-card">
        <div class="figure-card-header">
            <span class="figure-badge">Screenshot Verification</span>
            <span class="figure-title-text">{full_fig_title}</span>
        </div>
        <div class="figure-image-container">
            <img src="{b64_img}" alt="{alt_text}" class="figure-img" />
        </div>
        <div class="figure-caption-box">
            <div class="caption-text">{caption}</div>
        </div>
        <div class="figure-info-panel">
            <div class="file-path-row">
                <span class="panel-label">Asset Path:</span>
                <code class="path-code">{file_loc}</code>
            </div>
            <div class="description-block">
                <span class="panel-label">Technical Significance &amp; Verification:</span>
                <div class="desc-content">{desc_html}</div>
            </div>
        </div>
    </div>
</div>
"""

    processed_md = figure_pattern.sub(figure_replacer, md_text)
    
    # Fallback for any standalone image markdown
    def fallback_img(match):
        alt = match.group(1)
        rel_path = match.group(2)
        b64 = get_image_base64(rel_path)
        return f'<div class="fallback-img-box"><img src="{b64}" alt="{alt}" class="standalone-img" /></div>'
        
    processed_md = re.sub(r'!\[([^\]]*)\]\((IT-Helpdesk-Ticket-Classifier/outputs/[^\)]+)\)', fallback_img, processed_md)
    return processed_md

def build_cover_html():
    """Generates the HTML for the standalone academic cover page."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Cover Page - IT Helpdesk Support Ticket Classifier</title>
    <style>
        @page {
            size: A4 portrait;
            margin: 0;
        }

        * {
            box-sizing: border-box;
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
        }

        body {
            margin: 0;
            padding: 12mm;
            width: 210mm;
            height: 297mm;
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
            background-color: #ffffff;
            color: #0f172a;
        }

        .cover-outer-frame {
            width: 100%;
            height: 100%;
            border: 3px double #1e3a8a;
            outline: 1px solid #94a3b8;
            outline-offset: -7px;
            padding: 24px 28px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            align-items: center;
            text-align: center;
            background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
        }

        .college-header {
            width: 100%;
            padding-bottom: 12px;
        }

        .dept-title {
            font-size: 11pt;
            font-weight: 700;
            color: #1e3a8a;
            letter-spacing: 2px;
            text-transform: uppercase;
            margin-bottom: 4px;
        }

        .college-title {
            font-size: 17pt;
            font-weight: 800;
            color: #0f172a;
            letter-spacing: 0.8px;
            text-transform: uppercase;
            margin-bottom: 2px;
        }

        .autonomous-text {
            font-size: 10.5pt;
            font-weight: 600;
            color: #475569;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            margin-bottom: 4px;
        }

        .location-text {
            font-size: 9.5pt;
            color: #64748b;
            font-weight: 500;
            margin-bottom: 14px;
        }

        .programme-box {
            display: inline-block;
            background: #eff6ff;
            border: 1px solid #bfdbfe;
            padding: 6px 20px;
            border-radius: 6px;
        }

        .programme-title {
            font-size: 12.5pt;
            font-weight: 700;
            color: #1e40af;
            letter-spacing: 0.5px;
        }

        .batch-text {
            font-size: 9.5pt;
            font-weight: 600;
            color: #475569;
            margin-top: 2px;
        }

        .divider-bar {
            width: 85%;
            height: 3px;
            background: linear-gradient(90deg, #1e3a8a, #3b82f6, #1e3a8a);
            border-radius: 2px;
            margin: 10px 0;
        }

        .report-header-section {
            width: 100%;
            padding: 4px 0;
        }

        .course-info {
            font-size: 11pt;
            font-weight: 700;
            color: #0284c7;
            letter-spacing: 1px;
            text-transform: uppercase;
            margin-bottom: 8px;
        }

        .badge-pill {
            display: inline-block;
            background-color: #1e3a8a;
            color: #ffffff;
            font-size: 9pt;
            font-weight: 700;
            letter-spacing: 2px;
            padding: 4px 16px;
            border-radius: 20px;
            text-transform: uppercase;
            margin-bottom: 14px;
        }

        .project-title {
            font-size: 21pt;
            font-weight: 800;
            color: #0f172a;
            line-height: 1.25;
            margin: 0 0 8px 0;
        }

        .project-subtitle {
            font-size: 11.5pt;
            font-weight: 500;
            color: #475569;
            max-width: 580px;
            margin: 0 auto;
            line-height: 1.4;
        }

        .metadata-card {
            width: 92%;
            background: #ffffff;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05);
            overflow: hidden;
            margin: 8px 0;
        }

        .metadata-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 9.5pt;
        }

        .metadata-table tr {
            border-bottom: 1px solid #f1f5f9;
        }

        .metadata-table tr:last-child {
            border-bottom: none;
        }

        .meta-label {
            width: 38%;
            padding: 6.5px 14px;
            font-weight: 600;
            color: #475569;
            text-align: right;
            background: #f8fafc;
            border-right: 1px solid #e2e8f0;
        }

        .meta-val {
            width: 62%;
            padding: 6.5px 14px;
            font-weight: 500;
            color: #0f172a;
            text-align: left;
        }

        .name-highlight {
            font-size: 11pt;
            font-weight: 800;
            color: #1e3a8a;
            letter-spacing: 0.5px;
        }

        .cover-footer {
            width: 100%;
            padding-top: 8px;
        }

        .submission-text {
            font-size: 8.5pt;
            font-style: italic;
            color: #64748b;
            margin-bottom: 6px;
        }

        .submission-date {
            font-size: 10pt;
            font-weight: 700;
            color: #0f172a;
            letter-spacing: 1.5px;
        }
    </style>
</head>
<body>
    <div class="cover-outer-frame">
        <div class="college-header">
            <div class="dept-title">Department of Computer Science</div>
            <div class="college-title">Rajagiri College of Social Sciences</div>
            <div class="autonomous-text">(Autonomous)</div>
            <div class="location-text">Kalamassery, Kochi – 683 104, Kerala</div>
            <div class="programme-box">
                <div class="programme-title">Master of Computer Applications (MCA)</div>
                <div class="batch-text">Academic Batch: 2025 – 2027</div>
            </div>
        </div>

        <div class="divider-bar"></div>

        <div class="report-header-section">
            <div class="course-info">MCA306: Data Analytics Using Python</div>
            <div class="badge-pill">Mini Project Report</div>
            <h1 class="project-title">IT Helpdesk Support Ticket Classifier</h1>
            <div class="project-subtitle">Automating IT Support Routing &amp; Triage with Natural Language Processing and Supervised Machine Learning</div>
        </div>

        <div class="metadata-card">
            <table class="metadata-table">
                <tr>
                    <td class="meta-label">Candidate Name:</td>
                    <td class="meta-val name-highlight">NOVELIA JOSEPH</td>
                </tr>
                <tr>
                    <td class="meta-label">Register Number:</td>
                    <td class="meta-val"><strong>25204046</strong></td>
                </tr>
                <tr>
                    <td class="meta-label">Roll Number:</td>
                    <td class="meta-val"><strong>46</strong></td>
                </tr>
                <tr>
                    <td class="meta-label">Semester / Year:</td>
                    <td class="meta-val">Semester III (Third Semester) / 2026</td>
                </tr>
                <tr>
                    <td class="meta-label">Core Domain:</td>
                    <td class="meta-val">Machine Learning &amp; Natural Language Processing (NLP)</td>
                </tr>
                <tr>
                    <td class="meta-label">Model Architecture:</td>
                    <td class="meta-val">Multinomial Logistic Regression + TF-IDF Vectorization</td>
                </tr>
                <tr>
                    <td class="meta-label">Web Deployment:</td>
                    <td class="meta-val">Streamlit Interactive Dashboard</td>
                </tr>
            </table>
        </div>

        <div class="divider-bar"></div>

        <div class="cover-footer">
            <div class="submission-text">Submitted in partial fulfillment of the requirements for the continuous evaluation of MCA306 Data Analytics Using Python</div>
            <div class="submission-date">OCTOBER 2026</div>
        </div>
    </div>
</body>
</html>"""

def build_content_html():
    """Generates the HTML for all content pages of the project report."""
    with open(os.path.join(WORKSPACE_DIR, 'PROJECT_REPORT.md'), 'r', encoding='utf-8') as f:
        raw_md = f.read()

    # Pre-process figures and images
    processed_md = process_figures_and_images(raw_md)
    
    # Pre-process python code blocks with Pygments
    processed_md = highlight_code_blocks(processed_md)
    
    # Convert markdown to HTML
    html_body = markdown.markdown(
        processed_md,
        extensions=['tables', 'attr_list', 'def_list', 'nl2br']
    )
    
    # Custom post-processing for Section 1 metadata grid
    sec1_replacement = """
<div class="project-info-grid">
    <div class="info-cell">
        <span class="info-label">Candidate Name</span>
        <span class="info-value">Novelia Joseph</span>
    </div>
    <div class="info-cell">
        <span class="info-label">Register Number</span>
        <span class="info-value">25204046</span>
    </div>
    <div class="info-cell">
        <span class="info-label">Class Roll Number</span>
        <span class="info-value">46</span>
    </div>
    <div class="info-cell">
        <span class="info-label">Degree Programme</span>
        <span class="info-value">MCA (2025–2027)</span>
    </div>
    <div class="info-cell">
        <span class="info-label">Project Domain</span>
        <span class="info-value">Machine Learning &amp; NLP</span>
    </div>
    <div class="info-cell">
        <span class="info-label">Deployment Framework</span>
        <span class="info-value">Streamlit Web Application</span>
    </div>
</div>
"""
    html_body = re.sub(
        r'<ul>\s*<li><strong>Student Name:</strong>.*?</ul>',
        sec1_replacement,
        html_body,
        flags=re.DOTALL
    )

    # Insert precise page breaks before major logical divisions
    # 1. Section 3 starts on its own fresh page
    html_body = html_body.replace('<h2>3. Description of the Dataset</h2>', '<div class="section-break"></div><h2>3. Description of the Dataset</h2>')
    
    # 2. Section 4 (Procedures) starts on its own page
    html_body = html_body.replace('<h2>4. Summary of Procedures</h2>', '<div class="section-break"></div><h2>4. Summary of Procedures</h2>')
    html_body = html_body.replace('<h3>Step 6: Stratified Train-Test Splitting</h3>', '<div class="section-break"></div><h3>Step 6: Stratified Train-Test Splitting</h3>')
    
    # 3. Section 5 (Evaluation) starts on its own page
    html_body = html_body.replace('<h2>5. Evaluation and Results</h2>', '<div class="section-break"></div><h2>5. Evaluation and Results</h2>')
    
    # 4. Section 6 (Output Screenshots) starts on its own page with Section intro
    sec6_replacement = """
<div class="section-break"></div>
<h2>6. Output Screenshots</h2>
<p class="section-intro">This section presents the visual outputs, performance confusion heatmaps, per-class comparison charts, and live interactive Streamlit application screens verifying end-to-end model training, evaluation, and real-time inference.</p>
"""
    html_body = html_body.replace('<h2>6. Output Screenshots</h2>', sec6_replacement)
    
    # 5. Section 7 (Code) starts on its own page
    html_body = html_body.replace('<h2>7. Code</h2>', '<div class="section-break"></div><h2>7. Code</h2>')
    html_body = html_body.replace('<h3>7.2 Model Training', '<div class="section-break"></div><h3>7.2 Model Training')
    html_body = html_body.replace('<h3>7.3 Streamlit Interactive', '<div class="section-break"></div><h3>7.3 Streamlit Interactive')
    
    # 6. Section 8 (Conclusion) starts on its own page
    html_body = html_body.replace('<h2>8. Conclusion</h2>', '<div class="section-break"></div><h2>8. Conclusion</h2>')

    # Add code block header badges
    html_body = html_body.replace(
        '<h3>7.1 Dataset Setup Script (<code>setup_data.py</code>)</h3>',
        '<h3>7.1 Dataset Setup Script</h3><div class="script-badge"><code>setup_data.py</code> — Zenodo Data Acquisition &amp; Preprocessing Pipeline</div>'
    )
    html_body = html_body.replace(
        '<h3>7.2 Model Training, Feature Extraction, &amp; Evaluation Script (<code>train_model.py</code>)</h3>',
        '<h3>7.2 Model Training, Feature Extraction, &amp; Evaluation Script</h3><div class="script-badge"><code>train_model.py</code> — Text Vectorization, Model Training &amp; Evaluation Metrics</div>'
    )
    html_body = html_body.replace(
        '<h3>7.3 Streamlit Interactive Web Application (<code>app.py</code>)</h3>',
        '<h3>7.3 Streamlit Interactive Web Application</h3><div class="script-badge"><code>app.py</code> — Real-Time Inference Web Dashboard</div>'
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Project Report - IT Helpdesk Support Ticket Classifier</title>
    <style>
        @page {{
            size: A4 portrait;
            margin: 20mm 15mm 20mm 15mm;
        }}

        * {{
            box-sizing: border-box;
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
        }}

        body {{
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
            font-size: 10pt;
            line-height: 1.52;
            color: #1e293b;
            background-color: #ffffff;
            margin: 0;
            padding: 0;
        }}

        .section-break {{
            page-break-before: always;
            break-before: page;
        }}

        h1 {{
            font-size: 18pt;
            font-weight: 800;
            color: #0f172a;
            border-bottom: 2.5px solid #1e3a8a;
            padding-bottom: 6px;
            margin-top: 0;
            margin-bottom: 14px;
        }}

        h2 {{
            font-size: 13.5pt;
            font-weight: 700;
            color: #1e3a8a;
            border-bottom: 1.5px solid #93c5fd;
            padding-bottom: 4px;
            margin-top: 18px;
            margin-bottom: 10px;
            page-break-after: avoid;
            break-after: avoid;
        }}

        h3 {{
            font-size: 11pt;
            font-weight: 600;
            color: #0f172a;
            margin-top: 14px;
            margin-bottom: 6px;
            page-break-after: avoid;
            break-after: avoid;
        }}

        p, li {{
            font-size: 9.8pt;
            line-height: 1.52;
            color: #334155;
            margin-bottom: 6px;
        }}

        ul, ol {{
            margin-top: 4px;
            margin-bottom: 10px;
            padding-left: 22px;
        }}

        li {{
            margin-bottom: 4px;
        }}

        hr {{
            border: 0;
            height: 1px;
            background: #e2e8f0;
            margin: 16px 0;
        }}

        code {{
            font-family: 'Consolas', 'Courier New', monospace;
            background-color: #f1f5f9;
            color: #0f172a;
            padding: 1.5px 5px;
            border-radius: 4px;
            font-size: 8.8pt;
            border: 1px solid #e2e8f0;
        }}

        .section-intro {{
            font-size: 9.5pt;
            color: #475569;
            margin-bottom: 12px;
            font-style: italic;
        }}

        /* Project Info Grid in Section 1 */
        .project-info-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin: 12px 0 16px 0;
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 12px 14px;
        }}

        .info-cell {{
            display: flex;
            flex-direction: column;
            padding: 3px 6px;
        }}

        .info-label {{
            font-size: 8pt;
            font-weight: 600;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .info-value {{
            font-size: 10pt;
            font-weight: 700;
            color: #0f172a;
            margin-top: 2px;
        }}

        /* Table Styling */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0 14px 0;
            font-size: 8.8pt;
            page-break-inside: avoid;
            break-inside: avoid;
            border-radius: 6px;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        }}

        thead th {{
            background-color: #1e3a8a;
            color: #ffffff;
            font-weight: 600;
            text-align: left;
            padding: 6.5px 9px;
            border: 1px solid #1e3a8a;
        }}

        tbody td {{
            padding: 5.5px 9px;
            border: 1px solid #e2e8f0;
            color: #334155;
        }}

        tbody tr:nth-child(even) {{
            background-color: #f8fafc;
        }}

        /* ================= FIGURE CARDS (SECTION 6) ================= */
        .figure-page-wrapper {{
            page-break-inside: avoid;
            break-inside: avoid;
            margin-bottom: 14px;
        }}

        .figure-page-wrapper.figure-break {{
            page-break-before: always;
            break-before: page;
            padding-top: 4px;
        }}

        .figure-card {{
            background: #ffffff;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(15, 23, 42, 0.06);
        }}

        .figure-card-header {{
            background: #f8fafc;
            border-bottom: 1px solid #e2e8f0;
            padding: 8px 14px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}

        .figure-badge {{
            background: #1e3a8a;
            color: #ffffff;
            font-size: 7.5pt;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            padding: 2.5px 8px;
            border-radius: 4px;
        }}

        .figure-title-text {{
            font-size: 9.8pt;
            font-weight: 700;
            color: #0f172a;
        }}

        .figure-image-container {{
            text-align: center;
            padding: 10px 14px 6px 14px;
            background: #ffffff;
        }}

        .figure-img {{
            max-width: 96%;
            max-height: 460px;
            height: auto;
            border: 1px solid #cbd5e1;
            border-radius: 5px;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
            display: inline-block;
        }}

        .figure-caption-box {{
            padding: 5px 14px 6px 14px;
            text-align: center;
            border-bottom: 1px solid #f1f5f9;
        }}

        .caption-text {{
            font-size: 8.8pt;
            font-style: italic;
            font-weight: 600;
            color: #475569;
        }}

        .figure-info-panel {{
            background: #f8fafc;
            padding: 8px 14px;
            font-size: 8.6pt;
            color: #475569;
            line-height: 1.45;
        }}

        .file-path-row {{
            margin-bottom: 4px;
        }}

        .panel-label {{
            font-weight: 700;
            color: #334155;
            margin-right: 6px;
        }}

        .path-code {{
            font-size: 8.2pt;
        }}

        .desc-content {{
            margin-top: 3px;
            color: #334155;
        }}

        .desc-bullet {{
            margin-bottom: 3px;
        }}

        .desc-p {{
            margin-bottom: 4px;
        }}

        /* ================= CODE BLOCKS (SECTION 7) ================= */
        .script-badge {{
            display: inline-block;
            background: #f1f5f9;
            border-left: 3px solid #1e3a8a;
            padding: 3px 10px;
            font-size: 8.5pt;
            color: #475569;
            border-radius: 0 4px 4px 0;
            margin-bottom: 6px;
        }}

        .code-block-wrapper {{
            margin: 6px 0 14px 0;
            border: 1px solid #cbd5e1;
            border-radius: 6px;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
            background: #ffffff;
            page-break-inside: auto;
            break-inside: auto;
        }}

        .code-block-wrapper pre {{
            margin: 0;
            padding: 8px 12px;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 7.7pt;
            line-height: 1.34;
            background-color: #fafbfc;
            overflow-x: auto;
            white-space: pre-wrap;
            word-break: break-all;
        }}
    </style>
</head>
<body>
    <div class="content-container">
        {html_body}
    </div>
</body>
</html>"""

def convert_to_pdf():
    # 1. Generate Cover HTML & Render Cover PDF
    cover_html = build_cover_html()
    temp_cover_html = os.path.join(WORKSPACE_DIR, 'temp_cover.html')
    temp_cover_pdf = os.path.join(WORKSPACE_DIR, 'temp_cover.pdf')
    with open(temp_cover_html, 'w', encoding='utf-8') as f:
        f.write(cover_html)

    # 2. Generate Content HTML & Render Content PDF
    content_html = build_content_html()
    temp_content_html = os.path.join(WORKSPACE_DIR, 'temp_content.html')
    temp_content_pdf = os.path.join(WORKSPACE_DIR, 'temp_content.pdf')
    with open(temp_content_html, 'w', encoding='utf-8') as f:
        f.write(content_html)

    header_template = """
    <div style="font-size: 8pt; width: 100%; display: flex; justify-content: space-between; padding: 0 15mm; color: #94a3b8; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; border-bottom: 0.5px solid #e2e8f0; padding-bottom: 3px;">
        <span>IT Helpdesk Support Ticket Classifier — Project Report</span>
        <span>Novelia Joseph (Reg No: 25204046)</span>
    </div>
    """
    
    footer_template = """
    <div style="font-size: 8pt; width: 100%; display: flex; justify-content: space-between; padding: 0 15mm; color: #94a3b8; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; border-top: 0.5px solid #e2e8f0; padding-top: 3px;">
        <span>Rajagiri College of Social Sciences (Autonomous)</span>
        <span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span>
    </div>
    """

    print("Launching Microsoft Edge via Playwright...")
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='msedge')
        
        # Render Cover Page
        cover_page = browser.new_page()
        cover_page.goto(f"file:///{temp_cover_html.replace(os.sep, '/')}", wait_until='networkidle')
        cover_page.pdf(
            path=temp_cover_pdf,
            format='A4',
            print_background=True,
            margin={'top': '0mm', 'bottom': '0mm', 'left': '0mm', 'right': '0mm'},
            display_header_footer=False
        )
        cover_page.close()
        print("Cover page PDF generated.")

        # Render Content Pages
        content_page = browser.new_page()
        content_page.goto(f"file:///{temp_content_html.replace(os.sep, '/')}", wait_until='networkidle')
        content_page.pdf(
            path=temp_content_pdf,
            format='A4',
            print_background=True,
            margin={'top': '18mm', 'bottom': '18mm', 'left': '14mm', 'right': '14mm'},
            display_header_footer=True,
            header_template=header_template,
            footer_template=footer_template
        )
        content_page.close()
        print("Content pages PDF generated.")
        
        browser.close()

    # 3. Assemble PROJECT_REPORT.pdf (Cover + Content)
    pdf_output_path = os.path.join(WORKSPACE_DIR, 'PROJECT_REPORT.pdf')
    cover_reader = pypdf.PdfReader(temp_cover_pdf)
    content_reader = pypdf.PdfReader(temp_content_pdf)
    
    writer = pypdf.PdfWriter()
    for page in cover_reader.pages:
        writer.add_page(page)
    for page in content_reader.pages:
        writer.add_page(page)

    with open(pdf_output_path, 'wb') as f_out:
        writer.write(f_out)
        
    print(f"Stand-alone PROJECT_REPORT.pdf created: {pdf_output_path} ({len(writer.pages)} pages, {os.path.getsize(pdf_output_path):,} bytes)")

    # 4. Assemble PROJECT_REPORT_with_certificate.pdf (Cover + Certificate + Content)
    cert_pdf_path = os.path.join(WORKSPACE_DIR, 'DAUP_Lab Record Certificate Page(novelia).pdf')
    combined_pdf_path = os.path.join(WORKSPACE_DIR, 'PROJECT_REPORT_with_certificate.pdf')
    
    if os.path.exists(cert_pdf_path):
        cert_reader = pypdf.PdfReader(cert_pdf_path)
        combined_writer = pypdf.PdfWriter()
        
        # Cover page
        for page in cover_reader.pages:
            combined_writer.add_page(page)
            
        # Official Certificate (Page 1)
        combined_writer.add_page(cert_reader.pages[1])
        
        # Content pages
        for page in content_reader.pages:
            combined_writer.add_page(page)
            
        with open(combined_pdf_path, 'wb') as f_out:
            combined_writer.write(f_out)
            
        print(f"Combined PROJECT_REPORT_with_certificate.pdf created: {combined_pdf_path} ({len(combined_writer.pages)} pages, {os.path.getsize(combined_pdf_path):,} bytes)")

    # Clean up temporary artifacts
    for f in [temp_cover_html, temp_cover_pdf, temp_content_html, temp_content_pdf]:
        if os.path.exists(f):
            os.remove(f)

    print("Generation completed successfully!")

if __name__ == '__main__':
    convert_to_pdf()
