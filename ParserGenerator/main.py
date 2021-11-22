from Lexer import GrammarLexer
from Parser import Parser
from Compiler import Compiler
from os.path import join
# Since classically the combination of a lexer,parser, compiler is also a compiler

def generate_parser(*, src_filepath, target_filepath):
    """src must target a file, target_filepath must be the name of the output folder
    if verbose = True is chosen target_folder will also have intermediate steps written to it"""
    p = GrammarLexer()
    path1 = join(target_filepath, "Lexer_Output")
    p.lex(src_filepath=src_filepath, target_filepath=path1)
    a = Parser()
    path2 = join(target_filepath, "Parser_Output")
    g = a.parse(relative_filepath=path1, target_rel_filepath=path2)
    c = Compiler()
    path3 = join(target_filepath, "Parser")
    c.compile(src_filepath=path2,target_filepath=path3)


if __name__ == "__main__":
    import test #Executes test script if directly called