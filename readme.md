# Non-interference analyzer 

A static analyzer of non-interference (work in progress).

### How it works

1. User specifies an input file, written in one of the supported input languages.
2. The input is parsed into a parse-tree.
3. The analysis processes the parse tree and captures security-flow matrix data.
4. The result of previous step is written to a file (this is an intermediate result).
5. the captured matrix data is evaluated separately. 

Same, but more visually

```
input.java                           ┐
---> parser                          │
---> parse-tree                      ├─ "analysis phase"
---> analyze tree(*)                 │  
---> get matrix data                 │
---> write data to file              ┘

NEXT: evaluate matrix data           ─ "evaluation phase"  
```

`(*)` is the current active work area; to improve analysis of the tree and handle more (accurately) statements and expressions.


### Usage


1. **Install dependencies**

   ```
   pip install -r requirements.txt
   ```

2. **Run analyzer on input program**

   Supported input languages (extendable): Java (versions 7, 8, 11, and 17)

   ```
   python3 -m src [input program]
   ```

   For example

   ```
   python3 -m src programs/IFCprog1/Program.java
   ```

3. **For help** and command arguments, run 

   ```
   python3 -m src
   ```
   
### Developer commands

```
make parse_test      -- try parse all programs
make clean           -- remove generated files (except parser)
make help            -- other available commands
```

Notes: 

* The analyzer expects input in high-level input language, i.e., a .java file. 
  It is not necessary to compile the java programs.
  But bytecode may be interesting, so there are commands to generate bytecode.

* It is also not necessary to rebuild the parser; it is already built.
  But it is easy to rebuild, if necessary, with ANTLR and using the Makefile commands.

### Notes about design choices

* No optimizations are applied to the input program
* All variables, methods, etc. retain their original identifiers
* The Java parser is generated with [ANTLR](https://www.antlr.org/), from the grammars under `grammars/`.
* Using ANTLR has many benefits for this kind of project:
  * Can add front-end languages with low-ish overhead 
  * Can choose input languages so that comparisons with previous works is possible 
  * Adding OOP concepts later should be implementationally straightforward
  * Analyzer implementation freedom: any ANTLR target can be selected
  * See list of defined [grammars](https://github.com/antlr/grammars-v4) for interest
* Everything done here should be doable in compiler IR
  * parse tree has more information than necessary; the analysis could do with less
  * current design makes the analyzer light and isolated on purpose 
  * no reason so far why it could not take place inside a compiler
    


