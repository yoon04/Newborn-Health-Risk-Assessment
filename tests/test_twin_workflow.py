import unittest
from unittest.mock import patch
from flask import render_template
from pypdf import PdfReader
import app as application
from test_validation import valid_form
from test_ml_research import plots
from fuzzy_logic import assess_risk
from persistence import build_assessment_record
from ml_research import estimate_nicu_research
from pdf_report import build_pdf_report

class TwinWorkflowTests(unittest.TestCase):
    def test_both_names_required_for_twins(self):
        values,errors,_=application.validate_submission(valid_form(birth_plurality='twin'))
        self.assertIn('co_twin_name',errors)
        for bad in ['x'*81, 'Invalid\x01name']:
            _,errors,_=application.validate_submission(valid_form(birth_plurality='twin',co_twin_name=bad))
            self.assertIn('co_twin_name',errors)
        _,errors,_=application.validate_submission(valid_form(birth_plurality='twin',co_twin_name='Olivia',assessed_twin='3'))
        self.assertIn('assessed_twin',errors)

    def test_second_twin_identity_survives_storage_and_report(self):
        form=valid_form(birth_plurality='twin',baby_name='Emma',co_twin_name='Olivia',assessed_twin='2')
        values,errors,_=application.validate_submission(form)
        self.assertFalse(errors)
        self.assertEqual(values['baby_name'],'Olivia')
        self.assertEqual(estimate_nicu_research(values)['status'],'unavailable')
        with patch('fuzzy_logic.generate_visualizations',side_effect=plots):
            result=assess_risk(2,2,2,2,2,38.5,3200,28,'vaginal',0,{'status':'no'},'male')
        result.update(baby_name=values['baby_name'],twin_context=values['twin_context'],
                      weight_display='3200 g',ml_research=estimate_nicu_research(values))
        record=build_assessment_record(values,result,form,None)
        self.assertEqual(record.baby_name,'Olivia')
        self.assertEqual(record.result_snapshot['twin_context']['twin_1_name'],'Emma')
        self.assertEqual(record.raw_inputs['co_twin_name'],'Olivia')
        with application.app.test_request_context():
            html=render_template('results.html',results=result)
            self.assertIn('This assessment: Twin 2',html)
            self.assertIn('Start separate assessment for Twin 1',html)
            self.assertIn('Estimate unavailable',html)
            payload=application.build_report_payload(values,result)
            text=' '.join(p.extract_text() for p in PdfReader(build_pdf_report(payload)).pages)
            self.assertIn('This report assesses Twin 2 only',text)
            self.assertIn('Olivia',text)

    def test_plurality_is_before_names_and_other_twin_prefill_has_no_clinical_observations(self):
        client=application.app.test_client()
        html=client.get('/?birth_plurality=twin&baby_name=Emma&co_twin_name=Olivia&assessed_twin=2&birth_week=38&maternal_age=28&birth_weight=3200&appearance=2').get_data(as_text=True)
        self.assertLess(html.index('id="birth_plurality"'),html.index('id="baby_name"'))
        self.assertIn('value="Olivia"',html)
        self.assertIn('value="2" selected>Twin 2',html)
        self.assertNotIn('value="3200"',html)
        self.assertIn('id="co_twin_name"',html)

    def test_singleton_ignores_hidden_twin_names(self):
        values,errors,_=application.validate_submission(valid_form(birth_plurality='singleton',co_twin_name='Other',assessed_twin='2'))
        self.assertFalse(errors)
        self.assertNotIn('twin_context',values)
        self.assertEqual(values['baby_name'],'Baby Emma')
