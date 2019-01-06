from tokenizer import Token

def inds(tree):
  raises = []
  depth = 0
  for i, token in tree.iterChildren():
    if token in ["IND", "("]:
      if depth == 0:
        tree.pop(i)
        raises.append(i)
      depth += 1
    elif token in ["DND", ")"]:
      depth -= 1
      if depth == 0:
        tree.pop(i)
        start = raises.pop(-1)
        child = tree.doRaise("BLOCKS", start, i)
        for t in child.children:
          if t == "NL":
            break
        else:
          child.doRaise("BLOCK", 0, len(child.children))
  if depth != 0 or len(raises) != 0:
    raise IndentationError("Invalid indentation or unmatched brackets in {}".format(tree))

def nls(tree):
  last = 0
  for i, token in tree.iterChildren():
    if token == "NL" and (len(tree.children) == i + 1 or tree.children[i + 1] != "|"):
      tree.pop(i)
      if last < i:
        tree.doRaise("BLOCK", last, i)
        last += 1
    elif token == "NL":
      tree.pop(i)
      if tree.children[i] == "|":
        tree.pop(i)
  if last > 0 and last < len(tree.children):
    tree.doRaise("BLOCK", last, len(tree.children))

def asgns(tree):
  for i, token in tree.iterChildren():
    if token == "=":
      if i == 0:
        raise SyntaxError("Cannot assign something to nothing in {}.".format(tree))
      elif i + 1 == len(tree.children):
        raise SyntaxError("Cannot assign a variable to nothing in {}.".format(tree))
      tree.pop(i)
      tree.doRaise("ASGNVAR", i - 1, i)
      tree.doRaise("BLOCK", i, len(tree.children))
      tree.doRaise("ASGN", i - 1, i + 1)

def classes(tree):
  if tree.children[0] != "class":
    return
  tree.pop(0)
  tree.type = "CLASS"
  tree.doRaise("CLASSNAME", 0, 1)
  n = 1
  if tree.children[n] == "{":
    tree.pop(n)
    start = n
    for i, token in enumerate(tree.children[start:]):
      if token == "}":
        end = i + start
        break
    else:
      raise SyntaxError("Imbalanced brackets in {}.".format(tree))
    tree.pop(end)
    tree.doRaise("CLASSARGS", start, end)
    n += 1
  if tree.children[n] == ":":
    tree.pop(n)
    tree.doRaise("CLASSSUPER", n, n + 1)
    n += 1
  tree.doRaise("CLASSBODY", n, n + 1)


def funcs(tree):
  if len(tree.children) == 0 or tree.children[0] != "{":
    return
  n = 0
  while n < len(tree.children) and tree.children[n] == "{":
    tree.pop(n)
    for i, token in enumerate(tree.children[n:]):
      if token == "}":
        end = i + n
        break
    else:
      raise SyntaxError("Imbalanced brackets in {}.".format(tree))
    tree.pop(end)
    tree.doRaise("FUNCARGS", n, end)
    n += 1
    if tree.children[n] == ":":
      tree.pop(n)
      tree.doRaise("FUNCRET", n, n + 1)
      n += 1
    if isinstance(tree.children[n], Token):
      tree.doRaise("BLOCK", n, len(tree.children))
      n = len(tree.children)
    else:
      tree.doRaise("BLOCK", n, n + 1)
      n += 1
  tree.doRaise("FUNC", 0, n)


def ifs(tree):
  for i, token in tree.iterChildrenR():
    if token == "?":
      tree.pop(i)
      if i + 1 >= len(tree.children):
        raise SyntaxError("If has no body in {}.".format(tree))
      if i == 0:
        raise SyntaxError("If has no condition in {}.".format(tree))
      tree.doRaise("BLOCK", i, i + 1) #false
      tree.doRaise("BLOCK", i + 1, i + 2) #true
      # account for else-ifs by only extending back to the previous if
      end = 0
      for j, token in reversed([x for x in enumerate(tree.children[:i])]):
        if token == "?":
          end = j + 2 # account for the previous if's ? and true.
          break
      if end >= i:
        raise SyntaxError("If must be bracketed unless acting as elif in {}.".format(tree))
      tree.doRaise("BLOCK", end, i)
      tree.doRaise("IF", end, i + 2)


def cmps(tree):
  for i, token in tree.iterChildren():
    if token in ["==", "!=", "<=", ">=", "<", ">"]:
      tree.type = "CMP"
      tree.doRaise("BLOCK", 0, i)
      tree.doRaise("BLOCK", i + 1, len(tree.children))


def pr(tree):
  print(tree)



functions = [inds, nls, asgns, classes, funcs, ifs, cmps]
#functions = [inds, pr, nls]
