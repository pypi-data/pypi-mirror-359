from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
import json
from .util.util import commands_to_svg, extra_settings


class TTF2JSON:
    def __init__(self, ttf_path: str):
        self.ttf_path = ttf_path
        self.loaded = False

    def _load_ttf(self):
        try:
            self.ttf = TTFont(self.ttf_path)
        except IOError as e:
            print(f"font file can not be read: {self.ttf_path} - {e}")
            raise e
        self.loaded = True

    def convert2json(self, words: str = None):
        if not self.loaded:
            self._load_ttf()
        ttf = self.ttf
        words_dict = dict(zip(words, [1] * len(words)))
        cmap = ttf.getBestCmap()
        mapper = {
            ord(word): cmap[ord(word)]
            for word in words_dict
            if ord(word) in cmap
        }
        return self._convert(mapper)

    def dump2json(self, json_file):
        if not self.loaded:
            self._load_ttf()
        ttf = self.ttf
        cmap = ttf.getBestCmap()
        settings = self._convert(cmap)
        try:
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(settings, f, ensure_ascii=False)
        except Exception as e:
            print(f"fail to write to file:{json_file}")
            raise e

    def _convert(self, mapper):
        ttf = self.ttf
        head_table = ttf.get("head")
        glyf_table = ttf.get("glyf")
        units_per_em = head_table.unitsPerEm
        hmtx_table = ttf.get("hmtx")
        scale = (1000 * 100) / (units_per_em * 72)
        glyfs = {}
        for c in mapper:
            g = glyf_table[mapper[c]]
            if g.numberOfContours > 0:
                spen = SVGPathPen(glyf_table)
                g.draw(spen, glyf_table)
                commands = spen._commands
                obj = {
                    "o": commands_to_svg(commands, scale),
                    "x_min": round(g.xMin * scale),
                    "x_max": round(g.xMax * scale),
                    "ha": round(hmtx_table[mapper[c]][0] * scale),
                }
                glyfs[chr(c)] = obj
        extra = extra_settings(ttf)
        settings = {
            "glyphs": glyfs,
        }
        settings.update(extra)
        return settings
