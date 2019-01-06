# splits string program into a list of tokens who have a type (num, word, string, etc) and a value.

import re

class Token:
  def __init__(self, tid, val):
    self.val = val
    self.id = tid
    #IDs: 0->string, 1->number, 2->word, 3->symbol, 4->newline, 5->change-indent

  def __eq__(self, other):
    if isinstance(other, str):
      return self.val == other
    return self is other

  def __repr__(self):
    return self.val

# these regular expressions split up the program
comment = r"[ \t]*###[\S\s]*?###[ \t]*|[ \t]*#.*|[ \t\n]+(?=\n)"
reTokens = [
  r"\".*?\"", # string
  r"[0-9]+(?:\.[0-9]+)?", # number
  r"[a-zA-Z]+", # word
  r"==|!=|<=|>=|//|\+\+|--|[^\w\s]", # symbol
  r"\n[ \t]*" # indent, MUST BE 4TH
]

def tokenize(program):
  program = re.sub(comment, "", program) # remove comments
  # assemble the final regex
  toMatch = "(" + reTokens[0]
  for token in reTokens[1:]:
    toMatch += ")|(" + token

  tokens = []
  indent = 0
  indentSize = None # we need to find the indent size used

  for match in re.finditer(toMatch + ")", program):
    t = match.lastindex - 1 # which regex found it
    v = match.group(0) # contents of the match

    if t == 4: # newline or indent
      v = v[1:] # strip leading newline
      if indentSize is None and len(v) > 0:
        indentSize = len(v)

      if indentSize is not None:
        # add in special indent and deindent tokens, along with newline tokens
        newIndent = len(v) // indentSize
        if newIndent > indent:
          tokens += [Token(5, "IND") for _ in range(newIndent - indent)]
        elif newIndent < indent:
          tokens += [Token(5, "DND") for _ in range(indent - newIndent)]
          tokens.append(Token(4, "NL"))
        else:
          tokens.append(Token(4, "NL"))
        indent = newIndent
      else:
        tokens.append(Token(4, "NL"))
    else:
      tokens.append(Token(match.lastindex - 1, match.group(0)))

  return tokens
