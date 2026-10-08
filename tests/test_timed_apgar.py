import unittest
from unittest.mock import patch
from flask import render_template
from pypdf import PdfReader
import app as application
from fuzzy_logic import assess_risk, defuzzify_risk
from apgar_safety import APGAR_FIELDS, check_apgar_safety
from test_validation import valid_form
from test_database import valid_values
from persistence import build_assessment_record
from pdf_report import build_pdf_report


class TimedApgarTests(unittest.TestCase):
    @staticmethod
    def plots(inputs, levels, *args, **kwargs):
        return defuzzify_risk(levels or kwargs['module_risk_levels']['immediate']), {k: '' for k in ('apgar','week','weight','age','genetic','immediate','birth','family','final')}

    @staticmethod
    def observation(minute, scores):
        return {'minute': minute, 'components': dict(zip(APGAR_FIELDS, scores)), 'support': 'unknown'}

    def test_optional_missing_and_complete_repeat_validation(self):
        form = valid_form(apgar_mode='timed')
        values, errors, _ = application.validate_submission(form)
        self.assertFalse(errors)
        self.assertEqual([o['minute'] for o in values['apgar_observations']], [5])
        form.update({f'apgar_10_{k}': '2' for k in APGAR_FIELDS})
        form['apgar_10_pulse'] = '0'
        values, errors, _ = application.validate_submission(form)
        self.assertFalse(errors)
        self.assertEqual(values['pulse'], 0)
        self.assertEqual(values['apgar_observations'][0]['components']['pulse'], 2)

    def test_partial_invalid_or_tampered_observations_rejected(self):
        for changes in ({'apgar_1_pulse': '1'}, {'apgar_10_pulse': '3'},
                        {'apgar_5_support': 'invalid'}, {'apgar_mode': 'invented'}):
            form = valid_form(apgar_mode='timed')
            for key, value in changes.items():
                form[key] = value
            _, errors, _ = application.validate_submission(form)
            self.assertTrue(errors)

    @patch('fuzzy_logic.generate_visualizations', side_effect=plots)
    def test_repeat_scoring_depends_on_total_below_seven(self, _plots):
        for scores in ((2,2,1,2,2), (2,2,2,1,2), (0,2,2,2,2), (2,0,2,2,2), (1,2,1,1,1)):
            result = assess_risk(2,2,2,2,2,39,3200,28,'vaginal',0,{'status':'no'},'male',
                                 apgar_observations=[self.observation(5, scores)])
            self.assertEqual(result['repeat_observations_suggested'], sum(scores) < 7)
        result = assess_risk(2,2,2,2,2,39,3200,28,'vaginal',0,{'status':'no'},'male',
                             apgar_observations=[self.observation(5, (1,2,2,2,2))])
        self.assertFalse(result['repeat_observations_suggested'])

    @patch('fuzzy_logic.generate_visualizations', side_effect=plots)
    def test_latest_observation_used_without_averaging_or_erasing_history(self, _plots):
        timeline = [self.observation(1,(2,0,2,2,2)), self.observation(5,(2,2,1,2,2)), self.observation(10,(2,2,2,2,2))]
        result = assess_risk(2,0,2,2,2,39,3200,28,'vaginal',0,{'status':'no'},'male',apgar_observations=timeline)
        self.assertEqual(result['apgar_score'], 10)
        self.assertEqual(result['apgar_reference_minute'], 10)
        self.assertEqual(result['apgar_trend'], 'Total improved')
        self.assertTrue(result['apgar_timeline'][0]['alerts'])
        self.assertFalse(result['repeat_observations_suggested'])
        self.assertFalse(result['safety_override']['active'])
        self.assertEqual(result['overall_triage'], 'Routine care and observation')

    def test_component_notices_have_distinct_urgency(self):
        for component in ('grimace','activity'):
            for score in (0,1,2):
                values = dict.fromkeys(APGAR_FIELDS,2); values[component] = score
                notices=check_apgar_safety(**values)['notices']
                self.assertEqual(len(notices), 0 if score == 2 else 1)
                if notices:
                    self.assertEqual(notices[0]['urgency'], 'urgent' if score == 0 else 'review')

    @patch('fuzzy_logic.generate_visualizations', side_effect=plots)
    def test_timeline_saved_rendered_and_exported(self, _plots):
        values, raw = valid_values()
        timeline=[self.observation(1,(2,2,1,1,2)),self.observation(5,(2,2,1,2,2))]
        result=assess_risk(2,2,1,2,2,39,3200,28,'vaginal',0,{'status':'no'},'male',apgar_observations=timeline)
        result['weight_display']='3200 g'
        with application.app.app_context():
            record=build_assessment_record(values,result,raw,1); record.id=1
            payload=application.build_report_payload(values,result)
        with application.app.test_request_context('/'):
            html=render_template('results.html',results=result)
            detail=render_template('assessment_detail.html',assessment=record,plots={})
        text='\n'.join(p.extract_text() for p in PdfReader(build_pdf_report(payload)).pages)
        for output in (html,detail,text):
            self.assertIn('Immediate observation summary',output)
            self.assertNotIn('10-minute observation',output)
            self.assertNotIn('10 min: Not recorded',output)
            self.assertNotIn('not green',output)
        self.assertEqual(record.result_snapshot['apgar_timeline'],result['apgar_timeline'])

    def test_form_contains_two_time_points_and_repeat_rows(self):
        with application.app.test_request_context('/'):
            html,_=application.render_assessment_form()
        self.assertIn('1 minute after birth',html)
        self.assertIn('5 minutes after birth',html)
        self.assertIn('id="addRepeatObservation"',html)
        self.assertNotIn('Add clinician-requested observation',html)
        for minute in (1,10,15,20):
            for field in APGAR_FIELDS:
                self.assertIn(f'name="apgar_{minute}_{field}"',html)

    @patch('fuzzy_logic.generate_visualizations', side_effect=plots)
    def test_repeat_boundary_and_completed_repeat(self, _plots):
        for scores in ((1,1,1,1,2),(1,2,1,1,2),(1,2,1,2,2),(1,2,2,2,2),(2,2,2,2,2)):
            result=assess_risk(2,2,2,2,2,39,3200,28,'vaginal',0,{'status':'no'},'male',apgar_observations=[self.observation(5,scores)])
            self.assertEqual(result['repeat_observations_suggested'],sum(scores)<7)
            self.assertEqual(result['apgar_severity'],'good' if sum(scores)>=7 else 'moderate')
        observations=[self.observation(5,(1,1,1,1,2)),self.observation(10,(1,2,2,2,2))]
        result=assess_risk(2,2,2,2,2,39,3200,28,'vaginal',0,{'status':'no'},'male',apgar_observations=observations)
        self.assertFalse(result['repeat_observations_suggested'])
        self.assertTrue(result['repeat_scoring_indicated_at_five'])
        self.assertEqual(result['repeat_observation_status'],'recorded_improvement')
        self.assertEqual(result['inference_input_summary']['apgar_total'],9)
        self.assertEqual(result['inference_input_summary']['reference_minute'],10)

    @patch('fuzzy_logic.generate_visualizations', side_effect=plots)
    def test_green_total_does_not_hide_urgent_component(self,_plots):
        result=assess_risk(2,0,2,2,2,39,3200,28,'vaginal',0,{'status':'no'},'male',apgar_observations=[self.observation(5,(2,0,2,2,2))])
        self.assertEqual(result['apgar_severity'],'good')
        self.assertTrue(result['safety_override']['active'])
        self.assertEqual(result['overall_triage'],'Urgent evaluation')
        self.assertFalse(result['repeat_observations_suggested'])

    @patch('fuzzy_logic.apply_hierarchical_risk_rules', side_effect=AssertionError('Combined inference must not run'))
    @patch('fuzzy_logic.generate_visualizations', side_effect=plots)
    def test_time_specific_actions_and_independent_module_plans(self,_plots,_hierarchy):
        timeline=[self.observation(1,(2,0,2,2,2)),self.observation(5,(1,2,2,2,2))]
        result=assess_risk(2,2,2,2,2,30,1300,28,'vaginal',0,{'status':'no'},'male',apgar_observations=timeline)
        self.assertEqual(result['apgar_timeline'][0]['action_label'],'Urgent evaluation')
        self.assertEqual(result['apgar_timeline'][1]['action_label'],'Routine observation')
        self.assertEqual(len(result['module_actions']),3)
        self.assertEqual(result['module_actions'][0]['priority'],'Routine care and observation')
        self.assertEqual(result['module_actions'][1]['priority'],'Monitoring plan')
        self.assertEqual(result['overall_risk_index'],result['immediate_condition_risk_index'])
        self.assertIsNone(_plots.call_args.args[1])

    @patch('fuzzy_logic.generate_visualizations', side_effect=plots)
    def test_normal_results_hide_empty_additional_slots(self,_plots):
        result=assess_risk(2,2,2,2,2,39,3200,28,'vaginal',0,{'status':'no'},'male',apgar_observations=[self.observation(5,(1,2,2,2,2))])
        with application.app.test_request_context('/'):
            html=render_template('results.html',results=result)
        self.assertIn('Immediate observation summary and final result',html)
        self.assertNotIn('1-minute observation: Not recorded',html)
        self.assertNotIn('10-minute observation',html)
        self.assertNotIn('15-minute observation',html)
        self.assertNotIn('20-minute observation',html)
        self.assertNotIn('Overall Triage',html)
        self.assertIn('Recommended actions by module',html)

    @patch('fuzzy_logic.generate_visualizations', side_effect=plots)
    def test_final_summary_follows_graph_description_without_observation_cards(self,_plots):
        timeline=[self.observation(1,(2,0,2,2,2)),self.observation(5,(1,2,2,2,2))]
        result=assess_risk(2,2,2,2,2,39,3200,28,'vaginal',0,{'status':'no'},'male',apgar_observations=timeline)
        with application.app.test_request_context('/'):
            html=render_template('results.html',results=result)
        result['plot_paths']['immediate']='/static/test-immediate.png'
        with application.app.test_request_context('/'):
            html=render_template('results.html',results=result)
        self.assertLess(html.index('Graph interpretation:'),html.index('Immediate observation summary and final result'))
        self.assertIn('Care concerns', html)
        self.assertIn('Recommended actions', html)
        self.assertIn('Final immediate-condition index:', html)
        self.assertNotIn('<strong>Graph interpretation:', html)
        self.assertIn('1 minutes: APGAR 8/10',html)
        self.assertIn('5 minutes: APGAR 9/10',html)
        self.assertIn('Earlier component concerns remain documented',html)
        self.assertNotIn('Immediate condition by observation time',html)
        self.assertNotIn('Previous observation</h3>',html)
        self.assertIn('View rule explanations and assessment factors',html)
