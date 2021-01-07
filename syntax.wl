# this is a comment

###
this is a block comment
###

### assignment ###

# Variable declaration. Types are inferred based on the value of the argument.

age = 5
firstName = "Willow"

# Optionally, types can be specfied to give hints to the inference system. These type specification are valid anywhere a value or variable is used.

dollars = 3:Float   # types specified after a value.

# common types: Int, Float, Bool, List, Func, String

# All data is immutable by default
firstName.someProperty = 5   # error

# note that this applies to data, not variables. Variables can be reassigned.
firstName = "Pillow"  # no error

# To prevent reassigning, make a variable `const`
const number = 7
number = 3                  # error

# To make a variable mutable, add `mut` before it
mut lastName = "Willow"
lastName.someProperty = 7   # no error

# immutability also applies inside functions defined on an object. It effectively makes all properties of an object `const`.

### flow control ###

# Programs are composed of blocks, which can be a single statement or an indented group. Anywhere a block is used, either are valid.
# The value of a block is the value of its last statement.

# if statements take the form `if boolean true false`
out (if (age == 5) "am 5" "not 5")

# again, blocks can be used here.
if (age >= 16)
  out "You can drive!"
|     # we use a contintuation operator here to separate the blocks.
  out "You can't drive yet."

# note that in this case the | is acting as a continuation operator, separating two indented blocks while keeping them as a single statement

# else if statments look like
if false
  out "What?"
| (if true
  out "This seems right"
|
  out "1 / 2 is a fail.")

### pattern matching ###

# That else if is pretty ugly with the need for brackets, often pattern matching is a much cleaner alternative.
# Pattern matching uses the `match` keyword, which is followed by the value to match and then one or more match items. For example:

# implementation of fibbonacci
match x
  0 = 0
  1 = 1
  n = (fib (n - 1)) + (fib (n - 2))

# match works on classes as well
match maybe
  Just 1 = 2
  Just n = n
  Nothing = 0

# it does this by first checking the value's type matches that of the constructor, and then calling that constructor's respective deconstructor and comparing the result to the rest of the match item.
# in the above example, if `maybe` was `Just 2`, first the Nothing match item would be excluded. Next, Just's decontructor would be called on `maybe`, which would return `2`, the argument used to contruct `maybe`. Since `2` is not equal to `1`, the second match item would match and `n` would be set to `2`.

# match also supports conditions
match maybe
  Nothing = 0
  Just 0 = 0
  Just n if n < 0 = -1
  Just n if n > 0 = 1

### functions ###

`{}` declares a function. Just like other data, it can be typed. In this case, that type is its return type. After this declaration comes a block, which is the function body. The value of this block is what is returned by the functions.

five = {} 5         # returns 5

fiveAgain = {}:Int  # specify the return type
  5                 # also returns 5

six = {}:Int
  5
  6                 # returns 6, as that is the last value in the indented block.

# Functions can also take arguments inside the `{}`. For example:

sum = {a:Int b:Int} # types are again optional for arguments.
  a + b             # returns the sum of a and b.


# functions are called by simply putting the arguments after the name of the funcion, separated by spaces.
sum 3 4     # returns 7

# functions without any arguments are called with the 'unit', `()`.
five ()     # returns 5

# Function arguments can be made mutable (they default to immutable). An immutable argument can still be passed a mutable value, but a mutable argument cannot be passed an immutable value.
alter = {mut num:Int}
  num.someProperty = 2

num = 5
alter num     # error
mut num = 5
alter num     # valid

# simple loops use `loop` and will run the passed function forever
loop {}
  out "I will never end! Hahahahaha!"

# while loops use the `while` keyword and are passed a condition and a function to run.
flag = false
while flag {}
  inp = in "Press enter to exit."
  flag = inp == ""

# `for` loops are an alias for the `map` function, which maps a function across an iterable and collects
# the output into a copy of that same iterable.
for (range 10) {i}
  out i


### classes ###

class Animal
  # the `cons` keyword makes the following function a constructor.
  # This means it is in the outer scope, and is called on an uninitialized copy of the object.
  cons Animal = {name:String age:Num}
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

  aNewFunction = {i:Num}
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
  if m.something "yes" "no"

result = Just 5
hasError result # -> "no"
result = Nothing
hasError result # -> "yes"

# Class arguments can also be used in function defitions:

sumWithError = {a:Maybe{Num} b:Maybe{Num}}:Maybe{Num}
  if (a.something and b.something)
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
###eq = {a:A[eq] b:A}:Bool pass               # takes any type implementing some functions

# note that the above map example uses class arguments across a function defition. Here, the type of the list sets the value of A,
# and the function must conform to that value for it to be an allowed argument. The same thing happens with the function's return
# type and the map function's return type.

# an example list implementation

class List{A}
  cons Nil = {}
    @tail = Nothing

  cons Cons = {@item:A tail:List{A}}
    @tail = Just tail

  put = {@item:A}
    pass

  get = {i:Num}:A
    if (i == 0)
      @item
    |
      @tail.get (i - 1)
