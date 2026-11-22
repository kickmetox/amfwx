"""SDL_GPU compute pipeline test."""

from __future__ import annotations

import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx.gpu import GPUCompute

SOURCE = """
RWStructuredBuffer<float4> output : register(u0, space1);
[numthreads(64,1,1)]
void main(uint3 id : SV_DispatchThreadID) {
    output[id.x] = float4(1, 0, 0, 1);
}
"""


class GPUTests(unittest.TestCase):
    def test_compute_dispatch(self):
        try:
            gpu = GPUCompute()
        except Exception as error:
            self.skipTest(f"GPU nicht verfügbar: {error}")
        try:
            self.assertIn(gpu.driver(), ("direct3d12", "vulkan"))
            try:
                data = gpu.run_compute(SOURCE, 4)
            except Exception as error:
                self.skipTest(f"GPU/Shader nicht verfügbar: {error}")
            values = [struct.unpack_from("<4f", data, index * 16)
                      for index in range(4)]
            self.assertTrue(all(value == (1.0, 0.0, 0.0, 1.0)
                                for value in values))
        finally:
            gpu.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
