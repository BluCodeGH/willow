"""
Typechecking:
maps each value to an instance of Type using scopes
checking happens by ensuring each use of a variable conforms to the mapping, and adding detail to the mapping if need be.
the core properties of a type are: name, super, args, values

1. Go through all of the class definitions to build up definitions of types / check inheritance (variances checked here)
2. Go down the tree making sure all types line up. (don't worry, this is a minor detail)

Problem: How to make sure a function's types line up w/o knowing the arg types.
A: Sub in the function whenever its called. Issue: you could define an invalid function and it wouldnt be detected till its called.
B: Set up generic types for the function's arguments related however necessary, then go down the function's tree and check for conflicts.
Eg:
{A}
  a.show
# Generic type A, all that is known is that it defines show.

Problem: How to represent the type of the identity function, or any function whose return type depends on the types of its arguments.
A: Magic? Perhaps the function type needs to be defined by more than standard arguments.
- maybe not, eg pass the same object twice as two arguments for F{A A}
- this means changing the validation system, the object must be updated when checking such that checking if F{A A} is valid for two different types (who each indiviually match A) still works.
- it would probably be good practice to make a copy of all reusuable types (eg functions) before checking in general, so this could work.

Problem: How to represent callable type:
Answer: They implement the call function, or they are of the magic class Function

Problem: How to do type checking.
Answer: given an AST A and a scope S, we want to identify the return type of A along with verifying all types inside it match up.
Eg: function application
- get function's type: check it (token will be dereferenced from scope, function definition will return type)
- copy type
- apply type of calling argument (got via check()ing it) to 1st arg of F type (F[0].apply(A))
- return type of 2nd arg of F type

Problem: Polymorphic types wtf

Unknown, poly -> Unknown
Known name, poly -> Known name
Known args, poly -> Known args

"""

class Scope:
  def __init__(self, parent, _dict=None):
    self.parent = parent
    self.dict = _dict or {}

  def set(self, name, *args):
    if name in self.dict:
      self.dict[name].update(*args)
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

  def __repr__(self):
    return str(self.dict) + str(self.parent)

class GlobalScope(Scope):
  def __init__(self, _dict=None):
    self.dict = _dict or {}

  def set(self, name, *args):
    if name in self.dict:
      self.dict[name].update(*args)
    else:
      self.dict[name] = args[0]

  def defines(self, name):
    return name in self.dict

  def iterVals(self):
    yield from self.dict.values()

  def __repr__(self):
    return str(self.dict)

class Type:
  def __init__(self, *args, **kwargs):
    self.type = RealType(*args, **kwargs)
    self.type.refs.append(self)

  def verify(self, other):
    res = self.type.verify(other.type)
    if res is False:
      return False
    for ref in res.refs:
      ref.type = res
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
        _super = self.type.super
        fixing[self.type] = Type(name, arguments, _super, polymorphic=-1)
      else:
        fixing[self.type] = self
    return fixing[self.type]

  def __repr__(self):
    return str(self.type)

class RealType:
  _nextId = 0
  def __init__(self, name=None, arguments=None, _super=None, polymorphic=-1):
    self.name = name
    self.arguments = arguments
    self.super = _super
    self.polymorphic = polymorphic
    # -1: not polymorphic. 0: polymorphic. 1: will be polymorphic in the future
    self.refs = []
    self._id = None
    if name is None:
      self._id = RealType._nextId
      RealType._nextId += 1

  def verify(self, other):
    # verify that there are no valid others that are invalid for self
    # return a new RealType with data combined from both self and other

    print("verifying", self, other)

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
          if sa[0].verify(oa[0]) and oa[0].verify(sa[0]):
            res.arguments.append((sa[0], 0))
          else:
            print("Incompatable due to variance 0")
            return False
        elif sa[1] == -1: # oa can be subtype, therefore oa must fit sa
          if sa[0].verify(oa[0]):
            res.arguments.append((sa[0], oa[1]))
          else:
            print("Incompatable due to variance -1")
            return False
        elif sa[1] == 1: #oa can be supertype, therefore sa must fit oa
          if oa[0].verify(sa[0]):
            res.arguments.append((sa[0], oa[1]))
          else:
            print("Incompatable due to variance 1")
            return False
    else:
      res.arguments = self.arguments or other.arguments
    res.super = other.super or self.super

    polymorphic = res.refs[0].type.polymorphic
    for ref in res.refs:
      if polymorphic == -1:
        polymorphic = ref.type.polymorphic
      elif ref.type.polymorphic != -1 and ref.type.polymorphic != polymorphic:
        breakpoint(header="wtf")
    res.setPolymorphic(polymorphic)

    print("verified", res)
    return res

  def setPolymorphic(self, n):
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
    if self == other:
      return True
    if self.super is not None:
      return self.super.isSub(other)
    return False

  def __repr__(self):
    res = str(self.polymorphic) if self.polymorphic >= 0 else ""
    res += self.name or f"?{self._id}"
    if self.arguments:
      res += "{{{}}}".format(",".join([str(a[0]) for a in self.arguments]))
    return res

g = GlobalScope()

globalTypes = GlobalScope({
  "A": Type("A", []),
  "B": Type("B", []),
  "Function": Type("Function", [(Type(), 1), (Type(), -1)])
})

g.set("ai", globalTypes.get("A"))
g.set("bi", globalTypes.get("B"))

def check(ast, scope=None, types=None):
  if scope is None:
    scope = g
  if types is None:
    types = globalTypes

  def fixTest(toCheck):
    print("testing", toCheck)
    for v in types.iterVals():
      if v.type == toCheck.type:
        print("false")
        return False
    print("true")
    return True

  print("Checking {}, scope {}, types {}".format(ast, scope, types))

  if ast.id == "BLOCKS":
    scope = Scope(scope)
    return [check(child, scope, types) for child in ast.children][-1]

  if ast.id == "FAPP":
    fn = check(ast.children[0], scope, types)
    if fn.type.name is None or fn.type.polymorphic == 0:
      fn.verify(types.get("Function").copy())
    fn = fn.fix()
    #breakpoint()
    if fn.type.name != "Function":
      raise TypeError(f"Type {fn} is not Function.")
    if not fn.type.arguments[0][0].verify(check(ast.children[1], scope, types).fix()):
      raise TypeError
    return fn.type.arguments[1][0]

  if ast.id == "ATOM":
    if ast.children[0] == '(':
      return Type("Unit")
    if not scope.defines(ast.children[0]):
      raise TypeError("Name {} is not defined.".format(ast.children[0]))
    res = scope.get(ast.children[0])
    if len(ast.children) > 1 and not res.verify(check(ast.children[1], scope, types)):
      raise TypeError("Type hint does not match.")
    return res

  if ast.id == "ASSIGN":
    name = variable(ast.children[0])
    val = check(ast.children[1], scope, types)
    scope.set(name, val)
    return val

  if ast.id == "CLASSDEF":
    raise NotImplementedError

  if ast.id == "FUNC":
    scope = Scope(scope)
    # for t in types.iterVals():
    #   t.changePolymorphic(1)
    types = Scope(types)
    arguments = []
    t = Type()
    for child in reversed(ast.children[0].children):
      if child.id == "VARIABLE":
        name = variable(child)
        arguments.insert(0, (name, t))
        scope.set(name, t)
        t = Type()
      else:
        t = check(child, scope, types)

    blockRet = check(ast.children[-1], scope, types)

    #breakpoint()

    if len(ast.children) == 3:
      ret = check(ast.children[1], scope, types)
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
      args = [check(arg, scope, types) for arg in ast.children[1].children]
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
  if len(var.children) > 1 and var.children[-2] == "@":
    name = ''.join(*[t.val for t in var.children[-2:]])
  else:
    name = var.children[-1]
  return name
