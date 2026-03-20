# Compiler Construction - Lexer Project

This project is a simple lexical analyzer (scanner) for a mini programming language(mini-python).
It is part of compiler construction practice and focuses on turning source code into
tokens that can later be used by a parser.

The scanner currently recognizes:
- Keywords: `if`, `else`, `while`
- Identifiers
- Numbers
- Strings
- Operators
- Separators
- End-of-file (EOF)

## Project Structure

- `src/lexer.py`: Scanner logic
- `src/tokens.py`: Token class definition
- `src/main.py`: Entry point that reads a source file and prints tokens
- `src/sample_code.mpy`: Example mini-language program

## How To Run

1. Open a terminal in the project root:

	```bash
	cd /your_project_path/compiler_construction
	```

2. (Optional) Create and activate your virtual environment:

	```bash
    python3 -m venv venv
	source venv/bin/activate
	```

3. `main.py` currently reads from `sample_code.mpy`. Create the expected input file in `src/`:

	```bash
	cp src/sample_code.mpy 
	```

4. Run the program from the `src` directory:

	```bash
	cd src
	python3 main.py
	```

You should see scanner output in the terminal as tokens are read from the sample program.

