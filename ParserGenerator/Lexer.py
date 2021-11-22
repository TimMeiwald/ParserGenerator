# Always left, right

# If an expression evaluates to true with (LHS) as input then return true, and run next step with input (RHS)
# So it's always if(current_expr(LHS) == True): do next_expr(RHS), which itself then splits RHS Into a new LHS, RHS
from os.path import join
from os import getcwd
from collections import deque
import json
import enum

class Token():

    def __init__(self, type, content):
        self.type = type
        self.content = content

class TokenType(enum.Enum):
    # All negative so all ASCII values(also UTF-8) can be represented as nums
    # PEG 
    SEQUENCE = -1
    ORDERED_CHOICE = -2 
    ZERO_OR_MORE = -3
    ONE_OR_MORE = -4
    OPTIONAL = -5
    AND_PREDICATE = -6
    NOT_PREDICATE = -7
    VAR_NAME = -8
    TERMINAL = -9

    # Auxiliaries
    GRAMMAR = -10
    RULE = -11
    END_RULE = -12
    ASSIGNMENT = -13
    SUBEXPR = -14
    END_SUBEXPR = -15
    


class ParseTree():

    def __init__(self):
        """Takes a string and parses it according to parser generator grammar
        It is possible that it would make more sense to replace this with a regular tokenizer because
        this is possibly overcomplicated, and then let the AST.py do contextual checks because that would probs work
        but I don't want to do AST and Parse of chars at the same time because that would be complex and I wouldn't know
        where what is going wrong"""
        self.tree = deque()
    
    def push(self, token_type, token_content=None):
        #Every time something succeeds it pushes to the tree
        if(token_content == None):
            if(token_type == TokenType.ORDERED_CHOICE): token_content = "Ordered Choice, '/'"
            elif(token_type == TokenType.SEQUENCE): token_content = "Sequence, ','"
            elif(token_type == TokenType.OPTIONAL): token_content = "Optional, '?'"
            elif(token_type == TokenType.ONE_OR_MORE): token_content = "One or more, '+'"
            elif(token_type == TokenType.ZERO_OR_MORE): token_content = "Zero or more, '*'"
            elif(token_type == TokenType.AND_PREDICATE): token_content = "And predicate, '&'"
            elif(token_type == TokenType.NOT_PREDICATE): token_content = "Not predicate, '!'"
            elif(token_type == TokenType.GRAMMAR): token_content = "Grammar"
            elif(token_type == TokenType.RULE): token_content = "Rule Start"
            elif(token_type == TokenType.END_RULE): token_content = "Rule End"
            elif(token_type == TokenType.SUBEXPR): token_content = "Subexpression Start"
            elif(token_type == TokenType.END_SUBEXPR): token_content = "Subexpression End"
            elif(token_type == TokenType.ASSIGNMENT): token_content = "Assignment, '='"
            else:
                raise Exception(f"Should not get here!, type: {token_type}")
        token = Token(token_type, token_content)
        self.tree.append(token)

    def pop_as_JSON(self, verbose = True):
        msg = self.tree.pop()
        if(msg.type == TokenType.TERMINAL):
            print(f"'{msg.content}', {ord(msg.content)}")
            msg = [ord(msg.content), f"Terminal, {msg.content}"]
        elif(msg.type == TokenType.VAR_NAME):
            content = []
            for chr in msg.content:
                content.append(ord(chr))
            msg = [content, f"Variable Name, {msg.content}"]
        else:
            msg = [msg.type.value, msg.content]

        if(verbose == False):
            return [msg[0]]
        elif(verbose == True):
            return [*msg]
        else:
            raise TypeError("verbose must be a boolean value")





class GrammarLexer():

    def __init__(self, src = ""):
        self.position = 0
        self.src = src + " \0"
        self.length = len(self.src)
        self.current_rule_name = ""
        self.ParseTree = ParseTree()
        self.Alphabet_Lower = ["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"]
        self.Alphabet_Upper = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]
        self.Alphabet = [*self.Alphabet_Lower, *self.Alphabet_Upper]
        self.Num = ["1","2","3","4","5","6","7","8","9","0"]
        self.Underscore = "_"
        self.ops = ["/", ",", "*", "+", "!", "&"]
        self.name_char = [*self.Alphabet, *self.Num, self.Underscore]

    def lex(self, *, src_filepath, target_filepath, verbose=True):
        self.load_grammar_from_file(src_filepath)
        self.grammar()
        self.write_parse_tree_to_file(target_filepath, verbose)

    def abort(self, message):
        if(self.position >= self.length -1):
            raise Exception(f"""Rule: {self.current_rule_name} Position: EOF, Char: EOF, Message: {message}\n
                            Probably because of a surplus newline at the end     """)
        else:
            raise Exception(f"Rule: {self.current_rule_name} Position: {self.position}, Char: '{self.src[self.position]}', Message: {message} ")

    def write_parse_tree_to_file(self, relative_filepath, verbose = True):
        cwd = getcwd()
        path = join(cwd, relative_filepath + ".json")
        with open(path, "w") as fp:
            parse_tree = self.ParseTree
            list_to_write = []
            while(True):
                try:
                    line = parse_tree.pop_as_JSON(verbose)
                    list_to_write.append(line)
                except IndexError:
                    print(f"Dumped Tokens to {path}")
                    break
            list_to_write = list_to_write[::-1]
            fp.write(json.dumps(list_to_write))

    def load_grammar_from_file(self, relative_filepath):
        cwd = getcwd()
        path = join(cwd, relative_filepath)
        with open(path) as fp:
            self.src = fp.read() + "\0"
        self.length = len(self.src)

    def load_grammar(self, src):
        self.src = src + "\0"
        self.length = len(self.src)

    def whitespace(self):
        # Zero or more spaces basically
        while(True):
            if(self.src[self.position] == " "):
                self.position += 1
            if(self.src[self.position:self.position+1] == "\t"):
                self.position += 1
            if(self.src[self.position:self.position+1] == "\n"):
                self.position += 1
            else:
                break


    def op(self, func):
        if(self.position >= self.length -1):
            return "\0"
        self.whitespace() #Clears whitespace at every op because in this grammar whitespace is meaningless
        position = self.position
        if(func() == True):
            return True
        else:
            # Pop from AST here
            self.position = position
            return False

    def grammar(self):
        print("Reading Grammar")
        self.ParseTree.push(TokenType.GRAMMAR)
        while(True):
            count = 0 
            res = self.op(self.rule)
            if(res == "\0"):
                break
            if(res == True):
                count += 1
            if(res == False):
                self.abort(f"Failed to Parse: {self.src[self.position:self.position+10]}")
            elif(count == 0):
                # Should be an exception but cba at the moment
                self.abort("Grammar: Breaking due to repeated attempts at the same parse")
                break
        print("Lexing completed")

    def rule(self):
        self.whitespace()
        self.ParseTree.push(TokenType.RULE)
        if(self.op(self.name) == True):
            if(self.op(self.assignment) == True):
                self.ParseTree.push(TokenType.ASSIGNMENT)
                if(self.op(self.parsing_expr) == True):
                    if(self.op(self.end_rule) == True):
                        self.ParseTree.push(TokenType.END_RULE)
                        return True
        else:
            self.ParseTree.tree.pop() #Needed to do rule token first, so pops if it breaks there
        return False

    

    def name(self):
        if(self.src[self.position] == "<"):
            self.position += 1
            name_start = self.position
            if(self.src[self.position] in [*self.Alphabet, self.Underscore]):
                self.position += 1
                while(True):
                    if(self.src[self.position] in self.name_char):
                        self.position += 1
                    else:
                        break
                if(self.src[self.position] == ">"):
                    name_end = self.position
                    name = self.src[name_start:name_end]
                    self.position += 1
                    self.current_rule_name = name
                    self.ParseTree.push(TokenType.VAR_NAME, name)
                    self.whitespace()
                    return True
        return False


    def assignment(self):
        if(self.src[self.position] == "="):
            self.position += 1
            return True
        else:
            return False

    def end_rule(self):
        if(self.src[self.position] == ";"):
            self.position += 1
            return True
        else:
            return False
    

    def parsing_expr(self):
        # A parsing expression must start with a terminal, variable or open bracket, it should then
        # recursively follow a chain of stuff to completion
        if(self.src[self.position] == "&"):
            return self.op(self.and_predicate)
        elif(self.src[self.position] == "!"):
            return self.op(self.not_predicate)
        elif(self.src[self.position] == "<"):
            return self.op(self.variable)
        elif(self.src[self.position] == "("):
            return self.op(self.sub_parsing_expr)
        else:
            return self.op(self.terminal)

    def sub_parsing_expr(self):
        self.whitespace()
        if(self.src[self.position] == "("):
            self.position += 1
            self.whitespace()
            self.ParseTree.push(TokenType.SUBEXPR)
            if(self.src[self.position] == "&"):
                temp = self.op(self.and_predicate)
            elif(self.src[self.position] == "!"):
                temp = self.op(self.not_predicate)
            elif(self.src[self.position] == "<"):
                temp = self.op(self.variable)
            elif(self.src[self.position] == "("):
                temp = self.op(self.sub_parsing_expr)
            elif(self.src[self.position] == '"'):
                temp = self.op(self.terminal)
            else:
                raise Exception(f"Subparsing expr failed with token '{self.src[self.position]}'")
            if(temp == True):
                while(self.src[self.position] == ")"):
                    self.position += 1
                    self.ParseTree.push(TokenType.END_SUBEXPR)
                    self.whitespace()
                if(self.src[self.position] == "/"):
                    return self.op(self.ordered_choice)
                elif(self.src[self.position] == ","):
                    return self.op(self.sequence)
                elif(self.src[self.position] == "+"):
                    return self.op(self.one_or_more)
                elif(self.src[self.position] == "*"):
                    return self.op(self.zero_or_more)
                elif(self.src[self.position] == "?"):
                    return self.op(self.optional)
                elif(self.src[self.position] == ";"):
                    return True
                else:
                    self.abort("Unknown error in sub_parsing_expr")
            return False
        return False

    def terminal(self):
        if(self.src[self.position] in ['"',"'"]):
            self.position += 1
            terminal_value = self.src[self.position]
            if(terminal_value == "\\"):
                if(self.src[self.position+1] == "n"):
                    terminal_value = "\n"
                    self.position += 1
            self.position += 1 #For whichever character is in the middle
            if(self.src[self.position] in ['"',"'"]):
                self.position += 1
                self.ParseTree.push(TokenType.TERMINAL, terminal_value)
                self.whitespace()
                if(self.src[self.position] == "/"):
                    return self.op(self.ordered_choice)
                elif(self.src[self.position] == ","):
                    return self.op(self.sequence)
                elif(self.src[self.position] == "?"):
                    return self.op(self.optional)
                elif(self.src[self.position] == "+"):
                    return self.op(self.one_or_more)
                elif(self.src[self.position] == "*"):
                    return self.op(self.zero_or_more)
                elif(self.src[self.position] in [";", ")"]):
                    self.whitespace()
                    return True
                elif(self.src[self.position] == "<"):
                    self.abort("Can't have a variable directly after a terminal")
                else:
                    self.abort(f"No valid token following terminal, {terminal_value}")
        return False

    def variable(self):
        self.whitespace()
        if(self.op(self.name) == True):
            self.whitespace()
            if(self.src[self.position] == "/"):
                return self.op(self.ordered_choice)
            elif(self.src[self.position] == ","):
                return self.op(self.sequence)
            elif(self.src[self.position] == "?"):
                return self.op(self.optional)
            elif(self.src[self.position] == "+"):
                return self.op(self.one_or_more)
            elif(self.src[self.position] == "*"):
                return self.op(self.zero_or_more)
            elif(self.src[self.position] in [";", ")"]):
                return True
            elif(self.src[self.position] == "<"):
                self.abort("Can't have a variable directly after a variable")
            elif(self.src[self.position] in ['"',"'"]):
                self.abort("Can't have a terminal directly after a variable")
            else:
                self.abort(f"No valid token following variable, '{self.src[self.position]}'")
        return False


    

    def sequence(self):
        if(self.src[self.position] == ","):
            op = self.src[self.position]
            self.ParseTree.push(TokenType.SEQUENCE)
            self.position += 1
            self.whitespace()
            if(self.src[self.position] in [";", ")"]):
                    return False #Can't have false after sequence
            else:
                if(self.src[self.position] == "!"):
                    return self.op(self.not_predicate)
                elif(self.src[self.position] == "£"):
                    return self.op(self.and_predicate)
                elif(self.src[self.position] in ['"',"'"]):
                    return self.op(self.terminal)
                elif(self.src[self.position] == "<"):
                    return self.op(self.variable)
                elif(self.src[self.position] == "("):
                    return self.op(self.sub_parsing_expr)
                else:
                    self.abort(f"Unknown Error: {self.src[self.position]} after Sequence")
        else:
            return False

    def ordered_choice(self):
        self.whitespace()
        if(self.src[self.position] == "/"):
            op = self.src[self.position]
            self.ParseTree.push(TokenType.ORDERED_CHOICE)
            self.position += 1
            #Since it must be followed by a terminal
            self.whitespace()
            if(self.src[self.position] in [";", ")"]):
                return False #Can't have false after ordered choice
            else:
                if(self.src[self.position] == "!"):
                    return self.op(self.not_predicate)
                elif(self.src[self.position] == "£"):
                    return self.op(self.and_predicate)
                elif(self.src[self.position] in ['"',"'"]):
                    return self.op(self.terminal)
                elif(self.src[self.position] == "<"):
                    return self.op(self.variable)
                elif(self.src[self.position] == "("):
                    return self.op(self.sub_parsing_expr)
                else:
                    self.abort(f"Unknown Error: {self.src[self.position]} after Ordered Choice")
        else:
            return False

    def zero_or_more(self):
        if(self.src[self.position] == "*"):
            op = self.src[self.position]
            self.ParseTree.push(TokenType.ZERO_OR_MORE)
            self.position += 1
            self.whitespace()
            if(self.src[self.position] in [";", ")"]):
                return True 
            else:
                self.whitespace()
                if(self.src[self.position] == "?"):
                    return self.op(self.optional)
                elif(self.src[self.position] == ','):
                    return self.op(self.sequence)
                elif(self.src[self.position] == '/'):
                    return self.op(self.ordered_choice)
                else:
                    self.abort(f"Unknown Error: {self.src[self.position]} after Zero or more")
        else:   
            return False

    def one_or_more(self):
        if(self.src[self.position] == "+"):
            op = self.src[self.position]
            self.ParseTree.push(TokenType.ONE_OR_MORE)
            self.position += 1
            #Since it must be followed by a terminal
            self.whitespace()
            if(self.src[self.position] in [";", ")"]):
                return True 
            else:
                if(self.src[self.position] == "?"):
                    return self.op(self.optional)
                elif(self.src[self.position] == ','):
                    return self.op(self.sequence)
                elif(self.src[self.position] == '/'):
                    return self.op(self.ordered_choice)
                else:
                    self.abort(f"Unknown Error: {self.src[self.position]} after One or more")
        else:
            return False

    def optional(self):
        if(self.src[self.position] == "?"):
            op = self.src[self.position]
            self.ParseTree.push(TokenType.OPTIONAL)
            self.position += 1
            #Since it must be followed by a terminal
            self.whitespace()
            if(self.src[self.position] in [";", ")"]):
                return True 
            else:
                if(self.src[self.position] == ','):
                    return self.op(self.sequence)
                elif(self.src[self.position] == '/'):
                    return self.op(self.ordered_choice)
        else:
            return False

    def and_predicate(self):
        if(self.src[self.position] == "&"):
            op = self.src[self.position]
            self.ParseTree.push(TokenType.AND_PREDICATE)
            self.position += 1
            self.whitespace()
            #Since it must be followed by a terminal
            if(self.src[self.position] == "<"):
                    return self.op(self.variable)
            elif(self.src[self.position] in ["'",'"']):
                    return self.op(self.terminal)
            elif(self.src[self.position] == "("):
                return self.op(self.sub_parsing_expr)
            else:
                self.abort("Unknown Error in And predicate")
        else:
            return False

    def not_predicate(self):
        if(self.src[self.position] == "!"):
            op = self.src[self.position]
            self.ParseTree.push(TokenType.NOT_PREDICATE)
            self.position += 1
            self.whitespace()
            #Since it must be followed by a terminal
            if(self.src[self.position] == "<"):
                    return self.op(self.variable)
            elif(self.src[self.position] in ["'",'"']):
                    return self.op(self.terminal)
            elif(self.src[self.position] == "("):
                return self.op(self.sub_parsing_expr)
            else:
                self.abort("Unknown Error in Not predicate")
        else:
            return False



    
