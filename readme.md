# Non-interference analyzer 

A static analyzer implementing our information flow calculus (work in progress).

### How it works

1. User specifies an input file.
2. The input is parsed into a parse-tree.
3. The analysis processes the parse tree and captures security-flow matrix data.
4. The result of the previous step is written to a file (an intermediate result).
5. the captured matrix data is evaluated (separately). 

Same, but more visually, in two steps:

```
[input].java                         ┐
---> parser                          │
---> parse-tree                      ├─ analysis phase (* in progress)
---> analyze tree                    │  
---> gather matrix data              │
---> write data to [input].json      ┘

[input].json                         ┐
---> evaluate matrix data            ├─ evaluation phase [TODO]
---> get interesting infromation     ┘  
```

The data captured in the analysis phase includes:

```
 "input_prog"          // the analyzed program (file path)
 "result"              // analysis outcomes 
   "class_name"        // possibly nested, with dot operator
     "identifier"      // method name #1
       "method"        // method source code (for reference) 
       "flows"         // violating variable pairs [in, out]
       "variables"     // encountered variables, see note below 
     "identifier"      // method name #2 
       ...             // method data
   "class_name"        // another class (if any)
     ...               // class data
```

The variables list is not always complete. 
It will not include variables that occur only in "uninteresting" statements, e.g., an unused declaration would not show up in variables. 
This is because the analysis proceed by looking at specific statements in the program -- those that belong to the analysis syntax, like loops and conditionals -- and skips others.
The variables list contains all variables that occurred in the handled statements.

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

3. **For help**, and for a full list of command arguments, run 

   ```
   python3 -m src
   ```

### Repository organization

```
.
├─ grammars/               # specs for recognized inputs
├─ programs/               # example programs to analyze
├─ src                     # source code
│  ├─ parser/              # generated parser (from grammars)
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

* Running these commands assumes dev requirements are installed.

* The analyzer expects input in high-level input language, i.e., 
  a `.java` file. It is not necessary to compile the java programs.
  But bytecode may be interesting, so there are commands to generate 
  bytecode.

* It is also not necessary to rebuild the parser; it is already built
  (in `src/parser`). But it is easy to rebuild, if necessary, with 
  ANTLR and using the Makefile commands.

### About design choices

* No optimizations are applied to the input program; it is analyzed as-is.
* All variables, methods, etc. retain their original identifiers.
* The Java parser is generated with [ANTLR](https://www.antlr.org/), from the grammars.
* Using ANTLR has many benefits for this kind of project:
  * Can add front-end languages with low(-ish) overhead. 
  * Can choose input languages so that comparisons with previous works is possible.
  * Adding OOP concepts later should be implementationally straightforward.
  * Analyzer implementation freedom: any ANTLR target language (of 10).
  * See list of defined [grammars](https://github.com/antlr/grammars-v4), if this is of interest.
* Everything done here should be doable in compiler IR.
  * Parse tree has more information than necessary; the analysis could do with less.
  * Current design makes the analyzer light and isolated, for simplicity.
  * No reason so far why it could not take place inside a compiler.
