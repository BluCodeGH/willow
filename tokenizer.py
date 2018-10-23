import re

class Token:
  def __init__(self, tid, val):
    self.val = val
    self.id = tid

  def __eq__(self, other):
    return self.val == other

  def __repr__(self):
    return self.val

comment = r"#.*|\n[ \t]*(?=\n)"
reTokens = [
  r"\".*?\"", # string
  r"[0-9]+(?:\.[0-9]+)?", # number
  r"[a-zA-Z]+", # word
  r"\(|\)|==|!=|=|<=|>=|>|<|{|}|\[|\]|\"|'|\?|\||\.|//|/|\*|\+|-", # symbol
  r"\n[ \t]*" # indent
]
def tokenize(program):
  program = re.sub(comment, "", program)
  toMatch = "(" + reTokens[0]
  for token in reTokens[1:]:
    toMatch += ")|(" + token

  tokens = []
  indent = 0
  indentSize = None

  for match in re.finditer(toMatch + ")", program):
    t = match.lastindex - 1
    v = match.group(0)

    if t == 4: #indent
      v = v[1:]
      if indentSize is None and len(v) > 0:
        indentSize = len(v)

      if indentSize is not None:
        newIndent = len(v) // indentSize
        if newIndent > indent:
          tokens.append(Token(5, "IND"))
        elif newIndent < indent:
          tokens += [Token(5, "DND")] * (indent - newIndent)
        else:
          tokens.append(Token(4, "NL"))
        indent = newIndent
      else:
        tokens.append(Token(4, "NL"))
    else:
      tokens.append(Token(match.lastindex - 1, match.group(0)))

  return tokens
