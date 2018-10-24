class ContextTree:
  def __init__(self, t=None):
    self.children = []
    self.type = t

  def add(self, item):
    self.children.append(item)

  def __repr__(self):
    return str(self.type) + str(self.children)

class DepthMap:
  def __init__(self, tokens):
    self.tokens = tokens
    self.map = [[] for _ in range(len(tokens) + 1)]
    self.map[0] = [(1, "LINE")]

  def change(self, i, d, after, t=None):
    if after:
      i += 1
    if d == 1:
      if t == "LINE":
        self.map[i].append((d, t))
      else:
        for j, (_, compt) in enumerate(self.map[i] + [(None, "IND")]):
          if compt == "IND":
            self.map[i].insert(j, (d, t))
            break
    else:
      self.map[i].insert(0, (d, t))

  def cull(self, toCull):
    for i, token in enumerate(self.tokens):
      if token in toCull:
        self.tokens[i] = None
        pass

  def iterate(self):
    res = []
    buf = [Layer(None)]
    depth = 0
    for i, changes in enumerate(self.map):
      if i + 1 == len(self.map):
        changes = changes + [(-1, None)]
      for change, t in changes:
        if change == -1:
          while len(res) <= depth:
            res.append([])
          res[depth].append(buf[depth])
          buf[depth - 1].add(buf[depth], i - 1)
        elif change == 1:
          while len(buf) <= depth + 1:
            buf.append(None)
          buf[depth + 1] = Layer(t)
        depth += change
      if i < len(self.tokens) and self.tokens[i] is not None:
        buf[depth].add(self.tokens[i], i)
    for depth in res:
      for layer in depth:
        if len(layer.data) > 0:
          if layer.type is None:
            print("HMM!", layer)
          yield layer

  def tree(self):
    buf = [ContextTree("PROGRAM")]
    depth = 0
    for i, changes in enumerate(self.map):
      if i + 1 == len(self.map):
        changes = changes + [(-1, None)]
      for change, t in changes:
        if change == -1:
          buf[depth - 1].add(buf[depth])
        elif change == 1:
          while len(buf) <= depth + 1:
            buf.append(None)
          buf[depth + 1] = ContextTree(t)
        depth += change
      if i < len(self.tokens) and self.tokens[i] is not None:
        buf[depth].add(self.tokens[i])
    return buf[0]

  def __repr__(self):
    res = ""
    d = 0
    for i, token in enumerate(self.tokens):
      oc = 0
      for change, t in self.map[i]:
        if oc < 0 and change > 0:
          res += "\n" + "  " * d
        d += change
        if t is not None:
          res += str(t) + ","
        oc = change
      if len(self.map[i]) > 0:
        res += "\n" + "  " * d
      if token is not None:
        res += str(token) + " "
    return res


class Layer:
  def __init__(self, t):
    self.data = []
    self.mapping = []
    self.type = t

  def add(self, val, i):
    self.data.append(val)
    self.mapping.append(i)

  def __eq__(self, other):
    return self.data == other

  def __repr__(self):
    return str(self.type) + str(self.data)


def parse(funs, tokens):
  dm = DepthMap(tokens)
  for fun, cull in funs:
    for layer in dm.iterate():
      ops = fun(layer)
      for i, *op in ops:
        i = layer.mapping[i]
        dm.change(i, *op)
    dm.cull(cull)
    print(dm.tree())
  return dm
