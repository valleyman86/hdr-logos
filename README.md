# HDR Images on the Web

A concise warning and demonstration: HDR images can appear much brighter than
surrounding SDR content on ordinary webpages.

The comparison uses two separate 100×100 PNG files:

- `interrobang-sdr.png` — sRGB ICC profile
- `interrobang-hdr.png` — Rec.2020/PQ ICC profile

The files contain the same decoded RGBA pixels and byte-identical compressed
`IDAT` data. Only their embedded `iCCP` chunks differ.

## Verification

Run:

```sh
python3 scripts/verify_images.py interrobang-sdr.png interrobang-hdr.png
```

Expected file hashes:

```text
239d1a2a10ef497020fb58a507add963fb1857f1f8d5a262b81fa5817e8a683e  interrobang-sdr.png
4151d643107bc6de12a337b20f6a4036009d5588010a38ceae04ec74d14a84c7  interrobang-hdr.png
```

Both decode to this RGBA SHA-256 digest:

```text
6965f593d74425378b8072c6904714cf8abfc17191491f53fc8370910a3b8680
```

The site is plain static HTML with no build system or runtime dependencies.
