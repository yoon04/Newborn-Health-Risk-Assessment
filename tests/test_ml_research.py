import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from flask import render_template
from pypdf import PdfReader
import app as application
import ml_research
from fuzzy_logic import assess_risk
from persistence import build_assessment_record
from pdf_report import build_pdf_report
from test_validation import valid_form


def plots(*args, **kwargs):
    return None, {k: '' for k in ('apgar','week','weight','age','genetic','immediate','birth','family','final')}

class MLResearchTests(unittest.TestCase):
    def setUp(self):
        self.values = {'birth_plurality':'singleton', 'birth_week':39,
                       'birth_weight_g':3200, 'maternal_age':29}

    def test_trusted_model_produces_finite_probability(self):
        result = ml_research.estimate_nicu_research(self.values)
        self.assertEqual(result['status'], 'available', result)
        self.assertGreaterEqual(result['probability'], 0)
        self.assertLessEqual(result['probability'], 1)
        self.assertEqual(result['evaluation']['n'], 120000)
        json.dumps(result)

    def test_scope_failures_never_load_or_predict(self):
        cases = [{'birth_plurality':'unknown'}, {'birth_plurality':'multiple'},
                 {'birth_week':19}, {'birth_week':46},
                 {'birth_weight_g':226}, {'birth_weight_g':6000},
                 {'maternal_age':12}, {'maternal_age':50},
                 {'maternal_age':29.5}, {'maternal_age':float('nan')}]
        with patch('ml_research._load_artifacts') as loader:
            for override in cases:
                result = ml_research.estimate_nicu_research(dict(self.values, **override))
                self.assertEqual(result['status'],'unavailable', override)
                self.assertIsNone(result['probability'])
            loader.assert_not_called()

    def test_fractional_gestation_maps_to_completed_weeks_without_mutating_inputs(self):
        for week, expected in [(36.5,36), (37,37), (38.5,38), (39,39), (44.5,44), (45,45)]:
            values = dict(self.values, birth_week=week)
            original = dict(values)
            result = ml_research.estimate_nicu_research(values)
            whole_result = ml_research.estimate_nicu_research(dict(values, birth_week=expected))
            self.assertEqual(result['status'],'available', result)
            self.assertEqual(result['inputs']['gestational_age_weeks'],expected)
            self.assertEqual(result['input_encoding']['recorded_gestational_weeks'],week)
            self.assertEqual(result['probability'],whole_result['probability'])
            self.assertEqual(values,original)

    def test_checksum_mismatch_blocks_deserialization(self):
        ml_research._load_artifacts.cache_clear()
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1]) as directory:
            root=Path(directory)
            (root/'manifest.json').write_text(json.dumps({'model.joblib':'incorrect'}))
            (root/'model.joblib').write_bytes(b'not a model')
            with patch('ml_research.ARTIFACT_DIR',root), patch('joblib.load') as loader:
                with self.assertRaisesRegex(ValueError,'checksum'):
                    ml_research._load_artifacts()
                loader.assert_not_called()
        ml_research._load_artifacts.cache_clear()

    def test_prediction_failure_returns_unavailable(self):
        with patch('ml_research._load_artifacts',side_effect=RuntimeError('missing runtime')):
            with self.assertLogs('ml_research',level='ERROR'):
                result=ml_research.estimate_nicu_research(self.values)
        self.assertEqual(result['status'],'unavailable')
        self.assertIsNone(result['probability'])

    def test_low_ml_probability_cannot_cancel_apgar_override_or_actions(self):
        form=valid_form(birth_plurality='singleton',birth_week='39',pulse='1',respiration='1')
        values,errors,_=application.validate_submission(form)
        self.assertFalse(errors)
        with patch('fuzzy_logic.generate_visualizations',side_effect=plots):
            result=assess_risk(2,1,2,2,1,39,3200,28,'vaginal',0,{'status':'no'},'male')
        before=json.dumps(result['module_actions'])
        estimate=ml_research.estimate_nicu_research(values)
        result['ml_research']=estimate
        self.assertEqual(result['immediate_condition_risk_level'],'High')
        self.assertTrue(result['safety_override']['active'])
        self.assertEqual(json.dumps(result['module_actions']),before)
        result['weight_display']='3200 g'
        result['baby_name']='Baby Test'
        record=build_assessment_record(values,result,form,None)
        self.assertEqual(record.raw_inputs['birth_plurality'],'singleton')
        self.assertEqual(record.result_snapshot['ml_research'],estimate)
        with application.app.test_request_context():
            html=render_template('results.html',results=result)
            self.assertIn('ML research estimate: recorded NICU admission',html)
            self.assertIn('A low estimate cannot establish',html)
            payload=application.build_report_payload(values,result)
            pdf_text=' '.join(p.extract_text() for p in PdfReader(build_pdf_report(payload)).pages)
            self.assertIn('ML research estimate',pdf_text)
            self.assertIn('Research only',pdf_text)

    def test_saved_pdf_uses_original_estimate(self):
        form=valid_form(birth_plurality='singleton',birth_week='39')
        values,_,_=application.validate_submission(form)
        with patch('fuzzy_logic.generate_visualizations',side_effect=plots):
            result=assess_risk(2,2,2,2,2,39,3200,28,'vaginal',0,{'status':'no'},'male')
            result['ml_research']=ml_research.estimate_nicu_research(values)
            record=build_assessment_record(values,result,form,None)
            record.id=123
            with patch('app.estimate_nicu_research') as predictor:
                _,replayed=application._replay_assessment(record)
            predictor.assert_not_called()
        self.assertEqual(replayed['ml_research'],record.result_snapshot['ml_research'])
        with application.app.test_request_context():
            html=render_template('assessment_detail.html',assessment=record,plots={})
            self.assertIn('ML research estimate: recorded NICU admission',html)

    def test_missing_plurality_defaults_unknown_and_invalid_is_rejected(self):
        values,errors,_=application.validate_submission(valid_form())
        self.assertFalse(errors)
        self.assertEqual(values['birth_plurality'],'unknown')
        _,errors,_=application.validate_submission(valid_form(birth_plurality='1 OR 1'))
        self.assertIn('birth_plurality',errors)
