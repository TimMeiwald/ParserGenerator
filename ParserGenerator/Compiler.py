from os import getcwd
from os.path import join
import json 
from ParserGenerator.Lexer import TokenType
from ParserGenerator.Parser import Node
class Compiler():

    def __init__(self):
        """Takes an AST, and converts to instructions, 
        optimization passes must be completed on the AST beforehand"""
        self.AST = None
        self.code = ""
        self.indent = 0

    def compile(self, *, src_filepath, target_filepath):
        self.load_AST(src_filepath)
        code = self.generate_code(self.AST)
        cwd = getcwd()
        filepath = join(cwd, target_filepath + ".py")
        print(f"Wrote Parser to {filepath}")
        with open(filepath, "w") as fp:
            fp.write(code)


    def serialize_AST(self, node, verbose = False):
        content = ""
        if(node.type in [TokenType.VAR_NAME, TokenType.RULE]):
            for char in node.content:
                    content += chr(char) 
        elif(node.type == TokenType.TERMINAL):
            content = chr(node.content)
        else:
            content = None
        if(verbose == True):
            serial = [[node.type.value, node.type.name], [node.content, content], []]
        else:
            serial = [[node.type.value], [node.content], []] 
            #Double lists might seem wasteful but it means behaviour is identical for verbose version
            #Could potentially be changed at some point in favour of a dedicated raw AST to prettified AST function or something
        for child in node.children:
            c_serial = self.serialize_AST(child, verbose)
            serial[2].append(c_serial)
        return serial

    def pretty_print_AST(self, node):
        depth = -1
        self.pretty_print_kernel(node, depth)

    def pretty_print_kernel(self, node, depth):
        depth += 1
        for child in node.children:
            if(type(child) == bool):
                print("WARNING: ",child)
            elif(child.type in [TokenType.VAR_NAME, TokenType.RULE]):
                content = ""
                for char in child.content:
                    content += chr(char)
                print("    "*depth + f"type: {child.type}, content: {content}")
            elif(child.type == TokenType.TERMINAL):
                print("    "*depth + f"type: {child.type}, content: {chr(child.content)}")
            else:
                print("    "*depth + f"type: {child.type}")
            if(len(child.children) != 0):
                self.pretty_print_kernel(child, depth)

    def load_AST(self, relative_filepath):
        cwd = getcwd()
        filepath = join(cwd, relative_filepath + ".json")
        with open(filepath) as fp:
            ast_data = json.loads(fp.read())
        self.AST = self.__load_data(ast_data)
    
    def __load_data(self, ast_data):
        node = Node(TokenType(ast_data[0][0]), ast_data[1][0])
        for child in ast_data[2]:
            child = self.__load_data(child)
            node.children.append(child)
        return node

    def generate_code(self, node):
        self.indent = 0 #Resets it if you used it before
        return self.__grammar(node)

    def to_string(self, content):
        if(type(content) == int):
            if(content == 10):
                # Newline
                return r"\n"
            elif(content == 92):
                # backslash
                return r"\\"
            return chr(content)
        elif(type(content) == list):
            temp = ""
            for char in content:
                temp += chr(char)
            return temp
        else:
            raise Exception("to_string can only take ints or lists of ints")

    def write(self, message, indent_change=0, end = "\n"):
        if(message == ""):
            self.indent += indent_change
            return 
        else:
            string = self.indent*"    " + message + end
            self.indent += indent_change
            return string

    def __load_core_functions(self):
        from pathlib import Path

        path = Path(__file__).parent
        path = join(path, "CoreFunctions.py")
        with open(path) as fp:
            core_functions = fp.read() + "\n\n"
        return core_functions

    def __grammar(self, node):
        grammar  = ""
        #write corefunctions
        print("Compiling Grammar")
        grammar += self.__load_core_functions()
        self.write("", 1)
        for child in node.children:
            grammar += self.__rule(child)
        print("Compiling completed")
        return grammar

    def __rule(self, node):
        name = self.to_string(node.content)
        assert len(node.children) == 1 #Think it should always be 1 for this grammar at least
        child = node.children[0]
        rule = self.write("@AST_Generator_Decorator")
        rule += self.write(f"def {name}(self):", 1)
        rule += self.write(f"return self._rule({self.__kernel(child)})\n\n",-1)
        return rule

    def __kernel(self, node):
        type = node.type
        out = "[self._"  + str(type.name) + ", "
        if(type in [TokenType.SEQUENCE, TokenType.ORDERED_CHOICE]):
            child = node.children[0]
            out += "[" + self.__kernel(child) + ","
            child = node.children[1]
            out += self.__kernel(child) + "]"
        else:
            if(type in [TokenType.TERMINAL]):
                content_str = self.to_string(node.content)
                if(content_str not in  ["'", "''", "'''"]):
                    out += f"'{content_str}'"
                else:
                    out += f'"{content_str}"'
            elif(type == TokenType.VAR_NAME):
                content_str = self.to_string(node.content)
                out += f"self.{content_str}"
            else:
                child = node.children[0]
                out += "[" + self.__kernel(child) + "]"
        out += "]"
        return out
    

