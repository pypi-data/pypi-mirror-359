
<p align="center">
  <img width="248" height="250" src="https://github.com/user-attachments/assets/bfda7415-5798-4de5-90cc-8a07d0b44955" alt="Pillow logo">
</p>

# pyNVTT
## About

A simple Python Wrapper for NVTT3 library, useful to convert most relevant images formats to DDS while doing modding or game development.

---

## Installation
```batch
pip install pynvtt
```
---

## Examples

Minimal PNG to DDS conversion.

```python
from nvtt.surface import Surface
from nvtt.compression import CompressionOptions
from nvtt.output import OutputOptions
from nvtt.context import Context

surface = Surface("texture_01.png")
compression = CompressionOptions()
output = OutputOptions()
output.filename("texture_01.dds")
ctx = Context()
ctx.compress_all(surface, compression, output)
```

You can also use the `EasyDDS` class for your convenience.

```python
from nvtt.easy_dds import EasyDDS

EasyDDS.convert_img("texture_01.png")
```
This will create a DXT1 DDS with default mipmap generation with the same name in the same path.

---

Converting a Pillow image.

```python
from nvtt.surface import Surface
from nvtt.compression import CompressionOptions
from nvtt.output import OutputOptions
from nvtt.context import Context
from nvtt.enums import Format
from PIL import Image

img_surface = Surface(Image.open("texture_01.png"))

compression = CompressionOptions()
compression.format(Format.DXT1)

output = OutputOptions()
output.filename("texture_01.dds")

ctx = Context()
ctx.compress_all(img_surface, compression, output)
```
This will create a DXT1 DDS with default mipmap generation.

---

## Features

- NVTT 3.2.5 (with FreeImage 3.19.0.0)
- Multiple formats support (Mostly every format supported by FreeImage):
  - `.png`
  - `.tga`
  - `.webp`
  - `.jpg/.jpeg`
  - `.bmp`
  - `.tiff/.tif`
  - `.gif`
  - `.hdr`
  - `.dds`
  - `.psd`
- Partial API support:
  Includes `Surface`, `Context`, `OutputOptions`, and `CompressionOptions`.
- Mipmap level detection, minimum level and no mipmaps.
- Every DDS format supported (`DXT1`, `DXT5`, `BC7`, etc.)
- CUDA Acceleration support.

---

## License

Distributed under the [CC0 License](LICENSE).

