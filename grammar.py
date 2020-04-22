"""
This PEG parser is made up of three core functions: _atom, _choice and _sequence
Each corresponds to that type of PEG rule, and returns one of the following:
  None - the tokens did not match the rule
  ParseTree(None, []) - the lookahead succeeded or optional atom matched nothing
  ParseTree(None, [...]) - the tokens matched a sub-rule (defined with `()`)
  ParseTree(str, [...]) - the tokens matched a named rule
  str - this atom was matched

ParseTrees are combined with the .add function, making named rules sub-trees
and collapsing down sub-rules to a flat level.
Rules that start with_ are also collapsed.
Rules have tailing _ stripped.
"""

def log(*args):
  #print(*args)
  pass

class ParseTree:
  def __init__(self, rule=None, children=None):
    self.rule = rule
    self.children = []
    self.length = 0
    for child in (children or []):
      self.add(child)

  def add(self, res):
    if isinstance(res, int):
      raise TypeError
    if isinstance(res, ParseTree):
      self.length += res.length
      if res.rule is None or res.rule[0] == "_":
        self.children += res.children
      else:
        self.children.append(res)
    else:
      self.children.append(res)
      self.length += 1

  def print(self, depth):
    res = "  " * depth + "P" + str(self.rule) + "\n"
    for child in self.children:
      if isinstance(child, str):
        res += "  " * (depth + 1) + child + "\n"
      else:
        res += child.print(depth + 1)
    return res

  def __repr__(self):
    return self.print(0)

def memo(fn):
  called = {}
  def wrapper(tokens, depth):
    t = tuple(t.val for t in tokens)
    if t not in called:
      called[t] = fn(tokens, depth)
    else:
      log("  " * depth + " memo")
    return called[t]
  return wrapper

def choice(options):
  @memo
  def _choice(tokens, depth=0):
    for option in options:
      res = option(tokens, depth)
      if res is not None:
        return res
    return None
  return _choice

def sequence(rules):
  @memo
  def _sequence(tokens, depth):
    total = ParseTree()
    for rule in rules:
      res = rule(tokens[total.length:], depth)
      if res is None:
        return None
      total.add(res)
    return total
  return _sequence

def atom(rule):
  def _trueAtom(tokens, depth):
    if isinstance(rule[1], str):
      if rule[1][0] == "'" and rule[1][-1] == "'":
        if rule == "''":
          return ""
        if len(tokens) > 0 and tokens[0] == rule[1][1:-1]:
          log("  " * depth + "Matched", rule[1][1:-1])
          return rule[1][1:-1]
        return None
      if rule[1][0] == "$":
        if len(tokens) > 0 and tokens[0].type == rule[1][1:]:
          log("  " * depth + "Matched", tokens[0].val)
          return tokens[0].val
        return None
      # ruleName, *toDisallow = rule[1].split("-")
      # if ruleName in disallow:
      #   return None
      log("  " * depth + "Applying", rule[1], "to", tokens)
      res = grammar[rule[1]](tokens, depth + 1)
      if res is None:
        log("  " * depth + " Failed")
        return None
      log("  " * depth + " Success")
      return ParseTree(rule[1].rstrip("_"), [res])
    return rule[1](tokens, depth)

  @memo
  def _atom(tokens, depth):
    if rule[0] is None:
      return _trueAtom(tokens, depth)
    if rule[0] == "?":
      return _trueAtom(tokens, depth) or ParseTree()
    total = ParseTree()
    if rule[0] == "+":
      res = _trueAtom(tokens, depth)
      if res is None:
        return None
      total.add(res)
    if rule[0] in "+*":
      while True:
        res = _trueAtom(tokens[total.length:], depth)
        if res is None:
          return total
        total.add(res)
    if rule[0] == "&":
      if _trueAtom(tokens, depth) is None:
        return None
      return ParseTree()
    if rule[0] == "!":
      if _trueAtom(tokens, depth) is None:
        return ParseTree()
      return None
    raise AssertionError("rule was " + str(rule))
  return _atom

def smartSplit(string, splitter):
  res = []
  last = 0
  depth = 0
  inQuote = False
  for i, c in enumerate(string):
    if c == "'":
      inQuote = not inQuote
    elif not inQuote and c == "(":
      depth += 1
    elif not inQuote and c == ")":
      depth -= 1
    else:
      if not inQuote and depth == 0 and c == splitter:
        res.append(string[last:i])
        last = i + 1
  res.append(string[last:])
  return res

def _load(text):
  def _atom(text):
    if text[0] in "&!":
      res = [text[0], text[1:]]
    elif text[-1] in "?+*":
      res = [text[-1], text[:-1]]
    else:
      res = [None, text]
    if res[1][0] == "(" and res[1][-1] == ")":
      res[1] = _load(res[1][1:-1])
    return atom(res)
  def _sequence(text):
    res = []
    for s in smartSplit(text, " "):
      res.append(_atom(s.strip()))
    return sequence(res)
  res = choice([_sequence(c.strip()) for c in smartSplit(text, "/")])
  return res

grammar = {}
def load(text):
  rules = {}
  for line in text.splitlines():
    if line.strip() == '':
      continue
    name, rule = line.split("=", 1)
    rules[name.strip()] = rule.strip()
  toRemove = []
  for rule in rules.values():
    for word in smartSplit(rule, " "):
      word = word.strip(" &!?+*()/")
      if word and word[0] != "'" and "-" in word:
        toRemove.append((word[:word.index("-")], word[word.index("-") + 1:]))
  for name, remove in toRemove:
    rule = rules[name]
    rules[f"{name}-{remove}"] = rule.replace(f"/ {remove}", "")
  for name, rule in rules.items():
    log(name, "=", rule)
    grammar[name.strip()] = _load(rule.strip())

def parse(tokens, rule="BLOCKS"):
  res = grammar[rule](tokens, 0)
  res.rule = rule
  return res

with open("grammar.txt") as f:
  load(f.read())
