import sys
import re
import tokenizer
import ast
#import treeTypes

def go(program):
  tokens = tokenizer.tokenize(program)
  progAst = ast.parse(tokens)
  #progAst = treeTypes.Tree("PROGRAM", progAst)
  #parser.parse(syntax.funs, ast)
  return progAst


if __name__ == '__main__':
  with open(sys.argv[1]) as f:
    program = f.read()

  g = go(program)
  print(g)
