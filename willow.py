import sys
import tokenizer
import grammar
import syntax
import typeChecker

def go(program):
  program = tokenizer.tokenize(program)
  program = grammar.parse(program)
  program = syntax.AST(program)
  #print(program)
  program = typeChecker.check(program)
  return program


if __name__ == '__main__':
  with open(sys.argv[1]) as f:
    source = f.read()

  g = go(source)
  print(g)
