#!/usr/bin/env python3
"""Verify identical decoded pixels and isolate PNG chunk differences."""

from __future__ import annotations

import hashlib
import struct
import sys
import zlib
from pathlib import Path

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def chunks(path: Path):
    data = path.read_bytes()
    if not data.startswith(PNG_SIGNATURE):
        raise ValueError(f"{path} is not a PNG")
    offset = 8
    result = []
    while offset < len(data):
        length = struct.unpack(">I", data[offset : offset + 4])[0]
        kind = data[offset + 4 : offset + 8]
        payload = data[offset + 8 : offset + 8 + length]
        result.append((kind, payload))
        offset += 12 + length
    return result


def decode(path: Path):
    items = chunks(path)
    ihdr = next(payload for kind, payload in items if kind == b"IHDR")
    width, height, depth, color_type, _, _, interlace = struct.unpack(">IIBBBBB", ihdr)
    if depth != 8 or color_type not in (2, 6) or interlace != 0:
        raise ValueError("Verifier supports non-interlaced 8-bit RGB/RGBA PNGs")
    channels = 3 if color_type == 2 else 4
    packed = zlib.decompress(b"".join(p for k, p in items if k == b"IDAT"))
    stride = width * channels
    previous = bytearray(stride)
    rows = []
    cursor = 0
    for _ in range(height):
        filter_type = packed[cursor]
        cursor += 1
        row = bytearray(packed[cursor : cursor + stride])
        cursor += stride
        for index in range(stride):
            left = row[index - channels] if index >= channels else 0
            above = previous[index]
            upper_left = previous[index - channels] if index >= channels else 0
            if filter_type == 1:
                row[index] = (row[index] + left) & 255
            elif filter_type == 2:
                row[index] = (row[index] + above) & 255
            elif filter_type == 3:
                row[index] = (row[index] + ((left + above) // 2)) & 255
            elif filter_type == 4:
                estimate = left + above - upper_left
                choices = (abs(estimate - left), abs(estimate - above), abs(estimate - upper_left))
                predictor = (left, above, upper_left)[choices.index(min(choices))]
                row[index] = (row[index] + predictor) & 255
            elif filter_type != 0:
                raise ValueError(f"Unsupported filter {filter_type}")
        rows.append(bytes(row))
        previous = row
    pixels = b"".join(rows)
    rgb = b"".join(pixels[i : i + 3] for i in range(0, len(pixels), channels))
    alpha = (
        bytes(pixels[i + 3] for i in range(0, len(pixels), 4))
        if channels == 4
        else bytes([255]) * (width * height)
    )
    idat = b"".join(p for k, p in items if k == b"IDAT")
    return width, height, rgb, alpha, idat, items


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: verify_images.py SDR.png HDR.png")
    paths = [Path(arg) for arg in sys.argv[1:]]
    decoded = [decode(path) for path in paths]
    for path, image in zip(paths, decoded):
        print(f"{path}: file_sha256={sha256(path.read_bytes())}")
        print(f"  size={image[0]}x{image[1]} decoded_rgba_sha256={sha256(image[2] + image[3])}")
        print(f"  chunks={[kind.decode('ascii') for kind, _ in image[5]]}")
    assert decoded[0][0:4] == decoded[1][0:4], "Decoded pixels differ"
    assert decoded[0][4] == decoded[1][4], "Compressed IDAT data differs"
    non_profile_0 = [(k, p) for k, p in decoded[0][5] if k != b"iCCP"]
    non_profile_1 = [(k, p) for k, p in decoded[1][5] if k != b"iCCP"]
    assert non_profile_0 == non_profile_1, "A non-profile PNG chunk differs"
    print("PASS: decoded RGBA pixels and IDAT bytes are identical")
    print("PASS: the only PNG chunk difference is iCCP")
