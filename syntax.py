def nls(layer):
  tokens = layer.data
  res = []
  for i, token in enumerate(tokens):
    if token == "NL":
      res.append((i, -1, True))
      res.append((i, 1, True, "LINE"))
  return res

nls = (nls, ["NL"])

def inds(layer):
  tokens = layer.data
  res = []
  for i, token in enumerate(tokens):
    if token in ["IND", "("]:
      res.append((i, 1, False, "IND"))
      res.append((i, 1, False, "LINE"))
    elif token in ["DND", ")"]:
      res.append((i, -1, True))
      res.append((i, -1, True))
      if token == "DND" and len(tokens) > i + 1 and tokens[i + 1] != "|":
        res.append((i, -1, True))
        res.append((i, 1, True, "LINE"))
  return res

inds = (inds, ["IND", "DND", "(", ")"])

def asgns(layer):
  tokens = layer.data
  res = []
  for i, token in enumerate(tokens):
    if token == "=":
      res.append((0, 1, False, "ASGN"))
      res.append((0, 1, False, "VAR"))
      res.append((i, -1, False))
      res.append((i, 1, True, "VAL"))
      res.append((len(tokens) - 1, -1, True))
      res.append((len(tokens) - 1, -1, True))
  return res

asgns = (asgns, [])

def ifs(layer):
  tokens = layer.data
  res = []
  for i, token in enumerate(tokens):
    if token == "?":
      for j in range(i - 1, -1, -1):
        if tokens[j] == "|":
          res.append((j, 1, True, "IF"))
          res.append((j, 1, True, "BOOL"))
          break
      else:
        res.append((0, 1, False, "IF"))
        res.append((0, 1, False, "BOOL"))
      res.append((i, -1, False))
      res.append((i, 1, True, "YES"))
      res.append((len(tokens) - 1, -1, True))
      res.append((len(tokens) - 1, -1, True))
    if token == "|":
      res.append((i, -1, False))
      res.append((i, 1, True, "NO"))
  return res

ifs = (ifs, ["?", "|"])

def cmps(layer):
  tokens = layer.data
  res = []
  for i, token in enumerate(tokens):
    if token in ["==", "!=", "<=", ">=", "<", ">"]:
      res.append((0, 1, False, "CMP"))
      res.append((0, 1, False, "A"))
      res.append((i, -1, False))
      res.append((i, 1, True, "B"))
      res.append((len(tokens) - 1, -1, True))
      res.append((len(tokens) - 1, -1, True))
  return res

cmps = (cmps, [])

def funcs(layer):
  tokens = layer.data
  res = []
  for i, token in enumerate(tokens):
    if token == "{":
      res.append((i, 1, False, "FUNC"))
      res.append((i, 1, False, "ARGS"))
    elif token == "}":
      res.append((i, -1, True))
      res.append((i, 1, True, "STMT"))
      res.append((len(tokens) - 1, -1, True))
      res.append((len(tokens) - 1, -1, True))
  return res

funcs = (funcs, ["{", "}"])

def fapps(layer):
  res = []
  print(layer.data)
  if len(layer.data) > 1 and layer.type in ["LINE", "STMT", "VAL", "BOOL", "YES", "NO", "A", "B"]:
    res.append((0, 1, False, "FAPP"))
    res.append((len(layer.data) - 1, -1, True))
  return res

fapps = (fapps, [])

def pr(tokens):
  print(tokens)
  return []

pr = (pr, [])
funs = [inds, nls, asgns, funcs, ifs, cmps, fapps]
