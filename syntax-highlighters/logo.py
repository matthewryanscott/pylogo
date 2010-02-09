# This control file provides syntax-highlighting information for the Leo editor.
# It is in the public domain.

# Properties for logo mode.
properties = {
	"indentCloseBrackets": "]",
	"indentOpenBrackets": "[",
	"lineComment": ";",
	"lineUpClosingBracket": "false",
	"noWordSep": "_-+?:",
	"unalignedCloseBrackets": ")",
	"unalignedOpenBrackets": "(",
}

# Attributes dict for logo_main ruleset.
logo_main_attributes_dict = {
	"default": "null",
	"digit_re": "",
	"escape": "\\",
	"highlight_digits": "true",
	"ignore_case": "true",
	"no_word_sep": "_-+?:",
}

# Dictionary of attributes dictionaries for logo mode.
attributesDictDict = {
	"logo_main": logo_main_attributes_dict,
}

# Keywords dict for logo_main ruleset.
logo_main_keywords_dict = {
	"load": "keyword2",
	"list": "keyword3",
	"call": "keyword3",
	"and": "keyword3",
	"arc": "keyword4",
	"arctan": "keyword3",
	"ashift": "keyword3",
	"back": "keyword4",
	"bitand": "keyword3",
	"bitnot": "keyword3",
	"bitor": "keyword3",
	"bitxor": "keyword3",
	"bk": "keyword4",
	"clean": "keyword4",
	"clearscreen": "keyword4",
	"color": "keyword4",
	"color3": "keyword4",
	"cos": "keyword3",
	"cs": "keyword4",
	"define": "keyword2",
	"difference": "keyword3",
	"end": "keyword1",
	"endfill": "keyword4",
	"equal?": "keyword3",
	"equalp": "keyword3",
	"exp": "keyword3",
	"false": "literal2",
	"fd": "keyword4",
	"fence": "keyword4",
	"fill": "keyword4",
	"forward": "keyword4",
	"fs": "keyword4",
	"fullscreen": "keyword4",
	"global": "keyword2",
	"grater?": "keyword3",
	"greaterequal?": "keyword3",
	"greaterequalp": "keyword3",
	"greaterp": "keyword3",
	"heading": "keyword4",
	"hideturtle": "keyword4",
	"home": "keyword4",
	"ht": "keyword4",
	"iff": "keyword2",
	"iffalse": "keyword2",
	"ift": "keyword2",
	"iftrue": "keyword2",
	"int": "keyword3",
	"label": "keyword4",
	"left": "keyword4",
	"less?": "keyword3",
	"lessequalp": "keyword3",
	"lessp": "keyword3",
	"ln": "keyword3",
	"local": "keyword2",
	"localmake": "keyword2",
	"log10": "keyword3",
	"lshift": "keyword3",
	"lt": "keyword4",
	"make": "keyword2",
	"minus": "keyword3",
	"modulo": "keyword3",
	"name": "keyword2",
	"norefreash": "keyword4",
	"not": "keyword3",
	"or": "keyword3",
	"output": "keyword2",
	"pc": "keyword4",
	"pc3": "keyword4",
	"pd": "keyword4",
	"pe": "keyword4",
	"pencolor": "keyword4",
	"pencolor3": "keyword4",
	"pendown": "keyword4",
	"penerase": "keyword4",
	"penpaint": "keyword4",
	"penreverse": "keyword4",
	"penup": "keyword4",
	"penwidth": "keyword4",
	"pos": "keyword4",
	"power": "keyword3",
	"ppt": "keyword4",
	"product": "keyword3",
	"pu": "keyword4",
	"pw": "keyword4",
	"px": "keyword4",
	"quotient": "keyword3",
	"radarctan": "keyword3",
	"radcos": "keyword3",
	"radsin": "keyword3",
	"refreash": "keyword4",
	"remainder": "keyword3",
	"repeat": "keyword2",
	"right": "keyword4",
	"round": "keyword3",
	"rt": "keyword4",
	"scrunch": "keyword4",
	"setbackground": "keyword4",
	"setbg": "keyword4",
	"seth": "keyword4",
	"setheading": "keyword4",
	"setlabelheight": "keyword4",
	"setpalette": "keyword4",
	"setpc": "keyword4",
	"setpen": "keyword4",
	"setpencolor": "keyword4",
	"setpenpattern": "keyword4",
	"setpensize": "keyword4",
	"setpos": "keyword4",
	"setscrunch": "keyword4",
	"setx": "keyword4",
	"setxy": "keyword4",
	"sety": "keyword4",
	"showturtle": "keyword4",
	"sin": "keyword3",
	"splitscren": "keyword4",
	"sqrt": "keyword3",
	"ss": "keyword4",
	"st": "keyword4",
	"startfill": "keyword4",
	"sum": "keyword3",
	"test": "keyword2",
	"textscreen": "keyword4",
	"thing": "keyword2",
	"to": "keyword1",
	"towards": "keyword4",
	"true": "literal2",
	"ts": "keyword4",
	"window": "keyword4",
	"wrap": "keyword4",
	"xcor": "keyword4",
	"ycor": "keyword4",
}

# Dictionary of keywords dictionaries for logo mode.
keywordsDictDict = {
	"logo_main": logo_main_keywords_dict,
}

# Rules for logo_main ruleset.

def logo_rule0(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="literal3", pattern=":",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def logo_rule1(colorer, s, i):
    return colorer.match_mark_following(s, i, kind="literal1", pattern="\"",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, exclude_match=False)

def logo_rule2(colorer, s, i):
    return colorer.match_seq(s, i, kind="literal4", seq="0",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def logo_rule3(colorer, s, i):
    return colorer.match_seq(s, i, kind="literal4", seq="1",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def logo_rule4(colorer, s, i):
    return colorer.match_seq(s, i, kind="literal4", seq="2",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def logo_rule5(colorer, s, i):
    return colorer.match_seq(s, i, kind="literal4", seq="3",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def logo_rule6(colorer, s, i):
    return colorer.match_seq(s, i, kind="literal4", seq="4",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def logo_rule7(colorer, s, i):
    return colorer.match_seq(s, i, kind="literal4", seq="5",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def logo_rule8(colorer, s, i):
    return colorer.match_seq(s, i, kind="literal4", seq="6",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def logo_rule9(colorer, s, i):
    return colorer.match_seq(s, i, kind="literal4", seq="7",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def logo_rule10(colorer, s, i):
    return colorer.match_seq(s, i, kind="literal4", seq="8",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def logo_rule11(colorer, s, i):
    return colorer.match_seq(s, i, kind="literal4", seq="9",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def logo_rule12(colorer, s, i):
    return colorer.match_seq(s, i, kind="literal4", seq=".",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def logo_rule13(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="[",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def logo_rule14(colorer, s, i):
    return colorer.match_seq(s, i, kind="operator", seq="]",
        at_line_start=False, at_whitespace_end=False, at_word_start=False, delegate="")

def logo_rule15(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment4", seq=";;;;",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False)

def logo_rule16(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment3", seq=";;;",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False)

def logo_rule17(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment2", seq=";;",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False)

def logo_rule18(colorer, s, i):
    return colorer.match_eol_span(s, i, kind="comment1", seq=";",
        at_line_start=False, at_whitespace_end=False, at_word_start=False,
        delegate="", exclude_match=False)

def logo_rule19(colorer, s, i):
    return colorer.match_keywords(s, i)

# Rules dict for logo_main ruleset.
rulesDict1 = {
	"\"": [logo_rule1,],
	".": [logo_rule12,],
	"0": [logo_rule2,logo_rule19,],
	"1": [logo_rule3,logo_rule19,],
	"2": [logo_rule4,logo_rule19,],
	"3": [logo_rule5,logo_rule19,],
	"4": [logo_rule6,logo_rule19,],
	"5": [logo_rule7,logo_rule19,],
	"6": [logo_rule8,logo_rule19,],
	"7": [logo_rule9,logo_rule19,],
	"8": [logo_rule10,logo_rule19,],
	"9": [logo_rule11,logo_rule19,],
	":": [logo_rule0,],
	";": [logo_rule15,logo_rule16,logo_rule17,logo_rule18,],
	"?": [logo_rule19,],
	"@": [logo_rule19,],
	"A": [logo_rule19,],
	"B": [logo_rule19,],
	"C": [logo_rule19,],
	"D": [logo_rule19,],
	"E": [logo_rule19,],
	"F": [logo_rule19,],
	"G": [logo_rule19,],
	"H": [logo_rule19,],
	"I": [logo_rule19,],
	"J": [logo_rule19,],
	"K": [logo_rule19,],
	"L": [logo_rule19,],
	"M": [logo_rule19,],
	"N": [logo_rule19,],
	"O": [logo_rule19,],
	"P": [logo_rule19,],
	"Q": [logo_rule19,],
	"R": [logo_rule19,],
	"S": [logo_rule19,],
	"T": [logo_rule19,],
	"U": [logo_rule19,],
	"V": [logo_rule19,],
	"W": [logo_rule19,],
	"X": [logo_rule19,],
	"Y": [logo_rule19,],
	"Z": [logo_rule19,],
	"[": [logo_rule13,],
	"]": [logo_rule14,],
	"a": [logo_rule19,],
	"b": [logo_rule19,],
	"c": [logo_rule19,],
	"d": [logo_rule19,],
	"e": [logo_rule19,],
	"f": [logo_rule19,],
	"g": [logo_rule19,],
	"h": [logo_rule19,],
	"i": [logo_rule19,],
	"j": [logo_rule19,],
	"k": [logo_rule19,],
	"l": [logo_rule19,],
	"m": [logo_rule19,],
	"n": [logo_rule19,],
	"o": [logo_rule19,],
	"p": [logo_rule19,],
	"q": [logo_rule19,],
	"r": [logo_rule19,],
	"s": [logo_rule19,],
	"t": [logo_rule19,],
	"u": [logo_rule19,],
	"v": [logo_rule19,],
	"w": [logo_rule19,],
	"x": [logo_rule19,],
	"y": [logo_rule19,],
	"z": [logo_rule19,],
}

# x.rulesDictDict for logo mode.
rulesDictDict = {
	"logo_main": rulesDict1,
}

# Import dict for logo mode.
importDict = {}

