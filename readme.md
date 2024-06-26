# Non-interference analyzer 

A static analyzer implementing our information flow calculus (work in progress).

## How it works

1. User specifies an input file.
2. The input is parsed into a parse-tree.
3. The analysis processes the parse tree and captures security-flow matrix data.
4. The result of the previous step is written to a file (an intermediate result).
5. the captured matrix data is evaluated (separately). 

Same, but visually in two steps:

```
[input].java                         ┐
---> parser                          │
---> parse-tree                      ├─ analysis phase (* in progress)
---> analyze tree                    │  
---> gather matrix data              │
---> write data to [input].json      ┘

[input].json                         ┐
---> evaluate matrix data            ├─ evaluation phase [TODO]
---> get interesting info            ┘  
```

**Reading the analysis result**

The data captured in the analysis phase includes:

```
input              # path to the analyzed input file            str                
result             # analysis outcomes                          dict                
  class_name       # full hierarchical name                     dict[str,dict]     
    identifier     # method name #1                             dict[str,dict]     
      variables    # encountered variables, see note below      List[str]           
      source       # method source code, for reference          str                 
      flows        # violating variable pairs (in, out)         List[(str,str)]    
    identifier     # method name #2 (if any)                  
      …            # method data                  
  class_name       # another class (if any)                  
    …              # class data                  
```

The variables list does not necessarily contain every variable of the program.
It excludes variables that occur only in "uninteresting" statements, e.g., an unused variable declaration. 
This is because the analysis handles only specific statements -- those that belong to the analysis syntax -- and skips others.
The variables list contains variables that occurred in these handled statements.

The results do not show a full security flow matrix, but combining flows and variables is sufficient to capture fully the matrix data, since it is a binary matrix.

## Usage


1. **Install dependencies**

   ```
   pip install -r requirements.txt
   ```

2. **Run analyzer on input program**

   Supported input languages: Java v. 7/8/11/17.

   By default, the result is pretty-printed at the screen.
   To write the result to a file, specify `-o FILE`.

   ```
   python3 -m analysis [input program] {optional args}
   ```

   For example

   ```
   python3 -m analysis programs/IFCprog1/Program.java
   ```

3. **For help**, and for a full list of available arguments, run 

   ```
   python3 -m analysis
   ```


## Development

**About design choices**

* No optimizations are applied to the input program; it is analyzed as-is (excl. comments).
* All variables, methods, etc. retain their original identifiers.
* The Java parser is generated, with [ANTLR](https://www.antlr.org/), from the grammars.
* Using ANTLR has many benefits for this kind of project:
  * Can add front-end languages with low(-ish) overhead. 
  * Can choose input languages so that comparisons with previous works is possible.
  * Analyzer implementation freedom: can choose any ANTLR target language.
  * Adding OOP concepts later should be implementationally straightforward.
  * Immediately have a precise documented specification of supported inputs.
  * See list of available [grammars](https://github.com/antlr/grammars-v4) if this is of interest.
* Everything done here should be doable in compiler IR.
  * Parse tree has more information than necessary; the analysis could do with less.
  * Current design makes the analyzer light and isolated for simplicity.
  * No reason so far why it could not take place inside a compiler.   

**Repository organization**

```
.
├─ analysis/               # analyzer source code
│  ├─ parser/              # generated parser (from grammars)
│  └─ *                    # analyzer implementation
├─ grammars/               # input language specifications
├─ programs/               # example programs for analysis
├─ tests/                  # unit tests
├─ Makefile                # helpful commands
├─ readme.md               # instructions
├─ requirements.txt        # Python dependencies 
├─ requirements-dev.txt    # Python development dependencies
└─ setup.sh                # automation script for dev-env setup  
```````

**Commands**

Some helpful commands

```
make test     # run unit tests
make lint     # run linter
make ptest    # try parse all programs
make clean    # remove generated files (except parser)
make help     # lists other available commands
```

* Running these commands assumes dev requirements are installed.
  Run `setup.sh` for easy dev-setup.

* The analyzer expects input in high-level input language, i.e., 
  a `.java` file. It is not necessary to compile the java programs.
  But bytecode may be interesting, so there are commands to generate 
  bytecode.

* It is also not necessary to rebuild the parser; it is already built. 
  But it is easy to rebuild, if necessary, with ANTLR and using the Makefile commands.

