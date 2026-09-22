# HDR images on the web

[View the live comparison](https://valleyman86.github.io/hdr-logos/)

Two separate PNG files contain identical decoded RGBA pixels but different ICC
profiles: sRGB and Rec.2020/PQ.

Matching decoded RGBA SHA-256:

```text
6965f593d74425378b8072c6904714cf8abfc17191491f53fc8370910a3b8680
```

Verify locally:

```sh
python3 scripts/verify_images.py interrobang-sdr.png interrobang-hdr.png
```
