How to run the project?

`$ python generate.py data/xxx.txt data/xxx.txt output.png`

example

`$ python generate.py data/structure1.txt data/words1.txt output.png`

**Variable**

Type: custom class (crossword.Variable)

Attributes:
- i: starting row index (int)
- j: starting column index (int)
- direction: Variable.ACROSS or Variable.DOWN
- length: number of cells the word occupies (int)

Description:
Represents a single slot in the crossword puzzle (horizontal or vertical).

**self.crossword.overlaps**

Type: dict[tuple[Variable, Variable], tuple[int, int] | None]

Description:
- Maps pairs of variables to their overlap positions, if any.
- Each pair (x, y) maps to a tuple (i, j) meaning that
x[i] and y[j] share the same crossword cell.

**assignment**

Type: dict[Variable, str]

Description:
A mapping between crossword variables (slots) and the words currently assigned to them.

**self.domains**

Type: dict[Variable, set[str]]

Description:
The domain of each variable: all words that could potentially fill that slot.
These sets are reduced as constraints (length, overlap consistency, etc.) are enforced.

**self.crossword.neighbors(var)**

Type: set[Variable]

Description:
Returns all variables that overlap with var at least once.