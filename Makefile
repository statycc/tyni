all: test

help:
	@echo "ptest       ─ try parse all programs"
	@echo "test        ─ run unit tests"
	@echo "compile     ─ compile java programs to bytecode (.class)"
	@echo "bytecode    ─ translate .class files to readable bytecode"
	@echo "parser      ─ build a parser from grammars"
	@echo "rebuild     ─ forcibly re-build the parser"
	@echo "clean       ─ remove all generated files (except parser)"

### ANTLR SETUP
ANTLR_V=4.13.1  # must match version in requirements.txt
GRAMMAR=grammars/JavaLexer.g4 grammars/JavaParser.g4
TARGET=Python3
OUT=./src/parser

### JAVA FILES
PNAME = Program
P_DIR = programs
O_DIR = build
B_DIR = bytecode
PROGS = $(patsubst %/,%, $(patsubst $(P_DIR)/%,%, $(dir $(wildcard $(P_DIR)/*/$(PNAME).java))))

### ANALYSIS
ANALYZER = analysis
DEFAULT_OUT = out

test: dev-env test_analysis

dev-env:
	@test -d venv || python3 -m venv venv;
	@source venv/bin/activate;
	@pip3 install -q -r requirements-dev.txt

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

ptest:
	@$(foreach p, $(PROGS), \
		echo "PARSE $(p)" && python3 -m $(ANALYZER) $(P_DIR)/$(p)/$(PNAME).java --parse -l 0 ; )

test_analysis:
	pytest --cov=$(ANALYZER) tests

clean:
	@rm -rf $(O_DIR) $(B_DIR) $(DEFAULT_OUT)
	@find . -name \*.Program.txt -type f -delete
