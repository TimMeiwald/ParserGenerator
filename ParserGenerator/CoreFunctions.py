from collections import deque
from functools import wraps
class Node():
    def __init__(self, type, content=None):
        self.type = type
        self.content = content
        self.children = []

class ErrorStack():

    def __init__(self):
        self.stack = deque()

    def push_error(self, err_message):
        self.stack.append(err_message)

class Parser():

    def __init__(self, top_level_rule=None):
        self.src = ''
        self.position = 0
        self.length = 0
        self.top_level_rule = top_level_rule
        self.last_node = Node("_Grammar")
        self.trace = ErrorStack()
    
    def pretty_print(self, node, depth = 0):
        if(node.type == "_TERMINAL"):
            print(depth, depth*"    ",node.type, f"'{node.content}'")
        else:
            print(depth, depth*"    ",node.type, f"'{node.content}'")
        for child in node.children:
            ndepth = depth + 1
            self.pretty_print(child, ndepth)

    def Parse_Tree_to_AST(self, node):
        # Rules with preceding _ are not relevant to the AST but exist in the parse tree and need to be collapsed. 
        # Except terminals that need to be handled somehow
        ######################################################################
        # Don't touch!!! This was magic when I wrote it, Let alone now       #
        ######################################################################

        #Modifies Node in place.
        changes_made = False
        for index, child in enumerate(node.children):
            self.Parse_Tree_to_AST(child)
            if(child.type[0] == "_" and child.type != "_TERMINAL"):
                changes_made = True
                del node.children[index]
                for subchild in child.children[::-1]:
                    node.children.insert(index, subchild)

        if(changes_made == True):
            self.Parse_Tree_to_AST(node) # Basically keep collapsing children until there are no changes, 
            # not sure why I still need to recursively do it to child though
            #One would think you wouldn't strictly need that but hey ho


    def aggregate_terminals(self, node):
        if(node.content == None):
            node.content = ""
        flag = False
        for child in node.children:
            self.aggregate_terminals(child)
            if(child.type != "_TERMINAL"):
                flag = True
        if(flag == False):
            for child in node.children:
                node.content += child.content
            node.children = []

    def parse(self, src):
        self._set_src(src) 
        return self.top_level_rule()

    
    def _set_src(self, src):
        self.src = src
        self.length = len(src)
        self.position = 0
        self.last_node = Node("_Grammar")
        self.trace.stack.clear()

    def Errors(func):
        @wraps(func)
        def kernel(self, *Args, **Kwargs):
            temp = func(self, *Args, **Kwargs)
            func_name = func.__name__
            if(temp == True):
                if(func_name[0] != "_"):
                    self.trace.push_error(f"{func_name} succeeded")
            else:
                if(func_name[0] != "_"):
                    self.trace.push_error(f"{func_name} failed")
            return temp
        return kernel
    
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

    @Errors
    @AST_Generator_Decorator
    def _rule(self, args):
        func, arg = args
        return func(arg)

    def _token(self):
        if(self.position >= self.length):
            return True #Unsure if this should be true or false
        return self.src[self.position]

    @Errors
    @AST_Generator_Decorator
    def _TERMINAL(self, Arg: str) -> bool:
        assert len(Arg) == 1
        if(self._token() == Arg):
            self.position += 1
            return True
        else:
            return False
    @Errors
    @AST_Generator_Decorator
    def _VAR_NAME(self, func):
        #where func is a grammar rule
        temp_position = self.position
        if(func() == True):
            return True
        else:
            self.position = temp_position
            return False
    @Errors
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
    @Errors
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
    @Errors
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
    @Errors
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
    @Errors
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
    @Errors
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
    @Errors
    @AST_Generator_Decorator
    def _NOT_PREDICATE(self, args):
        func, arg = args[0]
        # Doesn't need to deal with consumptions since and predicate already does
        return not self._AND_PREDICATE(func(arg))
    @Errors
    @AST_Generator_Decorator
    def _SUBEXPR(self, args):
        func, arg = args[0]
        temp_position = self.position
        if(func(arg) == True):
            return True
        else:
            self.position = temp_position
            return False
