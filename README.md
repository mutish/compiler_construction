# Compiler Construction - Lexer Project

This project implements a basic lexical analyzer (scanner) for a mini Python-like language.
It is a compiler construction practice project focused on converting source code into tokens
that can be consumed by later phases (such as parsing and semantic analysis).

## What The Scanner Recognizes

- Keywords: `if`, `else`, `while`
- Identifiers
- Numbers (integers and decimal values)
- Strings (double-quoted)
- Operators (for example `+`, `-`, `*`, `/`, `=`, `==`, `!=`, `<`, `>`, `<=`, `>=`)
- Separators (`(`, `)`, `{`, `}`, `;`, `,`, `:`)
- End-of-file token (`EOF`)

## Project Structure

- `src/lexer.py` - Scanner logic (`Scanner` class)
- `src/tokens.py` - Token model (`Token` class)
- `src/main.py` - Entry point that reads source and prints tokens
- `src/sample_code.mpy` - Example mini-language input

## How To Run

1. Open a terminal in the project root:

```bash
cd /your_project_path/compiler_construction
```

2. (Optional) Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

3. Run the lexer:

```bash
python3 src/main.py
```

The program reads `src/sample_code.mpy` and prints tokens one by one.

## Example Output

Output follows this format:

```text
<TOKEN_TYPE, "lexeme", line N>
```

Example:

```text
<IDENTIFIER, "count", line 1>
<OPERATOR, "=", line 1>
<NUMBER, "0", line 1>
```

