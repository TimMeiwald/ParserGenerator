from functools import wraps
class Node():
    def __init__(self, type, content=None):
        self.type = type
        self.content = content
        self.children = []

class Parser():

    def __init__(self, top_level_rule=None):
        self.src = ''
        self.position = 0
        self.length = 0
        self.top_level_rule = top_level_rule
        self.last_node = Node("_Grammar")
    
    def parse(self, src):
        self._set_src(src) 
        return self.top_level_rule()

    def _set_src(self, src):
        self.src = src
        self.length = len(src)
        self.position = 0
        self.last_node = Node("_Grammar")

    
    def AST_Generator_Decorator(func):
        #Weird to define inside class but it gives the decorator access to class state
        #Which lets me do stateful things without using files
        @wraps(func)
        def kernel(self, *Args, **Kwargs):
            #Before Func
            func_name = func.__name__
            if(func_name == "_TERMINAL"):
                this_node = Node(func_name, Args[0])
                temp = func(self, *Args, **Kwargs)
                if(temp == True):
                    self.last_node.children.append(this_node)
                return temp
            else:
                this_node = Node(func_name)
                temp_node = self.last_node 
                self.last_node = this_node
                temp = func(self, *Args, **Kwargs)
                if(temp == True):
                    temp_node.children.append(this_node)
                    self.last_node = temp_node
                elif(temp == False):
                    self.last_node = temp_node
                else:
                    raise Exception
                #After func
                return temp
        return kernel


    @AST_Generator_Decorator
    def _rule(self, args):
        func, arg = args
        return func(arg)

    def _token(self):
        if(self.position >= self.length):
            return True #Unsure if this should be true or false
        return self.src[self.position]

    @AST_Generator_Decorator
    def _TERMINAL(self, Arg: str) -> bool:
        assert len(Arg) == 1
        if(self._token() == Arg):
            self.position += 1
            return True
        else:
            return False
    
    @AST_Generator_Decorator
    def _VAR_NAME(self, func):
        #where func is a grammar rule
        temp_position = self.position
        if(func() == True):
            return True
        else:
            self.position = temp_position
            return False
    
    @AST_Generator_Decorator
    def _ORDERED_CHOICE(self, args):
        LHS_func, LHS_arg = args[0]
        RHS_func, RHS_arg = args[1]
        temp_position = self.position
        if(LHS_func(LHS_arg) == True):
            return True
        self.position = temp_position
        if(RHS_func(RHS_arg) == True):
            return True
        self.position = temp_position
        return False    
    
    @AST_Generator_Decorator
    def _SEQUENCE(self, args):
        temp_position = self.position
        LHS_func, LHS_arg = args[0]
        RHS_func, RHS_arg = args[1]
        if(LHS_func(LHS_arg) == True):
            if(RHS_func(RHS_arg) == True):
                return True
            else:
                self.position = temp_position
                return False
        else:
            self.position = temp_position
            return False

    @AST_Generator_Decorator
    def _ZERO_OR_MORE(self, args):
        func, arg = args[0]
        while(True):
            temp_position = self.position
            if(func(arg) == True):
                continue
            else:
                self.position = temp_position
                break
        return True
    
    @AST_Generator_Decorator
    def _ONE_OR_MORE(self, args):
        func, arg = args[0]
        temp_position = self.position
        self._OPTIONAL(args)
        if(self.position != temp_position): #Should have incremented by one expression if optional was successful
            if(self._ZERO_OR_MORE(args) == True):
                return True
            else:
                self.position = temp_position
                return False
        else:
            self.position = temp_position
            return False
    
    @AST_Generator_Decorator
    def _OPTIONAL(self, args):
        #Much like zero or mroe this always returns true, just doesnt consume if failed
        func, arg = args[0]
        temp_position = self.position
        if(func(arg) == True):
            return True
        else:
            self.position = temp_position
            return True

    @AST_Generator_Decorator
    def _AND_PREDICATE(self, args):
        func, arg = args[0]
        temp_position = self.position
        if(func(arg) == True):
            self.position = temp_position
            return True
        else:
            self.position = temp_position
            return False

    @AST_Generator_Decorator
    def _NOT_PREDICATE(self, args):
        func, arg = args[0]
        # Doesn't need to deal with consumptions since and predicate already does
        return not self._AND_PREDICATE(func(arg))
    
    @AST_Generator_Decorator
    def _SUBEXPR(self, args):
        func, arg = args[0]
        temp_position = self.position
        if(func(arg) == True):
            return True
        else:
            self.position = temp_position
            return False


    @AST_Generator_Decorator
    def Test_Sequence_1(self):
        return self._rule([self._SEQUENCE, [[self._SEQUENCE, [[self._SEQUENCE, [[self._SEQUENCE, [[self._TERMINAL, 'a'],[self._TERMINAL, 'b']]],[self._TERMINAL, 'c']]],[self._TERMINAL, 'd']]],[self._TERMINAL, 'e']]])


    @AST_Generator_Decorator
    def Test_Ordered_Choice_1(self):
        return self._rule([self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._TERMINAL, 'a'],[self._TERMINAL, 'b']]],[self._TERMINAL, 'c']]],[self._TERMINAL, 'd']]],[self._TERMINAL, 'e']]])


    @AST_Generator_Decorator
    def Test_Zero_Or_More_1(self):
        return self._rule([self._ZERO_OR_MORE, [[self._TERMINAL, 'a']]])


    @AST_Generator_Decorator
    def Test_One_Or_More_1(self):
        return self._rule([self._ONE_OR_MORE, [[self._TERMINAL, 'a']]])


    @AST_Generator_Decorator
    def Test_Optional_1(self):
        return self._rule([self._OPTIONAL, [[self._TERMINAL, 'a']]])


    @AST_Generator_Decorator
    def Test_And_Predicate_1(self):
        return self._rule([self._AND_PREDICATE, [[self._TERMINAL, 'a']]])


    @AST_Generator_Decorator
    def Test_Not_Predicate_1(self):
        return self._rule([self._NOT_PREDICATE, [[self._TERMINAL, 'a']]])


    @AST_Generator_Decorator
    def Test_Subexpression_1(self):
        return self._rule([self._SUBEXPR, [[self._SEQUENCE, [[self._TERMINAL, 'a'],[self._TERMINAL, 'b']]]]])


    @AST_Generator_Decorator
    def Test_Var_Calls_1(self):
        return self._rule([self._SEQUENCE, [[self._VAR_NAME, self.Test_Ordered_Choice_1],[self._VAR_NAME, self.Test_Ordered_Choice_1]]])


    @AST_Generator_Decorator
    def _Alphabet_Lower(self):
        return self._rule([self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._TERMINAL, 'a'],[self._TERMINAL, 'b']]],[self._TERMINAL, 'c']]],[self._TERMINAL, 'd']]],[self._TERMINAL, 'e']]],[self._TERMINAL, 'f']]],[self._TERMINAL, 'g']]],[self._TERMINAL, 'h']]],[self._TERMINAL, 'i']]],[self._TERMINAL, 'j']]],[self._TERMINAL, 'k']]],[self._TERMINAL, 'l']]],[self._TERMINAL, 'm']]],[self._TERMINAL, 'n']]],[self._TERMINAL, 'o']]],[self._TERMINAL, 'p']]],[self._TERMINAL, 'q']]],[self._TERMINAL, 'r']]],[self._TERMINAL, 's']]],[self._TERMINAL, 't']]],[self._TERMINAL, 'u']]],[self._TERMINAL, 'v']]],[self._TERMINAL, 'w']]],[self._TERMINAL, 'x']]],[self._TERMINAL, 'y']]],[self._TERMINAL, 'z']]])


    @AST_Generator_Decorator
    def _Alphabet_Upper(self):
        return self._rule([self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._TERMINAL, 'A'],[self._TERMINAL, 'B']]],[self._TERMINAL, 'C']]],[self._TERMINAL, 'D']]],[self._TERMINAL, 'E']]],[self._TERMINAL, 'F']]],[self._TERMINAL, 'G']]],[self._TERMINAL, 'H']]],[self._TERMINAL, 'I']]],[self._TERMINAL, 'J']]],[self._TERMINAL, 'K']]],[self._TERMINAL, 'L']]],[self._TERMINAL, 'M']]],[self._TERMINAL, 'N']]],[self._TERMINAL, 'O']]],[self._TERMINAL, 'P']]],[self._TERMINAL, 'Q']]],[self._TERMINAL, 'R']]],[self._TERMINAL, 'S']]],[self._TERMINAL, 'T']]],[self._TERMINAL, 'U']]],[self._TERMINAL, 'V']]],[self._TERMINAL, 'W']]],[self._TERMINAL, 'X']]],[self._TERMINAL, 'Y']]],[self._TERMINAL, 'Z']]])


    @AST_Generator_Decorator
    def _Alphabet(self):
        return self._rule([self._ORDERED_CHOICE, [[self._VAR_NAME, self._Alphabet_Lower],[self._VAR_NAME, self._Alphabet_Upper]]])


    @AST_Generator_Decorator
    def _Num_Not_Zero(self):
        return self._rule([self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._TERMINAL, '1'],[self._TERMINAL, '2']]],[self._TERMINAL, '3']]],[self._TERMINAL, '4']]],[self._TERMINAL, '5']]],[self._TERMINAL, '6']]],[self._TERMINAL, '7']]],[self._TERMINAL, '8']]],[self._TERMINAL, '9']]])


    @AST_Generator_Decorator
    def _Num(self):
        return self._rule([self._ORDERED_CHOICE, [[self._VAR_NAME, self._Num_Not_Zero],[self._TERMINAL, '0']]])


    @AST_Generator_Decorator
    def Test_String(self):
        return self._rule([self._SEQUENCE, [[self._SEQUENCE, [[self._TERMINAL, '"'],[self._ZERO_OR_MORE, [[self._VAR_NAME, self._Alphabet]]]]],[self._TERMINAL, '"']]])


    @AST_Generator_Decorator
    def Sub(self):
        return self._rule([self._TERMINAL, '-'])


    @AST_Generator_Decorator
    def Decimal(self):
        return self._rule([self._TERMINAL, '.'])


    @AST_Generator_Decorator
    def Test_Float(self):
        return self._rule([self._ORDERED_CHOICE, [[self._SUBEXPR, [[self._SEQUENCE, [[self._SEQUENCE, [[self._SEQUENCE, [[self._OPTIONAL, [[self._VAR_NAME, self.Sub]]],[self._OPTIONAL, [[self._VAR_NAME, self._Num]]]]],[self._VAR_NAME, self.Decimal]]],[self._ZERO_OR_MORE, [[self._VAR_NAME, self._Num]]]]]]],[self._SUBEXPR, [[self._SEQUENCE, [[self._SEQUENCE, [[self._SEQUENCE, [[self._SEQUENCE, [[self._OPTIONAL, [[self._VAR_NAME, self.Sub]]],[self._VAR_NAME, self._Num_Not_Zero]]],[self._ZERO_OR_MORE, [[self._VAR_NAME, self._Num]]]]],[self._VAR_NAME, self.Decimal]]],[self._ZERO_OR_MORE, [[self._VAR_NAME, self._Num]]]]]]]]])


