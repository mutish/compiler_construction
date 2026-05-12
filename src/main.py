import ast

from ast_builder import ASTBuilder
from lexer import Scanner
import parse_tree
from parser import Parser
import sys
from icg import ICGenerator

def print_set_map(title, set_map):
    print(f"\n---- {title} ----")
    for symbol in sorted(set_map.keys()):
        values = ", ".join(sorted(set_map[symbol]))
        print(f"{symbol}: {{ {values} }}")


def parse_args(argv):
    filename = 'src/sample_code.mpy'
    trace = True
    show_grammar = False

    for arg in argv:
        if arg == '--no-trace':
            trace = False
        elif arg == '--show-grammar':
            show_grammar = True
        elif not arg.startswith('--'):
            filename = arg

    return filename, trace, show_grammar

def main():
    filename, trace, show_grammar = parse_args(sys.argv[1:])
    try:
        with open(filename, 'r') as file:
            source_code = file.read()
    except FileNotFoundError:
        print(f"Error: input file not found: {filename}")
        return
    
    #1. TOKENISATION
    scanner = Scanner(source_code)

    #secondary scanner instance for the parser to consume cleanly
    scanner_for_parser = Scanner(source_code)

    tokens = []
    while True:
        try:
            token = scanner.get_next_token()
            tokens.append(token)
            if token.type == "EOF":
                break
        except Exception as e:
            print(f"Error encountered: {e}")
            return

    print("---- Scanner Output ----")
    line_width = max(len("Line"), max(len(str(token.line)) for token in tokens))
    lexeme_width = max(len("Lexeme"), max(len(token.value) for token in tokens))
    token_width = max(len("Token"), max(len(token.type) for token in tokens))

    header = f"{'Line':<{line_width}}  {'Lexeme':<{lexeme_width}}  {'Token':<{token_width}}"
    separator = f"{'-' * line_width}  {'-' * lexeme_width}  {'-' * token_width}"
    print(header)
    print(separator)

    for token in tokens:
        print(f"{token.line:<{line_width}}  {token.value:<{lexeme_width}}  {token.type:<{token_width}}")

    #2. PARSER PHASE
    parser = Parser(scanner_for_parser)
    

    # 3. Print canonical parse-tree heading before grammar artifacts
    print("\n----Parse Tree ----")

    #show FIRST / FOLLOW / LL(1) table
    print_set_map("FIRST Sets", parser.grammar.first)
    print_set_map("FOLLOW Sets", parser.grammar.follow)

    print("\n---- LL(1) Parsing Table (filled entries) ----")
    for nonterminal in sorted(parser.grammar.parsing_table.keys()):
        row = parser.grammar.parsing_table[nonterminal]
        for terminal in sorted(row.keys()):
            production = " ".join(row[terminal])
            print(f"M[{nonterminal}, {terminal}] = {production}")

    try:
        if trace:
            print("\n---- Parser Tree ----")
        parse_tree = parser.parse()
        # 7. Show the parse tree and final parse status
        print()
        parse_tree.print_tree()
        if parser.errors:
            print("\nPARSING COMPLETED WITH RECOVERY")
            for issue in parser.errors:
                print(f"- {issue}")
            print("\n[!] ICG Aborted: Input contains syntax errors.")
        else:
            print("\nSUCCESS: Input successfully parsed")
            ast_builder = ASTBuilder()
            ast = ast_builder.build(parse_tree)
        
            icg = ICGenerator()
            icg.generate(ast)
            icg.print_quads()
        
    except SyntaxError as e:
        print(f"\nPARSING ERROR: {e}")

if __name__ == "__main__":
    main()