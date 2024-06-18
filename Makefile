ANTLRV=4.13.1  # must match install in requirements.txt
GRAMMAR=grammars/JavaLexer.g4 grammars/JavaParser.g4
TARGET=Python3
OUT=./src/parser

all: build

build: $(GRAMMAR)
	antlr4 -v $(ANTLRV) $(GRAMMAR) \
	-Dlanguage=$(TARGET) \
	-visitor -no-listener \
	-Xexact-output-dir \
	-o $(OUT)

clean:
	rm -rf $(OUT)