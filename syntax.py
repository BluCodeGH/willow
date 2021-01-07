"""
AST is called on a parse tree and transforms it into an AST. Generally this only
involves the removal of hardcoded strings, but is more complex in some cases.
"""

class AST:
  def __init__(self, parseTree, id_=None, children=None):
    self.id = None
    self.children = []
    if parseTree is not None:
      getattr(self, parseTree.rule.lower())(parseTree.children)
    else:
      self.id = id_
      self.children = children or []
    # self.id = id_
    # if self.id is None and process:
    # elif process:
    #   getattr(self, self.id.lower())(parseTree)
    # else:
    #   self.children = parseTree

  # helper to remove hardcoded strings and recursively build the AST
  def _noStrings(self, parseTree):
    for child in parseTree:
      if not isinstance(child, str):
        self.children.append(AST(child))

  def blocks(self, parseTree):
    self.id = "BLOCKS"
    self._noStrings(parseTree)

  def fapp(self, parseTree):
    self.id = "FAPP"
    operators = {
      "^": 1,
      "*": 2, "/": 2,
      "+": 3, "-": 3,
      "==": 4, "<": 4, ">": 4, "<=": 4, ">=": 4, "!=": 4,
      "or": 5, "and": 6
    }
    associativity = ["R", "L", "L", "L", "R", "R", "R"]
    # strip strings (newlines + continuation operators)
    for child in parseTree:
      if not isinstance(child, str):
        self.children.append(child)
    # recursive call, but can't apply one child so fall back.
    if len(self.children) == 1:
      res = AST(self.children[0])
      self.id = res.id
      self.children = res.children
      return
    # find the highest priority operator
    maxPriotity = 0
    index = None
    for i, child in enumerate(self.children):
      if child.rule == "WORD" and not isinstance(child.children[0], str) and child.children[0].rule == "ATOM":
        if operators.get(child.children[0].children[0], 0) > maxPriotity:
          maxPriotity = operators[child.children[0].children[0]]
          index = i
        elif operators.get(child.children[0].children[0], -1) == maxPriotity and associativity[maxPriotity - 1] == "L":
          index = i
    if index is not None: # we have an operator
      left = AST(None)
      left.fapp(self.children[:index])
      right = AST(None)
      right.fapp(self.children[index + 1:])
      self.children = [AST(None, "FAPP", [AST(self.children[index]), left]), right]
    else: # this is a direct function call (left associative)
      left = AST(None)
      left.fapp(self.children[:-1])
      self.children = [left, AST(self.children[-1])]

  def assign(self, parseTree):
    self.id = "ASSIGN"
    self._noStrings(parseTree)

  def classdef(self, parseTree):
    self.id = "CLASSDEF"
    self._noStrings(parseTree)

  def func(self, parseTree):
    self.id = "FUNC"
    self._noStrings(parseTree)

  def funcdef(self, parseTree):
    self.id = "FUNCDEF"
    self._noStrings(parseTree)

  def match(self, parseTree):
    self.id = "MATCH"
    self.children = [AST(parseTree[1])] + [AST(child) for child in parseTree[3:-1] if not isinstance(child, str)]

  def matchitem(self, parseTree):
    self.id = "MATCHITEM"
    self._noStrings(parseTree)

  def matchfapp(self, parseTree):
    self.fapp(parseTree)

  def variable(self, parseTree):
    self.id = "VARIABLE"
    self.children = parseTree

  def word(self, parseTree):
    self.id = "WORD"
    if isinstance(parseTree[0], str): # block
      self.children = [AST(parseTree[1])]
      start = 4
    else:
      self.children = [AST(parseTree[0])]
      start = 2
    self.children += parseTree[start::2] # dot accessors, value.property

  def atom(self, parseTree):
    self.id = "ATOM"
    if isinstance(parseTree[-1], str):
      self.children = [''.join(parseTree)]
    else: # Atom has type decorator
      self.children = [''.join(parseTree[:-1]), AST(parseTree[-1])]

  def type(self, parseTree):
    self.id = "TYPE"
    for child in parseTree:
      if child == ':':
        continue
      if isinstance(child, str):
        self.children.append(child)
      else:
        self.children.append(AST(child))

  def typeargs(self, parseTree):
    self.id = "TYPEARGS"
    self._noStrings(parseTree)

  def print(self, depth):
    res = "  " * depth + str(self.id) + "\n"
    for child in self.children:
      if isinstance(child, str):
        res += "  " * (depth + 1) + child + "\n"
      else:
        res += child.print(depth + 1)
    return res

  def __repr__(self):
    return self.print(0)
