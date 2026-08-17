# Formula OCR

Equation image / copied math text → editable LaTeX desktop app for Linux and Windows.

## Current features

- Open or drag/drop an equation image and run OCR automatically.
- `Ctrl+V` Smart Paste: clipboard image → OCR, clipboard text → Text-to-LaTeX conversion.
- Type or paste copied/rendered math text in `Text Input` and see a live LaTeX preview.
- Recover common flattened Unicode math patterns such as superscripts, subscripts, symbols, simple fractions, and selected sum patterns.
- Capture a screen region with `Ctrl+Shift+X` and run OCR immediately.
- Use `Ctrl+Alt+M` as a system-wide capture shortcut on Windows and Ubuntu X11.
- Copy OCR/conversion output automatically in the selected format.
- Choose Raw LaTeX, `$...$`, `\[...\]`, or `equation` output from one selector.
- Keep Auto OCR / Auto Copy / output format preferences between runs.
- Run local image OCR through `pix2tex` without sending the image to a remote API.
- Render Preview with local KaTeX assets when they are installed.
- Fall back automatically to CDN KaTeX, then matplotlib `mathtext`, when local assets are unavailable.
- Keep raw LaTeX as an editable secondary view.
- Show non-blocking warnings for suspicious formula OCR or heuristic Text-to-LaTeX recovery.
- Search local SQLite history, pin favorites, and delete individual entries.
- Exit safely with `Ctrl+C`; an in-progress OCR is allowed to finish before shutdown.
- Run unit tests on Ubuntu and Windows with GitHub Actions.

## Default workflow

```text
Global capture: Ctrl+Alt+M
                  ↓
          Select formula area
                  ↓
                 OCR
                  ↓
       KaTeX Rendered Preview
       └─ fallback: mathtext
                  ↓
       Editable LaTeX + History
                  ↓
           Clipboard copy

Image: Open / Drop / Capture / Smart Paste
                  ↓
                 OCR
                  ↓
       KaTeX Rendered Preview
       └─ fallback: mathtext
                  ↓
       Editable LaTeX + History
                  ↓
           Clipboard copy

Text: Type / Smart Paste
          ↓
  Text → LaTeX normalization
          ↓
    Live Rendered Preview
          ↓
      Convert Text 확정
          ↓
    History + optional copy
```

`Auto OCR` and `Auto Copy` are enabled by default. Text typing updates the preview with a short debounce, but it is only written to History when `Convert Text` or Smart Paste confirms the conversion.

## Preview renderer

Formula OCR v0.6.2 uses a three-stage Preview path:

```text
LaTeX
  ↓
Local KaTeX assets
  ↓ success
Rendered Preview

  └ local assets unavailable
          ↓
      CDN KaTeX

  └ KaTeX unavailable / parse failure
          ↓
matplotlib mathtext fallback
```

Run `python scripts/vendor_katex.py` once while online to download the official KaTeX 0.17.0 pre-built release, verify its SHA-256 digest, and keep only `katex.min.css`, `katex.min.js`, and WOFF2 fonts under `src/formula_ocr/assets/katex/`. After that, rich Preview does not need network access. `./scripts/setup_ubuntu.sh` performs this step automatically.

The KaTeX MIT license is stored alongside the vendored assets. `setuptools` package-data configuration includes the CSS, JavaScript, license, and WOFF2 fonts so later standalone builds can bundle the same offline renderer.

On Linux, Formula OCR adds `--disable-gpu` to `QTWEBENGINE_CHROMIUM_FLAGS` before creating the application. This keeps Qt WebEngine on Chromium's software-rendering path and avoids unnecessary GPU/Vulkan initialization for the lightweight formula Preview. Existing user-provided Chromium flags are preserved. This setting does not disable PyTorch OCR acceleration or change the rest of the Qt Widgets UI.

## Global capture shortcut

Formula OCR tries to start `Ctrl+Alt+M` automatically when the application launches.

- Windows: supported through the `pynput` Windows keyboard backend.
- Ubuntu/Linux X11: supported when an X server is running and `DISPLAY` is available.
- Wayland: currently disabled intentionally. `pynput` only receives limited events through Xwayland, so Formula OCR does not pretend the shortcut is reliable there.

When the global shortcut is available, Formula OCR does not need focus:

```text
PDF / browser / presentation focused
              ↓
         Ctrl+Alt+M
              ↓
       select equation
              ↓
 OCR → Auto Copy → paste anywhere
```

The existing `Ctrl+Shift+X` application shortcut remains available as a fallback when the Formula OCR window is focused.

## Text → LaTeX

The text converter is intentionally best-effort. It removes zero-width characters and handles common copied math forms such as:

```text
x² + y₁          → x^{2}+y_{1}
1/N              → \frac{1}{N}
α ≤ β → ∞        → \alpha\leq\beta\to\infty
L=N1i=1∑N(...)2  → L=\frac{1}{N}\sum_{i=1}^{N}(...)^{2}
```

When layout information has already been lost during copy, reconstruction can be ambiguous. The UI shows a warning instead of silently guessing ambiguous adjacent identifiers such as `mi`.

Formula image OCR currently operates in **Formula mode**. Select only the mathematical expression when possible. Natural-language text mixed into the image can be interpreted as mathematical symbols because `pix2tex` is a formula-recognition model rather than a general text OCR engine.

## Ubuntu development setup

Test target: Ubuntu 22.04+ with Python 3.10+.

```bash
cd formula_ocr
./scripts/setup_ubuntu.sh
./scripts/check_environment.sh
./scripts/run.sh
```

`pix2tex` can download model checkpoints on the first OCR run. The first run can therefore take longer and requires network access.

After pulling a version that adds or changes packaged assets, refresh with:

```bash
source .venv/bin/activate
python scripts/vendor_katex.py
python -m pip install -e ".[ocr,dev]"
```

### Manual setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python scripts/vendor_katex.py
python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
python -m pip install -e ".[ocr,dev]"
python -m formula_ocr
```

## Windows development setup

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python scripts/vendor_katex.py
python -m pip install -e ".[ocr,dev]"
python -m formula_ocr
```

## Keyboard shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl+Alt+M` | Global capture on Windows / Linux X11 |
| `Ctrl+O` | Open image |
| `Ctrl+V` | Smart Paste: image OCR or text conversion |
| `Ctrl+Shift+X` | Focused app capture region → OCR |
| `Ctrl+Enter` | Run image OCR manually |
| `Ctrl+Shift+C` | Copy selected output format |
| `Ctrl+C` in terminal | Safe application shutdown |

Press `Esc` while selecting a capture region to cancel and return to the main window.

## Validation

```bash
python -m pytest -q
python -m flake8 src tests scripts --max-line-length=100
```

## Known limitations

- Text-to-LaTeX cannot perfectly restore structure that the source application removed during copy. Warnings mark heuristic or ambiguous recovery.
- A fresh source checkout needs one online `scripts/vendor_katex.py` run before rich Preview becomes fully offline. If local assets are absent, CDN KaTeX and then local mathtext remain available as fallbacks.
- KaTeX supports a broad subset of TeX but not every LaTeX package or command. Unsupported expressions fall back to mathtext when possible.
- `pix2tex` is intended for mathematical expressions. Non-math screenshots can produce meaningless LaTeX.
- Region capture currently uses Qt screen capture. Some Wayland policies can block or limit desktop screenshots.
- The system-wide `Ctrl+Alt+M` shortcut is currently supported on Windows and Linux X11, but not treated as reliable on Wayland.

## Next milestone

1. Validate v0.6.2 offline KaTeX Preview on Ubuntu and Windows.
2. Add standalone Ubuntu and Windows builds that run `vendor_katex.py` before packaging.
3. Publish signed/versioned GitHub Releases for those standalone builds.
4. Add a Wayland global-shortcut backend through the XDG Desktop Portal where the desktop supports it.
5. Evaluate a separate Mixed Text + Formula mode without changing stable Formula mode.

## License

MIT. Bundled or downloaded third-party models and dependencies retain their own licenses. KaTeX is included under its MIT license.
