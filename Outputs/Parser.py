class Parser():

    def __init__(self, top_level_rule=None):
        self.src = ''
        self.position = 0
        self.length = 0
        self.top_level_rule = top_level_rule
    
    def parse(self, src):
        self._set_src(src) 
        return self.top_level_rule()

    def _set_src(self, src):
        self.src = src
        self.length = len(src)
        self.position = 0

    def _rule(self, args):
        func, arg = args
        return func(arg)

    def _token(self):
        if(self.position >= self.length):
            return True #Unsure if this should be true or false
        return self.src[self.position]

    def _TERMINAL(self, Arg: str) -> bool:
        assert len(Arg) == 1
        if(self._token() == Arg):
            self.position += 1
            return True
        else:
            return False

    def _VAR_NAME(self, func):
        #where func is a grammar rule
        temp_position = self.position
        if(func() == True):
            return True
        else:
            self.position = temp_position
            return False

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
    
    def _OPTIONAL(self, args):
        #Much like zero or mroe this always returns true, just doesnt consume if failed
        func, arg = args[0]
        temp_position = self.position
        if(func(arg) == True):
            return True
        else:
            self.position = temp_position
            return True

    def _AND_PREDICATE(self, args):
        func, arg = args[0]
        temp_position = self.position
        if(func(arg) == True):
            self.position = temp_position
            return True
        else:
            self.position = temp_position
            return False

    def _NOT_PREDICATE(self, args):
        func, arg = args[0]
        # Doesn't need to deal with consumptions since and predicate already does
        return not self._AND_PREDICATE(func(arg))
    
    def _SUBEXPR(self, args):
        func, arg = args[0]
        temp_position = self.position
        if(func(arg) == True):
            return True
        else:
            self.position = temp_position
            return False

    def Test_Sequence_1(self):
        return self._rule([self._SEQUENCE, [[self._SEQUENCE, [[self._SEQUENCE, [[self._SEQUENCE, [[self._TERMINAL, 'a'],[self._TERMINAL, 'b']]],[self._TERMINAL, 'c']]],[self._TERMINAL, 'd']]],[self._TERMINAL, 'e']]])


    def Test_Ordered_Choice_1(self):
        return self._rule([self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._TERMINAL, 'a'],[self._TERMINAL, 'b']]],[self._TERMINAL, 'c']]],[self._TERMINAL, 'd']]],[self._TERMINAL, 'e']]])


    def Test_Zero_Or_More_1(self):
        return self._rule([self._ZERO_OR_MORE, [[self._TERMINAL, 'a']]])


    def Test_One_Or_More_1(self):
        return self._rule([self._ONE_OR_MORE, [[self._TERMINAL, 'a']]])


    def Test_Optional_1(self):
        return self._rule([self._OPTIONAL, [[self._TERMINAL, 'a']]])


    def Test_And_Predicate_1(self):
        return self._rule([self._AND_PREDICATE, [[self._TERMINAL, 'a']]])


    def Test_Not_Predicate_1(self):
        return self._rule([self._NOT_PREDICATE, [[self._TERMINAL, 'a']]])


    def Test_Subexpression_1(self):
        return self._rule([self._SUBEXPR, [[self._SEQUENCE, [[self._TERMINAL, 'a'],[self._TERMINAL, 'b']]]]])


    def Test_Var_Calls_1(self):
        return self._rule([self._SEQUENCE, [[self._VAR_NAME, self.Test_Ordered_Choice_1],[self._VAR_NAME, self.Test_Ordered_Choice_1]]])


    def Alphabet_Lower(self):
        return self._rule([self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._TERMINAL, 'a'],[self._TERMINAL, 'b']]],[self._TERMINAL, 'c']]],[self._TERMINAL, 'd']]],[self._TERMINAL, 'e']]],[self._TERMINAL, 'f']]],[self._TERMINAL, 'g']]],[self._TERMINAL, 'h']]],[self._TERMINAL, 'i']]],[self._TERMINAL, 'j']]],[self._TERMINAL, 'k']]],[self._TERMINAL, 'l']]],[self._TERMINAL, 'm']]],[self._TERMINAL, 'n']]],[self._TERMINAL, 'o']]],[self._TERMINAL, 'p']]],[self._TERMINAL, 'q']]],[self._TERMINAL, 'r']]],[self._TERMINAL, 's']]],[self._TERMINAL, 't']]],[self._TERMINAL, 'u']]],[self._TERMINAL, 'v']]],[self._TERMINAL, 'w']]],[self._TERMINAL, 'x']]],[self._TERMINAL, 'y']]],[self._TERMINAL, 'z']]])


    def Alphabet_Upper(self):
        return self._rule([self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._TERMINAL, 'A'],[self._TERMINAL, 'B']]],[self._TERMINAL, 'C']]],[self._TERMINAL, 'D']]],[self._TERMINAL, 'E']]],[self._TERMINAL, 'F']]],[self._TERMINAL, 'G']]],[self._TERMINAL, 'H']]],[self._TERMINAL, 'I']]],[self._TERMINAL, 'J']]],[self._TERMINAL, 'K']]],[self._TERMINAL, 'L']]],[self._TERMINAL, 'M']]],[self._TERMINAL, 'N']]],[self._TERMINAL, 'O']]],[self._TERMINAL, 'P']]],[self._TERMINAL, 'Q']]],[self._TERMINAL, 'R']]],[self._TERMINAL, 'S']]],[self._TERMINAL, 'T']]],[self._TERMINAL, 'U']]],[self._TERMINAL, 'V']]],[self._TERMINAL, 'W']]],[self._TERMINAL, 'X']]],[self._TERMINAL, 'Y']]],[self._TERMINAL, 'Z']]])


    def Alphabet(self):
        return self._rule([self._ORDERED_CHOICE, [[self._VAR_NAME, self.Alphabet_Lower],[self._VAR_NAME, self.Alphabet_Upper]]])


    def Num_Not_Zero(self):
        return self._rule([self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._ORDERED_CHOICE, [[self._TERMINAL, '1'],[self._TERMINAL, '2']]],[self._TERMINAL, '3']]],[self._TERMINAL, '4']]],[self._TERMINAL, '5']]],[self._TERMINAL, '6']]],[self._TERMINAL, '7']]],[self._TERMINAL, '8']]],[self._TERMINAL, '9']]])


    def Num(self):
        return self._rule([self._ORDERED_CHOICE, [[self._VAR_NAME, self.Num_Not_Zero],[self._TERMINAL, '0']]])


    def Test_String(self):
        return self._rule([self._SEQUENCE, [[self._SEQUENCE, [[self._TERMINAL, '"'],[self._ZERO_OR_MORE, [[self._VAR_NAME, self.Alphabet]]]]],[self._TERMINAL, '"']]])


    def Sub(self):
        return self._rule([self._TERMINAL, '-'])


    def Decimal(self):
        return self._rule([self._TERMINAL, '.'])


    def Test_Float(self):
        return self._rule([self._ORDERED_CHOICE, [[self._SUBEXPR, [[self._SEQUENCE, [[self._SEQUENCE, [[self._SEQUENCE, [[self._OPTIONAL, [[self._VAR_NAME, self.Sub]]],[self._OPTIONAL, [[self._VAR_NAME, self.Num]]]]],[self._VAR_NAME, self.Decimal]]],[self._ZERO_OR_MORE, [[self._VAR_NAME, self.Num]]]]]]],[self._SUBEXPR, [[self._SEQUENCE, [[self._SEQUENCE, [[self._SEQUENCE, [[self._SEQUENCE, [[self._OPTIONAL, [[self._VAR_NAME, self.Sub]]],[self._VAR_NAME, self.Num_Not_Zero]]],[self._ZERO_OR_MORE, [[self._VAR_NAME, self.Num]]]]],[self._VAR_NAME, self.Decimal]]],[self._ZERO_OR_MORE, [[self._VAR_NAME, self.Num]]]]]]]]])


