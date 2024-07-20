all: lint test

help:
	@echo "test      ─ run unit tests"
	@echo "lint      ─ run linter"
	@echo "ptest     ─ try parse all programs"
	@echo "missing   ─ stmts missing test coverage (ignoring parser)"
	@echo "build     ─ compile java programs to bytecode"
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
P_DIR = examples
O_DIR = build
B_DIR = bytecode
PROGS = $(wildcard $(P_DIR)/*/*.java) $(wildcard benchmarks/JavaSourceCode/**/**/*.java)

### ANALYSIS
ANALYZER = analysis
DEFAULT_OUT = out

dev:
	@test -d venv || python3 -m venv venv;
	@source venv/bin/activate;
	@pip3 install -q -r requirements-dev.txt

build: $(P_DIR)
	@$(foreach p, $(PROGZ), javac -d ./$(O_DIR)/ $(P_DIR)/$(p)/*.java ; )

bytecode: $(O_DIR)
	@mkdir -p $(B_DIR)
	@$(foreach p, $(PROGZ), $(foreach c, $(notdir $(basename $(wildcard $(O_DIR)/$(p)/*.class))), \
	javap -cp $(O_DIR) -c $(p).$(c) >> $(B_DIR)/$(p).$(c).txt ; ))

parser: $(GRAMMAR)
	rm -rf $(POUT) && antlr4 -v $(ANTLR_V) $(GRAMMAR) -Dlanguage=$(TARGET) -visitor -no-listener -Xexact-output-dir -o $(OUT)

ptest: $(P_DIR)
	@$(foreach p, $(PROGS), echo "PARSE $(p)" && python3 -m $(ANALYZER) $(p) -r p -l 0 ; )

test:
	pytest --cov=$(ANALYZER) tests --show-capture=no

missing:
	pytest --cov-config=.cov_missing --cov-report term-missing:skip-covered --cov=$(ANALYZER) tests --show-capture=no

lint:
	flake8 $(ANALYZER) --count --show-source --statistics --exclude "$(ANALYZER)/parser"

cloc:
	cloc . --exclude-dir=venv,.idea,parser,out,build,.github,.pytest_cache,benchmarks

clean:
	@rm -rf $(O_DIR) $(B_DIR) $(DEFAULT_OUT)
	@rm -rf .pytest_cache tests/.pytest_cache .coverage .cov_missing
	@find . -name \*.Program.txt -type f -delete
