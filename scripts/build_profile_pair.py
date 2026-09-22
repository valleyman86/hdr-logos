#!/usr/bin/env python3
"""Build two PNGs with identical encoded pixels and different ICC profiles."""

from __future__ import annotations

import binascii
import struct
import sys
import zlib
from pathlib import Path

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def chunks(data: bytes):
    if not data.startswith(PNG_SIGNATURE):
        raise ValueError("Not a PNG")
    offset = len(PNG_SIGNATURE)
    while offset < len(data):
        length = struct.unpack(">I", data[offset : offset + 4])[0]
        kind = data[offset + 4 : offset + 8]
        payload = data[offset + 8 : offset + 8 + length]
        yield kind, payload
        offset += 12 + length


def make_chunk(kind: bytes, payload: bytes) -> bytes:
    crc = binascii.crc32(kind + payload) & 0xFFFFFFFF
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", crc)


def extract_icc(png_path: Path) -> bytes:
    for kind, payload in chunks(png_path.read_bytes()):
        if kind == b"iCCP":
            _, compressed = payload.split(b"\0", 1)
            if compressed[0] != 0:
                raise ValueError("Unsupported ICC compression method")
            return zlib.decompress(compressed[1:])
    raise ValueError(f"No ICC profile in {png_path}")


def write_with_profile(source: Path, profile: bytes, destination: Path) -> None:
    source_chunks = list(chunks(source.read_bytes()))
    ihdr = next(payload for kind, payload in source_chunks if kind == b"IHDR")
    idat = b"".join(payload for kind, payload in source_chunks if kind == b"IDAT")
    profile_payload = b"ICC Profile\0\0" + zlib.compress(profile, 9)
    output = b"".join(
        [
            PNG_SIGNATURE,
            make_chunk(b"IHDR", ihdr),
            make_chunk(b"iCCP", profile_payload),
            make_chunk(b"IDAT", idat),
            make_chunk(b"IEND", b""),
        ]
    )
    destination.write_bytes(output)


if __name__ == "__main__":
    if len(sys.argv) != 6:
        raise SystemExit(
            "usage: build_profile_pair.py SOURCE SRGB_ICC PQ_SOURCE_PNG SDR_OUT HDR_OUT"
        )
    source, srgb, pq_source, sdr_out, hdr_out = map(Path, sys.argv[1:])
    write_with_profile(source, srgb.read_bytes(), sdr_out)
    write_with_profile(source, extract_icc(pq_source), hdr_out)

