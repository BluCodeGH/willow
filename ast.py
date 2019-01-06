from astData import functions

class AST:
  def __init__(self, t, children):
    self.type = t
    self.children = children

  # encapsulate a section of the children into a subtree. This is called by
  # the ast functions as they iterate over the tree.
  def doRaise(self, t, start, stop):
    child = AST(t, self.children[start:stop])
    self.children = self.children[:start] + [child] + self.children[stop:]
    return child

  # get rid of unnecessary tokens such as brackets.
  def pop(self, i):
    return self.children.pop(i)

  def iterate(self):
    yield self # allow any changes made during iteration to apply before iterating over (perhaps new) children
    for child in self.children:
      if isinstance(child, AST):
        yield from child.iterate()

  # this method of iterating allows changes to be made to the AST safely during iteration.
  def itertokens(self):
    children = self.children.copy()
    for child in children:
      if child in self.children:
        yield self.children.index(child), child

  def __repr__(self):
    return "{}{}".format(self.type, self.children)

def parse(tokens):
  ast = AST("PROGRAM", tokens)
  for f in functions:
    for tree in ast.iterate():
      f(tree)
  return ast
