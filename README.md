# Formula OCR

Equation image → editable LaTeX desktop app for Linux and Windows.

## Current features

- Open PNG/JPG/JPEG/WebP/BMP files.
- Drag and drop an equation image.
- Paste an image from the clipboard with `Ctrl+V`.
- Capture a screen region with `Ctrl+Shift+X`, run OCR automatically, and copy raw LaTeX.
- Run local OCR through `pix2tex` without sending the image to a remote API.
- Edit the recognized LaTeX before copying it.
- Preview common LaTeX math using matplotlib mathtext.
- Copy raw LaTeX, `$...$`, `\[...\]`, or `equation` format.
- Search local SQLite history, pin favorites, and delete individual entries.
- Run unit tests on Ubuntu and Windows with GitHub Actions.

## Ubuntu development setup

Test target: Ubuntu 22.04+ with Python 3.10+.

```bash
cd formula_ocr
./scripts/setup_ubuntu.sh
./scripts/check_environment.sh
./scripts/run.sh
```

`pix2tex` can download model checkpoints on the first OCR run. The first run can therefore take longer and requires network access.

### Manual setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
python -m pip install -e ".[ocr,dev]"
python -m formula_ocr
```

## Windows development setup

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[ocr,dev]"
python -m formula_ocr
```

The GUI code is shared across Linux and Windows. Packaging into a standalone executable is planned after OCR/runtime validation on both platforms.

## Keyboard shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl+O` | Open image |
| `Ctrl+V` | Paste clipboard image |
| `Ctrl+Shift+X` | Capture region → OCR → copy raw LaTeX |
| `Ctrl+Enter` | Run OCR |

Press `Esc` while selecting a capture region to cancel and return to the main window.

## Validation

Core logic can be tested without loading the OCR model:

```bash
python -m pytest -q
```

## Known limitations

- The preview uses matplotlib `mathtext`, not a full TeX engine. OCR output can still be copied even when preview rendering fails.
- `pix2tex` is intended for mathematical expressions. Non-math screenshots can produce meaningless LaTeX, so results must be reviewed.
- Region capture currently uses Qt screen capture. Linux desktop security policies, especially some Wayland sessions, can block or limit desktop screenshots.
- `Ctrl+Shift+X` is an application shortcut, not a system-wide global hotkey. The Formula OCR window must be focused when starting capture.

## Next milestone

1. Validate region capture on Ubuntu X11/Wayland and Windows.
2. Add an optional system-wide global hotkey with explicit platform handling.
3. Replace the mathtext preview with a fuller LaTeX/KaTeX rendering path.
4. Add standalone Ubuntu and Windows builds and GitHub Releases.

## License

MIT. Note that bundled or downloaded third-party models and dependencies retain their own licenses.
