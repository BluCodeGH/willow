def inds(tree):
  print(tree)
  raises = []
  depth = 0
  for i, token in tree.itertokens():
    print(i, token, depth)
    if token in ["IND", "("]:
      if depth == 0:
        print("mutating", i)
        tree.pop(i)
        raises.append(i)
        print(tree)
      depth += 1
    elif token in ["DND", ")"]:
      depth -= 1
      if depth == 0:
        print("mutating", i)
        tree.pop(i)
        start = raises.pop(-1)
        child = tree.doRaise("IND", start, i)
        child.doRaise("BLOCK", 0, len(child.children))
        print(tree)
  if depth != 0 or len(raises) != 0:
    raise IndentationError("Invalid indentation or unmatched brackets in {}:\n{}".format(tree, (depth, raises)))

def nls(layer):
  tokens = layer.data
  res = []
  for i, token in enumerate(tokens):
    if token == "NL" and (len(tokens) == i + 1 or tokens[i + 1] != "|"):
      res.append((i, -1, True))
      res.append((i, 1, True, "BLOCK"))
  return res
nls = (nls, ["NL", "|"])


def asgns(layer):
  tokens = layer.data
  res = []
  for i, token in enumerate(tokens):
    if token == "=":
      res.append((0, 1, False, "ASGN"))
      res.append((0, 1, False, "VAR"))
      res.append((i, -1, False))
      res.append((i, 1, True, "BLOCK", True))
      res.append((len(tokens) - 1, -1, True))
      res.append((len(tokens) - 1, -1, True))
  return res
asgns = (asgns, ["="])

def classes(layer):
  tokens = layer.data
  res = []
  if tokens[0] == "class":
    print(tokens)
    res.append((1, 1, False, "CLASS"))
    res.append((1, 1, False, "CLASSNAME"))
    res.append((1, -1, True))
    n = 2
    if tokens[n] == "{":
      res.append((n + 1, 1, False, "CLASSARGS"))
      for i, token in enumerate(tokens[n + 1:]):
        if token == "}":
          res.append((i + n + 1, -1, True))
          n += i + 2
          break
    if tokens[n] == ":":
      res.append((n + 1, 1, False, "SUPERCLASS"))
      res.append((n + 1, -1, True))
      n += 2
    res.append((n, 1, False, "CLASSBODY", True))
    res.append((n, -1, True))
    res.append((n, -1, True))
  return res
classes = (classes, ["class"])


def funcs(layer):
  tokens = layer.data
  res = []
  multi = False
  for i, token in enumerate(tokens):
    if token == "{":
      if multi:
        res.append((i, -1, False))
      else:
        res.append((i, 1, False, "FUNC"))
      res.append((i, 1, False, "FUNCARGS"))
    elif token == "}":
      res.append((i, -1, True))
      res.append((i, 1, True, "BLOCK", True))
      if not multi:
        res.append((len(tokens) - 1, -1, True))
        res.append((len(tokens) - 1, -1, True))
      multi = True
  return res
funcs = (funcs, ["{", "}"])


def ifs(layer):
  tokens = layer.data
  lastIf = 0
  res = []
  for i, token in enumerate(tokens):
    if token == "?":
      res.append((lastIf, 1, False, "IF"))
      res.append((lastIf, 1, False, "BLOCK"))
      res.append((i, -1, False))
      res.append((i, 1, True, "BLOCK", True))
      res.append((i + 1, -1, True))
      res.append((i + 1, 1, True, "BLOCK", True))
      lastIf = i + 2
      res.append((len(tokens) - 1, -1, True))
      res.append((len(tokens) - 1, -1, True))
  return res
ifs = (ifs, ["?"])


def cmps(layer):
  tokens = layer.data
  res = []
  for i, token in enumerate(tokens):
    if token in ["==", "!=", "<=", ">=", "<", ">"]:
      res.append((0, 1, False, "CMP"))
      res.append((0, 1, False, "BLOCK"))
      res.append((i, -1, False))
      res.append((i, 1, True, "BLOCK"))
      res.append((len(tokens) - 1, -1, True))
      res.append((len(tokens) - 1, -1, True))
  return res
cmps = (cmps, [])


def pr(tokens):
  print(tokens)
  return []
pr = (pr, [])



#functions = [inds, nls, asgns, classes, funcs, ifs, cmps]
functions = [inds]
