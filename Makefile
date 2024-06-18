ANTLRV=4.13.1  # must match requirements.txt

GRAMMAR=Expr.g4
OUT=parser

all: build

build: Expr.g4
	@test -d $(OUT) || mkdir $(OUT)
	antlr4 -v $(ANTLRV) -Dlanguage=Python3 -visitor $(GRAMMAR) -o $(OUT)

clean:
	rm -rf $(OUT)