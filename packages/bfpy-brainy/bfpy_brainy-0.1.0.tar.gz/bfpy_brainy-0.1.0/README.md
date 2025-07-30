# Brainfuck Py

This is a simple python package that interprets and compiles Brainfuck code.

USE:


```` python
from brainfuck-py import BfInterpreter
from brainfuck-py import BfCompiler

interpreter = BfInterpreter()
compiler = BfCompiler()

bf = "+"*65 + "."

interpreter.interpret(bf) //Outputs A
compiler.compile(bf, "compiled") //Creates a program in your project's root folder with the name compiled along with C code of the same name.
````