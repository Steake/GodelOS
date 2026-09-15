import base64
import copy
import unittest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from godelOS.cognitive_sovereignty.forge_hardening import (
    make_task, verify_claim, validate_oracle_task, paired_power_plan, evaluate_world,
)


class ForgeHardeningTests(unittest.TestCase):
    def setUp(self):
        self.key = Ed25519PrivateKey.generate()
        public = self.key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        self.trust = {'operations': base64.b64encode(public).decode()}
        self.task, self.records = make_task(1, 4711, self.key, self.trust)

    def test_valid_signature_is_not_the_same_as_applicable_policy(self):
        claims = self.records['source']['claims']
        self.assertTrue(verify_claim(claims[2], self.trust))
        self.assertIn(claims[2]['payload']['item_id'], self.records['source']['expected']['rejected'])

    def test_tampering_and_untrusted_signer_are_rejected(self):
        claims = self.records['source']['claims']
        self.assertFalse(verify_claim(claims[4], self.trust))
        self.assertFalse(verify_claim(claims[5], self.trust))
        forged = copy.deepcopy(claims[5]); forged['public_key'] = self.trust['operations']
        self.assertFalse(verify_claim(forged, self.trust))

    def test_independent_oracle_rejects_wrong_answer_and_labels(self):
        self.assertTrue(validate_oracle_task(self.task, self.records, self.trust))
        wrong = copy.deepcopy(self.task)
        wrong['source']['expected_decision'] = 'invented'
        with self.assertRaises(ValueError):
            validate_oracle_task(wrong, self.records, self.trust)
        wrong = copy.deepcopy(self.task); wrong['source']['evidence'][-1]['authenticated'] = True
        with self.assertRaises(ValueError):
            validate_oracle_task(wrong, self.records, self.trust)

    def test_oracle_preserves_tied_optima(self):
        r = copy.deepcopy(self.records['source'])
        optimum = r['expected']['optimal_actions'][0]
        r['world']['plans']['tied'] = copy.deepcopy(r['world']['plans'][optimum])
        result = evaluate_world(r['world'], r['claims'], self.trust)
        self.assertIn('tied', result['optimal_actions'])

    def test_replicas_do_not_inflate_cluster_count(self):
        runs = []
        for replica in range(20):
            for condition, utility in [('identity-bearing', .9), ('content-matched', .8), ('identity-ablated', .8)]:
                runs.append({'cluster_id': 'one-family', 'benchmark_id': str(replica), 'phase': 'transfer',
                             'status': 'completed', 'condition_id': condition, 'scores': {'task_utility': utility}})
        plan = paired_power_plan(runs)
        self.assertFalse(plan['adequately_powered'])
        self.assertEqual(plan['comparisons']['content-matched']['clusters'], 1)

    def test_power_measures_paired_differences_not_raw_utility(self):
        runs = []
        for i in range(8):
            baseline = .2 + i*.05
            for condition, utility in [('identity-bearing', baseline+.1), ('content-matched', baseline), ('identity-ablated', baseline)]:
                runs.append({'cluster_id': str(i), 'benchmark_id': str(i), 'phase': 'transfer',
                             'status': 'completed', 'condition_id': condition, 'scores': {'task_utility': utility}})
        plan = paired_power_plan(runs)
        self.assertEqual(plan['comparisons']['content-matched']['paired_difference_sd'], .075)


if __name__ == '__main__':
    unittest.main()
