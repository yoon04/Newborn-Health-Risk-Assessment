from html import escape
from io import BytesIO
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Image, KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


TEAL = colors.HexColor('#0F766E')
DARK = colors.HexColor('#1F2937')
MUTED = colors.HexColor('#64748B')
PALE = colors.HexColor('#F3F6F5')
BORDER = colors.HexColor('#D8E2DF')
GREEN = colors.HexColor('#15803D')
AMBER = colors.HexColor('#B45309')
RED = colors.HexColor('#B91C1C')
PROJECT_ROOT = Path(__file__).resolve().parent
STATIC_ROOT = (PROJECT_ROOT / 'static').resolve()


def _ascii_text(value):
    text = str(value if value is not None else '')
    replacements = {
        '\u2013': '-', '\u2014': '-', '\u2011': '-', '\u2212': '-',
        '\u2018': "'", '\u2019': "'", '\u201c': '"', '\u201d': '"', '\u2022': '-',
    }
    for source, replacement in replacements.items():
        text = text.replace(source, replacement)
    return text.encode('ascii', 'replace').decode('ascii')


def _paragraph(value, style):
    return Paragraph(escape(_ascii_text(value)), style)


def _escaped(value):
    return escape(_ascii_text(value))


def _risk_label(score):
    score = float(score)
    if score < 30:
        return 'Low', GREEN
    if score < 70:
        return 'Moderate', AMBER
    return 'High', RED


def _page_footer(canvas, document):
    canvas.saveState()
    width, _height = A4
    canvas.setStrokeColor(BORDER)
    canvas.line(18 * mm, 14 * mm, width - 18 * mm, 14 * mm)
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(18 * mm, 9 * mm, 'Newborn Health Risk Assessment - Educational report')
    canvas.drawRightString(width - 18 * mm, 9 * mm, f'Page {document.page}')
    canvas.restoreState()


def _resolve_chart_path(path_value):
    if not path_value:
        return None
    normalized = str(path_value).strip().replace('\\', '/')
    if normalized.startswith('/static/'):
        normalized = normalized[1:]
    candidate = Path(normalized)
    if not candidate.is_absolute():
        candidate = PROJECT_ROOT / candidate
    try:
        resolved = candidate.resolve()
        resolved.relative_to(STATIC_ROOT)
    except (OSError, ValueError):
        return None
    if resolved.is_file() and resolved.suffix.lower() in {'.png', '.jpg', '.jpeg'}:
        return resolved
    return None


def _scaled_image(path_value, max_width, max_height):
    chart_path = _resolve_chart_path(path_value)
    if chart_path is None:
        return None
    image_width, image_height = ImageReader(str(chart_path)).getSize()
    scale = min(max_width / image_width, max_height / image_height)
    return Image(str(chart_path), width=image_width * scale, height=image_height * scale)


def _section_heading(title, heading_style):
    return _paragraph(title, heading_style)


def _bullet_paragraphs(items, style):
    return [
        Paragraph(f'<bullet>&bull;</bullet>{escape(_ascii_text(item))}', style, bulletText='-')
        for item in items
    ]


def build_pdf_report(report):
    """Build a detailed PDF that mirrors the web assessment result page."""
    output = BytesIO()
    document = SimpleDocTemplate(
        output,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=13 * mm,
        bottomMargin=20 * mm,
        title='Newborn Health Risk Assessment Results',
        author='Newborn Health Risk Assessment',
    )

    sample_styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'ReportTitle', parent=sample_styles['Title'], fontName='Helvetica-Bold',
        fontSize=20, leading=24, textColor=DARK, alignment=TA_CENTER, spaceAfter=2 * mm,
    )
    subtitle_style = ParagraphStyle(
        'ReportSubtitle', parent=sample_styles['Normal'], fontName='Helvetica',
        fontSize=9, leading=12, textColor=MUTED, alignment=TA_CENTER, spaceAfter=4 * mm,
    )
    heading_style = ParagraphStyle(
        'SectionHeading', parent=sample_styles['Heading2'], fontName='Helvetica-Bold',
        fontSize=12, leading=15, textColor=DARK, spaceBefore=1.5 * mm, spaceAfter=2 * mm,
    )
    body_style = ParagraphStyle(
        'Body', parent=sample_styles['BodyText'], fontName='Helvetica',
        fontSize=8.7, leading=12.5, textColor=DARK, alignment=TA_LEFT,
    )
    small_style = ParagraphStyle('Small', parent=body_style, fontSize=7.8, leading=10.5, textColor=MUTED)
    label_style = ParagraphStyle(
        'Label', parent=body_style, fontName='Helvetica-Bold', fontSize=8.3, textColor=MUTED,
    )
    header_style = ParagraphStyle('TableHeader', parent=label_style, textColor=colors.white)
    center_style = ParagraphStyle('Center', parent=body_style, alignment=TA_CENTER)
    bullet_style = ParagraphStyle(
        'Bullet', parent=body_style, leftIndent=10, firstLineIndent=-7,
        bulletIndent=2, spaceAfter=2,
    )

    story = [
        _paragraph('Assessment Results', title_style),
        _paragraph('Summary of newborn risk indicators', subtitle_style),
    ]
    generated_at = report.get('generated_at', '')
    if generated_at:
        story.append(_paragraph(f'Generated: {generated_at}', small_style))

    apgar = report.get('apgar', {})
    apgar_total = int(apgar.get('total', 0))
    apgar_level, apgar_color = (
        ('Needs immediate attention', RED) if apgar_total <= 3 else
        ('Needs attention', AMBER) if apgar_total <= 6 else
        ('Stable', GREEN)
    )
    apgar_overview = Table([[
        Paragraph(
            f'<font color="{apgar_color.hexval()}"><b>{apgar_total} / 10</b></font>',
            ParagraphStyle('ApgarScore', parent=title_style, fontSize=23, leading=27),
        ),
        Paragraph(
            f'<b>{_escaped(apgar.get("category", apgar_level))}</b><br/>'
            f'{_escaped(apgar.get("breakdown", ""))}', body_style,
        ),
    ]], colWidths=[40 * mm, 134 * mm])
    apgar_overview.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), PALE), ('BOX', (0, 0), (-1, -1), 0.8, BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('LEFTPADDING', (0, 0), (-1, -1), 9),
        ('RIGHTPADDING', (0, 0), (-1, -1), 9), ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.extend([_section_heading('APGAR Score Breakdown', heading_style), apgar_overview])

    component_cells = []
    for component in apgar.get('components', []):
        score = int(component.get('score', 0))
        score_color = RED if score == 0 else AMBER if score == 1 else GREEN
        component_cells.append([
            _paragraph(component.get('name', ''), label_style),
            Paragraph(
                f'<font color="{score_color.hexval()}"><b>{score} / 2</b></font>',
                ParagraphStyle('ComponentScore', parent=center_style, fontSize=14, leading=17),
            ),
            _paragraph(component.get('label', ''), center_style),
            _paragraph(component.get('note', ''), small_style),
        ])
    if component_cells:
        component_table = Table([component_cells], colWidths=[34.8 * mm] * len(component_cells))
        component_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white), ('GRID', (0, 0), (-1, -1), 0.5, BORDER),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'), ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('LEFTPADDING', (0, 0), (-1, -1), 5), ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 6), ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.extend([Spacer(1, 2 * mm), component_table])

    inputs = report.get('inputs', {})
    birth_cells = [
        ('Gestational Age', f"{inputs.get('birth_week', '')} weeks"),
        ('Birth Weight', inputs.get('birth_weight', '')),
        ("Mother's Age", f"{inputs.get('maternal_age', '')} years"),
        ("Child's Gender", inputs.get('child_gender', '')),
        ('Delivery Method', inputs.get('delivery_type', '')),
        ('Delivery Complication', inputs.get('delivery_complication', '')),
    ]
    birth_rows = []
    birth_value_style = ParagraphStyle('BirthValue', parent=body_style, fontName='Helvetica-Bold', fontSize=10)
    for row_start in range(0, len(birth_cells), 3):
        birth_rows.append([
            [_paragraph(label, label_style), _paragraph(value, birth_value_style)]
            for label, value in birth_cells[row_start:row_start + 3]
        ])
    birth_table = Table(birth_rows, colWidths=[58 * mm] * 3)
    birth_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), PALE), ('GRID', (0, 0), (-1, -1), 0.5, BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LEFTPADDING', (0, 0), (-1, -1), 7),
        ('RIGHTPADDING', (0, 0), (-1, -1), 7), ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.extend([_section_heading('Birth Summary', heading_style), birth_table])

    for module in report.get('risk_modules', []):
        risk_index = float(module.get('risk_index', 0))
        level, level_color = _risk_label(risk_index)
        module_box = Table([[
            Paragraph(
                f'<font color="{level_color.hexval()}"><b>{risk_index:.1f}</b></font><br/>'
                '<font size="7" color="#64748B">OF 100</font>',
                ParagraphStyle('ModuleScore', parent=title_style, fontSize=20, leading=22),
            ),
            Paragraph(
                f'<b>{_escaped(module.get("label", module.get("name", "")))}</b><br/>'
                f'<font size="8">Risk Index: <b>{risk_index:.1f} / 100</b> &nbsp; '
                f'Risk Level: <b>{_escaped(module.get("level", level))}</b></font><br/>'
                f'{_escaped(module.get("description", ""))}', body_style,
            ),
        ]], colWidths=[38 * mm, 136 * mm])
        module_box.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white), ('BOX', (0, 0), (-1, -1), 0.8, BORDER),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('LEFTPADDING', (0, 0), (-1, -1), 9),
            ('RIGHTPADDING', (0, 0), (-1, -1), 9), ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.extend([_section_heading(module.get('name', ''), heading_style), module_box])

    family_conditions = report.get('family_conditions', [])
    if family_conditions:
        family_rows = [[
            _paragraph('Disease', header_style), _paragraph('Who has it', header_style),
            _paragraph('Indicator', header_style),
        ]]
        for condition in family_conditions:
            family_rows.append([
                _paragraph(condition.get('disease', ''), body_style),
                _paragraph(condition.get('affected_relative', ''), body_style),
                _paragraph(f"{float(condition.get('risk_index', 0)):.1f} / 100", body_style),
            ])
        family_table = Table(family_rows, colWidths=[58 * mm, 76 * mm, 40 * mm], repeatRows=1)
        family_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), TEAL), ('GRID', (0, 0), (-1, -1), 0.5, BORDER),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LEFTPADDING', (0, 0), (-1, -1), 7),
            ('RIGHTPADDING', (0, 0), (-1, -1), 7), ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(KeepTogether([
            _section_heading('Family-History Details', heading_style),
            family_table,
        ]))

    plot_paths = report.get('plot_paths', {})
    birth_charts = [
        ("Baby's APGAR Score", plot_paths.get('apgar')), ('Gestational Age', plot_paths.get('week')),
        ('Birth Weight', plot_paths.get('weight')), ("Mother's Age", plot_paths.get('age')),
    ]
    if plot_paths.get('genetic'):
        birth_charts.append(('Family-History Indicator', plot_paths.get('genetic')))
    chart_cells = []
    for chart_title, path_value in birth_charts:
        chart_image = _scaled_image(path_value, 82 * mm, 46 * mm)
        if chart_image is not None:
            chart_cells.append([_paragraph(chart_title, label_style), Spacer(1, 1 * mm), chart_image])
    if chart_cells:
        chart_rows = []
        for row_start in range(0, len(chart_cells), 2):
            row = chart_cells[row_start:row_start + 2]
            if len(row) == 1:
                row.append('')
            chart_rows.append(row)
        chart_table = Table(chart_rows, colWidths=[87 * mm, 87 * mm])
        chart_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LEFTPADDING', (0, 0), (-1, -1), 2),
            ('RIGHTPADDING', (0, 0), (-1, -1), 2), ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(KeepTogether([
            _section_heading('Birth Chart Summary', heading_style),
            chart_table,
        ]))

    overall_risk_index = float(report.get('overall_risk_index', 0))
    final_level, final_color = _risk_label(overall_risk_index)
    overall_box = Table([[
        Paragraph(
            f'<font color="{final_color.hexval()}"><b>{overall_risk_index:.1f}</b></font><br/>'
            '<font size="7" color="#64748B">OF 100</font>',
            ParagraphStyle('OverallScore', parent=title_style, fontSize=22, leading=24),
        ),
        Paragraph(
            '<b>Hierarchical fuzzy result from immediate, birth-related, and family-history modules</b><br/>'
            f'Risk Index: <b>{overall_risk_index:.1f} / 100</b> &nbsp; '
            f'Risk Level: <b>{_escaped(report.get("risk_level", final_level))}</b> &nbsp; '
            f'Confidence: <b>{_escaped(report.get("confidence_level", "Low"))}</b><br/>'
            f'{_escaped(report.get("recommendation", ""))}', body_style,
        ),
    ]], colWidths=[40 * mm, 134 * mm])
    overall_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), PALE), ('BOX', (0, 0), (-1, -1), 1, final_color),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('LEFTPADDING', (0, 0), (-1, -1), 9),
        ('RIGHTPADDING', (0, 0), (-1, -1), 9), ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.extend([_section_heading('Overall Assessment Result', heading_style), overall_box])

    confidence_reasons = report.get('confidence_reasons', [])
    if confidence_reasons:
        story.append(KeepTogether([
            _section_heading('Confidence Basis', heading_style),
            *_bullet_paragraphs(confidence_reasons, bullet_style),
        ]))

    main_factors = report.get('main_contributing_factors', [])
    lower_factors = report.get('lower_impact_factors', [])
    main_flowables = [_paragraph('Main Contributing Factors', label_style)]
    for index, factor in enumerate(main_factors, start=1):
        main_flowables.extend([
            _paragraph(f"{index}. {factor.get('name', '')}", body_style),
            _paragraph(factor.get('description', ''), small_style), Spacer(1, 1 * mm),
        ])
    lower_flowables = [_paragraph('Lower-Impact Factors', label_style)]
    for factor in lower_factors:
        lower_flowables.extend([
            _paragraph(factor.get('name', ''), body_style),
            _paragraph(factor.get('description', ''), small_style), Spacer(1, 1 * mm),
        ])
    factors_table = Table([[main_flowables, lower_flowables]], colWidths=[87 * mm, 87 * mm])
    factors_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), PALE), ('GRID', (0, 0), (-1, -1), 0.5, BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8), ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
    ]))
    story.append(KeepTogether([
        _section_heading('Assessment Factors', heading_style),
        factors_table,
    ]))

    triggered_rules = report.get('triggered_rules', [])
    if triggered_rules:
        rule_rows = [[
            _paragraph('Rule', header_style), _paragraph('Name and description', header_style),
            _paragraph('Result', header_style), _paragraph('Activation', header_style),
        ]]
        for rule in triggered_rules:
            rule_rows.append([
                Paragraph(
                    f'<font color="{TEAL.hexval()}"><b>{_escaped(rule.get("id", ""))}</b></font><br/>'
                    f'{_escaped(rule.get("module", ""))}', small_style,
                ),
                Paragraph(
                    f'<b>{_escaped(rule.get("name", ""))}</b><br/>'
                    f'{_escaped(rule.get("description", ""))}', small_style,
                ),
                _paragraph(str(rule.get('outcome', '')).title(), small_style),
                _paragraph(f"{float(rule.get('activation', 0)):.2f} / 1.00", small_style),
            ])
        rule_table = Table(rule_rows, colWidths=[30 * mm, 92 * mm, 23 * mm, 29 * mm], repeatRows=1)
        rule_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), TEAL), ('GRID', (0, 0), (-1, -1), 0.5, BORDER),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5), ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.extend([
            _section_heading('Important Triggered Fuzzy Rules', heading_style),
            _paragraph('Activation strength is shown on a 0 to 1 scale. It is not a contribution percentage.', small_style),
            Spacer(1, 1.5 * mm), rule_table,
        ])

    final_chart = _scaled_image(plot_paths.get('final'), 174 * mm, 82 * mm)
    if final_chart is not None:
        story.append(KeepTogether([
            _section_heading('Overall Risk Index Chart', heading_style), final_chart, Spacer(1, 1.5 * mm),
            _paragraph(
                'How to read: The dashed curve shows the combined fuzzy-rule result. '
                'The vertical line marks the calculated Risk Index.', small_style,
            ),
            _paragraph(
                'Important: This is educational guidance only. It does not confirm disease or replace medical advice.',
                small_style,
            ),
        ]))

    disclaimer = Table([[
        Paragraph(
            '<b>Note:</b> This is not a clinical diagnosis. Please consult a healthcare professional for medical decisions.',
            body_style,
        ),
    ]], colWidths=[174 * mm])
    disclaimer.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FFF7ED')),
        ('BOX', (0, 0), (-1, -1), 0.7, colors.HexColor('#FED7AA')),
        ('LEFTPADDING', (0, 0), (-1, -1), 9), ('RIGHTPADDING', (0, 0), (-1, -1), 9),
        ('TOPPADDING', (0, 0), (-1, -1), 7), ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
    ]))
    story.extend([Spacer(1, 3 * mm), disclaimer])

    document.build(story, onFirstPage=_page_footer, onLaterPages=_page_footer)
    output.seek(0)
    return output
