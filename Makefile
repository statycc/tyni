all: lint test

help:
	@echo "test      ─ run unit tests"
	@echo "lint      ─ run linter"
	@echo "ptest     ─ try parse all programs"
	@echo "missing   ─ stmts missing test coverage (ignoring parser)"
	@echo "compile   ─ compile java programs to bytecode"
	@echo "bytecode  ─ compile java programs to -readable- bytecode"
	@echo "parser    ─ build a parser from grammars"
	@echo "cloc      ─ code stats (requires cloc)"
	@echo "clean     ─ remove all generated files (except parser)"

### ANTLR SETUP
ANTLR_V=4.13.1  # must match version in requirements.txt
GRAMMAR=grammars/JavaLexer.g4 grammars/JavaParser.g4
TARGET=Python3
POUT=./src/parser

### JAVA FILES
PNAME = Program
P_DIR = programs
O_DIR = build
B_DIR = bytecode
PROGZ = $(patsubst %/,%, $(patsubst $(P_DIR)/%,%, $(dir $(wildcard $(P_DIR)/*/$(PNAME).java))))
PROGS = $(wildcard $(P_DIR)/**/*.java) $(wildcard benchmarks/JavaSourceCode/**/**/*.java)
BENCH = $(wildcard benchmarks/JavaSourceCode/**/**/*.java)

### ANALYSIS
ANALYZER = analysis
OUTPUT = out

dev:
	@test -d venv || python3 -m venv venv;
	@source venv/bin/activate;
	@pip3 install -q -r requirements-dev.txt

compile: $(P_DIR)
	@$(foreach p, $(PROGZ), echo "COMPILE $(p)/*.java" && javac -d ./$(O_DIR)/ $(P_DIR)/$(p)/*.java ; )

bytecode: $(O_DIR)
	@mkdir -p $(B_DIR)
	@$(foreach p, $(PROGZ), $(foreach c, $(notdir $(basename $(wildcard $(O_DIR)/$(p)/*.class))), \
	javap -cp $(O_DIR) -c $(p).$(c) >> $(B_DIR)/$(p).$(c).txt ; ))

parser: $(GRAMMAR)
	rm -rf $(POUT) && antlr4 -v $(ANTLR_V) $(GRAMMAR) -Dlanguage=$(TARGET) -visitor -no-listener -Xexact-output-dir -o $(OUT)

ptest: $(P_DIR)
	@$(foreach p, $(PROGS), echo "PARSE $(p)" && python3 -m $(ANALYZER) $(p) -r p -l 0 ; )

bench:
	@python3 -m $(ANALYZER) benchmarks/JavaSourceCode -r a -l 0 -p "methods=0,time=0,code=0"

test:
	pytest --cov-config=.coveragerc --cov=$(ANALYZER) tests --show-capture=no

missing:
	pytest --cov-config=.coveragerc --cov=$(ANALYZER) tests --show-capture=no --cov-report term-missing:skip-covered

lint:
	flake8 $(ANALYZER) --count --show-source --statistics --exclude "$(ANALYZER)/parser"

cloc:
	cloc . --exclude-dir=venv,.idea,parser,out,build,.github,.pytest_cache,benchmarks

clean:
	@rm -rf $(O_DIR) $(B_DIR) $(OUTPUT)
	@rm -rf .pytest_cache tests/.pytest_cache .coverage .cov_missing
	@find . -name \*.Program.txt -type f -delete
