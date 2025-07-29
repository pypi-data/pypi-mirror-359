# tests/test_agent_spy.py

import sys
import os

# Add the parent directory to the path so we can import agent_spy
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from agent_spy import AgentSpy

class TestAgentspy(unittest.TestCase):
    def test_initialization(self):
        aw = AgentSpy(model="gpt-4o", enable_monitoring=False)
        self.assertEqual(aw.model, "gpt-4o")
        self.assertEqual(aw.input_tokens, 0)
        self.assertEqual(aw.output_tokens, 0)
        self.assertEqual(aw.total_tokens, 0)
        self.assertEqual(aw.cost, 0.0)

    def test_cost_calculation(self):
        aw = AgentSpy(model="gpt-4o", enable_monitoring=False)
        input_text = "Hello world " * 1000  # Approx 2000 tokens
        output_text = "This is a test response " * 500  # Approx 1000 tokens

        aw.start()  # Start monitoring (with monitoring disabled)
        aw.set_token_counts(input_text=input_text, output_text=output_text)
        aw.end()    # End monitoring and calculate cost

        expected_input_tokens = aw.count_tokens(input_text)
        expected_output_tokens = aw.count_tokens(output_text)
        self.assertEqual(aw.input_tokens, expected_input_tokens)
        self.assertEqual(aw.output_tokens, expected_output_tokens)

        cost = aw.cost_calculator.calculate_cost(aw.input_tokens, aw.output_tokens)
        self.assertAlmostEqual(aw.cost, cost)

if __name__ == '__main__':
    unittest.main()