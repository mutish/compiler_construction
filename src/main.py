from lexer import Scanner
import sys

def main():
    try:
        with open('src/sample_code.mpy', 'r') as file:
            source_code = file.read()
    except FileNotFoundError:
        print("Error: sample_code.mpy not found.")
        return
    
    scanner = Scanner(source_code)
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

if __name__ == "__main__":
    main()