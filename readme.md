# Non-interference analyzer 

A static analyzer implementing our information flow calculus (work in progress).

## How it works

1. User specifies an input file.
2. The input is parsed into a parse-tree.
3. Security-flow matrix data is captured from the parse tree.
4. The matrix data is evaluated against security levels using SMT solver. 

Same, but visually in steps:

```
[input].java                         ┐
---> parser                          ├─ parsing
---> parse-tree                      ┘
                                     ┐
---> analyze tree                    ├─ analysis
---> gather matrix data              ┘      
                                     ┐
---> evaluate matrix data            ├─ evaluation
---> get interesting info            ┘  
```

**Interpreting the analysis results**

The analyzer captures data during the execution phases, including e.g., input details, execution arguments, and timing information.
The data captured during the analysis and evaluation phases includes, for each method:

```
method name        # Full name, as class_name(s).method_name
variables (Vars)   # Encountered variables, see note below               
flows              # Interfering variable pairs (in, out)    
satisfiability     # SMT-solver outcome: SAT or UNSAT                 
model              # If SAT, the satisfiable security levels  
                   #   that make the program non-inteferring           
```

The variables list does not necessarily contain every variable of the method.
Variables that occur only in "uninteresting" statements, e.g., an unused variable declaration, are excluded.
To inspect all captured data, save the result to a file. 

## Usage


1. **Install dependencies**

   ```
   pip install -r requirements.txt
   ```

2. **Run analyzer on input program**

   Supported input languages: Java v. 7/8/11/17.

   By default, the result is pretty-printed at the screen.
   To write the result to a file, specify `--save`.

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
  But it is easy to rebuild, if necessary, with ANTLR and the Makefile commands.

