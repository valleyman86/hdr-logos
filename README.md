# HDR images on the web

[View the live comparison](https://valleyman86.github.io/hdr-logos/)

Two separate PNG files contain identical decoded RGBA pixels but different ICC
profiles: sRGB and Rec.2020/PQ.

Matching decoded RGBA SHA-256:

```text
6a49a9e642e713eaa478e1752fd3d5d095da1552006203b349589183d563763c
```

Verify locally:

```sh
python3 scripts/verify_images.py interrobang-sdr.png interrobang-hdr.png
```
