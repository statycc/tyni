# ᴛʏɴɪ

__The anytime non-interference analyzer.__

ᴛʏɴɪ is a static analyzer of data confidentiality issues, implementing the information flow logic $\top^{\ast}_{ɴɪ}$.
The name comes from anʏᴛime ɴon-ɪnterference, but since composition order is irrelevant, the letters compose to ᴛʏɴɪ. 

## How it works

1. User specifies an input file.
2. Input is parsed to obtain a parse-tree.
3. The parse tree is analyzed to construct a security-flow matrix (SFM).
4. The SFM is evaluated against a security policy and security classes using an SMT solver.

```
                   input.java
                        ↓
╔──── the ᴛʏɴɪ analyzer ──────────────────────────────╗
│  1. generate parse-tree : ANTLR parser              │
│  2. gather matrix data : logical analysis           │
│  3. evaluate matrix data : evaluation (Z3)          │
╚─────────────────────────────────────────────────────╝
                        ↓
                     result  
```

#### Interpreting the result

The analyzer captures details of the input file, data-flow facts, and timing information; incl. for each method:

    name               : Fully qualified method name
    variables          : Encountered variables, see note below               
    flows              : Interfering variable pairs (in, out)    
    satisfiability     : Solver outcome SAT/UNSAT                 
    model              : Security levels to make the method non-interfering
    skips              : Uncovered program statements (if any) 

* The variables list may be incomplete since "unintersting" variables are excluded.
* We can only make judgments for methods with full syntax coverage, otherwise the results are inconclusive.
* If a method includes uncovered statements, these statements are omitted by the analyzer and highlighted.
* To inspect all captured data, save the result to a file (use `--save` argument). 
* The full details of results gathered by the analyzer are defined in [`analysis/result`](analysis/result.py). 


## Getting started


1. Install dependencies

       pip install -r requirements.txt

   On an externally-managed environment, run

       python3 -m venv venv
       venv/bin/pip install -r requirements.txt

   and replace below `python3` with `venv/bin/python3`.

2. Run analyzer on input program

   By default, the result is pretty-printed at the screen.

       python3 -m analysis [input program] {optional args}

   The `programs` directory contains various input examples, e.g.:

       python3 -m analysis programs/ifcprog1/Program.java --save

3. For help and for a full list of available arguments, run

        python3 -m analysis


## About this repository 

#### Organization

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


#### Commands

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
