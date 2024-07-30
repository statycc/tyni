# Non-interference analyzer 

A static analyzer of data confidentiality issues, implementing our information flow calculus (work in progress).

## How it works

1. User specifies an input file.
2. Parse the input to obtain a parse-tree.
3. Capture a security-flow matrix from the parse tree.
4. Evaluate the matrix against security policy and security classes using a solver.

```
                                    input.java
                                         ↓
         ╔──── the analyzer ─────────────────────────────────────────────────╗
         │                                                                   │ 
         │  1. generate parse-tree   // parsing by ANTLR parser              │
         │                                                                   │
         │  2. gather matrix data    // data-flow analysis by IRC calculus   │
         │                                                                   │
         │  3. evaluate matrix data  // evaluation by solver                 │
         │                                                                   │
         ╚───────────────────────────────────────────────────────────────────╝
                                         ↓
              information about data confidentiality of the input program                              
```

## Interpreting analyzer results

The analyzer captures details of the input file, data-flow facts, and timing information;
including for each method:

```
name               : Fully qualified name
variables          : Encountered variables, see note below               
flows              : Interfering variable pairs (in, out)    
satisfiability     : Solver outcome SAT/UNSAT                 
model              : Security levels to make the method non-interfering
skips              : Uncovered program statements, if any 
```

* The variables list may be incomplete; variables that occur only in "uninteresting" statements (e.g., an unused variable declaration) are excluded.
* We can only make judgments for methods with full syntax coverage, otherwise the results are inconclusive.
* If a method includes uncovered statements, for practical reasons these statements are omitted by the analyzer, and highlighted.
* To inspect all captured data, save the result to a file. 
* The full details of results gathered by the analyzer are in [`analysis/result`](analysis/result.py). 


## Getting started


1. **Install dependencies**

   ```
   pip install -r requirements.txt
   ```

2. **Run analyzer on input program**

   By default, the result is pretty-printed at the screen.
   To write the result to a file, specify `--save`.

   ```
   python3 -m analysis [input program] {optional args}
   ```

   The `programs/` directory contains various example-inputs, for example:

   ```
   python3 -m analysis programs/ifcprog1/Program.java --save
   ```
   
   

3. **For help**, and for a full list of available arguments, run

   ```
   python3 -m analysis
   ```

4. **Other uses**

   <details><summary>Analyze and evaluate separately</summary>
  
    Use this strategy to evaluate the same program against different security policies, without repeating the prior steps.
    
    First, parse and analyze a program, and save the (intermediate) result to a file. 
    
    ```
    python3 -m analysis programs/ifcprog1/Program.java --run A --out result.json
    ```
    
    Then, give the prior result as input to the analyzer:
    
    ```
    python3 -m analysis result.json 
    ```
    
    </details>

## Development notes

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
  * See list of all available [grammars](https://github.com/antlr/grammars-v4) if this is of interest.
* Everything done here should be doable in compiler IR.
  * Parse tree has more information than necessary; the analysis could do with less.
  * Current design makes the analyzer light and isolated for simplicity.
  * No reason so far why it could not take place inside a compiler.


**Repository organization**

```
.
├─ analysis/               : analyzer source code
│  ├─ analyzers/           : analyzers for input languages
│  ├─ parser/              : generated parser (from grammars)
│  └─ *                    : implementation
├─ benchmarks/             : (submodule) benchmark suite
├─ grammars/               : input language specifications
├─ programs/               : example programs for analysis
├─ tests/                  : unit tests
├─ Makefile                : helpful commands
├─ readme.md               : instructions
├─ requirements.txt        : Python dependencies 
├─ requirements-dev.txt    : Python development dependencies
└─ setup.sh                : automation dev-env setup script

```````

**Commands**

Some helpful commands for development

```
make test                  : run unit tests
make lint                  : run linter
make ptest                 : try parse all programs & benchmarks
make compile               : try compile all programs
make clean                 : remove generated files (except parser)
make help                  : lists other available commands
```

* Running these commands assumes dev requirements are installed.
  Run `./setup.sh` for easy dev-setup.

* The analyzer expects input in high-level input language, i.e., a `.java` file.
  It is not necessary to compile the java programs, but

  * Bytecode may be interesting, so there are commands to generate bytecode.
  
  * The parser is more generous than a compiler, and will parse invalid 
    expressions. To make sure input programs are actually valid, 
    running them through a compiler is a useful sanity check.

* It is also not necessary to rebuild the parser; it is already built. 
  But can be rebuilt with the Makefile commands.

