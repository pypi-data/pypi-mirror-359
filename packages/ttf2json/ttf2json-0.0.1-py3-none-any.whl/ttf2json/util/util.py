"""
TRANSFORM COMMANDS TO SVG COMMANDS
Args:
    commands: pen commands
    scale: scale
"""


def commands_to_svg(commands, scale):
    svg_commands = []
    cmds = []
    last_command = ""
    last_m_command = ""
    for command in commands:
        cmd = command[0]
        xys = [
            round(int(float(item)) * scale)
            for item in command[1:].split(" ")
            if item != ""
        ]
        if last_command == "":
            cmds.append([cmd, xys])
            last_command = cmds[-1]
        else:
            if cmd == "V":
                cmds.append(["L", [last_command[-1][-2], xys[0]]])
            elif cmd == "H":
                cmds.append(["L", [xys[0], last_command[-1][-1]]])
            elif cmd == "Z":
                cmds.append(["L", last_m_command[-1]])
            else:
                cmds.append([cmd, xys])
            last_command = cmds[-1]
        if cmd == "M":
            last_m_command = cmds[-1]
    cmds.append(["Z", []])

    for command in cmds:
        if command[0] == "M":
            x, y = command[1]
            svg_commands.append("m {} {}".format(x, y))
        elif command[0] == "L":
            x, y = command[1]
            svg_commands.append("l {} {}".format(x, y))
        elif command[0] == "C":
            x1, y1, x2, y2, x3, y3 = command[1]
            svg_commands.append(
                "c {} {} {} {} {} {}".format(x3, y3, x2, y2, x1, y1)
            )
        elif command[0] == "Q":
            x1, y1, x2, y2 = command[1]
            svg_commands.append("q {} {} {} {}".format(x2, y2, x1, y1))
        elif command[0] == "Z":
            svg_commands.append("z ")
    return " ".join(svg_commands)


def get_specific_name(names, key):
    for name in names:
        if name.nameID == key:
            return name.toUnicode()
    return None


"""
COMPOSE SOME EXTRA SETTINGS
Args:
    ttf: TTFONT
"""


def extra_settings(ttf):
    hhea_table = ttf.get("hhea")
    name_table = ttf.get("name")
    head_table = ttf.get("head")
    post_table = ttf.get("post")
    units_per_em = head_table.unitsPerEm
    scale = (1000 * 100) / (units_per_em * 72)
    names = name_table.names
    resolution = 1000
    bounding_box = {
        "xMin": round(head_table.xMin * scale),
        "yMin": round(head_table.yMin * scale),
        "xMax": round(head_table.xMax * scale),
        "yMax": round(head_table.yMax * scale),
    }
    original_font_information = {
        "format": 0,
        "copyright": get_specific_name(names, 0),
        "fontFamily": get_specific_name(names, 1),
        "fontSubfamily": get_specific_name(names, 2),
        "uniqueID": get_specific_name(names, 3),
        "fullName": get_specific_name(names, 4),
        "version": get_specific_name(names, 5),
        "postScriptName": get_specific_name(names, 6),
        "trademark": get_specific_name(names, 7),
        "manufacturer": get_specific_name(names, 8),
        "designer": get_specific_name(names, 9),
        "manufacturerURL": get_specific_name(names, 11),
        "designerURL": get_specific_name(names, 12),
        "licence": get_specific_name(names, 13),
        "licenceURL": get_specific_name(names, 14),
    }

    return {
        "familyName": get_specific_name(names, 1),
        "ascender": round(hhea_table.ascender * scale),
        "descender": round(hhea_table.descender * scale),
        "underlinePosition": round(post_table.underlinePosition * scale),
        "underlineThickness": round(post_table.underlineThickness * scale),
        "boundingBox": bounding_box,
        "resolution": resolution,
        "original_font_information": original_font_information,
        "cssFontWeight": "normal",
        "cssFontStyle": "normal",
    }
