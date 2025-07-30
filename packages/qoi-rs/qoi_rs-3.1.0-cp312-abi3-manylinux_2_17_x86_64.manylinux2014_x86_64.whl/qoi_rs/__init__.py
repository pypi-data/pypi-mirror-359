from collections.abc import Buffer
from typing import TYPE_CHECKING

from . import types

__all__ = "encode", "decode", "encode_pillow", "decode_pillow"

if TYPE_CHECKING:

    def encode(
        data: types.Data,
        /, *,
        width: int,
        height: int,
        colour_space: types.ColourSpace = None,
        input_channels: types.RawChannels = None,
    ) -> bytes:
        pass

    def decode(data: Buffer, /) -> types.Image:
        pass

else:
    from ._qoi import encode, decode


def encode_pillow(
    image: types.PillowImage,
    /, *,
    colour_space: types.ColourSpace = None,
) -> bytes:
    # TODO: detect mode from arrow image: https://github.com/python-pillow/Pillow/issues/8329
    if image.mode == "RGB":
        # Pillow saves RGB images as RGBX
        mode = "RGBX"  # implementation detail of pillow?
    else:
        mode = image.mode

    return encode(
        image,
        width=image.width,
        height=image.height,
        colour_space=colour_space,
        input_channels=mode,
    )


def decode_pillow(data: Buffer) -> types.PillowImage:
    from PIL import Image
    image = decode(data)
    return Image.frombytes(
        image.mode,
        (image.width, image.height),
        image.data,
    )
