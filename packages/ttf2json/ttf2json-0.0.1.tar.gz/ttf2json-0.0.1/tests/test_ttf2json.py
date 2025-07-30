import os
from ttf2json import TTF2JSON


def test_convert2json():
    ttf_path = os.path.join(os.path.dirname(__file__), "ttf", "arial.ttf")
    ttf2json = TTF2JSON(ttf_path)
    fonts = ttf2json.convert2json("a1")
    assert fonts is not None
    assert len(fonts.get("glyphs")) == 2
    assert fonts.get("glyphs").get("a") is not None
    assert fonts.get("glyphs").get("1") is not None
