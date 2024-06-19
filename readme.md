# Non-interference analyzer 

A static analyzer of non-interference.

Supported input languages: 
* Java _(Java 7, Java 8, Java 11, Java 17)_

Overview

1. The analyzer parses the input.
2. While parsing, it captures e.g., security-flow matrix data.
3. The result of previous step is written to a file (this is an intermediate result).
4. TODO: the matrix data can be evaluated separately. 

**Usage**

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