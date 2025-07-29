import ctypes
from pathlib import Path
from .enums import Filters, WrapMode, AlphaMode, TextureType, RoundMode, Channel
from nvtt.utils.image_helper import get_bytes_from_image
from .core import nvtt


class Surface:
    """High-level wrapper for nvttSurface."""

    def __init__(self, image = None):
        """Creates an empty surface."""
        self._lib = nvtt._lib
        self._ptr = nvtt._lib.nvttCreateSurface()
        self._has_alpha = None
        if not self._ptr:
            raise RuntimeError("Failed to create nvttSurface.")
        
        if image is not None:
            if(type(image) is str):
                if not self.load(image):
                    raise RuntimeError(f"Failed to load image from file: {image}")
            else:
                img_bytes: bytes = get_bytes_from_image(image)
                if img_bytes is not None:
                    if not self.load_from_memory(img_bytes):
                        raise RuntimeError("Failed to load image from memory.")
                else:
                    raise TypeError("image must be a file path or an image object.")

    def __del__(self):
        """Destructor."""
        if getattr(self, "_ptr", None):
            self._lib.nvttDestroySurface(self._ptr)

    def clone(self) -> "Surface":
        "Creates a deep copy of this Surface, with its own internal data."
        new_ptr = self._lib.nvttSurfaceClone(self._ptr)
        if self.is_null:
            raise RuntimeError("Surface is null or has not been initialized.")
        surf: Surface = Surface()
        surf._ptr = new_ptr
        return surf

    @property
    def wrap_mode(self) -> WrapMode:
        """Returns the wrap mode of the surface."""
        return WrapMode(self._lib.nvttSurfaceWrapMode(self._ptr))

    @wrap_mode.setter
    def wrap_mode(self, value: WrapMode) -> None:
        """Set the Surface's wrap mode."""
        if self.is_null:
            raise RuntimeError("Surface is null or has not been initialized.")
        self._lib.nvttSetSurfaceWrapMode(self._ptr, int(value))

    @property
    def alpha_mode(self) -> AlphaMode:
        """Get the alpha mode of the surface."""
        return AlphaMode(self._lib.nvttSurfaceAlphaMode(self._ptr))
    
    @alpha_mode.setter
    def alpha_mode(self, value: AlphaMode) -> None:
        """Set the alpha mode of the surface."""
        if self.is_null:
            raise RuntimeError("Surface is null or has not been initialized.")
        self._lib.nvttSetSurfaceAlphaMode(self._ptr, int(value))

    @property
    def normal_map(self) -> bool:
        """Returns whether the image represents a normal map."""
        if self.is_null:
            raise RuntimeError("Surface is null or has not been initialized.")
        return bool(self._lib.nvttSurfaceIsNormalMap(self._ptr))

    @normal_map.setter
    def normal_map(self, value: bool) -> None:
        """Set whether the Surface represents a normal map, affects whether DDS files are written with the normal map flag"""
        if not isinstance(value, bool):
            raise TypeError("value must be bool")
        self._lib.nvttSetSurfaceNormalMap(self._ptr, value)

    @property
    def is_null(self) -> bool:
        """Returns if the surface is null."""
        return bool(self._lib.nvttSurfaceIsNull(self._ptr))

    @property
    def width(self) -> int:
        """Returns the width (X size) of the surface."""
        return self._lib.nvttSurfaceWidth(self._ptr)

    @property
    def height(self) -> int:
        """Returns the height (Y size) of the surface."""
        return self._lib.nvttSurfaceHeight(self._ptr)

    @property
    def depth(self) -> int:
        """Returns the depth (Z size) of the surface. 1 for 2D surfaces."""
        return self._lib.nvttSurfaceDepth(self._ptr)

    @property
    def type(self) -> TextureType:
        """Returns the dimensionality of the surface."""
        return TextureType(self._lib.nvttSurfaceType(self._ptr))

    def count_mipmaps(self, min_size: int = 1) -> int:
        """Returns the number of mipmaps in a mipmap chain."""
        if self.is_null:
            raise RuntimeError("Surface is null or has not been initialized.")
        return self._lib.nvttSurfaceCountMipmaps(self._ptr, min_size)

    def alpha_test_coverage(self, alpha_ref: float, alpha_channel: int) -> float:
        """Returns the approximate fraction (0 to 1) of the image with an alpha value greater than `alpha_ref`."""
        if self.is_null:
            raise RuntimeError("Surface is null or has not been initialized.")
        return self._lib.nvttSurfaceAlphaTestCoverage(
            self._ptr, alpha_ref, alpha_channel
        )

    def load(self, file: str, expect_signed: bool = False) -> bool:
        """Loads texture data from a file."""
        if not Path.exists(Path(file)):
            raise FileNotFoundError(f"File {file} does not exist.")

        has_alpha = ctypes.c_bool(False)
        result = self._lib.nvttSurfaceLoad(
            self._ptr,
            file.encode("utf-8"),
            ctypes.byref(has_alpha),
            expect_signed,
            None,
        )
        if not result:
            raise RuntimeError(f"Failed to load texture from {file}.")
        self._has_alpha = has_alpha.value
        return True
    
    def load_from_memory(self, data: bytes, expect_signed: bool = False) -> bool:
        """Variant of load() that reads from memory instead of a file."""
        size: int = len(data)
        has_alpha = ctypes.c_bool(False)
        ArrayType = ctypes.c_ubyte * size
        buf = ArrayType.from_buffer_copy(data)
        bytes_ptr = ctypes.cast(buf, ctypes.c_void_p)
        result = self._lib.nvttSurfaceLoadFromMemory(
            self._ptr,
            bytes_ptr,
            size,
            ctypes.byref(has_alpha),
            expect_signed,
            None
        )
        if not result:
            raise RuntimeError("Failed to load texture from memory.")
        
        self._has_alpha = has_alpha.value
        return True
    
    def save(self, file_name: str, is_hdr: bool = False) -> bool:
        """Saves the surface to a file."""
        if self.is_null:
            raise RuntimeError("Surface is null or has not been initialized.")
        result = self._lib.nvttSurfaceSave(self._ptr, file_name.encode("utf-8"), self.has_alpha, is_hdr, None)
        if not result:
            raise RuntimeError(f"Failed to save texture to {file_name}.")
        return result
    
    def resize(self, width: int, 
               height: int, 
               depth: int = 1, 
               filter: Filters = Filters.KAISER,
               filter_width: float = 1.0,
               ) -> None:
        """Resizes this surface to have size (`width` x `height` x `depth`) using a given filter."""
        if self.is_null:
            raise RuntimeError("Surface is null or has not been initialized.")
        self._lib.nvttSurfaceResize(self._ptr, width, height, depth, int(filter), filter_width, None, None)
        
    def resize_max(self, max_extent: int, mode: RoundMode = RoundMode.NONE, filter: Filters = Filters.KAISER) -> None:
        """Resizes this surface so that its largest side has length `max_extent`, subject to a rounding mode."""
        if self.is_null:
            raise RuntimeError("Surface is null or has not been initialized.")
        self._lib.nvttSurfaceResizeMax(self._ptr, max_extent, int(mode), int(filter), None)
        
    def resize_make_square(self, max_extent: int, mode: RoundMode = RoundMode.NONE, filter: Filters = Filters.KAISER) -> None:
        """Resizes this surface so that its longest side has length `max_entent` and the result is square or cubical."""
        if self.is_null:
            raise RuntimeError("Surface is null or has not been initialized.")
        self._lib.nvttSurfaceResizeMakeSquare(self._ptr, max_extent, int(mode), int(filter), None)

    def build_next_mipmap(self, filter: Filters, min_size: int = 1) -> bool:
        """Replaces this surface with a surface the size of the next mip in a mip chain (half the width and height), but with each channel cleared to a constant value."""
        if self.is_null:
            raise RuntimeError("Surface is null or has not been initialized.")
        return self._lib.nvttSurfaceBuildNextMipmapDefaults(
            self._ptr, int(filter), min_size, None
        )
        
    def canvas_size(self, width: int, height: int, depth: int = 1) -> None:
        """Crops or expands this surface from the (0,0,0) corner, with any new values cleared to 0."""
        if self.is_null:
            raise RuntimeError("Surface is null or has not been initialized.")
        self._lib.nvttSurfaceCanvasSize(self._ptr, width, height, depth, None)
        
    def can_make_next_mipmap(self, min_size: int = 1) -> bool:
        """Returns whether a the surface would have a next mip in a mip chain with minimum size `min_size`."""
        if self.is_null:
            raise RuntimeError("Surface is null or has not been initialized.")
        return bool(self._lib.nvttSurfaceCanMakeNextMipmap(self._ptr, min_size))
    
    def to_linear(self, gamma: float = 2.2) -> None:
        """
        Raises RGB channels to the power `gamma`.
        
        `gamma = 2.2` approximates sRGB-to-linear conversion..
        """
        if self.is_null:
            raise RuntimeError("Surface is null or has not been initialized.")
        self._lib.nvttSurfaceToLinear(self._ptr, gamma, None)
        
    def to_gamma(self, gamma: float = 2.2) -> None:
        """
        Raises RGB channels to the power `1/gamma`.

        `gamma = 2.2` approximates linear-to-sRGB conversion.
        """
        if self.is_null:
            raise RuntimeError("Surface is null or has not been initialized.")
        self._lib.nvttSurfaceToLinear(self._ptr, gamma, None)
        
    def to_linear_channel(self, channel: Channel, gamma: float = 2.2) -> None:
        """
        Raises the given channel to the power `gamma`.
        """
        if self.is_null:
            raise RuntimeError("Surface is null or has not been initialized.")
        if channel == Channel.ALPHA:
            print("Warning: Converting the alpha channel to linear is not supported. The alpha channel will be left unchanged.")
            return 
        self._lib.nvttSurfaceToLinearChannel(self._ptr, int(channel), gamma, None)
        
    def to_gamma_channel(self, channel: Channel, gamma: float = 2.2) -> None:
        """
        Raises the given channel to the power `1/gamma`.
        """
        if self.is_null:
            raise RuntimeError("Surface is null or has not been initialized.")
        if channel == Channel.ALPHA:
            print("Warning: Converting the alpha channel to gamma is not supported. The alpha channel will be left unchanged.")
            return 
        self._lib.nvttSurfaceToGammaChannel(self._ptr, int(channel), gamma, None)
        
    def to_srgb(self) -> None:
        """Applies the linear-to-sRGB transfer function to RGB channels."""
        if self.is_null:
            raise RuntimeError("Surface is null or has not been initialized.")
        self._lib.nvttSurfaceToSrgb(self._ptr, None)
        
    def to_srgb_unclamped(self) -> None:
        """Applies the linear-to-sRGB transfer function to RGB channels, but does not clamp output to [0,1]."""
        if self.is_null:
            raise RuntimeError("Surface is null or has not been initialized.")
        self._lib.nvttSurfaceToSrgbUnclamped(self._ptr, None)
        
    def to_linear_from_srgb(self) -> None:
        """Applies the sRGB-to-linear transfer function to RGB channels."""
        if self.is_null:
            raise RuntimeError("Surface is null or has not been initialized.")
        self._lib.nvttSurfaceToLinearFromSrgb(self._ptr, None)
    
    def to_linear_from_srgb_unclamped(self) -> None:
        """Applies the sRGB-to-linear transfer function to RGB channels, but does not clamp output to [0,1]."""
        if self.is_null:
            raise RuntimeError("Surface is null or has not been initialized.")
        self._lib.nvttSurfaceToLinearFromSrgbUnclamped(self._ptr, None)
        
    def to_xenon_srgb(self) -> None:
        """Converts colors in RGB channels from linear to a piecewise linear sRGB approximation."""
        if self.is_null:
            raise RuntimeError("Surface is null or has not been initialized.")
        self._lib.nvttSurfaceToXenonSrgb(self._ptr, None)
        
    def to_linear_from_xenon_srgb(self) -> None:
        """Converts colors in RGB channels from the Xenon sRGB piecewise linear sRGB approximation to linear."""
        if self.is_null:
            raise RuntimeError("Surface is null or has not been initialized.")
        self._lib.nvttSurfaceToLinearFromXenonSrgb(self._ptr, None)

    @property
    def has_alpha(self) -> bool:
        """Returns if the surface has an alpha channel."""
        if self.is_null:
            raise RuntimeError("Surface is null or has not been initialized.")
        return self._has_alpha