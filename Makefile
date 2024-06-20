all: parse_test

help:
	@echo "parse_test  ─ try parse all programs"
	@echo "bytecode    ─ translate .class files to readable bytecode"
	@echo "compile     ─ compile java programs to bytecode (.class)"
	@echo "parser      ─ build a parser from grammars"
	@echo "rebuild     ─ forcibly re-generate a parser"
	@echo "clean       ─ remove all generated files"

### ANTLR SETUP
ANTLR_V=4.13.1  # must match install in requirements.txt
GRAMMAR=grammars/JavaLexer.g4 grammars/JavaParser.g4
TARGET=Python3
OUT=./src/parser

### JAVA FILES
PNAME = Program
P_DIR = programs
O_DIR = build
B_DIR = bytecode
PROGS = $(patsubst %/,%, $(patsubst $(P_DIR)/%,%, $(dir $(wildcard $(P_DIR)/*/$(PNAME).java))))


compile: $(P_DIR)
	@$(foreach p, $(PROGS), javac -d ./$(O_DIR)/ $(P_DIR)/$(p)/*.java ; )

bytecode:
	@mkdir -p $(B_DIR)
	@$(foreach p, $(PROGS), $(foreach c, $(notdir $(basename $(wildcard $(O_DIR)/$(p)/*.class))), \
	javap -cp $(O_DIR) -c $(p).$(c) >> $(B_DIR)/$(p).$(c).txt ; ))

parser: $(GRAMMAR)
	antlr4 -v $(ANTLR_V) $(GRAMMAR) -Dlanguage=$(TARGET) -visitor -no-listener -Xexact-output-dir -o $(OUT)

rebuild:
	rm -rf $(OUT) && make parser

parse_test:
	@$(foreach p, $(PROGS), \
		echo "PARSE $(p)" && python3 -m src $(P_DIR)/$(p)/$(PNAME).java --parse -l 0 ; )

clean:
	@rm -rf $(O_DIR) $(B_DIR) output
	@find . -name \*.Program.txt -type f -delete
