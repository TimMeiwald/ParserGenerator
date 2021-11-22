from os.path import join
from os import getcwd
import json
from ParserGenerator.Lexer import TokenType

class Node():
    def __init__(self, type, content=None):
        self.type = type
        self.content = content
        self.children = []

    def append(self, obj):
        #Saves typing, not strictly necessary
        self.children.append(obj)

    def rehook(self):
        #Removes last node from parent and returns it to allow it to hook somewhere else
        #e.g Unhook last node from parent, then hook it to a new node then hook that node to the last nodes parent
        #Allows effectively for insertions of new nodes between stuff e.g Parent -> Child to Parent -> Intermediate -> Child
        #Solves postfix operator issues
        node = self.children[-1]
        self.children = self.children[:-1]
        return node


class Parser():

    def __init__(self):
        """Takes lexer tokens and spits out an AST"""
        self.src = None
        self.length = None
        self.position = 0
        self.last_node = None
    
    def pretty_print_AST(self, node):
        #print("\n")
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

    
    def load_tokens_from_file(self, relative_filepath):
        cwd = getcwd()
        path = join(cwd, relative_filepath + ".json")
        with open(path) as fp:
            src = json.loads(fp.read())
        return src 

    def parse(self, *, src=None, relative_filepath=None, target_rel_filepath=None):
        AST = self.makeAST(src, relative_filepath, target_rel_filepath)
        if(target_rel_filepath != None):
            self.dump_node_to_file(target_rel_filepath, AST)
        return AST

    def makeAST(self, src=None, relative_filepath=None, target_rel_filepath=None):
        #Input Sanitization
        if(src == None and relative_filepath == None):
            raise ValueError("Either src or relative filepath need to exist")
        elif(src != None and relative_filepath != None):
            raise ValueError("You cannot provide both the src directly and as a filepath")
        
        if(relative_filepath != None):
            src = self.load_tokens_from_file(relative_filepath)
        nsrc = []
        for token in src:
            nsrc.append(token[0]) #Strips human readable information if present, does nothing if not
        #Logic 
        self.src = nsrc
        self.length = len(self.src) -1 
        print("Parsing Grammar")
        g = self.grammar()
        print("Parsing Complete")
        return g

    def dump_node_to_file(self, target_rel_filepath, node,verbose=True):
        ast_string = json.dumps(self.serialize_AST(node, verbose))
        cwd = getcwd()
        filepath = join(cwd, target_rel_filepath + ".json")
        with open(filepath, "w") as fp:
            fp.write(ast_string)
        print(f"Dumped AST to {filepath}")

    def token(self, increment_position = 0):
        #Increment just allows immediate increment if necessary
        cur_token = self.src[self.position]
        self.position += increment_position
        return cur_token

    def grammar(self):
        grammar = Node(TokenType.GRAMMAR)
        self.position = 0
        if(self.token(1) != TokenType.GRAMMAR.value):
            raise Exception
        temp = True
        while(temp == True):
            temp = self.rule(grammar)
        return grammar

    def rule(self, super_node):
        if(self.position >= self.length):
            return False
        if(self.token(1) != TokenType.RULE.value): raise Exception
        if(type(self.token()) != list): raise Exception
        name = self.token()
        self.position += 1
        if(self.token(1) != TokenType.ASSIGNMENT.value): raise Exception
        rule_node = Node(TokenType.RULE, name)
        super_node.append(rule_node)
        temp = False
        while(temp != True):
            temp = self.other(rule_node)
            if(type(temp) == Node):
                rule_node.append(temp)
                temp = rule_node
            else:
                pass
                #print(f"Warning: {temp} is weird, type is {type(temp)}")
        if(self.token(1) != TokenType.END_RULE.value): raise Exception("Did not parse to end of rule")
        return True
    
    def other(self, super_node):
        token = self.token()
        if(token == TokenType.AND_PREDICATE.value):
            return self.prefix_op(super_node, TokenType.AND_PREDICATE)
        elif(token == TokenType.NOT_PREDICATE.value):
            return self.prefix_op(super_node, TokenType.NOT_PREDICATE)
        elif(token == TokenType.OPTIONAL.value):
            return self.postfix_op(super_node, TokenType.OPTIONAL)
        elif(token == TokenType.ONE_OR_MORE.value):
            return self.postfix_op(super_node, TokenType.ONE_OR_MORE)
        elif(token == TokenType.ZERO_OR_MORE.value):
            return self.postfix_op(super_node, TokenType.ZERO_OR_MORE)
        elif(token == TokenType.ORDERED_CHOICE.value):
            return self.bin_op(super_node, TokenType.ORDERED_CHOICE)
        elif(token == TokenType.SEQUENCE.value):
            return self.bin_op(super_node, TokenType.SEQUENCE)
        elif(token == TokenType.SUBEXPR.value):
            return self.subexpression(super_node)
        elif(token == TokenType.END_SUBEXPR.value):
            self.token(1)
            return True #Don't return true since we don't want to end expr
        elif(token == TokenType.END_RULE.value):
            #print("END RULE")
            return True
        elif(type(token) == int and token >= 0):
            return self.terminal()
        elif(type(token) == list):
            return self.variable()
        else:
            raise NotImplementedError(token)

    def terminal(self):
        content = self.token(1)
        node = Node(TokenType.TERMINAL, content)
        self.last_node = node
        return node

    def variable(self):
        content = self.token(1)
        node = Node(TokenType.VAR_NAME, content)
        self.last_node = node
        return node
    
    def subexpression(self, super_node):
        self.token(1)
        node = Node(TokenType.SUBEXPR)
        temp = False
        while(temp != True):
            temp = self.other(node)
            if(type(temp) == Node):
                node.append(temp)
                temp = node
            else:
                pass
                #print(f"Warning: {temp} is weird, type is {type(temp)}")
        self.last_node = node
        return node
    
    def bin_op(self, super_node, type):
        self.token(1)
        node = Node(type)
        LHS = super_node.rehook() #Gets last thing from super_node
        node.append(LHS)
        RHS = self.other(node)
        node.append(RHS)
        self.last_node = node
        return node

    def postfix_op(self, super_node, type):
        #Want to replace last node
        self.token(1)
        node = Node(type)

        if(self.last_node.type in [TokenType.SEQUENCE, TokenType.ORDERED_CHOICE]):
            LHS = self.last_node.rehook() #Last node, is it's right hand side
            node.append(LHS) #zero or more iwth right hand side attached
            self.last_node.append(node)
        else:
            LHS = super_node.rehook()
            node.append(LHS)
            return node
        
    def prefix_op(self, super_node, type):
        self.token(1)
        node = Node(type)
        next_node = self.other(node)
        node.append(next_node)
        return node    



