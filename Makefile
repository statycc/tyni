all: build


build: Expr.g4
	antlr4 -v 4.13.0 -Dlanguage=Python3 -visitor Expr.g4