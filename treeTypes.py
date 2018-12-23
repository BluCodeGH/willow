from tokenizer import Token
from ast import DepthMap, Layer

def getType(token):
  try:
    float(token.val)
    return "NUM"
  except ValueError:
    pass
  if token.val in ["true", "false"]:
    return "BOOL"
  if token.val in ["=", "?", "|", ".", "+", "-", "*", "/"]:
    return "OP"
  if token.val in ["==", "<", ">", "<=", ">="]:
    return "CMP"
  if len(token.val) >= 2 and token.val[0] == '"' and token.val[-1] == '"':
    return "STRING"
  return "VAR"

builtins = {"out": "STRING", "type": "TYPE"}
def types(tree):
  if len(tree.children) == 0:
    return
  if tree in ["IND", "ASGN"]:
    tree.returnVal = tree.children[-1].returnVal
  elif tree == "VAR":
    tree.returnVal = "VAR"
  elif tree == "IF":
    if tree.children[1].returnVal != tree.children[2].returnVal:
      raise Exception("Not-matching type for if statement result: " + str(tree))
    tree.returnVal = tree.children[1].returnVal
  elif tree == "CMP":
    tree.returnVal = "BOOL"
  elif tree == "FUNC":
    tree.returnVal = "FUNC"
  elif tree == "ARGS":
    tree.returnVal = None
  elif tree == "FAPP":
    if isinstance(tree.children[0], Tree):
      tree.returnVal = tree.children[0].children[1].returnVal
    elif tree.children[0].val in builtins:
      tree.returnVal = builtins[tree.children[0].val]
    else:
      tree.returnVal = "UNKNOWN"
  else:
    if isinstance(tree.children[0], Tree):
      tree.returnVal = tree.children[0].returnVal
    elif isinstance(tree.children[0], Token):
      tree.returnVal = getType(tree.children[0])

funs = [types]

class Tree:
  def __init__(self, t=None, source=None):
    self.children = []
    self.type = t
    self.returnVal = None
    if source is not None:
      self.parse(source)

  def add(self, item):
    self.children.append(item)

  def parse(self, source):
    buf = [self]
    depth = 0
    for i, changes in enumerate(source.map):
      if i + 1 == len(source.map):
        changes = changes + [(-1, None)]
      for change, t in changes:
        if change == -1:
          buf[depth - 1].add(buf[depth])
        elif change == 1:
          while len(buf) <= depth + 1:
            buf.append(None)
          buf[depth + 1] = Tree(t, None)
        depth += change
      if i < len(source.tokens) and source.tokens[i] is not None:
        buf[depth].add(source.tokens[i])

  def iterate(self):
    for child in self.children:
      if isinstance(child, Tree):
        yield from child.iterate()
    yield self

  def __eq__(self, other):
    return self.type == other

  def __repr__(self):
    return str(self.type) + str(self.children)#":" + str(self.returnVal) + str(self.children)

class Type:
  def __init__(self, res):
    self.res = res

  def resolve(self, args=None):
    pass

def parse(funs, tree):
  for fun in funs:
    for t in tree.iterate():
      fun(t)

