import json
import os
import subprocess
import tempfile
from pathlib import Path

import numpy as np
from fontTools.ttLib import TTFont
from matplotlib import font_manager
from webgpu.font import FontAtlas


def load_font_atlas(image_file: str | Path, atlas_file: str | Path) -> FontAtlas:
    image_file = Path(image_file)
    atlas_file = Path(atlas_file)

    if not image_file.exists() or not atlas_file.exists():
        raise FileNotFoundError("Font image or atlas file does not exist.")

    data = json.loads(atlas_file.read_text())
    atlas = data["atlas"]
    w = atlas["width"]
    h = atlas["height"]
    grid = atlas["grid"]
    x_shift = 2 / w
    y_shift = 2 / h
    advance = data["glyphs"][0]["advance"]

    img_data = image_file.read_bytes()
    image = np.frombuffer(img_data, dtype=np.uint8).reshape((h, w, 4))

    charset = " "
    for glyph in data["glyphs"]:
        if "planeBounds" in glyph:
            charset += chr(glyph["unicode"])

    return FontAtlas(
        char_width=grid["cellWidth"],
        char_height=grid["cellHeight"],
        x_shift=x_shift,
        y_shift=y_shift,
        chars_per_row=grid["columns"],
        n_rows=grid["rows"],
        font_size=atlas["size"],
        charset=charset,
        image=image,
        texture=None,
        texture_sampler=None,
        char_map={ord(c): i for i, c in enumerate(charset)},
        advance=advance,
    )


def _get_default_ttf_file() -> Path:
    for f in font_manager.fontManager.ttflist:
        fname = f.fname.lower()
        if "mono" in fname and fname.endswith("-regular.ttf"):
            return Path(f.fname)

    raise FileNotFoundError("No suitable font found. Please specify a font file.")


def get_characters_of_font(font_file: Path):
    unicode_map = set()
    for table in TTFont(font_file)["cmap"].tables:
        unicode_map.update(table.cmap.keys())

    unicode_map.discard(ord(" "))
    for i in range(33):
        unicode_map.discard(i)
    for i in range(0x80, 0xA0):
        unicode_map.discard(i)

    text = "".join([chr(i) for i in sorted(unicode_map)])
    return text


def generate_msdf_font(
    font_file: str | Path | None = None,
    size: float = 32.0,
    pxrange: int = 4,
    pxpadding: int = 2,
    characters: str | None = None,
) -> FontAtlas:
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        font_file = font_file or _get_default_ttf_file()
        print("Using font file:", font_file)
        text = characters or get_characters_of_font(Path(font_file))
        text = text.replace("\\", "\\\\").replace('"', '\\"')
        (tmpdir / "characters.txt").write_text(f'"{text}"', encoding="utf-8")
        cmd = [
            "msdf-atlas-gen",
            "-coloringstrategy distance",
            "-type mtsdf",
            "-pxalign on",
            "-uniformcellconstraint none",
            "-uniformcols 64",
            "-scanline",
            "-format bin",
            f"-pxrange {pxrange}",
            f"-pxpadding {pxpadding}",
            f"-font {font_file}",
            f"-minsize {size}",
            f"-charset characters.txt",
            f"-imageout font.data",
            f"-json font.json",
        ]
        cmd = " ".join(cmd).split()
        subprocess.check_output(cmd, cwd=tmpdir)
        return load_font_atlas(tmpdir / "font.data", tmpdir / "font.json")
