import subprocess

class BfInterpreter:
    def __init__(self):
        self.memory = [0] * 30000  # Initialize memory with 30,000 cells
        self.pointer = 0

    def interpret(self, bf:str):
        if "," in bf:
            a = input("Input: ")
        else:
            a = None

        i = 0
        bf_len = len(bf)
        while i < bf_len:
            command = bf[i]
            if command == ">":
                self.pointer += 1
                if self.pointer > len(self.memory) - 1:
                    self.pointer = 0
            elif command == "<":
                self.pointer -= 1
                if self.pointer < 0:
                    self.pointer = len(self.memory) - 1
            elif command == "+":
                self.memory[self.pointer] += 1
                if self.memory[self.pointer] > 255:
                    self.memory[self.pointer] = 0
            elif command == "-":
                self.memory[self.pointer] -= 1
                if self.memory[self.pointer] < 0:
                    self.memory[self.pointer] = 255
            elif command == ".":
                print(chr(self.memory[self.pointer]), end="")
            elif command == ",":
                if a is not None:
                    self.memory[self.pointer] = ord(a[0])
                    a = a[1:]
                else:
                    self.memory[self.pointer] = 0
            elif command == "[":
                if self.memory[self.pointer] == 0:
                    open_brackets = 1
                    while open_brackets > 0:
                        i += 1
                        if i >= bf_len:
                            break
                        if bf[i] == "[":
                            open_brackets += 1
                        elif bf[i] == "]":
                            open_brackets -= 1
            elif command == "]":
                if self.memory[self.pointer] != 0:
                    close_brackets = 1
                    while close_brackets > 0:
                        i -= 1
                        if i < 0:
                            break
                        if bf[i] == "]":
                            close_brackets += 1
                        elif bf[i] == "[":
                            close_brackets -= 1
            i += 1

class BfCompiler:
    class __init__():
        pass

    def compile(self, bf_code, output_file):
        c_code = [
            "//Generated C code from Brainfuck",
            "#include <stdio.h>",
            "int main() {",
            "    unsigned char tape[30000] = {0};",
            "    unsigned char *ptr = tape;"
        ]

        indent = "    "
        for char in bf_code:
            if char == '>':
                c_code.append(indent + "++ptr;")
            elif char == '<':
                c_code.append(indent + "--ptr;")
            elif char == '+':
                c_code.append(indent + "++*ptr;")
            elif char == '-':
                c_code.append(indent + "--*ptr;")
            elif char == '.':
                c_code.append(indent + "putchar(*ptr);")
            elif char == ',':
                c_code.append(indent + "*ptr = getchar();")
            elif char == '[':
                c_code.append(indent + "while (*ptr) {")
                indent += "    "
            elif char == ']':
                indent = indent[:-4]
                c_code.append(indent + "}")

        c_code.append("    return 0;")
        c_code.append("}")
    
        with open(output_file + ".c", "w") as f:
                f.write(c_code)
        
        # Compile the C code using gcc
        subprocess.run(["gcc", output_file, "-o", "out_exec"], check=True)