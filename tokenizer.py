import re

class Token:
  def __init__(self, ttype, val):
    self.type = ttype
    self.val = val

  def __eq__(self, other):
    if isinstance(other, str):
      return self.val == other
    if isinstance(other, Token):
      return self.type == other.type, self.val == other.val
    raise TypeError(f"Cannot compare token to {type(other)}.")

  def __repr__(self):
    return self.val

comment = r"[ \t]*#.*\n|\n(?=\n)"
reTokens = {
  "word": r"[0-9]+(?:\.[0-9]+)?|\"(?:\\\"|[^\"])*\"|[a-zA-Z_][a-zA-Z_0-9!?]*",
  "operator": r"==|!=|<=|>=|//|[^\w\s]",
  "indent": r"\n[ \t]*",
  "whitespace": r" +"
}

def tokenize(program):
  program = re.sub(comment, "", program)
  expr = '|'.join(f"(?P<{name}>{exp})" for name, exp in reTokens.items())
  expr = re.compile(expr)
  tokens = []
  i = 0
  indents = [0]
  while i < len(program):
    match = expr.match(program, i)
    if not match:
      print("Error: Didn't match", program[:20])
    i = match.end()
    if match.lastgroup == "whitespace":
      continue
    if match.lastgroup == "indent":
      indent = match.end() - match.start() - 1
      if indent > indents[-1]:
        tokens.append(Token("indent", "IND"))
        indents.append(indent)
      elif indent < indents[-1]:
        if indent not in indents:
          raise SyntaxError(f"Unknown indent value {indent}, found indents {indents}.")
        index = indents.index(indent) + 1
        tokens += [Token("indent", "DND")] * (len(indents) - index)
        tokens.append(Token("indent", "\\n"))
        indents = indents[:index]
      else:
        tokens.append(Token("indent", "\\n"))
      continue
    tokens.append(Token(match.lastgroup, program[match.start():match.end()]))
  return tokens
