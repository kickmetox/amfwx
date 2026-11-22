"""Small animation/timeline layer for AMFWX."""

from __future__ import annotations

import math


def linear(t):
    return max(0.0, min(1.0, t))


def ease_in(t):
    t = max(0.0, min(1.0, t))
    return t * t


def ease_out(t):
    t = max(0.0, min(1.0, t))
    return 1.0 - (1.0 - t) * (1.0 - t)


def ease_in_out(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def cubic_bezier(x1, y1, x2, y2):
    def easing(t):
        t = max(0.0, min(1.0, t))
        low, high = 0.0, 1.0
        for _ in range(18):
            mid = (low + high) / 2.0
            value = (3 * (1 - mid) ** 2 * mid * x1 +
                     3 * (1 - mid) * mid ** 2 * x2 + mid ** 3)
            if value < t:
                low = mid
            else:
                high = mid
        u = (low + high) / 2.0
        return (3 * (1 - u) ** 2 * u * y1 +
                3 * (1 - u) * u ** 2 * y2 + u ** 3)
    return easing


class Animation:
    def __init__(self, duration=0.3, start=0.0, end=1.0,
                 easing=ease_in_out, on_update=None):
        self.duration = max(0.001, float(duration))
        self.start = start
        self.end = end
        self.easing = easing
        self.on_update = on_update
        self.elapsed = 0.0
        self.finished = False

    def reset(self):
        self.elapsed = 0.0
        self.finished = False
        return self

    def value(self):
        t = min(1.0, self.elapsed / self.duration)
        eased = self.easing(t)
        if isinstance(self.start, (int, float)) and isinstance(
                self.end, (int, float)):
            return self.start + (self.end - self.start) * eased
        return self.end if t >= 1.0 else self.start

    def advance(self, seconds):
        if self.finished:
            return self.value()
        self.elapsed += max(0.0, seconds)
        if self.elapsed >= self.duration:
            self.elapsed = self.duration
            self.finished = True
        if self.on_update is not None:
            self.on_update(self.value())
        return self.value()


class Timeline:
    def __init__(self):
        self.animations = []

    def add(self, animation):
        self.animations.append(animation)
        return animation

    def reset(self):
        for animation in self.animations:
            animation.reset()
        return self

    def advance(self, seconds):
        for animation in self.animations:
            animation.advance(seconds)
        return self

    @property
    def finished(self):
        return all(animation.finished for animation in self.animations)


class AnimatedValue:
    def __init__(self, value, duration=0.3, easing=ease_in_out):
        self.value = value
        self.animation = Animation(duration, value, value, easing)
        self._target = value

    def to(self, target, duration=None):
        self.animation.start = self.value
        self.animation.end = target
        self.animation.duration = max(0.001, float(
            duration if duration is not None else self.animation.duration))
        self.animation.reset()
        self._target = target
        return self

    def advance(self, seconds):
        if self.animation.finished:
            self.value = self._target
            return self.value
        self.value = self.animation.advance(seconds)
        return self.value
