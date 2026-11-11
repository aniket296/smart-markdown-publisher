"""Print typography theme registry returning CSS compatible with PyMuPDF fitz.Story."""

from src.models.print_profile import ThemeId


def get_theme_css(theme: ThemeId, base_font_size: int = 11) -> str:
    """Return complete, print-tuned CSS rules compatible with fitz.Story HTML rendering."""
    font_size = max(8, min(base_font_size, 18))
    code_size = max(7, font_size - 1)
    small_size = max(7, font_size - 2)

    common_rules = f"""
/* Common print elements & callout styling */
pre {{
    background-color: #F1F5F9;
    border: 1pt solid #CBD5E1;
    padding: 8pt 10pt;
    margin: 8pt 0 10pt 0;
    font-family: Courier, monospace;
    font-size: {code_size}pt;
    line-height: 1.35;
    white-space: pre-wrap;
    word-wrap: break-word;
}}

code {{
    font-family: Courier, monospace;
    font-size: {code_size}pt;
    background-color: #F1F5F9;
    padding: 1pt 3pt;
}}

pre code {{
    background-color: transparent;
    padding: 0;
}}

table {{
    width: 100%;
    border-collapse: collapse;
    margin: 10pt 0 12pt 0;
    font-size: {code_size}pt;
}}

th {{
    background-color: #E2E8F0;
    color: #0F172A;
    font-weight: bold;
    text-align: left;
    padding: 6pt 8pt;
    border: 0.75pt solid #94A3B8;
}}

td {{
    padding: 5pt 8pt;
    border: 0.5pt solid #CBD5E1;
    vertical-align: top;
}}

tr:nth-child(even) td {{
    background-color: #F8FAFC;
}}

blockquote {{
    border-left: 3pt solid #64748B;
    background-color: #F8FAFC;
    margin: 8pt 0;
    padding: 6pt 10pt;
    color: #334155;
}}

hr {{
    border: none;
    border-top: 1pt solid #CBD5E1;
    margin: 14pt 0;
}}

img {{
    max-width: 100%;
    height: auto;
}}

.callout {{
    border-left: 4pt solid #0D9488;
    background-color: #F0FDFA;
    padding: 8pt 10pt;
    margin: 10pt 0;
}}

.callout-title {{
    font-weight: bold;
    font-size: {code_size}pt;
    margin: 0 0 4pt 0;
    letter-spacing: 0.5pt;
}}

.callout-note {{
    border-left: 4pt solid #0284C7;
    background-color: #F0F9FF;
}}
.callout-note .callout-title {{
    color: #0369A1;
}}

.callout-tip {{
    border-left: 4pt solid #0D9488;
    background-color: #F0FDFA;
}}
.callout-tip .callout-title {{
    color: #0F766E;
}}

.callout-important {{
    border-left: 4pt solid #7C3AED;
    background-color: #F5F3FF;
}}
.callout-important .callout-title {{
    color: #6D28D9;
}}

.callout-warning {{
    border-left: 4pt solid #D97706;
    background-color: #FFFBEB;
}}
.callout-warning .callout-title {{
    color: #B45309;
}}

.callout-caution {{
    border-left: 4pt solid #DC2626;
    background-color: #FEF2F2;
}}
.callout-caution .callout-title {{
    color: #B91C1C;
}}

.toc-container {{
    background-color: #F8FAFC;
    border: 1pt solid #CBD5E1;
    padding: 10pt 14pt;
    margin-bottom: 16pt;
}}

.toc-heading {{
    font-size: {font_size + 3}pt;
    font-weight: bold;
    color: #0F172A;
    margin: 0 0 8pt 0;
    border-bottom: 1pt solid #CBD5E1;
    padding-bottom: 4pt;
}}

.toc-list {{
    margin: 4pt 0;
    padding-left: 16pt;
    font-size: {code_size}pt;
}}
"""

    if theme == ThemeId.ACADEMIC:
        theme_specific = f"""
/* Theme: ACADEMIC - Serif typography, justified paragraphs, centered classic headings */
body {{
    font-family: Times, "Times New Roman", Georgia, serif;
    font-size: {font_size}pt;
    line-height: 1.55;
    color: #111827;
    text-align: justify;
}}

p {{
    margin: 0 0 8pt 0;
    text-align: justify;
}}

h1 {{
    font-family: Times, "Times New Roman", Georgia, serif;
    font-size: {font_size + 8}pt;
    font-weight: bold;
    text-align: center;
    color: #0F172A;
    margin: 16pt 0 10pt 0;
    border-bottom: 1pt solid #334155;
    padding-bottom: 4pt;
}}

h2 {{
    font-family: Times, "Times New Roman", Georgia, serif;
    font-size: {font_size + 4}pt;
    font-weight: bold;
    color: #1E293B;
    margin: 14pt 0 6pt 0;
}}

h3, h4, h5, h6 {{
    font-family: Times, "Times New Roman", Georgia, serif;
    font-size: {font_size + 1}pt;
    font-weight: bold;
    font-style: italic;
    color: #334155;
    margin: 10pt 0 4pt 0;
}}

th {{
    background-color: #F1F5F9;
    border-top: 1.5pt solid #0F172A;
    border-bottom: 1pt solid #0F172A;
    border-left: none;
    border-right: none;
}}

td {{
    border-left: none;
    border-right: none;
    border-bottom: 0.5pt solid #CBD5E1;
}}
"""
    elif theme == ThemeId.EXECUTIVE:
        theme_specific = f"""
/* Theme: EXECUTIVE - High-contrast navy headings, generous line-height, modern whitepaper spacing */
body {{
    font-family: Helvetica, Arial, "Segoe UI", sans-serif;
    font-size: {font_size}pt;
    line-height: 1.65;
    color: #1E293B;
}}

p {{
    margin: 0 0 10pt 0;
}}

h1 {{
    font-family: Helvetica, Arial, sans-serif;
    font-size: {font_size + 9}pt;
    font-weight: bold;
    color: #0F172A;
    margin: 18pt 0 10pt 0;
    border-bottom: 2pt solid #1E3A8A;
    padding-bottom: 5pt;
}}

h2 {{
    font-family: Helvetica, Arial, sans-serif;
    font-size: {font_size + 5}pt;
    font-weight: bold;
    color: #1E3A8A;
    margin: 14pt 0 7pt 0;
}}

h3, h4, h5, h6 {{
    font-family: Helvetica, Arial, sans-serif;
    font-size: {font_size + 2}pt;
    font-weight: bold;
    color: #0D9488;
    margin: 11pt 0 5pt 0;
}}

blockquote {{
    border-left: 4pt solid #1E3A8A;
    background-color: #EFF6FF;
    color: #1E3A8A;
    font-style: italic;
}}

th {{
    background-color: #1E3A8A;
    color: #FFFFFF;
    border-color: #1E3A8A;
}}
"""
    elif theme == ThemeId.COMPACT:
        compact_font = max(8, font_size - 1)
        theme_specific = f"""
/* Theme: COMPACT - Tight vertical spacing, dense layout for study guides and exam handouts */
body {{
    font-family: Helvetica, Arial, "Segoe UI", sans-serif;
    font-size: {compact_font}pt;
    line-height: 1.25;
    color: #0F172A;
}}

p {{
    margin: 0 0 4pt 0;
}}

ul, ol {{
    margin: 3pt 0 5pt 0;
    padding-left: 14pt;
}}

li {{
    margin-bottom: 2pt;
}}

h1 {{
    font-family: Helvetica, Arial, sans-serif;
    font-size: {compact_font + 5}pt;
    font-weight: bold;
    color: #0F172A;
    margin: 8pt 0 4pt 0;
    border-bottom: 1pt solid #64748B;
    padding-bottom: 2pt;
}}

h2 {{
    font-family: Helvetica, Arial, sans-serif;
    font-size: {compact_font + 3}pt;
    font-weight: bold;
    color: #0F766E;
    margin: 7pt 0 3pt 0;
}}

h3, h4, h5, h6 {{
    font-family: Helvetica, Arial, sans-serif;
    font-size: {compact_font + 1}pt;
    font-weight: bold;
    color: #334155;
    margin: 5pt 0 2pt 0;
}}

pre {{
    padding: 4pt 6pt;
    margin: 4pt 0;
    font-size: {small_size}pt;
}}

table {{
    margin: 5pt 0;
    font-size: {small_size}pt;
}}

th, td {{
    padding: 3pt 5pt;
}}
"""
    else:
        # Default: ThemeId.TECHNICAL
        theme_specific = f"""
/* Theme: TECHNICAL - Clean sans-serif, slate-tinted code blocks, bold section rules, structured grid tables */
body {{
    font-family: Helvetica, Arial, "Segoe UI", sans-serif;
    font-size: {font_size}pt;
    line-height: 1.48;
    color: #0F172A;
}}

p {{
    margin: 0 0 8pt 0;
}}

ul, ol {{
    margin: 4pt 0 8pt 0;
    padding-left: 18pt;
}}

li {{
    margin-bottom: 3pt;
}}

h1 {{
    font-family: Helvetica, Arial, sans-serif;
    font-size: {font_size + 8}pt;
    font-weight: bold;
    color: #0F172A;
    margin: 14pt 0 8pt 0;
    border-bottom: 1.5pt solid #0D9488;
    padding-bottom: 4pt;
}}

h2 {{
    font-family: Helvetica, Arial, sans-serif;
    font-size: {font_size + 4}pt;
    font-weight: bold;
    color: #0F766E;
    margin: 12pt 0 6pt 0;
    border-bottom: 0.5pt solid #CBD5E1;
    padding-bottom: 2pt;
}}

h3, h4, h5, h6 {{
    font-family: Helvetica, Arial, sans-serif;
    font-size: {font_size + 2}pt;
    font-weight: bold;
    color: #1E293B;
    margin: 10pt 0 4pt 0;
}}

th {{
    background-color: #0F172A;
    color: #F8FAFC;
    border: 0.75pt solid #334155;
}}
"""

    return theme_specific.strip() + "\n" + common_rules.strip() + "\n"
