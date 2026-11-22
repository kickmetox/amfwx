import sys
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx.shaders import compile_hlsl
src='''RWTexture2D<float4> output : register(u0);\n[numthreads(8,8,1)] void main(uint3 id : SV_DispatchThreadID) { output[id.xy] = float4(1,0,0,1); }'''
b=compile_hlsl(src); print(len(b),b[:4])
