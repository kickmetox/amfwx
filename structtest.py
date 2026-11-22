import sys,ctypes
sys.path.insert(0,r"D:\AI_Temp\AMFWX")
from amfwx.gpu import GPUComputePipelineCreateInfo,GPUShaderCreateInfo,StorageBufferBinding
print(ctypes.sizeof(GPUComputePipelineCreateInfo), [(n,getattr(GPUComputePipelineCreateInfo,n).offset) for n,_ in GPUComputePipelineCreateInfo._fields_])
print(ctypes.sizeof(StorageBufferBinding))
