## Portable Python runtime (optional, for "no install" targets)

If the target VM does **not** have Python installed, you can bundle a portable runtime
inside the download so the user only needs to unzip and run `start.bat`.

### Recommended: Windows embeddable Python

1) On a build machine, download the official **Windows embeddable** Python zip
matching your architecture (usually x64) and version.

2) Extract it into:

`runtime/python/`

So you end up with:

- `runtime/python/python.exe`
- `runtime/python/python313.zip` (or similar)

3) Rebuild the package with `scripts/build_zip.ps1`.

The generated `start.bat` will automatically use `runtime/python/python.exe` if present.

### Notes

- This does **not** install Python system-wide.
- You may still need to ensure the runtime can run `pip`/wheels; for offline labs,
  provide dependency wheels in `wheelhouse/`.

