# Non-interference analyzer 

A static analyzer of data confidentiality issues, implementing our information flow logic (work in progress).

## How it works

1. User specifies an input file.
2. Parse the input to obtain a parse-tree.
3. Capture a security-flow matrix from the parse tree.
4. Evaluate the matrix against security policy and security classes using an SMT solver.

                             input.java
                                  ↓
         ╔──── the analyzer ──────────────────────────────────────╗
         │  1. generate parse-tree   // ANTLR parser              │
         │  2. gather matrix data    // analysis by NI logic      │
         │  3. evaluate matrix data  // evaluation (Z3)           │
         ╚────────────────────────────────────────────────────────╝
                                  ↓
                               result


## Interpreting results

The analyzer captures details of the input file, data-flow facts, and timing information; incl. for each method:

    name               : Fully qualified method name
    variables          : Encountered variables, see note below               
    flows              : Interfering variable pairs (in, out)    
    satisfiability     : Solver outcome SAT/UNSAT                 
    model              : Security levels to make the method non-interfering
    skips              : Uncovered program statements (if any) 

* The variables list may be incomplete; variables that occur only in "uninteresting" statements (e.g., an unused variable declaration) are excluded.
* We can only make judgments for methods with full syntax coverage, otherwise the results are inconclusive.
* If a method includes uncovered statements, these statements are omitted by the analyzer and highlighted.
* To inspect all captured data, save the result to a file (use `--save` argument). 
* The full details of results gathered by the analyzer are defined in [`analysis/result`](analysis/result.py). 


## Getting started


1. Install dependencies

       pip install -r requirements.txt

2. Run analyzer on input program

   By default, the result is pretty-printed at the screen.

       python3 -m analysis [input program] {optional args}

   The `programs` directory contains various input examples, e.g.:

       python3 -m analysis programs/ifcprog1/Program.java --save

3. For help and for a full list of available arguments, run

        python3 -m analysis


## Repository organization

    .
    ├─ .github/                # instructions and workflows      
    ├─ analysis/               # the analyzer source code
    │  ├─ analyzers/           # NI data-flow analysis
    │  ├─ parser/              # parser generated from grammars
    │  └─ *                    # other source code
    ├─ benchmarks/             # (submodule) ifspec benchmark suite
    ├─ grammars/               # input language specifications
    ├─ programs/               # example inputs for analysis
    ├─ tests/                  # analysis unit tests
    └─ *                       # development utilities, etc.


## Commands

Some helpful commands for development

    make test        # run unit tests
    make lint        # run linter
    make ptest       # try parse all programs & benchmarks
    make compile     # try compile all programs
    make clean       # remove generated files (except parser)
    make help        # lists other available commands

* Running these commands assumes dev requirements are installed (run `setup.sh` for setup).
* The analyzer expects input in high-level input language (a Java file).
* It is not necessary to compile the java programs, but doing so has benefits (e.g., checking input is valid)
* The parser is pre-built (but can be re-built with the Makefile commands).

#### About design choices

* No optimizations are applied to the input program; it is analyzed as-is (excl. comments).
* All variables, methods, etc. retain their original identifiers.
* The Java parser is generated, with [ANTLR](https://www.antlr.org/), from the grammars.
* Using ANTLR has many benefits for this kind of project:
    * Can add front-end languages with low(-ish) overhead.
    * Can choose input languages so that comparisons with previous works is possible.
    * Analyzer implementation freedom: can choose any ANTLR target language.
    * Adding OOP concepts later should be implementationally straightforward.
    * Immediately have a precise documented specification of supported inputs.
    * See list of all available [grammars](https://github.com/antlr/grammars-v4) if this is of interest.
* Everything done here should be doable in compiler IR.
    * Parse tree has more information than necessary; the analysis could do with less.
    * Current design makes the analyzer light and isolated for simplicity.
    * No reason so far why it could not take place inside a compiler.
