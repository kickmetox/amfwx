import sys,struct
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx.gpu import GPUCompute
src='''RWStructuredBuffer<float4> output : register(u0);\n[numthreads(64,1,1)] void main(uint3 id : SV_DispatchThreadID) { output[id.x] = float4(1,0,0,1); }'''
try:
 g=GPUCompute(); print("driver",g.driver()); data=g.run_compute(src,4); print(len(data),[struct.unpack_from('<4f',data,i*16) for i in range(4)]); g.close()
except Exception as e: print("ERR",e)
