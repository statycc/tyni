# Non-interference analyzer 

A static analyzer of non-interference.

Supported input languages: 
* Java _(Java 7, Java 8, Java 11, Java 17)_

Overview

1. Parse the input.
2. While parsing, the analysis captures security-flow matrix data.
3. The result of previous step is written to a file (this is an intermediate result).
4. TODO: the matrix data can be evaluated separately. 

### Usage

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
   
   The result will be saved to file.


### Notes

* No optimizations are applied to the input program
* All variables have their original names
* The Java parser is generated with [ANTLR4](https://www.antlr.org/) from the grammars under `grammars/`.
* The above enables fast prototyping and adding front-end languages later with low overhead
  * the goal is to allow comparing with previous works (but maintain implementation freedom about how that is done)
  * see list of [grammars](https://github.com/antlr/grammars-v4) for details
  * this approach is flexible to accommodate adding OOP concepts later
* Everything done here should be doable in compiler IR
