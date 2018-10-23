# this is a comment


### assignment ###

# declare different types
num age = 5
string firstName = "Willow"
# types are inferred
lastName = "Lang"
type lastName # `string`

#use let to assign constants
let num myConst = 2
myConst = 5 #error

# other types: bool, list, func


### flow control ###

# a block can be a single statement or an intented group. Anywhere a block is used either are valid,
# although an intented block can only be used at the end of a line without needing brackets.
# if statements take the form `boolean ? true | false`
out (age == 5 ? "am 5" | "not 5")
# again, blocks can be used here, although an if statement does not require only a single indented block.

myConst != 2 ?
  out "How did a const change?"
|
  out "Let statements work."

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
func outAge = {num age}
  out "I am {} years old." age

# The above function could be inlined as such
outAge = {num age} out "I am {} years old." age

# function chaining uses the `.` operator, reminiscent of function composition. The difference is that
# the `.` operator is reversed, `(f . g) x` represents `g (f x)`
# Why? because reading forwards is easier than reading backwards.

