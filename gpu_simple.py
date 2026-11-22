import sys,ctypes
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx.gpu import GPUCompute,GPUComputePipelineCreateInfo,SHADERFORMAT_DXIL
from amfwx.shaders import compile_dxil
src='[numthreads(1,1,1)] void main() {}'
g=GPUCompute(); b=compile_dxil(src); buf=ctypes.create_string_buffer(b,len(b))
i=GPUComputePipelineCreateInfo(); i.code_size=len(b); i.code=ctypes.cast(buf,ctypes.c_void_p); i.entrypoint=b'main'; i.format=SHADERFORMAT_DXIL; i.threadcount_x=1; i.threadcount_y=1; i.threadcount_z=1
p=g.library.SDL_CreateGPUComputePipeline(g.device,ctypes.byref(i)); print("pipeline",p,g.library.SDL_GetError()); g.close()
