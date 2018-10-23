import sys
import re
import tokenizer
import parser
import syntax

def go(program):
  tokens = tokenizer.tokenize(program)
  ast = parser.parse(syntax.funs, tokens)
  return ast

if __name__ == '__main__':
  with open(sys.argv[1]) as f:
    program = f.read()

  g = go(program)
  print(g)
