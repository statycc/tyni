# Non-interference analyzer 

A static analyzer of non-interference.

Supported input languages (extendable): 
* Java _(versions 7, 8, 11, and 17)_

What happens under the hood:

1. User specifies an input file, written in one of the supported input languages.
2. The input is parsed into a parse-tree.
3. The analysis runs over the parse tree, and captures security-flow matrix data.
4. The result of previous step is written to a file -- this is an intermediate result.
5. TODO: the captured matrix data can be evaluated separately. 

### Usage

1. Install dependencies

   ```
   pip install -r requirements.txt
   ```

2. Run

   ```
   python3 -m src [input program]
   ```
   
   for example

   ```
   python3 -m src programs/IFCprog1/Program.java
   ```

   For usage help, run 

   ```
   python3 -m src
   ```
   
### Developer commands

```
make compile         -- compiles java programs to bytcode (.class)
make bytecode        -- transpate the above to "readble bytecode" for inspection
make parser          -- compile parser from grammars
make rebuild_parser  -- forces recompile of the parser
make parse_test      -- try parse all programs
make clean           -- remove generated files (except parser)
```

### Notes

* No optimizations are applied to the input program
* All variables retain their original names
* The Java parser is generated with [ANTLR](https://www.antlr.org/) v4 from the grammars under `grammars/`.
* The parser fails on unicode symbols in comments, so I removed those
* ANTLR enables fast prototyping and adding front-end languages later with low overhead
  * This allows comparing with previous works (but maintains implementation freedom)
  * See list of [grammars](https://github.com/antlr/grammars-v4) for interest
  * Adding OOP concepts later should be (implementationally) straightforward 
* Everything done here should be doable in compiler IR

