# Formula OCR

Equation image → editable LaTeX desktop app for Linux and Windows.

## Current features

- Open PNG/JPG/JPEG/WebP/BMP files.
- Drag and drop an equation image.
- Paste an image from the clipboard with `Ctrl+V`.
- Run local OCR through `pix2tex` without sending the image to a remote API.
- Edit the recognized LaTeX before copying it.
- Preview common LaTeX math using matplotlib mathtext.
- Copy raw LaTeX, `$...$`, `\[...\]`, or `equation` format.
- Keep the latest 100 recognized formulas in a local SQLite history.
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
| `Ctrl+Enter` | Run OCR |

## Validation

Core logic can be tested without loading the OCR model:

```bash
python -m pytest -q
```

## Known limitations

- The preview uses matplotlib `mathtext`, not a full TeX engine. OCR output can still be copied even when preview rendering fails.
- `pix2tex` is intended for mathematical expressions. Non-math screenshots can produce meaningless LaTeX, so results must be reviewed.
- Region screenshot capture and a system-wide global hotkey are intentionally not in v0.1 because Linux Wayland/X11 and Windows use different capture/security paths. They are the next milestone.

## Next milestone

1. Region screenshot capture with explicit Linux Wayland/X11 handling.
2. Optional system-wide hotkey.
3. Favorite/pinned formulas and history search.
4. Full LaTeX/KaTeX preview.
5. Standalone Ubuntu and Windows builds and GitHub Releases.

## License

MIT. Note that bundled or downloaded third-party models and dependencies retain their own licenses.
