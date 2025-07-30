from parsimonious import Grammar

PPEG_ADOC = r"""

blocks          = block+

text_line       = ~r"[^\n]+\n" 
line            = ~r"[^\n]+\n"

code_block      = block_title? source_header (delimitted_source_lines / bare_source_lines)
delimitted_source_lines = four_dashes text_line+ four_dashes comment_line*

text = ~r"[-_\w\s\(\)\[\]\|!@#{}&^%$+=<,>.?/]+"
text_line = text "\n"

nonempty_line   = ~r"\w[^\n]+\n"
empty_line  = ~r"[ \t]*\n"

# .Problem setup | .Figure 1.2: Hello world    NOT '... function()'
block_title = ~r"[.][^.]\n"

# == Section to improve yourself | = Chapter about good stuff
section_title_level_0 = ~r"[=][-\w\s\(\)\[\]\|!@#{}&^%$+=<,>.?/]+\n"


# '[source,python]'
source_header = ~r"\[source,python\]\s*\n"

# no horizontal rules delimitting the source code block
bare_source_lines = text_line+ (empty_line comment_line+)? empty_line

# <1> good code here
comment_line        = ~r"<\d+>\s" text_line

# ---- | -----------------------
four_dashes = ~r'----[-]*\s*\n'
# ==== | =======================
four_equals = ~r'====[=]*\s*\n'
"""


UNUSED = r"""
text            = ~"[- A-Z 0-9 :\";',!@#$%^&*()_+-={}<>?,./]*"i
text_block      = (line / text_line)+ empty_line
"""