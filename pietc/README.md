## Files

### `lex.py`

Defines the tokens used by the lisp interpreter.

### `parse.py`

The grammar for the lisp interpreter.

### `eval.py`

`eval.py` defines how the grammar is interpreted logically.
Here are where *procedures* are defined, which are the functions that manipulate the environment within a particular scope (represented as a dictionary between "symbols" and their definitions).
The main control loop for this module is defined by the function `evaluate`.

### `piet.py`

An overhaul on how `piet` commands are managed.
This file holds the definitions for *operations*, which are functions that contribute to the end program that will be drawn to the image.

### `image.py`

Currently underdeveloped, this file attempts to overhaul the methods by which the end codels for the `piet` program are drawn.
