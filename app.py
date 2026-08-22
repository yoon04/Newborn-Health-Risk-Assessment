import math
import os
import re
import secrets
from datetime import datetime
from urllib.parse import urlparse

from dotenv import load_dotenv
from flask import Flask, abort, redirect, render_template, request, send_file, url_for
from flask_login import current_user, login_required, login_user, logout_user
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db, login_manager, migrate
from fuzzy_logic import assess_risk, convert_weight_to_grams
from models import Assessment, User
from pdf_report import build_pdf_report
from persistence import save_assessment

# Load project-local configuration before reading DATABASE_URL and SECRET_KEY.
# Existing environment variables remain authoritative (override=False).
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
database_url = os.environ.get('DATABASE_URL', '').strip()
if database_url.startswith('postgres://'):
    database_url = 'postgresql+psycopg://' + database_url[len('postgres://'):]
elif database_url.startswith('postgresql://'):
    database_url = 'postgresql+psycopg://' + database_url[len('postgresql://'):]
if not database_url:
    # A local SQLite fallback keeps the app importable for development/tests.
    # Production deployments should always set DATABASE_URL to PostgreSQL.
    database_url = 'sqlite:///:memory:'
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
migrate.init_app(app, db)
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to continue.'
login_manager.login_message_category = 'info'
REPORT_TOKEN_MAX_AGE_SECONDS = 60 * 60


@login_manager.user_loader
def load_user(user_id):
    try:
        return db.session.get(User, int(user_id))
    except (TypeError, ValueError, SQLAlchemyError):
        db.session.rollback()
        return None

if not os.path.exists('static'):
    os.makedirs('static')

APGAR_FIELDS = ('appearance', 'pulse', 'grimace', 'activity', 'respiration')
WEIGHT_UNITS = {'g', 'kg', 'lb'}
CHILD_GENDERS = {'male', 'female'}
DELIVERY_TYPES = {'vaginal', 'assisted', 'cesarean'}
DELIVERY_COMPLICATIONS = {'0', '1'}
FAMILY_HISTORY_STATUSES = {'yes', 'no', 'unknown'}
AFFECTED_RELATIVES = {'father', 'mother', 'both_parents', 'other_family_member', 'unknown'}
FAMILY_DISEASE_OPTIONS = (
    ('asthma', 'Asthma'),
    ('blood_clotting_disorder', 'Blood clotting disorder'),
    ('breast_cancer', 'Breast cancer'),
    ('colorectal_cancer', 'Colorectal cancer'),
    ('congenital_heart_disease', 'Congenital heart disease'),
    ('cystic_fibrosis', 'Cystic fibrosis'),
    ('diabetes', 'Diabetes'),
    ('epilepsy', 'Epilepsy or seizure disorder'),
    ('familial_hypercholesterolemia', 'Familial high cholesterol'),
    ('hemophilia', 'Hemophilia'),
    ('high_blood_pressure', 'High blood pressure'),
    ('heart_disease', 'Heart disease'),
    ('kidney_disease', 'Kidney disease'),
    ('muscular_dystrophy', 'Muscular dystrophy'),
    ('ovarian_cancer', 'Ovarian cancer'),
    ('prostate_cancer', 'Prostate cancer'),
    ('sickle_cell_disease', 'Sickle cell disease'),
    ('stroke', 'Stroke'),
    ('thalassemia', 'Thalassemia'),
    ('thyroid_cancer', 'Thyroid cancer'),
)
OTHER_FAMILY_DISEASE = ('other_not_listed', 'Other disease / not listed')
FAMILY_DISEASE_LABELS = dict((*FAMILY_DISEASE_OPTIONS, OTHER_FAMILY_DISEASE))
MAX_USER_NAME_LENGTH = 120
MAX_USER_EMAIL_LENGTH = 320
USER_EMAIL_PATTERN = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
MIN_PASSWORD_LENGTH = 8
MIN_BIRTH_WEIGHT_G = 100
MAX_BIRTH_WEIGHT_G = 6000
DECIMAL_NUMBER_PATTERN = re.compile(r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)')


def _parse_finite_number(raw_value):
    """Return a finite float, or None for blank/malformed/non-finite input."""
    value = (raw_value or '').strip()
    if not value or not DECIMAL_NUMBER_PATTERN.fullmatch(value):
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if math.isfinite(parsed) else None


def validate_submission(form):
    """Validate and normalize a submission before fuzzy processing."""
    errors = {}
    values = {}

    for field in APGAR_FIELDS:
        raw_value = (form.get(field) or '').strip()
        if raw_value not in {'0', '1', '2'}:
            errors[field] = 'Select an APGAR score of 0, 1, or 2.'
        else:
            values[field] = int(raw_value)

    raw_week = (form.get('birth_week') or '').strip()
    birth_week = _parse_finite_number(raw_week)
    if birth_week is None:
        errors['birth_week'] = 'Enter a valid gestational age.'
    elif not 20 <= birth_week <= 45:
        errors['birth_week'] = 'Gestational age must be between 20 and 45 weeks.'
    elif not math.isclose(birth_week * 2, round(birth_week * 2), abs_tol=1e-9):
        errors['birth_week'] = 'Gestational age must use half-week increments, such as 38 or 38.5.'
    else:
        values['birth_week'] = birth_week

    raw_age = (form.get('maternal_age') or '').strip()
    if not re.fullmatch(r'\d+', raw_age):
        errors['maternal_age'] = 'Enter the mother\'s age as a whole number.'
    else:
        maternal_age = int(raw_age)
        if not 12 <= maternal_age <= 60:
            errors['maternal_age'] = 'Mother\'s age must be between 12 and 60 years.'
        else:
            values['maternal_age'] = maternal_age

    child_gender = (form.get('child_gender') or '').strip().lower()
    if child_gender not in CHILD_GENDERS:
        errors['child_gender'] = 'Select the child\'s gender.'
    else:
        values['child_gender'] = child_gender

    weight_unit = (form.get('weight_unit') or '').strip().lower()
    raw_weight = (form.get('birth_weight') or '').strip()
    weight_value = _parse_finite_number(raw_weight)
    if weight_unit not in WEIGHT_UNITS:
        errors['birth_weight'] = 'Select a valid birth-weight unit: g, kg, or lb.'
    elif weight_value is None:
        errors['birth_weight'] = 'Enter a valid birth weight.'
    elif weight_value <= 0:
        errors['birth_weight'] = 'Birth weight must be greater than zero.'
    else:
        birth_weight_g = convert_weight_to_grams(weight_value, weight_unit)
        if not MIN_BIRTH_WEIGHT_G <= birth_weight_g < MAX_BIRTH_WEIGHT_G:
            errors['birth_weight'] = 'Birth weight must convert to at least 100 g and less than 6,000 g.'
        else:
            values['weight_value'] = weight_value
            values['weight_unit'] = weight_unit
            values['birth_weight_g'] = birth_weight_g

    delivery_type = (form.get('delivery_type') or '').strip().lower()
    if delivery_type not in DELIVERY_TYPES:
        errors['delivery_type'] = 'Select vaginal, assisted, or Cesarean delivery.'
    else:
        values['delivery_type'] = delivery_type

    raw_complication = (form.get('delivery_comp') or '').strip()
    if raw_complication not in DELIVERY_COMPLICATIONS:
        errors['delivery_comp'] = 'Select whether a delivery complication occurred.'
    else:
        values['delivery_comp'] = int(raw_complication)

    family_status = (form.get('family_history_status') or '').strip().lower()
    disease_choice = (form.get('family_disease') or '').strip().lower()
    affected_relative = (form.get('affected_relative') or '').strip().lower()

    if family_status not in FAMILY_HISTORY_STATUSES:
        errors['family_history_status'] = 'Select Yes, No, or Unknown for family disease history.'
    elif family_status == 'yes':
        if disease_choice not in FAMILY_DISEASE_LABELS:
            errors['family_disease'] = 'Select a disease or choose Other disease / not listed.'
        if affected_relative not in AFFECTED_RELATIVES:
            errors['affected_relative'] = 'Select who has the disease.'

    values['family_history'] = {
        'status': family_status if family_status in FAMILY_HISTORY_STATUSES else '',
        'disease': FAMILY_DISEASE_LABELS.get(disease_choice, '') if family_status == 'yes' else '',
        'affected_relative': affected_relative if family_status == 'yes' and affected_relative in AFFECTED_RELATIVES else '',
    }
    return values, errors, []


def validate_registration(form):
    """Validate registration fields and return normalized values."""
    errors = {}
    name = (form.get('name') or '').strip()
    email = (form.get('email') or '').strip().lower()
    password = form.get('password') or ''
    confirm_password = form.get('confirm_password') or ''

    if not name:
        errors['name'] = 'Enter your name.'
    elif len(name) > MAX_USER_NAME_LENGTH or any(not character.isprintable() for character in name):
        errors['name'] = 'Name must be 120 or fewer printable characters.'

    if not email:
        errors['email'] = 'Enter your email address.'
    elif len(email) > MAX_USER_EMAIL_LENGTH or not USER_EMAIL_PATTERN.fullmatch(email):
        errors['email'] = 'Enter a valid email address.'

    if len(password) < MIN_PASSWORD_LENGTH:
        errors['password'] = f'Password must be at least {MIN_PASSWORD_LENGTH} characters.'
    if password != confirm_password:
        errors['confirm_password'] = 'Passwords do not match.'

    return {
        'name': name,
        'email': email,
        'password': password,
    }, errors


def _safe_next_url(target):
    """Allow only local redirects after login."""
    if not target:
        return None
    parsed = urlparse(target)
    if parsed.scheme or parsed.netloc or not target.startswith('/') or target.startswith('//'):
        return None
    return target


def render_assessment_form(errors=None, form_data=None, family_rows=None, status=200):
    submitted_unit = (form_data or {}).get('weight_unit', 'lb')
    display_weight_unit = submitted_unit if submitted_unit in WEIGHT_UNITS else 'lb'
    return render_template(
        'form.html',
        errors=errors or {},
        form_data=form_data or {},
        family_rows=family_rows or [],
        display_weight_unit=display_weight_unit,
        family_disease_options=FAMILY_DISEASE_OPTIONS,
        other_family_disease=OTHER_FAMILY_DISEASE,
    ), status


def _report_serializer():
    return URLSafeTimedSerializer(app.config['SECRET_KEY'], salt='newborn-pdf-report')


def build_report_payload(values, results):
    component_names = {
        'appearance': 'Appearance',
        'pulse': 'Pulse',
        'grimace': 'Grimace',
        'activity': 'Activity',
        'respiration': 'Respiration',
    }
    components = []
    for field in APGAR_FIELDS:
        detail = results['component_detail'][field]
        components.append({
            'name': component_names[field],
            'score': int(detail['score']),
            'label': detail['label'],
            'note': detail['note'],
        })

    family_conditions = [
        {
            'disease': item['disease'],
            'affected_relative': item['affected_relative'],
            'risk_index': float(item['risk_index']),
        }
        for item in results.get('family_history_items', [])
    ]

    return {
        'generated_at': datetime.now().astimezone().strftime('%Y-%m-%d %H:%M %Z'),
        'inputs': {
            'birth_week': values['birth_week'],
            'birth_weight': results['weight_display'],
            'maternal_age': values['maternal_age'],
            'child_gender': values['child_gender'].title(),
            'delivery_type': results['delivery_type'],
            'delivery_complication': results['delivery_complication'],
            'family_history_status': values['family_history']['status'].title(),
            'family_disease': values['family_history']['disease'],
            'affected_relative': results['family_history_items'][0]['affected_relative'] if results['family_history_items'] else '',
        },
        'apgar': {
            'components': components,
            'total': int(results['apgar_score']),
            'category': results['apgar_category'],
            'breakdown': results['apgar_breakdown'],
        },
        'risk_modules': [
            {
                'name': 'Immediate Condition Risk',
                'label': 'Immediate',
                'risk_index': float(results['immediate_condition_risk_index']),
                'level': results['immediate_condition_risk_level'],
                'description': (
                    'APGAR is the main signal. A reported complication raises concern most '
                    'strongly when APGAR is already concerning.'
                ),
            },
            {
                'name': 'Birth-Related Risk',
                'label': 'Birth Risk',
                'risk_index': float(results['birth_related_risk_index']),
                'level': results['birth_related_risk_level'],
                'description': (
                    'This module uses gestational age, birth weight, maternal age, and delivery '
                    'information with overlapping fuzzy memberships.'
                ),
            },
            {
                'name': 'Family-History Risk',
                'label': 'Family Risk',
                'risk_index': float(results['family_history_risk_index']),
                'level': results['family_history_risk_level'],
                'description': results['family_history_summary'],
            },
        ],
        'family_conditions': family_conditions,
        'plot_paths': results['plot_paths'],
        'overall_risk_index': float(results['overall_risk_index']),
        'risk_level': results['risk_level'],
        'confidence_level': results['confidence_level'],
        'confidence_reasons': results['confidence_reasons'],
        'main_contributing_factors': results['main_contributing_factors'],
        'lower_impact_factors': results['lower_impact_factors'],
        'triggered_rules': results['triggered_rules'],
        'user_guidance': results['user_guidance'],
        'family_history_summary': results['family_history_summary'],
        'recommendation': results['recommendation'],
    }


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    errors = {}
    form_data = {}
    if request.method == 'POST':
        form_data = request.form.to_dict(flat=True)
        values, errors = validate_registration(request.form)
        if not errors:
            try:
                if User.query.filter_by(email=values['email']).first() is not None:
                    errors['email'] = 'An account with this email already exists.'
                else:
                    user = User(
                        name=values['name'],
                        email=values['email'],
                        password_hash=generate_password_hash(values['password']),
                    )
                    db.session.add(user)
                    db.session.commit()
                    login_user(user)
                    return redirect(url_for('index'))
            except IntegrityError:
                db.session.rollback()
                errors['email'] = 'An account with this email already exists.'
            except SQLAlchemyError:
                db.session.rollback()
                app.logger.exception('User registration could not be saved.')
                errors['form'] = 'Registration is temporarily unavailable. Please try again.'

    return render_template('register.html', errors=errors, form_data=form_data)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    errors = {}
    form_data = {}
    next_url = request.args.get('next', '')
    if request.method == 'POST':
        form_data = request.form.to_dict(flat=True)
        email = (request.form.get('email') or '').strip().lower()
        password = request.form.get('password') or ''
        next_url = request.form.get('next') or next_url
        try:
            user = User.query.filter_by(email=email).first() if email else None
            if user is not None and user.password_hash and check_password_hash(user.password_hash, password):
                login_user(user)
                return redirect(_safe_next_url(next_url) or url_for('index'))
            errors['form'] = 'Invalid email or password.'
        except SQLAlchemyError:
            db.session.rollback()
            app.logger.exception('Login lookup failed.')
            errors['form'] = 'Login is temporarily unavailable. Please try again.'

    return render_template(
        'login.html',
        errors=errors,
        form_data=form_data,
        next_url=_safe_next_url(next_url) or '',
    )


@app.get('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        values, errors, family_rows = validate_submission(request.form)
        if errors:
            return render_assessment_form(
                errors=errors,
                form_data=request.form.to_dict(flat=True),
                family_rows=family_rows,
                status=400,
            )

        results = assess_risk(
            values['appearance'], values['pulse'], values['grimace'],
            values['activity'], values['respiration'], values['birth_week'],
            values['birth_weight_g'], values['maternal_age'], values['delivery_type'],
            values['delivery_comp'], values['family_history'], values['child_gender'],
        )
        results['weight_display'] = (
            f"{values['weight_value']} {values['weight_unit']} "
            f"({values['birth_weight_g']:.0f}g)"
        )
        results['assessment_id'] = None
        if results.get('overall_risk_index') is not None:
            try:
                stored_assessment = save_assessment(
                    values,
                    results,
                    request.form.to_dict(flat=True),
                    current_user.id,
                )
                results['assessment_id'] = stored_assessment.id
            except SQLAlchemyError:
                db.session.rollback()
                app.logger.exception('Assessment calculation succeeded but database save failed.')
                results['storage_warning'] = (
                    'The assessment was calculated, but it could not be saved. '
                    'Check the database configuration and migrations.'
                )
        report_payload = build_report_payload(values, results)
        results['pdf_report_token'] = _report_serializer().dumps(report_payload)
        return render_template('results.html', results=results)

    return render_assessment_form()


@app.post('/report.pdf')
@login_required
def download_report():
    token = (request.form.get('report_token') or '').strip()
    try:
        report_payload = _report_serializer().loads(
            token,
            max_age=REPORT_TOKEN_MAX_AGE_SECONDS,
        )
    except SignatureExpired:
        return 'This PDF download link has expired. Please run the assessment again.', 400
    except BadSignature:
        return 'The PDF report request is invalid. Please run the assessment again.', 400

    pdf_stream = build_pdf_report(report_payload)
    return send_file(
        pdf_stream,
        mimetype='application/pdf',
        as_attachment=True,
        download_name='newborn_health_risk_summary.pdf',
        max_age=0,
    )


@app.get('/assessments')
@login_required
def assessment_history():
    try:
        assessments = (
            Assessment.query
            .filter(Assessment.user_id == current_user.id)
            .order_by(Assessment.created_at.desc())
            .limit(100)
            .all()
        )
    except SQLAlchemyError:
        db.session.rollback()
        return render_template(
            'assessments.html',
            assessments=[],
            storage_error='Assessment history is unavailable until the database is configured and migrated.',
        ), 503
    return render_template('assessments.html', assessments=assessments, storage_error='')


@app.get('/assessments/<int:assessment_id>')
@login_required
def assessment_detail(assessment_id):
    try:
        assessment = (
            Assessment.query
            .filter_by(id=assessment_id, user_id=current_user.id)
            .first()
        )
    except SQLAlchemyError:
        db.session.rollback()
        return 'Assessment history is unavailable until the database is configured and migrated.', 503
    if assessment is None:
        abort(404)
    return render_template('assessment_detail.html', assessment=assessment)

if __name__ == '__main__':
    app.run(debug=True)
