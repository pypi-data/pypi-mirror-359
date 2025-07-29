import ctypes
from .surface import Surface
from .compression import CompressionOptions
from .output import OutputOptions
from .enums import Filters
from .core import nvtt

class Context:
    """High-level wrapper for nvttContext."""
    
    def __init__(self):
        """Creates a new instance of Context."""
        self._lib = nvtt._lib
        self._ptr = nvtt._lib.nvttCreateContext()
        if not self._ptr:
            raise RuntimeError("Failed to create NVTT context.")
        
    def __del__(self):
        """Destructor."""
        if getattr(self, '_ptr', None):
            self._lib.nvttDestroyContext(self._ptr)
            
    def enable_cuda_acceleration(self, enabled: bool):
        """Enable CUDA acceleration; initializes CUDA if not already initialized.."""
        if not self._ptr:
            raise RuntimeError("Context has already been destroyed or not initialized.")
        self._lib.nvttSetContextCudaAcceleration(self._ptr, ctypes.c_bool(enabled))
        
    @property
    def is_cuda_acceleration_enabled(self) -> bool:
        """Check if CUDA acceleration is enabled."""
        if not self._ptr:
            raise RuntimeError("Context has already been destroyed or not initialized.")
        return self._lib.nvttContextIsCudaAccelerationEnabled(self._ptr)
    
    def output_header(self, surface: Surface, mipmap_count: int, co: CompressionOptions, oo: OutputOptions):
        """Write the #Container's header to the output."""
        if not self._ptr:
            raise RuntimeError("Context has already been destroyed or not initialized.")
        return self._lib.nvttContextOutputHeader(self._ptr, surface._ptr, mipmap_count, 
                                                 co._ptr, oo._ptr)
        
    def compress(self, surface: Surface, face: int, mipmap: int, co: CompressionOptions, oo: OutputOptions):
        """Compress the Surface and write the compressed data to the output."""
        if not self._ptr:
            raise RuntimeError("Context has already been destroyed or not initialized.")
        return self._lib.nvttContextCompress(self._ptr, surface._ptr, face, mipmap, 
                                             co._ptr, oo._ptr)
        
    def compress_all(self, surface: Surface, co: CompressionOptions, oo: OutputOptions, face=0, min_level = 1, mipmap_filter: Filters = Filters.MITCHELL, do_mips: bool = True):
        """Compress the Surface and write the compressed data to the output including all mipmap levels at once."""
        mipmap_count: int = surface.count_mipmaps(min_level) if do_mips else 1
        self.output_header(surface, mipmap_count, co, oo)
        self.compress(surface, face, 0, co, oo)
        mip: int = 1
        while surface.can_make_next_mipmap(min_level):
            if not surface.build_next_mipmap(int(mipmap_filter), min_level):
                raise RuntimeError(f"Failed to build a mipmap level for surface {surface._ptr}.")
            mip += 1
            if not self.compress(surface, face, mip, co, oo):
                raise RuntimeError(f"Failed to compress the {surface._ptr} surface.")
        
    def estimate_size(self, surface: Surface, mipmap_count: int, co: CompressionOptions):
        """Returns the total compressed size of mips, without compressing the image."""
        if not self._ptr:
            raise RuntimeError("Context has already been destroyed or not initialized.")
        return self._lib.nvttContextEstimateSize(self._ptr, surface._ptr, mipmap_count, co._ptr)