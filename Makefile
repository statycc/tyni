all: compile

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

rebuild_parser:
	rm -rf $(OUT)
	make parser

parse_test:
	@$(foreach p, $(PROGS), python3 -m src $(P_DIR)/$(p)/$(PNAME).java --parse -l vvvv ; )

clean:
	@rm -rf $(O_DIR) $(B_DIR) output
	@find . -name \*.Program.txt -type f -delete
