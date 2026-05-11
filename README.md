# Compiler Construction - Complete Pipeline

A complete compiler implementation for a mini Python-like language featuring a full pipeline from lexical analysis through intermediate code generation.

## Compiler Phases

This project implements a **four-phase compiler**:

1. **Lexical Analysis (Lexer)** - Tokenizes source code into tokens
2. **Syntax Analysis (Parser)** - Builds a parse tree using LL(1) parsing
3. **AST Construction** - Converts parse tree into a clean Abstract Syntax Tree
4. **Intermediate Code Generation (ICG)** - Generates three-address code (quadruples)

## Grammar

The language supports the following constructs:

```
<program> ::= <stmt_list>
<stmt> ::= <assignment> | <if_stmt> | <while_stmt>
<assignment> ::= ID "=" <expr>
<if_stmt> ::= "if" <cond> ":" <stmt> "else" ":" <stmt>
<while_stmt> ::= "while" <cond> ":" <stmt>
<cond> ::= <expr> RELOP <expr>
<expr> ::= <term> <expr_prime>
<expr_prime> ::= ("+" | "-") <expr> | epsilon
<term> ::= ID | NUM | STR
```

See `CFG.txt` for the complete grammar definition.

## Lexer Features

- **Keywords:** `if`, `else`, `while`
- **Identifiers:** Variable names
- **Numbers:** Integer and decimal values
- **Strings:** Double-quoted literals
- **Operators:** `+`, `-`, `*`, `/`, `=`, `==`, `!=`, `<`, `>`, `<=`, `>=`
- **Separators:** `:`, `,`, `;`, `(`, `)`, `{`, `}`

## Project Structure

```
src/
├── main.py              # Entry point for the compiler pipeline
├── lexer.py             # Lexical analyzer (Scanner)
├── tokens.py            # Token data class
├── parser.py            # LL(1) table-driven parser
├── grammar.py           # Grammar definition and LL(1) table generation
├── parse_tree.py        # Parse tree node representation
├── ast_nodes.py         # AST node classes
├── ast_builder.py       # Parse tree to AST conversion
├── icg.py               # Intermediate Code Generator
├── quadruple.py         # Three-address code quadruple representation
├── error_handler.py     # Error collection and panic-mode recovery
├── sample_code.mpy      # Example input program
└── sample_error_demo.mpy # Example program with syntax errors
CFG.txt                 # Formal grammar specification
README.md               # This file
```

## How To Run

1. **Navigate to the project:**

```bash
cd /your_project_path/compiler_construction
```

2. **Set up environment (optional but recommended):**

```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Run the compiler:**

```bash
python src/main.py [--no-trace] [--show-grammar] [input_file]
```

**Options:**
- `--no-trace` - Skip detailed parser trace output
- `--show-grammar` - Display FIRST/FOLLOW sets and LL(1) table
- `input_file` - Source code file (defaults to `src/sample_code.mpy`)

4. **Example with error recovery:**

```bash
python src/main.py src/sample_error_demo.mpy
```

## Example Output

The compiler produces four main sections:

### 1. Scanner Output
```
Line  Lexeme   Token
----  -------  -------
1     while    KEYWORD
1     x        IDENTIFIER
1     >        OPERATOR
```

### 2. Parse Tree
```
<program>
└── <stmt_list>
    ├── <stmt>
    │   └── <while_stmt>
    │       ├── while('while')
    │       ├── <cond>
    │       └── ...
```

### 3. Parsing Status
- **SUCCESS:** If parsing completes without errors
- **PARSING COMPLETED WITH RECOVERY:** If errors occurred but panic-mode recovery succeeded

### 4. Intermediate Code (Three-Address Code)
```
---- Intermediate Code (Three-Address Code) ----
  0: L1:
  1:     t1 = x > 5
  2:     if_false t1 goto L2
  3:     t2 = msg == "Hello"
  4:     if_false t2 goto L3
  5:     t3 = x + 2
  6:     x = t3
```

## Error Handling

The parser uses **panic-mode recovery** to continue parsing after encountering errors:
- Records meaningful error messages (line number and what was expected)
- Synchronizes to the next valid token based on FOLLOW sets
- Allows the parser to recover and continue processing
- Lists all errors at the end of parsing

## Example Program

`src/sample_code.mpy`:
```
while x > 5:
    if msg == "Hello":
        x = x + 2
    else:
        x = x - 1
```

This generates intermediate code representing the control flow, conditional branches, and arithmetic operations.

