from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_submodules


PROJECT_ROOT = Path(SPECPATH).parent

# OCR runtime의 package data와 동적 backend를 standalone 배포물에 포함한다.
datas = collect_data_files("formula_ocr", includes=["assets/katex/**"])
datas += collect_data_files("pix2tex")
hiddenimports = collect_submodules("pix2tex") + collect_submodules("pynput")

analysis = Analysis(
    [str(PROJECT_ROOT / "src" / "formula_ocr" / "__main__.py")],
    pathex=[str(PROJECT_ROOT / "src")],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(analysis.pure)

executable = EXE(
    pyz,
    analysis.scripts,
    [],
    exclude_binaries=True,
    name="FormulaOCR",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
)

bundle = COLLECT(
    executable,
    analysis.binaries,
    analysis.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="FormulaOCR",
)
