from formula_ocr.ui.latex_preview import build_katex_html


def test_build_katex_html_escapes_user_input() -> None:
    document = build_katex_html(r"x<y & z\"q")

    assert 'data-tex="x&lt;y &amp; z\\&quot;q"' in document
    assert "katex@0.17.0" in document
    assert "throwOnError: true" in document


def test_build_katex_html_does_not_embed_script_from_latex() -> None:
    document = build_katex_html('</script><script>alert("x")</script>')

    assert '&lt;/script&gt;&lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt;' in document
    assert '</script><script>alert("x")</script>' not in document


def test_build_katex_html_uses_relative_assets_for_offline_preview() -> None:
    document = build_katex_html(r"\frac{1}{N}", use_local_assets=True)

    assert 'href="katex.min.css"' in document
    assert 'src="katex.min.js"' in document
    assert "cdn.jsdelivr.net" not in document
    assert "https://" not in document
