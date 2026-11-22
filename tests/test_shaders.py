"""HLSL shader compilation tests."""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from amfwx.shaders import ShaderError, compile_hlsl


SOURCE = """
RWTexture2D<float4> output : register(u0);
[numthreads(8,8,1)]
void main(uint3 id : SV_DispatchThreadID) {
    output[id.xy] = float4(1, 0, 0, 1);
}
"""


class ShaderTests(unittest.TestCase):
    def test_compile_compute(self):
        blob = compile_hlsl(SOURCE)
        self.assertGreater(len(blob), 32)
        self.assertEqual(blob[:4], b"DXBC")

    def test_invalid_shader(self):
        with self.assertRaises(ShaderError):
            compile_hlsl("this is not hlsl")


if __name__ == "__main__":
    unittest.main(verbosity=2)
