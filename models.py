"""Database models for stored newborn risk assessments."""

from sqlalchemy import CheckConstraint, func
from flask_login import UserMixin

from extensions import db


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=True)
    email = db.Column(db.String(320), nullable=True, unique=True, index=True)
    # Nullable keeps legacy users created before authentication readable. New
    # registrations always populate this field with a Werkzeug hash.
    password_hash = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.now())

    assessments = db.relationship(
        'Assessment',
        back_populates='user',
        passive_deletes=True,
    )


class Assessment(db.Model):
    __tablename__ = 'assessments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True,
        index=True,
    )

    # Raw, normalized input values used by the assessment calculation.
    appearance = db.Column(db.SmallInteger, nullable=False)
    pulse = db.Column(db.SmallInteger, nullable=False)
    grimace = db.Column(db.SmallInteger, nullable=False)
    activity = db.Column(db.SmallInteger, nullable=False)
    respiration = db.Column(db.SmallInteger, nullable=False)
    apgar_total = db.Column(db.SmallInteger, nullable=False)
    birth_week = db.Column(db.Numeric(4, 1), nullable=False)
    birth_weight_input = db.Column(db.Numeric(10, 3), nullable=False)
    birth_weight_unit = db.Column(db.String(8), nullable=False)
    birth_weight_g = db.Column(db.Integer, nullable=False)
    maternal_age = db.Column(db.SmallInteger, nullable=False)
    child_gender = db.Column(db.String(20), nullable=False)
    delivery_type = db.Column(db.String(30), nullable=False)
    delivery_complication = db.Column(db.Boolean, nullable=False)
    family_history_status = db.Column(db.String(20), nullable=False)
    family_disease_name = db.Column(db.String(120), nullable=True)
    family_affected_relative = db.Column(db.String(30), nullable=True)
    raw_inputs = db.Column(db.JSON, nullable=False, default=dict)

    # Persisted calculated values. The algorithm version makes historical
    # results distinguishable when the fuzzy rule base changes later.
    immediate_risk_index = db.Column(db.Numeric(6, 2), nullable=False)
    immediate_risk_level = db.Column(db.String(20), nullable=False)
    birth_related_risk_index = db.Column(db.Numeric(6, 2), nullable=False)
    birth_related_risk_level = db.Column(db.String(20), nullable=False)
    family_history_risk_index = db.Column(db.Numeric(6, 2), nullable=False)
    family_history_risk_level = db.Column(db.String(20), nullable=False)
    overall_risk_index = db.Column(db.Numeric(6, 2), nullable=False, index=True)
    risk_level = db.Column(db.String(20), nullable=False, index=True)
    confidence_level = db.Column(db.String(20), nullable=False)
    confidence_reasons = db.Column(db.JSON, nullable=False, default=list)
    main_contributing_factors = db.Column(db.JSON, nullable=False, default=list)
    lower_impact_factors = db.Column(db.JSON, nullable=False, default=list)
    triggered_rules = db.Column(db.JSON, nullable=False, default=list)
    user_guidance = db.Column(db.JSON, nullable=False, default=dict)
    apgar_breakdown = db.Column(db.Text, nullable=False)
    apgar_category = db.Column(db.String(40), nullable=False)
    apgar_severity = db.Column(db.String(20), nullable=False)
    apgar_component_detail = db.Column(db.JSON, nullable=False, default=dict)
    family_history_summary = db.Column(db.Text, nullable=False)
    recommendation = db.Column(db.Text, nullable=False)
    result_snapshot = db.Column(db.JSON, nullable=False, default=dict)
    algorithm_version = db.Column(db.String(40), nullable=False, default='fuzzy-v2', index=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)

    user = db.relationship('User', back_populates='assessments')

    __table_args__ = (
        CheckConstraint('appearance BETWEEN 0 AND 2', name='ck_assess_appearance'),
        CheckConstraint('pulse BETWEEN 0 AND 2', name='ck_assess_pulse'),
        CheckConstraint('grimace BETWEEN 0 AND 2', name='ck_assess_grimace'),
        CheckConstraint('activity BETWEEN 0 AND 2', name='ck_assess_activity'),
        CheckConstraint('respiration BETWEEN 0 AND 2', name='ck_assess_respiration'),
        CheckConstraint('apgar_total BETWEEN 0 AND 10', name='ck_assess_apgar_total'),
        CheckConstraint('birth_weight_g > 0', name='ck_assess_birth_weight'),
    )
