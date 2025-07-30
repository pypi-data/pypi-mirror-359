import warnings
import json
import argparse
from .ttf2json import TTF2JSON


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--ttf_file", type=str, required=True, help="input ttf font file"
    )
    parser.add_argument(
        "--json_file", type=str, required=True, help="output json file"
    )
    parser.add_argument(
        "--words", type=str, required=False, help="provide words you need"
    )
    parser.add_argument(
        "--words_from_file",
        type=str,
        required=False,
        help="从文件读取需要转换的文字",
    )
    args = parser.parse_args()
    font_file = args.ttf_file
    json_file = args.json_file
    words = args.words
    from_file = args.words_from_file

    if words is not None and from_file is not None:
        warnings.warn(
            "both words and from_file is not empty, prefer words and ignores from_file"
        )

    if from_file is not None:
        try:
            with open(from_file, "r") as ffile:
                try:
                    words = ffile.read()
                except IOError:
                    warnings.warn(
                        f"can not read the open file:{from_file},the file will be ignored"
                    )
        except (FileNotFoundError, PermissionError):
            warnings.warn(
                f"can not open the from file:{from_file},the file will be ignored"
            )

    ttf2json = TTF2JSON(font_file)
    if words is not None:
        settings = ttf2json.convert2json(words)
        try:
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(settings, f, ensure_ascii=False)
        except PermissionError:
            warnings.warn(f"can not write to the json file:{json_file}")
    else:
        ttf2json.dump2json(json_file)
    print("finished")


if __name__ == "__main__":
    main()
