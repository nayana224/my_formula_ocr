# Formula OCR

Equation image / copied math text → editable LaTeX desktop app for Linux and Windows.

## Current features

- Open or drag/drop an equation image and run OCR automatically.
- `Ctrl+V` Smart Paste: clipboard image → OCR, clipboard text → Text-to-LaTeX conversion.
- Type or paste copied/rendered math text in `Text Input` and see a live LaTeX preview.
- Recover common flattened Unicode math patterns such as superscripts, subscripts, symbols, simple fractions, and selected sum patterns.
- Capture a screen region with `Ctrl+Shift+X` and run OCR immediately.
- Copy OCR/conversion output automatically in the selected format.
- Choose Raw LaTeX, `$...$`, `\[...\]`, or `equation` output from one selector.
- Keep Auto OCR / Auto Copy / output format preferences between runs.
- Run local image OCR through `pix2tex` without sending the image to a remote API.
- Show the rendered Preview as the primary result and keep raw LaTeX as an editable secondary view.
- Show non-blocking warnings for suspicious formula OCR or heuristic Text-to-LaTeX recovery.
- Search local SQLite history, pin favorites, and delete individual entries.
- Exit safely with `Ctrl+C`; an in-progress OCR is allowed to finish before shutdown.
- Run unit tests on Ubuntu and Windows with GitHub Actions.

## Default workflow

```text
Image: Open / Drop / Capture / Smart Paste
                  ↓
                 OCR
                  ↓
          Rendered Preview
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

## Keyboard shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl+O` | Open image |
| `Ctrl+V` | Smart Paste: image OCR or text conversion |
| `Ctrl+Shift+X` | Capture region → OCR |
| `Ctrl+Enter` | Run image OCR manually |
| `Ctrl+Shift+C` | Copy selected output format |
| `Ctrl+C` in terminal | Safe application shutdown |

Press `Esc` while selecting a capture region to cancel and return to the main window.

## Validation

```bash
python -m pytest -q
python -m flake8 src tests --max-line-length=100
```

## Known limitations

- Text-to-LaTeX cannot perfectly restore structure that the source application removed during copy. Warnings mark heuristic or ambiguous recovery.
- The preview uses matplotlib `mathtext`, not a full TeX engine. Output can still be copied when preview rendering fails.
- `pix2tex` is intended for mathematical expressions. Non-math screenshots can produce meaningless LaTeX.
- Region capture currently uses Qt screen capture. Some Wayland policies can block or limit desktop screenshots.
- `Ctrl+Shift+X` is an application shortcut, not a system-wide global hotkey.

## Next milestone

1. Validate v0.4.0 Smart Paste and Text-to-LaTeX on Ubuntu and Windows.
2. Add an optional system-wide global hotkey with explicit platform handling.
3. Replace mathtext preview with a fuller LaTeX/KaTeX rendering path.
4. Evaluate a separate Mixed Text + Formula mode without changing stable Formula mode.
5. Add standalone Ubuntu and Windows builds and GitHub Releases.

## License

MIT. Note that bundled or downloaded third-party models and dependencies retain their own licenses.
