"""Animation layer tests."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx import AnimatedValue, Animation, Timeline, ease_in_out


class AnimationTests(unittest.TestCase):
    def test_easing_and_animation(self):
        self.assertEqual(ease_in_out(0.0), 0.0)
        self.assertEqual(ease_in_out(1.0), 1.0)
        animation = Animation(1.0, 0, 10)
        self.assertEqual(animation.advance(0.5), 5.0)
        self.assertTrue(animation.advance(0.6) == 10.0)
        self.assertTrue(animation.finished)

    def test_timeline_and_animated_value(self):
        timeline = Timeline()
        first = timeline.add(Animation(0.5, 0, 1))
        second = timeline.add(Animation(0.5, 1, 2))
        timeline.advance(0.25)
        self.assertFalse(first.finished)
        timeline.advance(0.5)
        self.assertTrue(timeline.finished)
        value = AnimatedValue(0, 1.0).to(10)
        value.advance(0.5)
        self.assertGreater(value.value, 0)
        value.advance(0.6)
        self.assertEqual(value.value, 10)


if __name__ == "__main__":
    unittest.main(verbosity=2)
