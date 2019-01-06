# Todo:
# mutability
# exceptions & handling
# lists / arrays & dicts



# this is a comment

###
this is a block comment
###

### assignment ###

# declare different types. Types are inferred based on the value of the argument

age = 5
firstName = "Willow"
lastName = 3:Float    # types can be specified

# other types: Num, Bool, List, Func, String


### flow control ###

# a block can be a single statement or an intented group. Anywhere a block is used, either are valid.
# if statements take the form `boolean ? true false`
out (age == 5 ? "am 5" "not 5")
# again, blocks can be used here.

age >= 16 ?
  out "You can drive!"
|     # we use a contintuation operator here to separate the blocks.
  out "You can't drive yet."

# note that in this case the | is acting as a continuation operator, separating two indented blocks
# while keeping them as a single statement

# else if statments look like
false ?
  out "What?"
| true ?
  out "This seems right"
|
  out "1 / 2 is a fail."

# while loops use the `while` keyword.
flag = false
while flag
  inp = in "Press enter to exit."
  flag = inp == ""

# `for` loops are an alias for the `map` function, which maps a function across an iterable and collects
# the output into a copy of that same iterable.
for (range 10) {i}
  out i


### functions ###

# the `{}` operator declars a function. It is followed by an optional return type, and then a block for the function body
myFunc = {}
  out "This is my function"
  out "It does lots of things"

# arguments go inside the `{}` and specify a type.
outAge = {name:String age:Num}:String
  fmt "Hello {}, I am {} years old." name age


### classes ###

class Animal
  cons Animal = {name:String age:Num} # the `cons` keyword makes the following function a constructor. This means it 
                                      # is in the outer scope, and is called on an uninitialized copy of the object.
    @name = name # object variables are prefixed with an @, and are different from their non-@ versions.
    @age = age

  cons Animal2 = {@name:String @age:Num} # object variables can be set directly from method arguments.
    pass

  print = {} # an instance method
    out "My name is {} and I am {} years old." @name @age

# The preceding class would be used as such:
anim = Animal "Stockings" 6
anim.print # -> My name is Stockings and I am 6 years old.
anim = Animal "Fido" 2
anim.print # -> My name is Fido and I am 2 years old.


### subclasses ###

class Cat:Animal
  cons Cat = {@name:String @age:Num}
    out "Meow."

  print = {}
    out "{} says 'Meow!'" @name

  aNewFunction{i:Num}
    out "{} was called with {}" @name i

#which can then be used as such:

animalPrinter = {a:Animal}
  out "Printing animal"
  a.print
  out "Printing done."

a = Animal "Splash" 2
c = Cat "Puss" 1
animalPrinter a
animalPrinter c


### class arguments ###

# sometimes it is useful to allow a class's type to be dependant on another, unknown class. This
# can be seen in things like lists, which store an element of an unknown type. A list of numbers
# should be different than a list of strings, which is where class arguments come in.

class Maybe{A}
  cons Nothing = {}
    @something = false

  cons Just = {@contents:A}
    @something = true

hasError = {m:Maybe}
  m.something ? "yes" "no"

result = Just 5
hasError? result # -> "no"
result = Nothing
hasError? result # -> "yes"

# Class arguments can also be used in function defitions:

sumWithError = {a:Maybe{Num} b:Maybe{Num}}:Maybe{Num}
  a.something and b.something ?
    Just (a.contents + b.contents)
  |
    Nothing

sumWithError (Just 5) (Just 2) # -> 7
sumWithError (Just 5) Nothing # -> Nothing
sumWithError (Just 5) (Just "yes") # -> compile-time type error


### advanced functions ###

# Some example function restrictions:

func1 = {name}:String pass                 # takes unknown type
func2 = {name:String}:String pass          # takes string
map = {l:List{A} f:Func{A B}}:List{B} pass # takes a list of any type and a function using that type
eq = {a:A[eq] b:A}:Bool pass              # takes any type implementing some functions
driveACar = {car:<Car}:String pass        # takes any subclass of a car, but not a car itself.

# note that the above map example uses class arguments across a function defition. Here, the type of the list sets the value of A,
# and the function must conform to that value for it to be an allowed argument. The same thing happens with the function's return
# type and the map function's return type.


# functions can also provide multiple sets of arguments, the first one that matches will be used.
func3 = {a:String b:String}
  out "using strings {} and {}" a b
| {a:Num b:Num}
  out "using Nums {} and {}" a b


# an example list implementation

class List{A}
  cons Nil = {}
    @tail = Nothing

  cons Cons = {@item:A tail:List{A}}
    @tail = Just tail

  put = {@item:A}
    pass

  get = {i:Num}:A
    i == 0 ?
      @item
    |
      @tail.get (i - 1)
