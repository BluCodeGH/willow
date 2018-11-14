# Todo:
# mutability
# exceptions & handling
# lists / arrays & dicts



# this is a comment

### assignment ###

# declare different types. Types are inferred based on the value of the argument

age = 5
firstName = "Willow"
lastName = string "Lang" # types can be specified

classOf lastName  # => string

# other types: bool, list, func, str


### flow control ###

# a block can be a single statement or an intented group. Anywhere a block is used either are valid.
# if statements take the form `boolean ? true | false`
out (age == 5 ? "am 5" | "not 5")
# again, blocks can be used here.

age >= 16 ?
  out "You can drive!"
|
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
  flag = in == ""

# for loops are done with the `map` function, which maps a function across an iterable and collects
# the output into a copy of that same iterable.
map (range 10) {i}
  out i


### functions ###

# the `{}` operator declars a function. Its only argument is a block for the function body
func myFunc = {}
  out "This is my function"
  out "It does lots of things"

# arguments go inside the `{}` and specify a type.
func outAge = {str name, num age}
  out "Hello {}, I am {} years old." name age

# The above function could be inlined as such
outAge = {str name, num age} out "Hello {}, I am {} years old." name age



### classes ###

# in willow, types and classes are synonomous.
# the minimal class is:
class Class1
# which defines an empty class, and can be initiated as such:
myClass1 = new Class1

# classes can also have constructors and methods, such as in
class Class2
  Class2 = {int num} # a constructor. The convention is to name this the same as the class.
    @num = num
|                    # methods before this are constructors, methods after are object methods
  print = {}         # an object method
    out @num

myClass2 = new Class2 5
myClass2.print

# classes become much more powerful with the introduction of class arguments.
# Here is an example box class

class Box {itemType}
  Box = {*itemType contents}
    @contents = contents
|
  retrieve = {}
    @contents

# the constructor (also called Box) take an anonomous type (signified by the *) and saves it in the itemType variable
# this is not simply a class variable as it can be use to specify a type of box by a function, such as:

openStringBox = {Box{string} box}
  box.retrieve

# in which only boxes containing strings are valid arguments

# this anonomous type declaration can be used in other ways as well, such as defining a proper map function:

let map = {list{*A} list, func{*A *B} f}

# Here, the anonomous type is the argument to another type, and both occurrences of *A must be the same type.
# Anonomous types can be filtered by functions implemented as well as arguments.
# For example, the following function only takes types which can be shown and equated

eq5 = {*A[show eq] obj}
  obj == 5 ?
    out "{} is equal to five." obj
  |
    out "{} is not equal to five." obj

# The last feature of classes is multiple global constructors, which are demonstrated by the maybe class

class Maybe {itemType}
  Nothing = {}
    @something = false

  Just = {*itemType item}
    @something = true
    @item = item
|
  unpack = {}
    @something ?
      @item
    |
      err

# Now a Maybe object can be instantiated by either `Nothing` or `Just x`, and can be filtered by the type of item.
# This leads to the nice creation of a list class:

class List {itemType}
  Nil = {}
    @tail = Nothing

  Cons = {itemType item, List tail}
    @item = item
    @tail = Maybe tail

  List = {itemType item}
    @item = item
    @tail = Maybe Nil
|
  append = {itemType item}
    @tail = Maybe (Cons @item @tail)
    @item = item

  get = {int i}
    i == 0 ?
      @item
    |
      @tail.something ?
        @tail.get (i - 1)
      |
        err
