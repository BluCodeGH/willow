class AST:
  def __init__(self, parseTree, id_=None, process=True):
    self.id = id_
    self.children = []
    if self.id is None and process:
      getattr(self, parseTree.rule.lower())(parseTree.children)
    elif process:
      getattr(self, self.id.lower())(parseTree)
    else:
      self.children = parseTree

  def _noStrings(self, parseTree):
    for child in parseTree:
      if not isinstance(child, str):
        self.children.append(AST(child))

  def blocks(self, parseTree):
    self.id = "BLOCKS"
    self._noStrings(parseTree)

  def block(self, parseTree):
    self.id = "BLOCK"
    self._noStrings(parseTree)

  def fapp(self, parseTree):
    operators = {
      "^": 1,
      "*": 2, "/": 2,
      "+": 3, "-": 3,
      "==": 4, "<": 4, ">": 4, "<=": 4, ">=": 4, "!=": 4,
      "or": 5, "and": 6
    }
    associativity = ["R", "L", "L", "L", "R", "R", "R"]
    self.id = "FAPP"
    for child in parseTree:
      if not isinstance(child, str):
        self.children.append(child)
    if len(self.children) == 1:
      self.id = "BLOCK"
      self.children = [AST(self.children[0])]
      return
    maxPriotity = 0
    index = None
    for i, child in enumerate(self.children):
      if child.rule == "ATOM":
        if operators.get(child.children[0], 0) > maxPriotity:
          maxPriotity = operators[child.children[0]]
          index = i
        elif operators.get(child.children[0], -1) == maxPriotity and associativity[maxPriotity - 1] == "L":
          index = i
    if index is not None:
      self.children = [AST([AST(self.children[index]), AST(self.children[:index], "FAPP")], "FAPP", False), AST(self.children[index + 1:], "FAPP")]
    elif len(self.children) > 2:
      self.children = [AST(self.children[:-1], "FAPP"), AST(self.children[-1])]
    else:
      self.children = [AST(child) for child in self.children]

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
    if isinstance(parseTree[1], str):
      self.children = [AST(parseTree[2])] + [AST(child) for child in parseTree[5:-1] if not isinstance(child, str)]
    else:
      self.children = [AST(parseTree[1])] + [AST(child) for child in parseTree[3:-1] if not isinstance(child, str)]

  def matchitem(self, parseTree):
    self.id = "MATCHITEM"
    self._noStrings(parseTree)

  def matchfapp(self, parseTree):
    self.fapp(parseTree)

  def variable(self, parseTree):
    self.id = "VARIABLE"
    self.children = parseTree

  def atom(self, parseTree):
    self.id = "ATOM"
    self.children = parseTree

  def type(self, parseTree):
    self.id = "TYPE"
    self.children = parseTree[1:]

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
