import sys, functools

def test(parser, method, src):
    print("\n")
    parser._set_src(src)
    result = method()
    print(f"Result: {result}, Position: {parser.position}")
    if(result == False):
        for i in parser.trace.stack:
            print(i)
    parser.Parse_Tree_to_AST(parser.last_node)
    parser.pretty_print(parser.last_node)
    return result, parser.position

def test_decorator(func):
    func_name = func.__name__
    def inner(parser):
        print(f"Testing {func_name}")
        result = func(parser)
        print(f"Completed {func_name}\n")
        return result
    return inner

@test_decorator
def test_Sequence_1(parser):
    assert test(parser, parser.Test_Sequence_1, "abcde") == (True, 5)
    assert test(parser, parser.Test_Sequence_1, "abfde") == (False, 0)
    assert test(parser, parser.Test_Sequence_1, "abcde  aeafgaiu") == (True, 5)

@test_decorator
def test_Ordered_Choice_1(parser):
    assert test(parser, parser.Test_Ordered_Choice_1, "abcde") == (True, 1)
    assert test(parser, parser.Test_Ordered_Choice_1, "bcde") == (True, 1)
    assert test(parser, parser.Test_Ordered_Choice_1, "cde") == (True, 1)
    assert test(parser, parser.Test_Ordered_Choice_1, "de") == (True, 1)
    assert test(parser, parser.Test_Ordered_Choice_1, "e") == (True, 1)
    assert test(parser, parser.Test_Ordered_Choice_1, "fabcde") == (False,0)

@test_decorator
def test_Zero_Or_More_1(parser):
    assert test(parser, parser.Test_Zero_Or_More_1, "abcde") == (True, 1)
    assert test(parser, parser.Test_Zero_Or_More_1, "aaade") == (True, 3)
    assert test(parser, parser.Test_Zero_Or_More_1, "faade") == (True, 0)
    assert test(parser, parser.Test_Zero_Or_More_1, "") == (True, 0)

@test_decorator
def test_One_Or_More_1(parser):
    assert test(parser, parser.Test_One_Or_More_1, "abcde") == (True, 1)
    assert test(parser, parser.Test_One_Or_More_1, "aaade") == (True, 3)
    assert test(parser, parser.Test_One_Or_More_1, "faade") == (False, 0)
    assert test(parser, parser.Test_One_Or_More_1, "") == (False, 0)

@test_decorator
def test_Optional_1(parser):
    #Much like Zero or more optional always returns True, if it succeeds it consumes input if it doesn't, it doesn't
    assert test(parser, parser.Test_Optional_1, "abcde") == (True, 1)
    assert test(parser, parser.Test_Optional_1, "fbcde") == (True, 0)
    assert test(parser, parser.Test_Optional_1, "") == (True, 0)

@test_decorator
def test_And_Predicate_1(parser):
    assert test(parser, parser.Test_And_Predicate_1, "abcde") == (True, 0)
    assert test(parser, parser.Test_And_Predicate_1, "fbcde") == (False, 0)
    assert test(parser, parser.Test_And_Predicate_1, "") == (False, 0)

@test_decorator
def test_Not_Predicate_1(parser):
    assert test(parser, parser.Test_Not_Predicate_1, "abcde") == (False, 0)
    assert test(parser, parser.Test_Not_Predicate_1, "fbcde") == (True, 0)
    assert test(parser, parser.Test_Not_Predicate_1, "") == (True, 0)

@test_decorator
def test_Subexpression_1(parser):
    assert test(parser, parser.Test_Subexpression_1, "abcde") == (True, 2)
    assert test(parser, parser.Test_Subexpression_1, "bcde") == (False, 0)
    assert test(parser, parser.Test_Subexpression_1, "cde") == (False, 0)
    assert test(parser, parser.Test_Subexpression_1, "a") == (False, 0)
    assert test(parser, parser.Test_Subexpression_1, "ab") == (True, 2)
    assert test(parser, parser.Test_Subexpression_1, "fabcde") == (False,0)

@test_decorator
def test_Var_Calls_1(parser):
    assert test(parser, parser.Test_Var_Calls_1, "abcde") == (True, 2)
    assert test(parser, parser.Test_Var_Calls_1, "bcde") == (True, 2)
    assert test(parser, parser.Test_Var_Calls_1, "cde") == (True, 2)
    assert test(parser, parser.Test_Var_Calls_1, "de") == (True, 2)
    assert test(parser, parser.Test_Var_Calls_1, "e") == (False, 0)
    assert test(parser, parser.Test_Var_Calls_1, "fabcde") == (False,0)

@test_decorator
def test_String_1(parser):
    assert test(parser, parser.Test_String, '"abcde"') == (True, 7)
    assert test(parser, parser.Test_String, '"bcde"') == (True, 6)
    assert test(parser, parser.Test_String, '"cde"') == (True, 5)
    assert test(parser, parser.Test_String, '"de" ') == (True, 4)
    assert test(parser, parser.Test_String, '"e"') == (True, 3)
    assert test(parser, parser.Test_String, '"fabcde') == (False,0)
    assert test(parser, parser.Test_String, '"') == (False,0)
    assert test(parser, parser.Test_String, 'aganoeg"') == (False,0)
    assert test(parser, parser.Test_String, '') == (False,0)

@test_decorator
def test_Float_1(parser):
    assert test(parser, parser.Test_Float, '1235') == (False, 0)
    assert test(parser, parser.Test_Float, '1235.') == (True, 5)
    assert test(parser, parser.Test_Float, '10.5') == (True, 4)
    assert test(parser, parser.Test_Float, '') == (False, 0)
    assert test(parser, parser.Test_Float, '1.5') == (True, 3)
    assert test(parser, parser.Test_Float, '1.') == (True,2)
    assert test(parser, parser.Test_Float, '0.') == (True, 2)
    assert test(parser, parser.Test_Float, '.964"') == (True,4)
    assert test(parser, parser.Test_Float, '-1235') == (False, 0)
    assert test(parser, parser.Test_Float, '-1235.') == (True, 6)
    assert test(parser, parser.Test_Float, '-10.5') == (True, 5)
    assert test(parser, parser.Test_Float, '') == (False, 0)
    assert test(parser, parser.Test_Float, '-1.5') == (True, 4)
    assert test(parser, parser.Test_Float, '-1.') == (True,3)
    assert test(parser, parser.Test_Float, '-0.') == (True, 3)
    assert test(parser, parser.Test_Float, '-.964"') == (True,5) #" not consided a float, but it considers -.964 a float as it should. The enclosing rule will say that a float can't be folowed by e.g "

    assert test(parser, parser.Test_Float, '123') == (False, 0)
    assert test(parser, parser.Test_Float, '10') == (False, 0)
    assert test(parser, parser.Test_Float, '1') == (False, 0)
    assert test(parser, parser.Test_Float, '0') == (False, 0)
    assert test(parser, parser.Test_Float, '964"') == (False, 0)
    assert test(parser, parser.Test_Float, '-1235') == (False, 0)
    assert test(parser, parser.Test_Float, '-10') == (False, 0)
    assert test(parser, parser.Test_Float, '-1') == (False, 0)
    assert test(parser, parser.Test_Float, '-1') == (False, 0)
    assert test(parser, parser.Test_Float, '-0') == (False, 0)
    assert test(parser, parser.Test_Float, '-964"') == (False, 0)
    assert test(parser, parser.Test_Float, '-964.0') == (True, 6)

@test_decorator
def test_Multiexpr(parser):
    #Tests that I can simply put multiple expressions behind each other. In this case loads of floats
    assert test(parser, parser.Test_Multiexpr, '1235') == (False, 0)
    assert test(parser, parser.Test_Multiexpr, '1235.0') == (True, 6)
    assert test(parser, parser.Test_Multiexpr, '1235.0 1234') == (True, 7) #True but ends still at 6 + space
    assert test(parser, parser.Test_Multiexpr, '1235.0 1234.5') == (True, 13) 
    assert test(parser, parser.Test_Multiexpr, '1235.0 1234.5 0.') == (True, 16) 

if __name__ == "__main__":
    from main import generate_parser
    generate_parser(src_filepath="Inputs\\test.txt", target_filepath="Outputs") #Generates test parser from test.txt
    from Outputs.Parser import Parser 
    p = Parser()
    test_Sequence_1(p)
    test_Ordered_Choice_1(p)
    test_Zero_Or_More_1(p)
    test_One_Or_More_1(p)
    test_Optional_1(p)
    test_And_Predicate_1(p)
    test_Subexpression_1(p)
    test_Var_Calls_1(p)
    test_String_1(p)
    test_Float_1(p)
    test_Multiexpr(p)
    print("\n\n\n\n\n\n")

    #p._set_src('1235.0 1234.5 0.')
    #p.Test_Multiexpr()
    #n = p.last_node
    #Parse_Tree_to_AST(n)
    #pretty_print_parse_tree(n)