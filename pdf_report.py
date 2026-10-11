from html import escape
from io import BytesIO
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


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


def _major_section_heading(title, heading_style):
    banner = Table([[_paragraph(title, heading_style)]], colWidths=[174 * mm])
    banner.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), TEAL),
        ('BOX', (0, 0), (-1, -1), 0.8, TEAL),
        ('LEFTPADDING', (0, 0), (-1, -1), 9),
        ('RIGHTPADDING', (0, 0), (-1, -1), 9),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
    ]))
    banner.spaceBefore = 4 * mm
    banner.spaceAfter = 3 * mm
    banner.keepWithNext = True
    return banner


def _bullet_paragraphs(items, style):
    return [
        Paragraph(f'<bullet>&bull;</bullet>{escape(_ascii_text(item))}', style, bulletText='-')
        for item in items
    ]


def _birth_summary_heading(report):
    baby_name = str(report.get('baby_name') or '').strip()
    return f'Birth Summary of {baby_name}' if baby_name else 'Birth Summary of the Newborn Baby'


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
        fontSize=22, leading=28, textColor=DARK, alignment=TA_CENTER, spaceAfter=3 * mm,
    )
    subtitle_style = ParagraphStyle(
        'ReportSubtitle', parent=sample_styles['Normal'], fontName='Helvetica',
        fontSize=11, leading=16, textColor=MUTED, alignment=TA_CENTER, spaceAfter=5 * mm,
    )
    heading_style = ParagraphStyle(
        'SectionHeading', parent=sample_styles['Heading2'], fontName='Helvetica-Bold',
        fontSize=15, leading=20, textColor=TEAL, spaceBefore=4 * mm, spaceAfter=2.5 * mm,
        keepWithNext=True,
    )
    major_heading_style = ParagraphStyle(
        'MajorSectionHeading', parent=sample_styles['Heading1'], fontName='Helvetica-Bold',
        fontSize=17, leading=22, textColor=colors.white, spaceAfter=0,
    )
    body_style = ParagraphStyle(
        'Body', parent=sample_styles['BodyText'], fontName='Helvetica',
        fontSize=11, leading=16, textColor=DARK, alignment=TA_LEFT, spaceAfter=1.5 * mm,
    )
    small_style = ParagraphStyle('Small', parent=body_style, fontSize=11, leading=16, textColor=MUTED)
    label_style = ParagraphStyle(
        'Label', parent=body_style, fontName='Helvetica-Bold', fontSize=11, leading=16, textColor=MUTED,
    )
    header_style = ParagraphStyle('TableHeader', parent=label_style, textColor=colors.white)
    center_style = ParagraphStyle('Center', parent=body_style, alignment=TA_CENTER)
    bullet_style = ParagraphStyle(
        'Bullet', parent=body_style, leftIndent=10, firstLineIndent=-7,
        bulletIndent=2, spaceAfter=5,
    )

    story = [
        _paragraph('Assessment Results', title_style),
        _paragraph('Summary of newborn risk indicators', subtitle_style),
    ]
    if report.get('recalculation_note'):
        story.append(_paragraph(report['recalculation_note'], small_style))
    generated_at = report.get('generated_at', '')
    if generated_at:
        story.append(_paragraph(f'Generated: {generated_at}', small_style))

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
    birth_value_style = ParagraphStyle('BirthValue', parent=body_style, fontName='Helvetica-Bold', fontSize=11)
    for row_start in range(0, len(birth_cells), 3):
        birth_rows.append([
            [_paragraph(label, label_style), _paragraph(value, birth_value_style)]
            for label, value in birth_cells[row_start:row_start + 3]
        ])
    birth_table = Table(birth_rows, colWidths=[58 * mm] * 3)
    birth_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), PALE), ('GRID', (0, 0), (-1, -1), 0.5, BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8), ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.extend([Spacer(1, 7 * mm), _section_heading(_birth_summary_heading(report), heading_style), birth_table])
    if str(inputs.get('delivery_complication', '')).startswith('Yes'):
        story.extend(_bullet_paragraphs([
            'Selected complication types provide clinical context.',
            'The calculation uses only whether any complication was reported; individual types do not receive separate numerical weights.',
        ], bullet_style))

    story.append(PageBreak())
    story.append(_major_section_heading('1. Immediate observations and birth record', major_heading_style))

    safety = report.get('safety_override', {})
    if safety.get('active'):
        story.append(_section_heading('Urgent APGAR component alert', heading_style))
        story.extend(_bullet_paragraphs([a['reason'] for a in safety['alerts']], bullet_style))
        story.append(_paragraph(safety['action'], body_style))
        story.append(_paragraph('Component safety rules set the immediate-condition module to High; indices are not probabilities. A low ML estimate cannot cancel this alert.', body_style))

    for notice in report.get('assessment_notices', []):
        story.append(_section_heading(notice['reason'], heading_style))
        story.append(_paragraph(notice['action'], body_style))
        story.append(_paragraph('This assessment notice raises triage independently of the fuzzy index; it does not prescribe treatment.', small_style))

    timeline = report.get('apgar_timeline', [])
    if timeline and not report.get('immediate_observation_summary'):
        story.append(_section_heading('Recorded APGAR observations', heading_style))
        story.append(_paragraph(f"{report.get('apgar_trend', '')}. Latest recorded observation: {report.get('apgar_reference_minute')} minutes after birth. This historical record does not establish the baby's condition now.", body_style))
        for minute in sorted({1, 5} | {o['minute'] for o in timeline}):
            row = next((o for o in timeline if o['minute'] == minute), None)
            if row:
                components = ' / '.join(str(row['components'][k]) for k in ('appearance','pulse','grimace','activity','respiration'))
                story.append(_paragraph(f"{minute} min: A/P/G/A/R {components}; total {row['total']}/10; support: {row['support']}. {row['category']}. Immediate index {row['immediate_index']:.1f}/100 ({row['immediate_level']}). Recommended action: {row['action_label']}.", body_style))
                story.append(_paragraph(row['action'], body_style))
                story.extend(_bullet_paragraphs([n['reason'] for n in row['notices'] + row['alerts']], bullet_style))
            else:
                story.append(_paragraph(f'{minute} min: Not recorded', body_style))
        story.append(_paragraph('Earlier concerns remain documented; a higher total does not confirm their resolution. Scores are not averaged. Scores recorded during support require clinician interpretation.', small_style))
        story.append(_paragraph('Fuzzy inference uses the five components and APGAR total from the latest complete recorded observation, plus whether any delivery complication was reported. Selected complication types are documentation context and do not receive separate numerical weights. Earlier scores provide history, not an averaged input. Risk indices and triage are outputs.', small_style))
        if report.get('repeat_observation_message'):
            story.append(_paragraph(report['repeat_observation_message'], body_style))

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

    component_rows = [[
        _paragraph('Component', header_style),
        _paragraph('Score', header_style),
        _paragraph('Recorded finding', header_style),
        _paragraph('Meaning', header_style),
    ]]
    for component in apgar.get('components', []):
        score = int(component.get('score', 0))
        score_color = RED if score == 0 else AMBER if score == 1 else GREEN
        component_rows.append([
            _paragraph(component.get('name', ''), label_style),
            Paragraph(
                f'<font color="{score_color.hexval()}"><b>{score} / 2</b></font>',
                ParagraphStyle('ComponentScore', parent=center_style, fontSize=14, leading=17),
            ),
            _paragraph(component.get('label', ''), body_style),
            _paragraph(component.get('note', ''), small_style),
        ])
    if len(component_rows) > 1:
        component_table = Table(component_rows, colWidths=[34 * mm, 23 * mm, 50 * mm, 67 * mm], repeatRows=1)
        component_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), TEAL),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, BORDER),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
            ('LEFTPADDING', (0, 0), (-1, -1), 7), ('RIGHTPADDING', (0, 0), (-1, -1), 7),
            ('TOPPADDING', (0, 0), (-1, -1), 7), ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ]))
        story.extend([Spacer(1, 2 * mm), component_table])

    story.append(PageBreak())
    story.append(_major_section_heading('2. Assessment module results', major_heading_style))

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
                f'<font size="11">Risk Index: <b>{risk_index:.1f} / 100</b> &nbsp; '
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

    twins = report.get('twin_context')
    if twins:
        story.append(_section_heading('Twin assessment identity', heading_style))
        story.append(_paragraph(f"Twin 1: {twins['twin_1_name']}; Twin 2: {twins['twin_2_name']}. This report assesses Twin {twins['assessed_twin']} only. The other twin requires a separate assessment.", body_style))

    ml = report.get('ml_research')
    story.append(PageBreak())
    story.append(_major_section_heading('3. ML research estimate', major_heading_style))
    story.append(_section_heading('Recorded NICU admission estimate', heading_style))
    if ml and ml.get('status') == 'available':
        story.append(_paragraph(f"Research-only estimate: {ml['probability_percent']:.1f}% probability of recorded NICU admission. Model: {ml['model_version']}.", body_style))
        inputs_ml = ml.get('inputs', {})
        story.append(_paragraph(f"Model inputs: {inputs_ml.get('gestational_age_weeks')} weeks, {inputs_ml.get('birth_weight_g')} g, maternal age {inputs_ml.get('maternal_age')} years. Singleton birth.", body_style))
        encoding_ml = ml.get('input_encoding')
        if encoding_ml:
            story.append(_paragraph(f"Recorded gestation: {encoding_ml['recorded_gestational_weeks']} weeks. ML uses {encoding_ml['completed_gestational_weeks']} completed weeks in CDC format. Clinical and fuzzy inputs remain unchanged.", body_style))
        evaluation_ml = ml.get('evaluation', {})
        metric_rows = [
            [_paragraph('Metric', header_style), _paragraph('Value', header_style), _paragraph('Meaning', header_style)],
            [_paragraph('AUROC - Area Under the Receiver Operating Characteristic Curve', body_style), _paragraph(f"{evaluation_ml.get('auroc', 0):.3f}", body_style), _paragraph('Separates admissions from non-admissions across thresholds. Higher is better; 0.5 is similar to chance and 1.0 is perfect separation.', small_style)],
            [_paragraph('AUPRC - Area Under the Precision-Recall Curve', body_style), _paragraph(f"{evaluation_ml.get('auprc', 0):.3f}", body_style), _paragraph('Summarizes precision and recall for admission. Higher is better, but the value depends on admission prevalence.', small_style)],
            [_paragraph('Brier score - probability prediction error score (not an abbreviation)', body_style), _paragraph(f"{evaluation_ml.get('brier', 0):.4f}", body_style), _paragraph('Average squared difference between predicted probabilities and recorded outcomes. Lower is better; 0 is perfect.', small_style)],
        ]
        metric_table = Table(metric_rows, colWidths=[62 * mm, 22 * mm, 90 * mm], repeatRows=1)
        metric_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), TEAL), ('GRID', (0, 0), (-1, -1), 0.5, BORDER),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6), ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.extend([
            _section_heading('Historical 2023 model evaluation', heading_style),
            _paragraph(f"Evaluation records: {evaluation_ml.get('n')}", small_style),
            Spacer(1, 1.5 * mm), metric_table,
        ])
    else:
        story.append(_paragraph('Estimate unavailable. ' + (ml.get('reason', '') if ml else 'No ML estimate was recorded for this assessment.'), body_style))
    ml_facts = ['Research only: a low estimate cannot establish safety. APGAR alerts and module actions remain independent; this estimate does not determine admission, treatment, or discharge.']
    if ml:
        if ml.get('scope'):
            ml_facts.append(ml['scope'])
        ml_facts.extend(ml.get('limitations', []))
    story.append(_section_heading('Model scope and interpretation facts', heading_style))
    story.extend(_bullet_paragraphs(ml_facts, bullet_style))

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
    story.append(PageBreak())
    story.append(_major_section_heading('4. Charts and clinical monitoring details', major_heading_style))
    if not chart_cells and not report.get('immediate_observation_summary') and not report.get('birth_monitoring'):
        story.append(_paragraph('No additional charts or clinical monitoring details were recorded for this report.', small_style))
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
            _section_heading('Birth input charts', heading_style),
            chart_table,
        ]))

    if report.get('immediate_observation_summary'):
        chart = _scaled_image(plot_paths.get('immediate'), 174 * mm, 82 * mm)
        if chart is not None:
            story.append(chart)
        story.extend(_bullet_paragraphs(['Graph interpretation: curves represent fuzzy rule activation; the vertical line marks the centre-of-area risk index.', 'The index is not a probability; component alerts independently guide action.'], bullet_style))
        story.append(_section_heading('Immediate observation summary and final result', heading_style))
        immediate_facts = report.get('immediate_facts') or [report['immediate_observation_summary']]
        story.extend(_bullet_paragraphs(immediate_facts, bullet_style))
    if report.get('birth_monitoring'):
        birth = report['birth_monitoring']
        story.append(_section_heading('Recorded birth findings and final result', heading_style))
        if birth.get('finding_facts'):
            story.extend(_bullet_paragraphs(birth['finding_facts'], bullet_style))
            story.append(_section_heading('Reason for this result', heading_style))
            story.extend(_bullet_paragraphs(birth['reason_facts'], bullet_style))
        elif birth.get('summary'):
            story.extend(_bullet_paragraphs([birth['summary']], bullet_style))
            story.append(_section_heading('Reason for this result', heading_style))
            story.extend(_bullet_paragraphs([birth['result_reason']], bullet_style))
        else:
            fallback_facts = [f"{finding['name']}: {finding['value']} - {finding['category']}." for finding in birth['inputs']]
            fallback_facts.append(birth['final_result'])
            story.extend(_bullet_paragraphs(fallback_facts, bullet_style))
        for title, key in [('Monitoring concerns', 'concerns'), ('Recommended monitoring actions', 'actions')]:
            story.append(_section_heading(title, heading_style))
            story.extend(_bullet_paragraphs(birth[key], bullet_style))
        story.append(_section_heading('Method and limitations', heading_style))
        story.extend(_bullet_paragraphs([birth['explanation'], birth['limitations']], bullet_style))
    story.append(PageBreak())
    if report.get('module_actions'):
        actions = report['module_actions']
        story.extend([
            _major_section_heading('5. Recommended actions and result', major_heading_style),
            _section_heading('Recommended actions by module', heading_style),
        ])
        module_titles = {
            'Immediate condition': 'Immediate Condition Risk',
            'Birth-related monitoring': 'Birth-Related Monitoring',
            'Family-history follow-up': 'Family-History Follow-up',
        }
        for action in actions:
            story.append(KeepTogether([
                _section_heading(module_titles.get(action['module'], action['module']), heading_style),
                *_bullet_paragraphs([
                    f"Risk level: {action['level']}.",
                    f"Priority: {action['priority']}.",
                    action['action'],
                ], bullet_style),
            ]))
    elif report.get('assessment_semantics') == 'separate-v3':
        story.append(KeepTogether([
            _major_section_heading('5. Recommended actions and result', major_heading_style),
            _section_heading('Overall Triage', heading_style),
            _paragraph(report.get('overall_triage', ''), body_style),
            _paragraph(report.get('recommendation', ''), body_style),
            _paragraph('Immediate condition and birth-related monitoring determine triage. Family history guides follow-up separately.', small_style),
            _section_heading('Family-History Follow-up Plan', heading_style),
            _paragraph(report.get('family_history_follow_up', ''), body_style),
        ]))
    else:
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
                f'<font size="11">Risk Index: <b>{overall_risk_index:.1f} / 100</b> &nbsp; '
                f'Risk Level: <b>{_escaped(report.get("risk_level", final_level))}</b> &nbsp; '
                f'Rule clarity (heuristic): <b>{_escaped(report.get("confidence_level", "Low"))}</b><br/>'
                f'{_escaped(report.get("recommendation", ""))}</font>', body_style,
            ),
        ]], colWidths=[40 * mm, 134 * mm])
        overall_box.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), PALE), ('BOX', (0, 0), (-1, -1), 1, final_color),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('LEFTPADDING', (0, 0), (-1, -1), 9),
            ('RIGHTPADDING', (0, 0), (-1, -1), 9), ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(KeepTogether([
            _major_section_heading('5. Recommended actions and result', major_heading_style),
            _section_heading('Overall Assessment Result', heading_style),
            overall_box,
        ]))

    story.append(PageBreak())
    story.append(_major_section_heading('6. Supporting assessment details', major_heading_style))
    confidence_reasons = report.get('confidence_reasons', [])
    if confidence_reasons:
        story.append(KeepTogether([
            _section_heading('Rule clarity basis (heuristic)', heading_style),
            _paragraph('Rule clarity is not calibrated uncertainty or clinical predictive accuracy.', small_style),
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
    if final_chart is not None and report.get('assessment_semantics') != 'separate-v3':
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
