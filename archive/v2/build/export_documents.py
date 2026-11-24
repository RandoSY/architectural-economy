"""
Build publication-grade PDF (ReportLab) and native Microsoft Word DOCX (Pandoc + OOXML styling)
from manuscript/architectural_economy_v2.md, embedding Figures 1-8 cleanly.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Tuple

import matplotlib
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable,
    Image,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parent.parent
MD_PATH = ROOT / "manuscript" / "architectural_economy_v2.md"
PDF_OUT = ROOT / "manuscript" / "Architectural_Economy_v2.pdf"
DOCX_OUT = ROOT / "manuscript" / "Architectural_Economy_v2.docx"

# Harmonized palette matching manuscript schematics & charts
C_DARK = colors.HexColor("#1C2B36")
C_SLATE = colors.HexColor("#5B6B7A")
C_BLUE = colors.HexColor("#2E6F95")
C_BLUE_HDR = colors.HexColor("#DCE8F0")
C_BLUE_STRIPE = colors.HexColor("#F4F8FB")
C_TEAL = colors.HexColor("#1F7A68")
C_RULE = colors.HexColor("#C7D0D9")
C_EQ_BG = colors.HexColor("#F5F8FA")


def register_fonts() -> None:
    ttf_dir = Path(matplotlib.__file__).resolve().parent / "mpl-data" / "fonts" / "ttf"
    fonts = {
        "Serif": "DejaVuSerif.ttf",
        "Serif-Bold": "DejaVuSerif-Bold.ttf",
        "Serif-Italic": "DejaVuSerif-Italic.ttf",
        "Serif-BoldItalic": "DejaVuSerif-BoldItalic.ttf",
        "Sans": "DejaVuSans.ttf",
        "Sans-Bold": "DejaVuSans-Bold.ttf",
        "Sans-Italic": "DejaVuSans-Oblique.ttf",
        "Sans-BoldItalic": "DejaVuSans-BoldOblique.ttf",
        "Mono": "DejaVuSansMono.ttf",
    }
    for name, fname in fonts.items():
        pdfmetrics.registerFont(TTFont(name, str(ttf_dir / fname)))

    pdfmetrics.registerFontFamily(
        "Serif",
        normal="Serif",
        bold="Serif-Bold",
        italic="Serif-Italic",
        boldItalic="Serif-BoldItalic",
    )
    pdfmetrics.registerFontFamily(
        "Sans",
        normal="Sans",
        bold="Sans-Bold",
        italic="Sans-Italic",
        boldItalic="Sans-BoldItalic",
    )


def latex_to_rl_html(expr: str) -> str:
    """Convert inline/display LaTeX math into clean ReportLab rich-text markup."""
    s = expr.strip()
    replacements = [
        (r"\text{Constraint}", "Constraint"),
        (r"\text{elem}", "elem"),
        (r"\text{gene}", "gene"),
        (r"\text{max}", "max"),
        (r"\max", "max"),
        (r"\min", "min"),
        (r"\alpha", "α"),
        (r"\beta", "β"),
        (r"\gamma", "γ"),
        (r"\varepsilon", "ε"),
        (r"\epsilon", "ε"),
        (r"\sigma", "σ"),
        (r"\eta", "η"),
        (r"\in", "∈"),
        (r"\ge", "≥"),
        (r"\le", "≤"),
        (r"\times", "×"),
        (r"\cdot", "·"),
        (r"\pm", "±"),
        (r"\to", "→"),
        (r"\rightarrow", "→"),
        (r"\wedge", "∧"),
        (r"\vee", "∨"),
        (r"\neg", "¬"),
        (r"\{", "{"),
        (r"\}", "}"),
    ]
    for old, new in replacements:
        s = s.replace(old, new)

    # Subscripts: _{...} or _x
    s = re.sub(r"_\{([^}]+)\}", r"<sub>\1</sub>", s)
    s = re.sub(r"_([A-Za-z0-9])", r"<sub>\1</sub>", s)
    # Superscripts: ^{...} or ^x
    s = re.sub(r"\^\{([^}]+)\}", r"<sup>\1</sup>", s)
    s = re.sub(r"\^([A-Za-z0-9])", r"<sup>\1</sup>", s)
    return s


def md_inline_to_rl(text: str) -> str:
    """Convert Markdown inline syntax (bold, italic, code, math, URLs) to ReportLab XML."""
    # Escape XML entities first
    s = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    # Inline math $...$
    def _math_sub(m: re.Match) -> str:
        inner = latex_to_rl_html(m.group(1))
        return f"<i>{inner}</i>"

    s = re.sub(r"(?<!\$)\$(?!\$)([^$]+?)(?<!\$)\$(?!\$)", _math_sub, s)

    # Inline code `...`
    s = re.sub(r"`([^`]+)`", r'<font name="Mono" size="8.4">\1</font>', s)

    # Bold+Italic, Bold, Italic
    s = re.sub(r"\*\*\*(.+?)\*\*\*", r"<b><i>\1</i></b>", s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"<i>\1</i>", s)

    # Auto-link bare URLs cleanly in subtle steel-blue
    s = re.sub(
        r"(https?://[^\s<>]+)",
        r'<font color="#2E6F95"><a href="\1">\1</a></font>',
        s,
    )
    return s


def build_styles() -> dict:
    return {
        "title": ParagraphStyle(
            "Title",
            fontName="Sans-Bold",
            fontSize=18.5,
            leading=23,
            textColor=C_DARK,
            spaceAfter=6,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle",
            fontName="Serif-Italic",
            fontSize=11.0,
            leading=15,
            textColor=C_SLATE,
            spaceAfter=8,
        ),
        "meta": ParagraphStyle(
            "Meta",
            fontName="Sans",
            fontSize=8.6,
            leading=12.5,
            textColor=C_SLATE,
            spaceAfter=2,
        ),
        "h2": ParagraphStyle(
            "H2",
            fontName="Sans-Bold",
            fontSize=12.2,
            leading=16,
            textColor=C_DARK,
            spaceBefore=14,
            spaceAfter=5,
            keepWithNext=True,
        ),
        "h3": ParagraphStyle(
            "H3",
            fontName="Sans-Bold",
            fontSize=10.3,
            leading=14,
            textColor=C_BLUE,
            spaceBefore=10,
            spaceAfter=4,
            keepWithNext=True,
        ),
        "h4": ParagraphStyle(
            "H4",
            fontName="Sans-Bold",
            fontSize=9.6,
            leading=13.5,
            textColor=C_DARK,
            spaceBefore=8,
            spaceAfter=3,
            keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "Body",
            fontName="Serif",
            fontSize=9.4,
            leading=14.0,
            textColor=C_DARK,
            alignment=TA_JUSTIFY,
            spaceAfter=6,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            fontName="Serif",
            fontSize=9.2,
            leading=13.5,
            textColor=C_DARK,
            alignment=TA_LEFT,
            leftIndent=14,
            firstLineIndent=-9,
            spaceAfter=4,
        ),
        "eq": ParagraphStyle(
            "Equation",
            fontName="Serif",
            fontSize=9.2,
            leading=13.5,
            textColor=C_DARK,
            alignment=TA_CENTER,
        ),
        "caption": ParagraphStyle(
            "Caption",
            fontName="Sans",
            fontSize=8.3,
            leading=11.8,
            textColor=C_SLATE,
            alignment=TA_LEFT,
            spaceBefore=4,
            spaceAfter=10,
        ),
        "tbl_hdr": ParagraphStyle(
            "TblHdr",
            fontName="Sans-Bold",
            fontSize=7.4,
            leading=9.8,
            textColor=C_DARK,
            alignment=TA_LEFT,
        ),
        "tbl_cell": ParagraphStyle(
            "TblCell",
            fontName="Sans",
            fontSize=7.5,
            leading=10.0,
            textColor=C_DARK,
            alignment=TA_LEFT,
        ),
        "tbl_cell_c": ParagraphStyle(
            "TblCellC",
            fontName="Sans",
            fontSize=7.5,
            leading=10.0,
            textColor=C_DARK,
            alignment=TA_CENTER,
        ),
        "ref": ParagraphStyle(
            "Ref",
            fontName="Serif",
            fontSize=8.2,
            leading=11.6,
            textColor=C_DARK,
            leftIndent=18,
            firstLineIndent=-18,
            spaceAfter=3.5,
        ),
    }


def make_header_footer(canvas, doc):
    canvas.saveState()
    page_w, page_h = letter
    margin = 0.85 * inch

    # Running header (top left)
    canvas.setFont("Sans", 7.4)
    canvas.setFillColor(C_SLATE)
    canvas.drawString(margin, page_h - 0.52 * inch, "ARCHITECTURAL ECONOMY  /  HYPOTHESIS & PERSPECTIVE")
    canvas.setStrokeColor(C_RULE)
    canvas.setLineWidth(0.5)
    canvas.line(margin, page_h - 0.58 * inch, page_w - margin, page_h - 0.58 * inch)

    # Running footer (bottom right)
    canvas.setFont("Sans", 8.0)
    canvas.setFillColor(C_SLATE)
    canvas.drawRightString(page_w - margin, 0.50 * inch, f"Working manuscript (v2)  •  {doc.page}")
    canvas.restoreState()


def parse_markdown_table(lines: List[str], styles: dict, content_w: float) -> Table:
    rows_raw = []
    aligns = []
    for i, ln in enumerate(lines):
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if i == 1 and all(re.match(r"^:?-{2,}:?$", c) for c in cells):
            for c in cells:
                if c.startswith(":") and c.endswith(":"):
                    aligns.append("C")
                else:
                    aligns.append("L")
            continue
        rows_raw.append(cells)

    n_cols = len(rows_raw[0])
    if not aligns:
        aligns = ["L"] + ["C"] * (n_cols - 1)

    table_data = []
    for r_idx, row in enumerate(rows_raw):
        styled_row = []
        for c_idx, cell in enumerate(row):
            if r_idx == 0:
                st = ParagraphStyle(
                    "tmp_h",
                    parent=styles["tbl_hdr"],
                    alignment=TA_CENTER if aligns[c_idx] == "C" else TA_LEFT,
                )
            else:
                st = styles["tbl_cell_c"] if aligns[c_idx] == "C" else styles["tbl_cell"]
            styled_row.append(Paragraph(md_inline_to_rl(cell), st))
        table_data.append(styled_row)

    # Smart column widths: wider first column for labels, balanced remaining columns
    if n_cols == 3:
        col_widths = [content_w * 0.24, content_w * 0.36, content_w * 0.40]
    elif n_cols == 7:
        col_widths = [
            content_w * 0.22,
            content_w * 0.14,
            content_w * 0.13,
            content_w * 0.14,
            content_w * 0.13,
            content_w * 0.12,
            content_w * 0.12,
        ]
    elif n_cols == 8:
        col_widths = [
            content_w * 0.21,
            content_w * 0.105,
            content_w * 0.105,
            content_w * 0.11,
            content_w * 0.11,
            content_w * 0.11,
            content_w * 0.125,
            content_w * 0.125,
        ]
    else:
        col_widths = [content_w / n_cols] * n_cols

    tbl = Table(table_data, colWidths=col_widths, repeatRows=1)
    ts = [
        ("BACKGROUND", (0, 0), (-1, 0), C_BLUE_HDR),
        ("LINEABOVE", (0, 0), (-1, 0), 1.2, C_BLUE),
        ("LINEBELOW", (0, 0), (-1, 0), 0.9, C_BLUE),
        ("LINEBELOW", (0, -1), (-1, -1), 1.0, C_BLUE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]
    for r in range(1, len(table_data)):
        if r % 2 == 0:
            ts.append(("BACKGROUND", (0, r), (-1, r), C_BLUE_STRIPE))
        ts.append(("LINEBELOW", (0, r), (-1, r), 0.35, C_RULE))
    tbl.setStyle(TableStyle(ts))
    return tbl


def export_pdf() -> None:
    register_fonts()
    styles = build_styles()
    margin = 0.85 * inch
    content_w = letter[0] - 2 * margin

    doc = SimpleDocTemplate(
        str(PDF_OUT),
        pagesize=letter,
        leftMargin=margin,
        rightMargin=margin,
        topMargin=0.78 * inch,
        bottomMargin=0.75 * inch,
        title="Architectural Economy in Biological and Technological Systems (v2)",
        author="Independent Researcher",
    )

    lines = MD_PATH.read_text(encoding="utf-8").splitlines()
    story = []
    i = 0
    in_refs = False
    is_title_block = True

    while i < len(lines):
        raw = lines[i]
        stripped = raw.strip()

        if not stripped:
            i += 1
            continue

        # Horizontal rule
        if stripped == "---":
            is_title_block = False
            story.append(Spacer(1, 4))
            story.append(HRFlowable(width="100%", thickness=0.6, color=C_RULE, spaceAfter=8))
            i += 1
            continue

        # Title (# ...)
        if stripped.startswith("# "):
            story.append(Paragraph(md_inline_to_rl(stripped[2:].strip()), styles["title"]))
            i += 1
            continue

        # Subtitle & metadata in header block
        if is_title_block and stripped.startswith("**") and stripped.endswith("**"):
            story.append(Paragraph(md_inline_to_rl(stripped[2:-2].strip()), styles["subtitle"]))
            i += 1
            continue
        if is_title_block and (stripped.startswith("*Author:") or stripped.startswith("*Date:")):
            story.append(Paragraph(md_inline_to_rl(stripped), styles["meta"]))
            i += 1
            continue

        # Headings
        if stripped.startswith("## "):
            is_title_block = False
            heading = stripped[3:].strip()
            in_refs = heading.lower() == "references"
            story.append(Paragraph(md_inline_to_rl(heading), styles["h2"]))
            i += 1
            continue
        if stripped.startswith("### "):
            story.append(Paragraph(md_inline_to_rl(stripped[4:].strip()), styles["h3"]))
            i += 1
            continue
        if stripped.startswith("#### "):
            story.append(Paragraph(md_inline_to_rl(stripped[5:].strip()), styles["h4"]))
            i += 1
            continue

        # Display equation ($$...$$)
        if stripped.startswith("$$") and stripped.endswith("$$"):
            eq_text = latex_to_rl_html(stripped[2:-2].strip())
            eq_para = Paragraph(f"<i>{eq_text}</i>", styles["eq"])
            eq_box = Table([[eq_para]], colWidths=[content_w])
            eq_box.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), C_EQ_BG),
                ("LINEBEFORE", (0, 0), (0, -1), 2.2, C_BLUE),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]))
            story.append(Spacer(1, 3))
            story.append(eq_box)
            story.append(Spacer(1, 6))
            i += 1
            continue

        # Markdown image + optional following Figure caption
        img_match = re.match(r"^!\[[^\]]*\]\(([^)]+)\)$", stripped)
        if img_match:
            rel_img = img_match.group(1)
            img_path = (MD_PATH.parent / rel_img).resolve()
            with PILImage.open(img_path) as im:
                iw, ih = im.size
            aspect = ih / float(iw)
            draw_w = min(content_w, 6.6 * inch)
            draw_h = draw_w * aspect
            if draw_h > 3.6 * inch:
                draw_h = 3.6 * inch
                draw_w = draw_h / aspect
            rl_img = Image(str(img_path), width=draw_w, height=draw_h)
            rl_img.hAlign = "CENTER"

            block = [Spacer(1, 4), rl_img]
            # Peek ahead for caption
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines) and lines[j].strip().startswith("**Figure "):
                block.append(Paragraph(md_inline_to_rl(lines[j].strip()), styles["caption"]))
                i = j + 1
            else:
                block.append(Spacer(1, 6))
                i += 1
            story.append(KeepTogether(block))
            continue

        # Markdown table + optional following Table caption
        if stripped.startswith("|"):
            tbl_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                tbl_lines.append(lines[i])
                i += 1
            tbl = parse_markdown_table(tbl_lines, styles, content_w)
            block = [Spacer(1, 4), tbl]
            j = i
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines) and lines[j].strip().startswith("**Table "):
                block.append(Paragraph(md_inline_to_rl(lines[j].strip()), styles["caption"]))
                i = j + 1
            else:
                block.append(Spacer(1, 6))
            story.append(KeepTogether(block))
            continue

        # References (numbered list inside References section)
        if in_refs and re.match(r"^\d+\.\s+", stripped):
            story.append(Paragraph(md_inline_to_rl(stripped), styles["ref"]))
            i += 1
            continue

        # Bullet list (* ... or indented   * ...)
        if re.match(r"^\s*[\*\-]\s+", raw):
            indent_lvl = len(raw) - len(raw.lstrip())
            item_text = re.sub(r"^\s*[\*\-]\s+", "", raw).strip()
            st = styles["bullet"]
            if indent_lvl >= 2:
                st = ParagraphStyle("SubBullet", parent=styles["bullet"], leftIndent=26, firstLineIndent=-9)
            bullet_char = "◦" if indent_lvl >= 2 else "•"
            story.append(Paragraph(f"{bullet_char}&nbsp;&nbsp;{md_inline_to_rl(item_text)}", st))
            i += 1
            continue

        # Numbered list (outside References)
        num_match = re.match(r"^(\d+)\.\s+(.*)$", stripped)
        if num_match and not in_refs:
            num, body_txt = num_match.group(1), num_match.group(2)
            # Collect continuation indented lines (like display math under numbered list)
            story.append(Paragraph(f"<b>{num}.</b>&nbsp;&nbsp;{md_inline_to_rl(body_txt)}", styles["bullet"]))
            i += 1
            continue

        # Indented display equation under a numbered item
        if stripped.startswith("$$"):
            eq_text = latex_to_rl_html(stripped.strip("$").strip())
            eq_para = Paragraph(f"<i>{eq_text}</i>", styles["eq"])
            story.append(eq_para)
            i += 1
            continue

        # Standard paragraph (join consecutive plain lines)
        para_lines = [stripped]
        i += 1
        while i < len(lines):
            nxt = lines[i].strip()
            if (
                not nxt
                or nxt.startswith(("#", "|", "![", "$$", "---"))
                or re.match(r"^\s*[\*\-]\s+", lines[i])
                or re.match(r"^\d+\.\s+", nxt)
            ):
                break
            para_lines.append(nxt)
            i += 1
        para_text = " ".join(para_lines)
        story.append(Paragraph(md_inline_to_rl(para_text), styles["body"]))

    doc.build(story, onFirstPage=make_header_footer, onLaterPages=make_header_footer)
    print(f"Exported PDF -> {PDF_OUT}")


def style_docx_xml(docx_path: Path) -> None:
    """
    Post-process Pandoc-generated DOCX XML for crisp academic styling:
    0.85-inch margins, Cambria/Calibri typography, slate-blue heading colors,
    shaded table headers with clean horizontal borders, and running header/footer.
    """
    W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    ET.register_namespace("w", W_NS)
    ET.register_namespace("r", R_NS)

    def wtag(name: str) -> str:
        return f"{{{W_NS}}}{name}"

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        with zipfile.ZipFile(docx_path, "r") as zf:
            zf.extractall(tmp)

        # 1. Style word/styles.xml (fonts, colors, spacing)
        styles_xml = tmp / "word" / "styles.xml"
        tree = ET.parse(styles_xml)
        root = tree.getroot()

        # Set default font to Cambria 10.5pt
        doc_defaults = root.find(wtag("docDefaults"))
        if doc_defaults is not None:
            rpr_def = doc_defaults.find(f"{wtag('rPrDefault')}/{wtag('rPr')}")
            if rpr_def is not None:
                rfonts = rpr_def.find(wtag("rFonts"))
                if rfonts is None:
                    rfonts = ET.SubElement(rpr_def, wtag("rFonts"))
                for attr in ["ascii", "hAnsi", "cs", "eastAsia"]:
                    rfonts.set(wtag(attr), "Cambria")
                for attr in ["asciiTheme", "hAnsiTheme", "cstheme", "eastAsiaTheme"]:
                    rfonts.attrib.pop(wtag(attr), None)
                sz = rpr_def.find(wtag("sz"))
                if sz is None:
                    sz = ET.SubElement(rpr_def, wtag("sz"))
                sz.set(wtag("val"), "21")  # 10.5 pt

        # Clean heading styles (Calibri bold, dark slate/steel blue)
        heading_cfg = {
            "Heading1": ("Calibri", "36", "1C2B36"),
            "Heading2": ("Calibri", "26", "1C2B36"),
            "Heading3": ("Calibri", "22", "2E6F95"),
            "Heading4": ("Calibri", "20", "1C2B36"),
            "Title": ("Calibri", "38", "1C2B36"),
        }
        for st in root.findall(wtag("style")):
            sid = st.get(wtag("styleId"))
            if sid in heading_cfg:
                font_name, half_pts, hex_col = heading_cfg[sid]
                rpr = st.find(wtag("rPr"))
                if rpr is None:
                    rpr = ET.SubElement(st, wtag("rPr"))
                rfonts = rpr.find(wtag("rFonts"))
                if rfonts is None:
                    rfonts = ET.SubElement(rpr, wtag("rFonts"))
                for attr in ["ascii", "hAnsi", "cs"]:
                    rfonts.set(wtag(attr), font_name)
                for attr in ["asciiTheme", "hAnsiTheme", "cstheme"]:
                    rfonts.attrib.pop(wtag(attr), None)
                col = rpr.find(wtag("color"))
                if col is None:
                    col = ET.SubElement(rpr, wtag("color"))
                col.set(wtag("val"), hex_col)
                col.attrib.pop(wtag("themeColor"), None)
                sz = rpr.find(wtag("sz"))
                if sz is None:
                    sz = ET.SubElement(rpr, wtag("sz"))
                sz.set(wtag("val"), half_pts)
                if rpr.find(wtag("b")) is None:
                    ET.SubElement(rpr, wtag("b"))

        tree.write(styles_xml, encoding="utf-8", xml_declaration=True)

        # 2. Style word/document.xml (margins + clean shaded tables + centered images)
        doc_xml = tmp / "word" / "document.xml"
        dtree = ET.parse(doc_xml)
        droot = dtree.getroot()
        body = droot.find(wtag("body"))

        # Set 0.85 inch margins (1224 twips) and attach header/footer
        sect_pr = body.find(wtag("sectPr"))
        if sect_pr is None:
            sect_pr = ET.SubElement(body, wtag("sectPr"))
        pg_mar = sect_pr.find(wtag("pgMar"))
        if pg_mar is None:
            pg_mar = ET.SubElement(sect_pr, wtag("pgMar"))
        pg_mar.set(wtag("top"), "1224")
        pg_mar.set(wtag("bottom"), "1224")
        pg_mar.set(wtag("left"), "1224")
        pg_mar.set(wtag("right"), "1224")
        pg_mar.set(wtag("header"), "600")
        pg_mar.set(wtag("footer"), "600")

        # Format every table with steel-blue top/bottom borders and shaded header row
        for tbl in body.findall(f".//{wtag('tbl')}"):
            tbl_pr = tbl.find(wtag("tblPr"))
            if tbl_pr is None:
                tbl_pr = ET.Element(wtag("tblPr"))
                tbl.insert(0, tbl_pr)
            # Full width 100%
            tbl_w = tbl_pr.find(wtag("tblW"))
            if tbl_w is None:
                tbl_w = ET.SubElement(tbl_pr, wtag("tblW"))
            tbl_w.set(wtag("w"), "5000")
            tbl_w.set(wtag("type"), "pct")

            # Clean academic horizontal borders
            borders = tbl_pr.find(wtag("tblBorders"))
            if borders is not None:
                tbl_pr.remove(borders)
            borders = ET.SubElement(tbl_pr, wtag("tblBorders"))
            for bname, sz_val, col_val in [
                ("top", "10", "2E6F95"),
                ("bottom", "10", "2E6F95"),
                ("insideH", "4", "C7D0D9"),
                ("left", "0", "auto"),
                ("right", "0", "auto"),
                ("insideV", "0", "auto"),
            ]:
                b = ET.SubElement(borders, wtag(bname))
                b.set(wtag("val"), "none" if sz_val == "0" else "single")
                b.set(wtag("sz"), sz_val)
                b.set(wtag("color"), col_val)

            # Cell padding
            cell_mar = tbl_pr.find(wtag("tblCellMar"))
            if cell_mar is not None:
                tbl_pr.remove(cell_mar)
            cell_mar = ET.SubElement(tbl_pr, wtag("tblCellMar"))
            for side, val in [("top", "80"), ("bottom", "80"), ("left", "100"), ("right", "100")]:
                el = ET.SubElement(cell_mar, wtag(side))
                el.set(wtag("w"), val)
                el.set(wtag("type"), "dxa")

            rows = tbl.findall(wtag("tr"))
            for r_idx, tr in enumerate(rows):
                fill = "DCE8F0" if r_idx == 0 else ("F4F8FB" if r_idx % 2 == 0 else None)
                for tc in tr.findall(wtag("tc")):
                    tc_pr = tc.find(wtag("tcPr"))
                    if tc_pr is None:
                        tc_pr = ET.Element(wtag("tcPr"))
                        tc.insert(0, tc_pr)
                    if fill:
                        shd = tc_pr.find(wtag("shd"))
                        if shd is None:
                            shd = ET.SubElement(tc_pr, wtag("shd"))
                        shd.set(wtag("val"), "clear")
                        shd.set(wtag("color"), "auto")
                        shd.set(wtag("fill"), fill)
                    if r_idx == 0:
                        # Bold header text in Calibri 9pt
                        for r in tc.findall(f".//{wtag('r')}"):
                            rpr = r.find(wtag("rPr"))
                            if rpr is None:
                                rpr = ET.Element(wtag("rPr"))
                                r.insert(0, rpr)
                            if rpr.find(wtag("b")) is None:
                                ET.SubElement(rpr, wtag("b"))
                            sz = rpr.find(wtag("sz"))
                            if sz is None:
                                sz = ET.SubElement(rpr, wtag("sz"))
                            sz.set(wtag("val"), "18")
                    else:
                        for r in tc.findall(f".//{wtag('r')}"):
                            rpr = r.find(wtag("rPr"))
                            if rpr is None:
                                rpr = ET.Element(wtag("rPr"))
                                r.insert(0, rpr)
                            sz = rpr.find(wtag("sz"))
                            if sz is None:
                                sz = ET.SubElement(rpr, wtag("sz"))
                            sz.set(wtag("val"), "18")

        # Add clean running header and page-numbered footer
        header_xml = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:hdr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            '<w:p><w:pPr><w:pBdr><w:bottom w:val="single" w:sz="4" w:space="4" w:color="C7D0D9"/></w:pBdr></w:pPr>'
            '<w:r><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:color w:val="5B6B7A"/><w:sz w:val="16"/></w:rPr>'
            '<w:t>ARCHITECTURAL ECONOMY  /  HYPOTHESIS &amp; PERSPECTIVE</w:t></w:r></w:p></w:hdr>'
        )
        footer_xml = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            '<w:p><w:pPr><w:jc w:val="right"/></w:pPr>'
            '<w:r><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:color w:val="5B6B7A"/><w:sz w:val="17"/></w:rPr>'
            '<w:t xml:space="preserve">Working manuscript (v2)  •  Page </w:t></w:r>'
            '<w:r><w:fldChar w:fldCharType="begin"/></w:r>'
            '<w:r><w:instrText xml:space="preserve"> PAGE </w:instrText></w:r>'
            '<w:r><w:fldChar w:fldCharType="separate"/></w:r>'
            '<w:r><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:color w:val="5B6B7A"/><w:sz w:val="17"/></w:rPr><w:t>1</w:t></w:r>'
            '<w:r><w:fldChar w:fldCharType="end"/></w:r></w:p></w:ftr>'
        )
        (tmp / "word" / "header1.xml").write_text(header_xml, encoding="utf-8")
        (tmp / "word" / "footer1.xml").write_text(footer_xml, encoding="utf-8")

        # Register header1.xml and footer1.xml in [Content_Types].xml
        ct_path = tmp / "[Content_Types].xml"
        ct_text = ct_path.read_text(encoding="utf-8")
        if "header1.xml" not in ct_text:
            insert = (
                '<Override PartName="/word/header1.xml" '
                'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml"/>'
                '<Override PartName="/word/footer1.xml" '
                'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>'
            )
            ct_text = ct_text.replace("</Types>", insert + "</Types>")
            ct_path.write_text(ct_text, encoding="utf-8")

        # Register relationships in word/_rels/document.xml.rels
        rels_path = tmp / "word" / "_rels" / "document.xml.rels"
        rels_text = rels_path.read_text(encoding="utf-8")
        hdr_rid = "rIdHeaderV2"
        ftr_rid = "rIdFooterV2"
        if hdr_rid not in rels_text:
            rel_insert = (
                f'<Relationship Id="{hdr_rid}" '
                'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/header" Target="header1.xml"/>'
                f'<Relationship Id="{ftr_rid}" '
                'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer1.xml"/>'
            )
            rels_text = rels_text.replace("</Relationships>", rel_insert + "</Relationships>")
            rels_path.write_text(rels_text, encoding="utf-8")

        # Link headerReference & footerReference in sectPr
        hdr_ref = ET.Element(wtag("headerReference"))
        hdr_ref.set(wtag("type"), "default")
        hdr_ref.set(f"{{{R_NS}}}id", hdr_rid)
        ftr_ref = ET.Element(wtag("footerReference"))
        ftr_ref.set(wtag("type"), "default")
        ftr_ref.set(f"{{{R_NS}}}id", ftr_rid)
        sect_pr.insert(0, ftr_ref)
        sect_pr.insert(0, hdr_ref)

        dtree.write(doc_xml, encoding="utf-8", xml_declaration=True)

        # Repack DOCX cleanly
        out_tmp = tmp / "repacked.docx"
        with zipfile.ZipFile(out_tmp, "w", zipfile.ZIP_DEFLATED) as zout:
            for file in tmp.rglob("*"):
                if file.is_file() and file != out_tmp:
                    zout.write(file, file.relative_to(tmp).as_posix())
        shutil.copy2(out_tmp, docx_path)


def export_docx() -> None:
    cmd = [
        "pandoc",
        str(MD_PATH),
        "-o",
        str(DOCX_OUT),
        "--from",
        "markdown+tex_math_dollars+pipe_tables",
        "--resource-path",
        f"{MD_PATH.parent};{ROOT / 'figures'}",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    if res.stderr.strip():
        print("Pandoc notes:", res.stderr.strip())
    style_docx_xml(DOCX_OUT)
    print(f"Exported Word DOCX -> {DOCX_OUT}")


if __name__ == "__main__":
    export_pdf()
    export_docx()
