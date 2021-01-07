"""
Typechecking:
maps each value to an instance of Type using scopes
checking happens by ensuring each use of a variable conforms to the mapping, and adding detail to the mapping if need be.
the core properties of a type are: name, super, args, values

1. Go through all of the class definitions to build up definitions of types / check inheritance (variances checked here)
2. Go down the tree making sure all types line up. (don't worry, this is a minor detail)
"""

def log(*args):
  # print(*args)
  pass

# Manages nested scopes
class Scope:
  def __init__(self, parent, _dict=None):
    self.parent = parent
    self.dict = _dict or {}

  def set(self, name, *args):
    if name in self.dict:
      self.dict[name] = args[0]
    elif self.parent.defines(name):
      self.parent.set(name, *args)
    else:
      self.dict[name] = args[0]

  def defines(self, name):
    return name in self.dict or self.parent.defines(name)

  def iterVals(self):
    yield from self.dict.values()
    yield from self.parent.iterVals()

  def get(self, name):
    if not self.defines(name):
      raise KeyError("Name {} not defined in {}".format(name, self))
    if name in self.dict:
      return self.dict[name]
    return self.parent.get(name)

  def copy(self):
    return Scope(self.parent.copy(), self.dict.copy())

  def __repr__(self):
    return str(self.dict) + str(self.parent)

# Top level scope
class GlobalScope(Scope):
  def __init__(self, _dict=None):
    self.dict = _dict or {}

  def set(self, name, *args):
    self.dict[name] = args[0]

  def defines(self, name):
    return name in self.dict

  def iterVals(self):
    yield from self.dict.values()

  def copy(self):
    return GlobalScope(self.dict.copy())

  def __repr__(self):
    if len(self.dict) < 5:
      return str(self.dict)
    return "{G}"

# Pointer to a RealType
class Type:
  def __init__(self, *args, **kwargs):
    self.type = RealType(*args, **kwargs)
    self.type.refs.append(self)

  def verify(self, other):
    res = self.type.verify(other.type)
    if res is False:
      return False
    def update(t):
      for ref in t.refs:
        ref.type = t
      if t.arguments:
        for arg, _ in t.arguments:
          update(arg.type)
    update(res)
    return res

  def copy(self, copying=None):
    if copying is None:
      copying = {}
    if self.type not in copying:
      name = self.type.name
      if self.type.arguments is not None:
        arguments = [(arg.copy(copying), v) for arg, v in self.type.arguments]
      else:
        arguments = None
      _super = self.type.super
      polymorphic = self.type.polymorphic
      copying[self.type] = Type(name, arguments, _super, polymorphic)
    return copying[self.type]

  def fix(self, fixing=None):
    if fixing is None:
      fixing = {}
    if self.type not in fixing:
      if self.type.arguments is not None or self.type.polymorphic == 0:
        name = self.type.name
        if self.type.arguments is not None:
          arguments = [(arg.fix(fixing), v) for arg, v in self.type.arguments]
        else:
          arguments = None
        if self.type.properties is not None:
          properties = {k: v.checkfix(fixing) for k, v in self.type.properties.items()}
        else:
          properties = None
        _super = self.type.super
        fixing[self.type] = Type(name, arguments, _super, -1, properties)
      else:
        fixing[self.type] = self
    return fixing[self.type]

  def checkfix(self, fixing, checking=None):
    if self.type in fixing:
      return fixing[self.type]
    checking = checking or {}
    if self.type not in checking:
      checking[self.type] = Type()
      if self.type.arguments is not None:
        arguments = [(arg.checkfix(fixing, checking), v) for arg, v in self.type.arguments]
      else:
        arguments = None
      if self.type.properties is not None:
        properties = {k: v.checkfix(fixing, checking) for k, v in self.type.properties.items()}
      else:
        properties = None
      res = Type(self.type.name, arguments, self.type.super, self.type.polymorphic, properties)
      for ref in checking[self.type].type.refs:
        ref.type = res.type
    return checking[self.type]

  def print(self, *args):
    return self.type.print(*args)

  def __repr__(self):
    return str(self.type)

class RealType:
  _nextId = 0
  def __init__(self, name=None, arguments=None, _super=None, polymorphic=-1, properties=None):
    self.name = name
    self.arguments = arguments
    self.super = _super
    self.polymorphic = polymorphic
    self.properties = properties or {}
    # -1: not polymorphic. 0: polymorphic. 1: will be polymorphic in the future
    self.refs = []
    self._id = None
    if name is None:
      self._id = RealType._nextId
      RealType._nextId += 1

  def verify(self, other):
    # verify that there are no valid others that are invalid for self
    # return a new RealType with data combined from both self and other

    log("verifying", self, other)

    res = RealType()
    res.refs = self.refs + other.refs
    if self.name and other.name and self.name != other.name and not other.isSub(self):
      print("Invalid due to name")
      return False
    res.name = other.name or self.name
    if self.arguments is not None and other.arguments is not None:
      res.arguments = []
      if len(self.arguments) != len(other.arguments):
        print("Invalid due to arg length")
        return False
      for sa, oa in zip(self.arguments, other.arguments):
        if (sa[1] == 0 and oa[1] != 0) or (sa[1] != 0 and oa[1] == sa[1] * -1):
          print("Incompatable due to variances")
          return False #other's argument's variance is more permissive / opposite permissive than ours.
        if sa[1] == 0:
          if sa[0].type.verify(oa[0].type) and oa[0].type.verify(sa[0].type):
            res.arguments.append((sa[0].type.verify(oa[0].type).wrap(), 0))
          else:
            print("Incompatable due to variance 0")
            return False
        elif sa[1] == 1: # oa can be subtype, therefore oa must fit sa
          if sa[0].type.verify(oa[0].type):
            res.arguments.append((sa[0].type.verify(oa[0].type).wrap(), oa[1]))
          else:
            print("Incompatable due to variance -1")
            return False
        elif sa[1] == -1: #oa can be supertype, therefore sa must fit oa
          if oa[0].type.verify(sa[0].type):
            res.arguments.append((oa[0].type.verify(sa[0].type).wrap(), oa[1]))
          else:
            print("Incompatable due to variance 1")
            return False
        res.arguments[-1][0].refs = sa[0].type.refs + oa[0].type.refs
    else:
      res.arguments = self.arguments or other.arguments
    res.super = other.super or self.super

    polymorphic = -1
    for ref in res.refs:
      if polymorphic == -1:
        polymorphic = ref.type.polymorphic
      elif ref.type.polymorphic != -1 and ref.type.polymorphic != polymorphic:
        breakpoint(header="wtf")
    res.setPolymorphic(polymorphic)

    for prop, t in other.properties.items():
      if self.properties and prop not in self.properties:
        print("Invalid due to missing property")
        return False
      if prop in self.properties and not (self.properties[prop] == t or self.properties[prop].verify(t)):
        print("Invalid due to different property")
        return False
    res.properties = self.properties.copy()
    res.properties.update(other.properties)

    log("verified", res)
    return res

  def setPolymorphic(self, n):
    if self.polymorphic < n:
      self.polymorphic = n
    if self.arguments is not None:
      for t, _ in self.arguments:
        t.type.setPolymorphic(n)

  def changePolymorphic(self, d):
    if self.polymorphic > 0:
      self.polymorphic += d
    if self.arguments is not None:
      for t, _ in self.arguments:
        t.type.changePolymorphic(d)

  def isSub(self, other):
    if self.super is not None:
      res = other.verify(self.super.type) is not False
      return res
    return False

  def wrap(self):
    t = Type()
    t.type = self
    self.refs.append(t)
    return t

  def print(self, printing=None):
    printing = printing or {"MAX": 0}
    res = str(self.polymorphic) if self.polymorphic >= 0 else ""
    if self.name:
      res += self.name
    else:
      if self._id not in printing:
        printing[self._id] = printing["MAX"]
        printing["MAX"] += 1
      res += "?" + str(printing[self._id])
    if self.arguments:
      res += "{{{}}}".format(",".join([a[0].print(printing) for a in self.arguments]))
    if self.properties:
      res += "{{{}}}".format(",".join([f"{name}:{val.print(printing)}" for name, val in self.properties.items()]))
    if self.super:
      res += ":" + self.super.print(printing)
    return res

  def __repr__(self):
    res = str(self.polymorphic) if self.polymorphic >= 0 else ""
    res += self.name or f"?{self._id}"
    if self.arguments:
      res += "{{{}}}".format(",".join([str(a[0]) for a in self.arguments]))
    if self.properties:
      res += str(self.properties)
    if self.super:
      res += ":" + str(self.super)
    return res

g = GlobalScope()

globalTypes = GlobalScope({
  "Unit": Type("Unit", []),
  "A": Type("A", []),
  "B": Type("B", []),
  "Function": Type("Function", [(Type(), 1), (Type(), -1)]),
  "List": Type("List", [(Type(), 0)]),
  "Num": Type("Num"),
  "Bool": Type("Bool")
})

#globalTypes.get("A").type.properties["b"] = globalTypes.get("B")
#globalTypes.get("B").type.properties["a"] = globalTypes.get("A")

g.set("ai", globalTypes.get("A"))
g.set("bi", globalTypes.get("B"))
g.set("li", globalTypes.get("List"))
g.set("true", globalTypes.get("Bool"))
g.set("false", globalTypes.get("Bool"))
for i in range(10):
  g.set(str(i), globalTypes.get("Num"))
g.set("+", Type("Function", [
  (globalTypes.get("Num"), 1),
  (Type("Function", [
    (globalTypes.get("Num"), 1),
    (globalTypes.get("Num"), -1)
  ]), -1)
]))
g.set("-", Type("Function", [
  (globalTypes.get("Num"), 1),
  (Type("Function", [
    (globalTypes.get("Num"), 1),
    (globalTypes.get("Num"), -1)
  ]), -1)
]))
g.set("/", Type("Function", [
  (globalTypes.get("Num"), 1),
  (Type("Function", [
    (globalTypes.get("Num"), 1),
    (globalTypes.get("Num"), -1)
  ]), -1)
]))
t = Type(polymorphic=0)
g.set("if", Type("Function", [
  (globalTypes.get("Bool"), 1),
  (Type("Function", [
    (t, 1),
    (Type("Function", [
      (t, 1),
      (t, -1)
    ]), -1)
  ]), -1)
]))
g.set("==", Type("Function", [
  (globalTypes.get("Num"), 1),
  (Type("Function", [
    (globalTypes.get("Num"), 1),
    (globalTypes.get("Bool"), -1)
  ]), -1)
]))
g.set(">", Type("Function", [
  (globalTypes.get("Num"), 1),
  (Type("Function", [
    (globalTypes.get("Num"), 1),
    (globalTypes.get("Bool"), -1)
  ]), -1)
]))

def check(ast, scope=None, types=None, context=None):
  if scope is None:
    scope = g
  if types is None:
    types = globalTypes
  # sys.setrecursionlimit(300)

  log("Checking {}, scope {}, types {}, context {}".format(ast, scope, types, context))

  if ast.id == "BLOCKS":
    scope = Scope(scope)
    return [check(child, scope, types, context) for child in ast.children][-1]

  if ast.id == "FAPP":
    fn = check(ast.children[0], scope, types, context)
    if fn.type.name is None or fn.type.polymorphic == 0:
      fn.verify(types.get("Function").copy())
    fn = fn.fix()
    if fn.type.name != "Function":
      raise TypeError(f"Type {fn} is not Function.")
    # breakpoint()
    arg = check(ast.children[1], scope, types, context)
    arg2 = arg.fix()
    if not fn.type.arguments[0][0].verify(arg2):
      raise TypeError
    return fn.type.arguments[1][0]

  if ast.id == "WORD":
    res = check(ast.children[0], scope, types, context)
    for part in ast.children[1:]:
      if part not in res.type.properties:
        if res.type.name is None:
          res.type.properties[part] = Type()
        else:
          raise TypeError(f"Type {res} has no property {part}")
      res = res.type.properties[part]
    return res

  if ast.id == "ATOM":
    if ast.children[0] == '()':
      return Type("Unit")
    if ast.children[0][0] != "@":
      if not scope.defines(ast.children[0]):
        raise TypeError("Name {} is not defined.".format(ast.children[0]))
      res = scope.get(ast.children[0])
    else:
      if not context or "classScope" not in context or not context["classScope"].defines(ast.children[0][1:]):
        raise TypeError("Name {} is not defined.".format(ast.children[0]))
      res = context["classScope"].get(ast.children[0][1:])
    if len(ast.children) > 1 and not res.verify(check(ast.children[1], scope, types, context)):
      raise TypeError("Type hint does not match.")
    return res

  if ast.id == "ASSIGN":
    name, classScope, cons = variable(ast.children[0])
    base = Type()
    if ast.children[1].id == "FUNC":
      if classScope:
        context["classScope"].set(name, base)
      else:
        scope.set(name, base)
      print("set", name, base)
    val = check(ast.children[1], scope, types, context)
    if not base.verify(val):
      raise TypeError(f"Recursive induced {base} doesn't match function {val}")
    if classScope:
      context["classScope"].set(name, val)
    elif cons:
      if val.type.name != "Function":
        raise TypeError(f"Type {val} is not Function.")
      arg = val.type
      while arg.arguments[1][0].type.name == "Function":
        arg = arg.arguments[1][0].type
      #classType = context["classType"].copy()
      #classType.type.setPolymorphic(0)
      arg.arguments[1] = (context["classType"], arg.arguments[1][1])
      scope.parent.set(name, val)
    else:
      scope.set(name, val)
    return val

  if ast.id == "CLASSDEF":
    name, *_ = variable(ast.children[0])
    context = context or {}
    if "classScope" in context:
      context["classScope"] = Scope(context["classScope"])
    else:
      context["classScope"] = GlobalScope()
    typesScope = Scope(types)
    args = []
    if ast.children[1].id == "TYPEARGS":
      for child in ast.children[1].children:
        args.append((check(child, scope, typesScope, context), 0))
    res = Type(name, args)
    context["classType"] = res
    types.set(name, res)
    innerScope = Scope(scope)
    res.type.properties = innerScope.dict
    for child in ast.children[-1].children:
      check(child, innerScope, typesScope, context)

    for arg, _ in args:
      arg.type.changePolymorphic(-1)
    args = {arg.type: None for arg, _ in args}
    def infer(argType, current=1):
      if argType in args:
        if args[argType] is None:
          args[argType] = current
        elif args[argType] == -current:
          args[argType] = 0
      if not argType.arguments:
        return
      for arg, variance in argType.arguments:
        infer(arg.type, current * variance)
    for key, defined in innerScope.dict.items():
      infer(defined.type)
    for arg, variance in args.items():
      if variance is None:
        variance = 0
      for i, (realArg, _) in enumerate(res.type.arguments):
        if realArg.type == arg:
          res.type.arguments[i] = (realArg, variance)
          break

    for name, defined in context["classScope"].dict.items():
      res.type.properties[name] = defined
    for name, defined in innerScope.dict.items():
      if defined.type.name == "Function":
        _defined = defined.type.arguments[1][0]
        while _defined.type.name == "Function":
          _defined = _defined.type.arguments[1][0]
        if _defined.type == res.type:
          continue
      # res.type.properties[name] = defined

    if ast.children[-2].id == "TYPE":
      superclass = types.get(ast.children[-2].children[0])
      supercopy = superclass.copy()
      supercopy.type.name = None
      if not supercopy.verify(res):
        raise TypeError("Doesn't match as subtype")
      res.type.super = superclass

    return res

  if ast.id == "FUNC":
    scope = Scope(scope)
    types = Scope(types)
    arguments = []
    t = Type()
    for child in reversed(ast.children[0].children):
      if child.id == "VARIABLE":
        name, classScope, *_ = variable(child)
        arguments.insert(0, (name, t))
        if classScope:
          context["classScope"].set(name, t)
        else:
          scope.set(name, t)
        t = Type()
      else:
        t = check(child, scope, types, context)

    if not arguments:
      arguments = [("unit", globalTypes.get("Unit"))]

    blockRet = check(ast.children[-1], scope, types, context)

    if len(ast.children) == 3:
      ret = check(ast.children[1], scope, types, context)
    else:
      ret = Type()
    if not ret.verify(blockRet):
      raise TypeError

    for i, (_, t) in enumerate(reversed(arguments)):
      res = types.get("Function").copy()
      if not res.type.arguments[0][0].verify(t):
        raise TypeError
      if not res.type.arguments[1][0].verify(ret):
        raise TypeError
      ret = res
    for t in types.dict.values():
      t.type.changePolymorphic(-1)
    return ret

  if ast.id == "TYPE":
    name = ast.children[0]
    if len(ast.children) > 1:
      args = [check(arg, scope, types, context) for arg in ast.children[1].children]
      base = types.get(name).copy()
      if len(base.type.arguments) != len(args):
        raise TypeError(f"Different lengths of arguments for type {base}")
      for i, arg in enumerate(base.type.arguments):
        if not arg[0].verify(args[i]):
          raise TypeError
      return base
    if not types.defines(name):
      if isinstance(types, GlobalScope):
        raise TypeError(f"Unknown type {name}")
      types.set(name, Type(polymorphic=1))
    res = types.get(name)
    if not res.type.polymorphic > 0:
      res = res.copy()
    return res

  raise ValueError(f"Unknown AST type {ast.id}")

def variable(var):
  name = var.children[-1]
  cons = False
  classScope = False
  for child in var.children[:-1]:
    if child == "cons":
      cons = True
    if child == "@":
      classScope = True
  return name, classScope, cons
