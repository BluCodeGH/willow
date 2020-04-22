import copy
from ast import AST
from tokenizer import Token

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

"""


class Type:
  def __init__(self, name=None, arguments=None, values=None, _super=None):
    self.name = name
    self.arguments = arguments # Arguments is a list of tuples with a type and a variant, 1 allows super and -1 allows sub, 0 neither
    self.values = values # A dictionary mapping names of values to their types
    self.super = _super
    if self.super is not None and not copy.deepcopy(self.super).apply(self):
      raise Exception("Type {} does not meet requirements for supertype {}".format(self, self.super))

  def apply(self, other):
    # update ourself with the data from the other, error if conflict. Asking "does other fit our requirements"
    # can be thought of as "is there a valid other that is invalid for us"
    if self.name is not None and other.name is not None and self.name != other.name and not other.isSub(self):
      print("Incompatable due to name")
      return False
    if self.name is None or other.name is not None:
      self.name = other.name
    if self.arguments is not None and other.arguments is not None:
      if len(self.arguments) != len(other.arguments):
        print("Incompatable due to args")
        return False
      for sa, oa in [(self.arguments[i], other.arguments[i]) for i in range(len(self.arguments))]:
        if (sa[1] == 0 and oa[1] != 0) or (sa[1] != 0 and oa[1] == sa[1] * -1):
          print("Incompatable due to variances")
          return False #other's argument's variance is less permissive / opposite permissive than ours.

        if sa[1] == 0 and (not copy.deepcopy(sa[0]).apply(oa[0]) or not copy.deepcopy(oa[0]).apply(sa[0])):
          print("Incompatable due to variance values 1")
          return False
        if sa[1] == -1 and not copy.deepcopy(sa[0]).apply(oa[0]): # oa can be subtype, therefore oa must fit sa
          print("Incompatable due to variance values 2")
          return False
        if sa[1] == 1 and not copy.deepcopy(oa[0]).apply(sa[0]): #oa can be supertype, therefore sa must fit oa
          print("Incompatable due to variance values 3")
          return False
    self.arguments = copy.deepcopy(other.arguments)
    if self.values is not None:
      if other.values is None:
        return False
      for name, t in self.values.items():
        if name not in other.values or not t.apply(other.values[name]):
          print("Incompatable due to value name {}".format(name))
          return False
    self.values = other.values
    return True

  def isSub(self, other):
    if self == other:
      return True
    if self.super is not None:
      return self.super.isSub(other)
    return False

  def __contains__(self, item):
    return self.values is not None and item in self.values

  def __eq__(self, other):
    return self.name == other.name and self.arguments == other.arguments and self.values == other.values and self.super == other.super

  def __repr__(self):
    res = self.name or "?"
    if self.arguments is not None:
      res += "{{{}}}".format(",".join([str(a[0]) for a in self.arguments]))
    if self.values is not None:
      res += "[{}]".format(",".join(["{}:{}".format(k, v) for k, v in self.values.items()]))
    return res

class Scope:
  def __init__(self, parent, _dict=None):
    self.parent = parent
    self.dict = _dict or {}

  def update(self, name, *args):
    if name in self.dict:
      self.dict[name].update(*args)
    elif self.parent.defines(name):
      self.parent.update(name, *args)
    else:
      self.dict[name] = args[0]

  def defines(self, name):
    return name in self.dict or self.parent.defines(name)

  def define(self, name, _type):
    if self.defines(name):
      raise ValueError("Cannot redefine {}".format(name))
    self.dict[name] = _type

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

  def update(self, name, *args):
    if name in self.dict:
      self.dict[name].update(*args)
    else:
      self.dict[name] = args[0]

  def defines(self, name):
    return name in self.dict

  def define(self, name, _type):
    self.dict[name] = _type

  def __repr__(self):
    return str(self.dict)

g = GlobalScope()
#g.define("test", Type("Test"))
#g.define("out", Type("Function", [Type("String"), Type("String")]))
#g.define("for", Type("Function", []))
gt = Type()
dt = Type("D", [], {})
et = Type("E", [], {}, dt)
at = Type("A", [(dt, -1)])
bt = Type("B", [(et, 0)], {}, at)
f1 = Type("Function", [(at, -1), (dt, 1)], {})

g.define("dt", dt)
g.define("et", et)
g.define("gt", gt)
g.define("at", at)
g.define("bt", bt)
g.define("f1", f1)

types = {n:t for n, t in g.dict.items() if isinstance(t, Type)}
def getTypes(ast):
  pass

# blocks, block, typed, asgn, asgnvar, classname, classsuper, classbody, classargs, funcret, func, funcargs
def check(ast, scope=None):
  if scope is None:
    scope = g
  #print("Checking {}, scope {}".format(ast, scope))
  if isinstance(ast, Token):
    if not scope.defines(ast.val):
      ast.error("Name {} is not defined.".format(ast.val))
    return scope.get(ast.val)

  if ast.type == "BLOCKS":
    scope = Scope(scope)
    res = None
    for child in ast.children:
      res = check(child, scope)
    return res

  if ast.type == "BLOCK":
    fType = check(ast.children[0])
    if fType.name == "Function":
      base = fType
    else:
      if "call" not in fType:
        ast.children[0].error("Cannot call {}".format(ast))
      base = fType.values["call"]
    base = copy.deepcopy(base)
    if base.arguments[0][0].apply(check(ast.children[1])):
      return base.arguments[1][0]
    ast.children[0].error("Type mismatch calling {}".format(ast))

  if ast.type == "TYPED":
    base = copy.deepcopy(check(ast.children[0]))
    t = ast.children[1]
    t = makeType(t, scope)
    if not base.apply(t):
      ast.error("Cannot type as {}".format(t))
    return base

  if ast.type == "ASGN":
    val = check(ast.children[1], scope)
    scope.define(ast.children[0].val, val)
    return val

  if ast.type == "FUNC":
    pass

  raise ValueError("Didn't account for AST type {}".format(ast.type))


def makeType(ast, scope):
  name = ast.children[0].val
  argsAllowed = False
  if name in types:
    base = copy.deepcopy(types[name])
    argsAllowed = True
  elif scope.defines(name):
    base = scope.get(name)
  else:
    base = Type(name)
    scope.define(name, base)
  for child in ast.children[1:]:
    if child.type == "TYPEARGS":
      if not argsAllowed:
        child.error("Cannot specify arguments to unspecified type.")
      if len(child.children) != len(base.arguments):
        child.error("Invalid number of arguments for type {}".format(base))
      args = []
      for i, arg in enumerate(child.children):
        args.append((makeType(arg, scope), base.arguments[i])) ################Deal with unknown variance.
      base.apply(Type(None, args))
    elif child.type == "TYPEFUNCS":
      defns = {t.val:Type("Function", [Type(), Type()], {}) for t in child.children}
      base.apply(Type(None, None, defns))
  return base
