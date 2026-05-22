# -*- coding: utf-8 -*-
"""Gera style.min.css a partir de style.css (Sprint 4 — RNF04)."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "css" / "style.css"
DST = ROOT / "css" / "style.min.css"


def minify(css: str) -> str:
    css = re.sub(r"/\*[\s\S]*?\*/", "", css)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{}:;,>+~])\s*", r"\1", css)
    return css.strip()


def main():
    raw = SRC.read_text(encoding="utf-8")
    DST.write_text(minify(raw), encoding="utf-8")
    print(f"OK: {DST} ({DST.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
