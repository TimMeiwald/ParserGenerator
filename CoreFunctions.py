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