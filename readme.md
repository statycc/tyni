# Non-interference analyzer 

A static analyzer of non-interference.

### How it works

1. User specifies an input file, written in one of the supported input languages.
2. The input is parsed into a parse-tree.
3. The analysis processes the parse tree and captures security-flow matrix data.
4. The result of previous step is written to a file (this is an intermediate result).
5. TODO: the captured matrix data is evaluated separately. 

Same, but more visually

```
input.java                           ┐
---> parser                          │
---> parse-tree                      ├─ "analysis phase"
---> analyze tree                    │  
---> matrix data                     │
---> write matrix data to file       ┘

NEXT: evaluate matrix data           ─ "evaluation phase"  
```


### Usage

Supported input languages (extendable):
* Java (versions 7, 8, 11, and 17)

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

3. For help and command arguments, run 

   ```
   python3 -m src
   ```
   
### Developer commands

The analyzer expects high-level input language inputs, i.e., a .java file. 
It is not necessary to compile the java programs 
(but bytecodes may be interesting, so there are commands for it below).

It is also not necessary to rebuild the parser; it is already built.
But it is easy to rebuild if necessary.

```
make compile         -- compiles all java programs to bytecode (.class files)
make bytecode        -- translates .class files to "readble bytecode"
make parser          -- compile parser from grammars
make rebuild_parser  -- force recompilation of the parser
make parse_test      -- try parse all programs
make clean           -- remove generated files (except parser)
```

### Notes about design choices

* No optimizations are applied to the input program
* All variables retain their original names
* The Java parser is generated with [ANTLR](https://www.antlr.org/), from the grammars under `grammars/`.
* Using ANTLR has many benefits for this kind of project:
  * Can add front-end languages with low-ish overhead 
  * Can choose input languages that make comparisons with previous works possible 
  * Adding OOP concepts later should be implementationally straightforward
  * Analyzer implementation freedom; any ANTLR target can be selected
  * See list of [grammars](https://github.com/antlr/grammars-v4) for interest
* Everything done here should be doable in compiler IR
  * parse tree has more information than necessary; the analysis could do with less
  * this analyzer design is light and isolated on purpose, but no reason so far why
    it could not take place inside a compiler.
    


