"""
This PEG parser is made up of three core functions: _atom, _choice and _sequence
Each corresponds to that type of PEG rule, and returns one of the following:
  None - the tokens did not match the rule
  ParseTree(None, []) - the lookahead succeeded or optional atom matched nothing
  ParseTree(None, [...]) - the tokens matched a sub-rule (defined with `()`)
  ParseTree(str name, [...]) - the tokens matched a named rule
  str - this atom was matched

ParseTrees are combined with the .add function, making named rules sub-trees
and collapsing down sub-rules to a flat level.
Rules that start with _ are also collapsed.
Rules have tailing _ stripped.

The grammar is a dictionary mapping rules to functions which implement it. The
syntax is similar to standard PEG with the addition of $type which matches any
tokens of a certain type.
"""

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

# memoization decorator
def memo(fn):
  called = {}
  def wrapper(tokens):
    t = tuple(t.val for t in tokens)
    if t not in called:
      called[t] = fn(tokens)
    return called[t]
  return wrapper

# Matches first option
def choice(options):
  @memo
  def _choice(tokens):
    for option in options:
      res = option(tokens)
      if res is not None:
        return res
    return None
  return _choice

# Matches all of passed rules or none
def sequence(rules):
  @memo
  def _sequence(tokens):
    total = ParseTree()
    for rule in rules:
      res = rule(tokens[total.length:])
      if res is None:
        return None
      total.add(res)
    return total
  return _sequence

# Implements an atom (a string literal or a reference to a rule) with optional
# modifiers (*, !, ?, etc). Rule is a tuple of (modifier, value)
def atom(rule):
  # determines if tokens matches the rule, ignoring modifiers.
  def _trueAtom(tokens):
    if isinstance(rule[1], str):
      if rule[1][0] == "'" and rule[1][-1] == "'":
        if rule == "''":
          return ""
        if len(tokens) > 0 and tokens[0] == rule[1][1:-1]:
          return rule[1][1:-1]
        return None
      if rule[1][0] == "$":
        if len(tokens) > 0 and tokens[0].type == rule[1][1:]:
          return tokens[0].val
        return None
      res = grammar[rule[1]](tokens)
      if res is None:
        return None
      return ParseTree(rule[1].rstrip("_"), [res])
    return rule[1](tokens)

  # determines if tokens matches the rule, including modifiers.
  @memo
  def _atom(tokens):
    if rule[0] is None:
      return _trueAtom(tokens)
    if rule[0] == "?":
      return _trueAtom(tokens) or ParseTree()
    total = ParseTree()
    if rule[0] == "+":
      res = _trueAtom(tokens)
      if res is None:
        return None
      total.add(res)
    if rule[0] in "+*":
      while True:
        res = _trueAtom(tokens[total.length:])
        if res is None:
          return total
        total.add(res)
    if rule[0] == "&":
      if _trueAtom(tokens) is None:
        return None
      return ParseTree()
    if rule[0] == "!":
      if _trueAtom(tokens) is None:
        return ParseTree()
      return None
    raise AssertionError("rule was " + str(rule))
  return _atom

# only split string at splitter when not in a quote and at the lowest (depth)
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

# called on the text of each rule (and sub-rule). Splits it into choices / atoms
# and wraps the related functions.
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

# load the grammar
grammar = {}
def load(text):
  rules = {}
  for line in text.splitlines():
    if line.strip() == '':
      continue
    name, rule = line.split("=", 1)
    rules[name.strip()] = rule.strip()
  for name, rule in rules.items():
    grammar[name.strip()] = _load(rule.strip())

def parse(tokens, rule="BLOCKS"):
  res = grammar[rule](tokens)
  res.rule = rule
  return res

with open("grammar.txt") as f:
  load(f.read())
