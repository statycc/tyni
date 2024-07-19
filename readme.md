# Non-interference analyzer 

A static analyzer implementing our information flow calculus (work in progress).

## How it works

1. User specifies an input file.
2. Parse the input to obtain a parse-tree.
3. Capture Security-flow matrix data from the parse tree.
4. Evaluate the matrix data against security levels using an SMT solver.

```
[input].java                         ┐
---> parser                          ├─ ❶ parsing 
---> parse-tree                      ┘
                                     ┐
---> analyze tree                    ├─ ❷ analysis 
---> gather matrix data              ┘      
                                     ┐
---> evaluate matrix data            ├─ ❸ evaluation 
---> get interesting info            ┘  
```

## Interpreting analyzer results

The analyzer captures data during the execution phases, including input file details, execution arguments, and timing information.
The data captured during the analysis and evaluation phases includes, for each method:

```
method name        # Full name (class.method)
identifiers        # Names of encountered variables, see note below               
flows              # Interfering variable pairs (in, out)    
satisfiability     # SMT-solver outcome, SAT or UNSAT                 
model              # If SAT, security levels to make the method non-interfering
skips              # List of unhandled statements           
```

* The variables list may be incomplete; variables that occur only in "uninteresting" statements (e.g., an unused variable declaration) are excluded.
* 
* To inspect all captured data, save the result to a file. 

## Getting Started


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
   python3 -m analysis programs/ifcprog1/Program.java
   ```

3. **For help**, and for a full list of available arguments, run

   ```
   python3 -m analysis
   ```

### Advanced usage

1. **Analyze and evaluate separately.**

   It is possible to run analysis and evaluation separately.
   This allows to evaluate the same program against different security policies, without repeating the prior steps.
   
   First, parse and analyze a program, and save the result to a file. 

   ```
   python3 -m analysis programs/IFCprog1/Program.java --run A --out result.json
   ```
   
   Then, give the prior result as input to the analyzer.

   ```
   python3 -m analysis result.json 
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

Some helpful commands for development

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

