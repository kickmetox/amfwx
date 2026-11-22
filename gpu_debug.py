import sys,ctypes
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx.gpu import GPUCompute,GPUComputePipelineCreateInfo
from amfwx.shaders import compile_dxil
g=GPUCompute(); # currently debug False
# create a debug device directly
dev=g.library.SDL_CreateGPUDevice(8, True, None); print("debug dev",bool(dev),g.library.SDL_GetError())
src='RWStructuredBuffer<float4> output : register(u0);\n[numthreads(1,1,1)] void main(){ output[0]=float4(1,0,0,1); }'
b=compile_dxil(src); buf=ctypes.create_string_buffer(b,len(b)); i=GPUComputePipelineCreateInfo(); i.code_size=len(b); i.code=ctypes.cast(buf,ctypes.c_void_p); i.entrypoint=b'main'; i.format=8; i.num_readwrite_storage_buffers=1; i.threadcount_x=i.threadcount_y=i.threadcount_z=1
p=g.library.SDL_CreateGPUComputePipeline(dev,ctypes.byref(i)); print("p",p,g.library.SDL_GetError())
