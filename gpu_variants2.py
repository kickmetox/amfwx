import sys,ctypes
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx.gpu import GPUCompute,GPUComputePipelineCreateInfo
from amfwx.shaders import compile_dxil
g=GPUCompute()
for name,src in [('id','[numthreads(1,1,1)] void main(uint3 id:SV_DispatchThreadID) {}'),('const','RWStructuredBuffer<float4> output : register(u0);\n[numthreads(1,1,1)] void main(){ output[0]=float4(1,0,0,1); }'),('id2','RWStructuredBuffer<float4> output : register(u0);\n[numthreads(1,1,1)] void main(uint3 id:SV_DispatchThreadID){ output[0]=float4(1,0,0,1); }')]:
 b=compile_dxil(src); buf=ctypes.create_string_buffer(b,len(b)); i=GPUComputePipelineCreateInfo(); i.code_size=len(b); i.code=ctypes.cast(buf,ctypes.c_void_p); i.entrypoint=b'main'; i.format=8; i.num_readwrite_storage_buffers=1 if name!='id' else 0; i.threadcount_x=i.threadcount_y=i.threadcount_z=1
 p=g.library.SDL_CreateGPUComputePipeline(g.device,ctypes.byref(i)); print(name,"ok" if p else "fail",g.library.SDL_GetError())
g.close()
