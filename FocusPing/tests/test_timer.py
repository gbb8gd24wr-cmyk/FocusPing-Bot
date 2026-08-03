import unittest

from focusping.timer import Phase, SessionPlan, format_remaining, total_seconds


class PhaseTests(unittest.TestCase):
    def test_phase_rejects_invalid_values(self):
        with self.assertRaises(ValueError):
            Phase("", 60, "focus")
        with self.assertRaises(ValueError):
            Phase("Focus", 0, "focus")
        with self.assertRaises(ValueError):
            Phase("Focus", 60, "pause")


class SessionPlanTests(unittest.TestCase):
    def test_plan_alternates_focus_and_breaks(self):
        plan = SessionPlan(focus_minutes=25, break_minutes=5, cycles=3)

        self.assertEqual(
            [phase.name for phase in plan.phases()],
            ["Focus 1/3", "Break after focus 1", "Focus 2/3", "Break after focus 2", "Focus 3/3"],
        )

    def test_plan_can_skip_breaks(self):
        plan = SessionPlan(focus_minutes=1, break_minutes=1, cycles=2, include_breaks=False)

        self.assertEqual(len(plan.phases()), 2)
        self.assertEqual(total_seconds(plan.phases()), 120)

    def test_plan_rejects_non_positive_values(self):
        with self.assertRaises(ValueError):
            SessionPlan(focus_minutes=0)
        with self.assertRaises(ValueError):
            SessionPlan(cycles=0)


class FormattingTests(unittest.TestCase):
    def test_format_remaining(self):
        self.assertEqual(format_remaining(0), "00:00")
        self.assertEqual(format_remaining(65), "01:05")
        self.assertEqual(format_remaining(-1), "00:00")


if __name__ == "__main__":
    unittest.main()