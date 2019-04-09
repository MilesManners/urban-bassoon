from collections import namedtuple
import re

Token = namedtuple('Token', ['type', 'value'])
DefNode = namedtuple('DefNode', ['name', 'argNames', 'body'])
IntegerNode = namedtuple('IntegerNode', ['value'])
CallNode = namedtuple('CallNode', ['name', 'argExprs'])
VarRefNode = namedtuple('VarRefNode', ['value'])

class Tokenizer:
  TOKEN_TYPES = [
    ('def', r'\bdef\b'),
    ('end', r'\bend\b'),
    ('identifier', r'\b[a-zA-Z]+\b'),
    ('integer', r'\b[0-9]+\b'),
    ('oparen', r'\('),
    ('cparen', r'\)'),
    ('comma', r',')
  ]

  def __init__(self, code):
    self.code = code

  def tokenize(self):
    tokens = []
    while self.code:
      tokens.append(self.tokenizeOneToken())
      self.code = self.code.strip()
    return tokens
  
  def tokenizeOneToken(self):
    for tokenType in Tokenizer.TOKEN_TYPES:
      type, regex = tokenType
      m = re.compile(regex).match(self.code)
      if m:
        value = m.group()
        self.code = self.code[len(value):]
        return Token(type, value)
    
    raise Exception(f'Couldn\'t match token on {self.code}')

class Parser:
  def __init__(self, tokens):
    self.tokens = tokens

  def parse(self):
    return self.parseDef()

  def parseDef(self):
    self.consume('def')
    name = self.consume('identifier').value
    argNames = self.parseArgNames()
    body = self.parseExpr()
    self.consume('end')
    return DefNode(name, argNames, body)

  def parseArgNames(self):
    argNames = []

    self.consume('oparen')

    if self.peek('identifier'):
      argNames.append(self.consume('identifier').value)
      while self.peek('comma'):
        self.consume('comma')
        argNames.append(self.consume('identifier').value)

    self.consume('cparen')

    return argNames

  def parseExpr(self):
    if self.peek('integer'):
      return self.parseInteger()
    elif self.peek('identifier') and self.peek('oparen', 1):
      return self.parseCall()
    else:
      return self.parseVarRef()

  def parseInteger(self):
    return IntegerNode(self.consume('integer').value)

  def parseCall(self):
    name = self.consume('identifier').value
    argExprs = self.parseArgsExprs()
    return CallNode(name, argExprs)

  def parseArgsExprs(self):
    argExprs = []

    self.consume('oparen')

    if not self.peek('cparen'):
      argExprs.append(self.parseExpr())
      while self.peek('comma'):
        self.consume('comma')
        argExprs.append(self.parseExpr())

    self.consume('cparen')

    return argExprs

  def parseVarRef(self):
    return VarRefNode(self.consume('identifier').value)

  def consume(self, expectedType):
    token = self.tokens.pop(0)
    if token.type == expectedType:
      return token
    else:
      raise Exception(f'Expected token type "{expectedType}" but got "{token.type}"')
  
  def peek(self, expectedType, offset=0):
    return self.tokens[offset].type == expectedType
      
class Generator:
  def generate(self, node):
    if type(node) is DefNode:
      return f'function {node.name} ({", ".join(node.argNames)}) {{ return {self.generate(node.body)} }}' 
    elif type(node) is CallNode:
      return f'{node.name}({", ".join(map(self.generate, node.argExprs))})'
    elif type(node) is IntegerNode:
      return node.value
    elif type(node) is VarRefNode:
      return node.value
    else:
      raise Exception(f'Unexpected node type: {type(node)}')

tokens = Tokenizer(open('test.src').read()).tokenize()
tree = Parser(tokens).parse()
generated = Generator().generate(tree)

RUNTIME = 'const add = (x, y) => x + y'
TEST = 'console.log(f(1, 2))'

print('\n'.join([RUNTIME, generated, TEST]))
