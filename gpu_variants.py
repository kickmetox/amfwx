import sys,ctypes
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx.gpu import GPUCompute,GPUComputePipelineCreateInfo,SHADERFORMAT_DXIL,SHADERFORMAT_DXBC
from amfwx.shaders import compile_dxil,compile_hlsl
g=GPUCompute()
shaders=[
 ('rw-empty','RWStructuredBuffer<float4> output : register(u0);\n[numthreads(1,1,1)] void main() {}'),
 ('rw-write','RWStructuredBuffer<float4> output : register(u0);\n[numthreads(1,1,1)] void main(uint3 id:SV_DispatchThreadID) { output[id.x]=float4(1,0,0,1); }'),
 ('space','RWStructuredBuffer<float4> output : register(u0, space0);\n[numthreads(1,1,1)] void main(uint3 id:SV_DispatchThreadID) { output[id.x]=float4(1,0,0,1); }'),
]
for name,src in shaders:
 for target,fmt in ((8,'dxil'),(4,'dxbc')):
  try:
   b=compile_dxil(src) if fmt=='dxil' else compile_hlsl(src,target='cs_5_1')
   buf=ctypes.create_string_buffer(b,len(b)); i=GPUComputePipelineCreateInfo(); i.code_size=len(b); i.code=ctypes.cast(buf,ctypes.c_void_p); i.entrypoint=b'main'; i.format=target; i.num_readwrite_storage_buffers=1; i.threadcount_x=1; i.threadcount_y=1; i.threadcount_z=1
   p=g.library.SDL_CreateGPUComputePipeline(g.device,ctypes.byref(i)); print(name,fmt,"ok" if p else "fail",g.library.SDL_GetError())
  except Exception as e: print(name,fmt,"err",e)
g.close()
