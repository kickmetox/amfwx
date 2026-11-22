"""Small DSP layer for AMFWX (gain, mix, biquad filters)."""

from __future__ import annotations

import math


class AudioBuffer:
    def __init__(self, channels=2, rate=48000, frames=0):
        self.channels = int(channels)
        self.rate = int(rate)
        self.data = [[0.0] * int(frames) for _ in range(self.channels)]

    @property
    def frames(self):
        return len(self.data[0]) if self.data else 0

    def clear(self):
        for channel in self.data:
            for index in range(len(channel)):
                channel[index] = 0.0
        return self

    def from_interleaved(self, samples):
        frames = len(samples) // max(1, self.channels)
        self.data = [[0.0] * frames for _ in range(self.channels)]
        for frame in range(frames):
            for channel in range(self.channels):
                self.data[channel][frame] = samples[frame * self.channels +
                                                    channel]
        return self

    def to_interleaved(self):
        result = []
        for frame in range(self.frames):
            for channel in range(self.channels):
                result.append(self.data[channel][frame])
        return result


class Gain:
    def __init__(self, gain=1.0):
        self.gain = float(gain)

    def process(self, buffer):
        for channel in buffer.data:
            for index in range(len(channel)):
                channel[index] *= self.gain
        return buffer


class Mixer:
    def __init__(self, gains=None):
        self.gains = list(gains or [])

    def process(self, buffers):
        if not buffers:
            return AudioBuffer()
        frames = min(buffer.frames for buffer in buffers)
        channels = min(buffer.channels for buffer in buffers)
        output = AudioBuffer(channels, buffers[0].rate, frames)
        for index, buffer in enumerate(buffers):
            gain = self.gains[index] if index < len(self.gains) else 1.0
            for channel in range(channels):
                for frame in range(frames):
                    output.data[channel][frame] += (
                        buffer.data[channel][frame] * gain)
        return output


class Biquad:
    """RBJ cookbook biquad; lowpass/highpass."""

    def __init__(self, rate=48000, frequency=1000.0, q=0.707,
                 kind="lowpass"):
        self.rate = float(rate)
        self.frequency = float(frequency)
        self.q = float(q)
        self.kind = kind
        self._state = {}
        self._design()

    def _design(self):
        omega = 2.0 * math.pi * self.frequency / self.rate
        alpha = math.sin(omega) / (2.0 * self.q)
        cos = math.cos(omega)
        if self.kind == "highpass":
            b0 = (1 + cos) / 2
            b1 = -(1 + cos)
            b2 = (1 + cos) / 2
        else:
            b0 = (1 - cos) / 2
            b1 = 1 - cos
            b2 = (1 - cos) / 2
        a0 = 1 + alpha
        a1 = -2 * cos
        a2 = 1 - alpha
        self.b = [b0 / a0, b1 / a0, b2 / a0]
        self.a = [1.0, a1 / a0, a2 / a0]
        self._state = {}

    def process(self, buffer):
        for channel_index, channel in enumerate(buffer.data):
            x1 = x2 = y1 = y2 = 0.0
            for index, sample in enumerate(channel):
                value = (self.b[0] * sample + self.b[1] * x1 +
                         self.b[2] * x2 - self.a[1] * y1 -
                         self.a[2] * y2)
                x2, x1 = x1, sample
                y2, y1 = y1, value
                channel[index] = value
            self._state[channel_index] = (x1, x2, y1, y2)
        return buffer


class DspGraph:
    """Sequential DSP chain: each node receives and returns an AudioBuffer."""

    def __init__(self, nodes=None):
        self.nodes = list(nodes or [])

    def add(self, node):
        self.nodes.append(node)
        return node

    def clear(self):
        self.nodes.clear()
        return self

    def process(self, buffer):
        for node in self.nodes:
            result = node.process(buffer)
            if result is not None:
                buffer = result
        return buffer

    def __len__(self):
        return len(self.nodes)
