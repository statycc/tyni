# Non-interference analyzer 

A static analyzer of non-interference (work in progress).

### How it works

1. User specifies an input file, in one of the supported input languages.
2. The input is parsed into a parse-tree.
3. The analysis processes the parse tree and captures security-flow matrix data.
4. The result of previous step is written to a file (this is an intermediate result).
5. the captured matrix data is evaluated separately. 

Same, but more visually

```
input.java                           ┐
---> parser                          │
---> parse-tree                      ├─ analysis phase
---> analyze tree(*)                 │  
---> get matrix data                 │
---> write data to input.json        ┘

input.json                           ┐
---> evaluate matrix data            ├─ evaluation phase
---> TODO...                         ┘  
```

`(*)` the current active area; to improve analysis of the tree and handle more (accurately) statements and expressions.

The data captured by the analysis includes:

```
 "input_prog"        // input file path; the analyzed program
 "result"            // analysis outcome for each method in the class 
   "identifier"      // method name #1
     "method"        // the raw source code (for reference) 
     "flows"         // violating variable pairs as [in, out]
     "variables"     // encountered variables, see note below 
   "identifier2"     // method name #2 ...
     ... 
```

The variables list is not necessary complete. 
It will not include variables that occur only in "uninteresting" statements (e.g., an unused declaration would not show up in this list). 
These uninteresting cases are outside the scope of the analysis syntax anyway.

This output structure also assumes 1 class/input file, which is a normal assumption for Java, but not other languages.
A better file structure would be result > class name > methods.

### Usage


1. **Install dependencies**

   ```
   pip install -r requirements.txt
   ```

2. **Run analyzer on input program**

   Supported input languages: Java (v. 7/8/11/17)

   ```
   python3 -m src [input program]
   ```

   For example

   ```
   python3 -m src programs/IFCprog1/Program.java
   ```

3. **For help**, and for full list of command arguments, run 

   ```
   python3 -m src
   ```

### Repository organization

```
.
├─ grammars/               # specs for recognized inputs
├─ programs/               # example programs to analyze
├─ src                     # source code
│  ├─ parser/              # generated parser for grammars
│  └─ *                    # analyzer implementation
├─ Makefile                # helpful commands
├─ readme.md               # instructions
├─ requirements.txt        # Python dependencies 
├─ requirements-dev.txt    # development dependencies
└─ setup.sh                # automation script for dev setup  
```
   
### Developer commands

```
make ptest  : try parse all programs
make clean  : remove generated files (except parser)
make help   : other available commands
```

Notes

* Running these commands assumes dev requirements are installed.

* The analyzer expects input in high-level input language, i.e., 
  a `.java` file. It is not necessary to compile the java programs.
  But bytecode may be interesting, so there are commands to generate 
  bytecode.

* It is also not necessary to rebuild the parser; it is already built
  (in `src/parser`). But it is easy to rebuild, if necessary, with 
  ANTLR and using the Makefile commands.

### Notes about design choices

* No optimizations are applied to the input program.
* All variables, methods, etc. retain their original identifiers.
* The Java parser is generated with [ANTLR](https://www.antlr.org/), from the grammars under `grammars/`.
* Using ANTLR has many benefits for this kind of project:
  * Can add front-end languages with low(-ish) overhead. 
  * Can choose input languages so that comparisons with previous works is possible.
  * Adding OOP concepts later should be implementationally straightforward.
  * Implementation freedom: any of the 10 ANTLRv4 targets can be selected.
  * See list of defined [grammars](https://github.com/antlr/grammars-v4), if this is of interest.
* Everything done here should be doable in compiler IR.
  * Parse tree has more information than necessary; the analysis could do with less.
  * Current design makes the analyzer light and isolated on purpose.
  * No reason so far why it could not take place inside a compiler.
    


