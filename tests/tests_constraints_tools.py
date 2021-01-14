import unittest

from tool.constraints_tools import evaluate_condition


class MyTestCase(unittest.TestCase):
    def test_reward_good(self):

        self.assertEqual(evaluate_condition(("cond1", "<", 1, 2, 0), 0), 2)
        self.assertEqual(evaluate_condition(("cond1", "=", 1, 2, 0), 1), 2)
        self.assertEqual(evaluate_condition(("cond1", "<=", 1, 2, 0), 0), 2)
        self.assertEqual(evaluate_condition(("cond1", "!=", 1, 2, 0), 0), 2)

    def test_reward_bad(self):
        self.assertEqual(evaluate_condition(("cond1", "<", 1, 2, 0), 3), 0)
        self.assertEqual(evaluate_condition(("cond1", "=", 1, 2, 0), 3), 0)
        self.assertEqual(evaluate_condition(("cond1", "<=", 1, 2, 0), 3), 0)
        self.assertEqual(evaluate_condition(("cond1", "!=", 1, 2, 0), 0), 0)


if __name__ == '__main__':
    unittest.main()
