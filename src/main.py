from lexer import Scanner
import sys

def main():
    try:
        with open('sample_code.mpy', 'r') as file:
            source_code = file.read()
    except FileNotFoundError:
        print("Error: sample_code.mpy not found.")
        return
    
    scanner = Scanner(source_code)

    print("---- Scanner Output ----")

    while True:
        try:
            token =  scanner.get_next_token()
            print(token)

            if token.type == "EOF":
                break
        except Exception as e:
            print(f"Error encountered: {e}")
            break

if __name__ == "__main__":
    main()