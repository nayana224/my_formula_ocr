# Formula OCR

Equation image → editable LaTeX desktop app for Linux and Windows.

## Current features

- Open, paste, or drag/drop an equation image and run OCR automatically.
- Capture a screen region with `Ctrl+Shift+X` and run OCR immediately.
- Copy OCR output automatically in the selected format.
- Choose Raw LaTeX, `$...$`, `\[...\]`, or `equation` output from one selector.
- Keep Auto OCR / Auto Copy / output format preferences between runs.
- Run local OCR through `pix2tex` without sending the image to a remote API.
- Edit recognized LaTeX and preview common math with matplotlib mathtext.
- Search local SQLite history, pin favorites, and delete individual entries.
- Exit safely with `Ctrl+C`; an in-progress OCR is allowed to finish before shutdown.
- Run unit tests on Ubuntu and Windows with GitHub Actions.

## Default workflow

The default settings are optimized to avoid repetitive button clicks:

```text
Open / Paste / Drop / Capture
        ↓
      OCR
        ↓
  Preview + History
        ↓
Clipboard copy
```

`Auto OCR` and `Auto Copy` are enabled by default. Turn either option off in the main window when manual control is preferred. The selected output format is also saved for the next run.

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
| `Ctrl+Shift+X` | Capture region → OCR |
| `Ctrl+Enter` | Run OCR manually |
| `Ctrl+Shift+C` | Copy selected output format |
| `Ctrl+C` in terminal | Safe application shutdown |

Press `Esc` while selecting a capture region to cancel and return to the main window.

## Validation

Core logic can be tested without loading the OCR model:

```bash
python -m pytest -q
python -m flake8 src tests --max-line-length=100
```

## Known limitations

- The preview uses matplotlib `mathtext`, not a full TeX engine. OCR output can still be copied even when preview rendering fails.
- `pix2tex` is intended for mathematical expressions. Non-math screenshots can produce meaningless LaTeX, so results must be reviewed.
- Region capture currently uses Qt screen capture. Linux desktop security policies, especially some Wayland sessions, can block or limit desktop screenshots.
- `Ctrl+Shift+X` is an application shortcut, not a system-wide global hotkey. The Formula OCR window must be focused when starting capture.

## Next milestone

1. Validate the v0.3 automated workflow on Ubuntu and Windows.
2. Add an optional system-wide global hotkey with explicit platform handling.
3. Replace the mathtext preview with a fuller LaTeX/KaTeX rendering path.
4. Add standalone Ubuntu and Windows builds and GitHub Releases.

## License

MIT. Note that bundled or downloaded third-party models and dependencies retain their own licenses.
