import copy
import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
        constraints; in this case, the length of the word.)
        """
        for var in self.domains:
            # A copy of the set of words from the domain
            words = set(self.domains[var])
            # For each word that could fill the variable, check whether it satisfies the unary constraint (word length).
            for word in words:
                # If the number of letters in the word doesn’t match, it is inconsistent with the unary constraint.
                if len(word) != var.length:
                    self.domains[var].remove(word)

    def revise(self, x, y) -> bool:
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        words_x = self.domains[x]
        words_y = self.domains[y]
        overlap = self.crossword.overlaps[x, y]
        if overlap is None:
            # No revision needed
            return False
        # unpack the tuple of the crossword overlaps
        x_index, y_index = overlap
        # iterate over a copy of the set to avoid mutations
        for word_x in set(words_x):
            is_consistent = False
            for word_y in words_y:
                if word_x[x_index] == word_y[y_index]:
                    is_consistent = True
                    break
            if not is_consistent:
                words_x.remove(word_x)
                revised = True
        return revised


    def ac3(self, arcs=None) -> bool:
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # If no arcs, start with queue of all arcs
        if not arcs:
            arcs = []
            for var in self.crossword.variables:
                for neighbor in self.crossword.neighbors(var):
                    arcs.append((var, neighbor))
        # Create a list of queued arcs
        queue = list(arcs)

        while queue:
            # Remove and return last element of the queue list, returns True if it removed anything.
            x, y = queue.pop()
            # Looks at the overlap of x and y
            if self.revise(x, y):
                # If nothing in the domain
                if not self.domains[x]:
                    return False
                # Add neighbours to the queue - except the revised one
                # Check whether other variables (z) are still consistent with respect to x
                for z in (self.crossword.neighbors(x) - {y}):
                    queue.append((z, x))
        return True


    def assignment_complete(self, assignment) -> bool:
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        # Loop over every variable in the crossword, should have one entry per variable
        for var in self.domains:
            if var not in assignment:
                return False
        return True


    def consistent(self, assignment: dict) -> bool:
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        assignment is a dict: {Variable: "word"}
        assignment.keys() are Variables. assignment.values() are strings
        """
        # No repeated words (all-different): number of unique words ≠ number of assigned variables
        # at least one word has been reused → inconsistent.
        if len(set(assignment.values())) != len(set(assignment.keys())):
            return False
        # Word must fit the slot's length
        for var, word in assignment.items():
            # Length constraint (unary)
            if var.length != len(word):
                return False
            # Overlap constraint between neighbors (binary)
            # For any neighbor that is already assigned, the letters at the overlapping position must match
            for neighbor in self.crossword.neighbors(var):
                if neighbor in assignment.keys():
                    x_index, y_index = self.crossword.overlaps[var, neighbor]
                    # Compare the letters at the shared cell
                    if word[x_index] != assignment[neighbor][y_index]:
                        return False
        return True

    def order_domain_values(self, var, assignment: dict) -> list:
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        (sorted from least damaging ➜ most damaging).
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        scores = {}  # number of neighbor values it rules out, lower the score, the better the word

        for word in self.domains[var]:
            ruled_out = 0
            # Check each neighbor that isn't already assigned
            for neighbor in self.crossword.neighbors(var):
                # If neighbor already has a fixed word in the current partial assignment,
                # it doesn't lose "options" anymore, so don't include it in ruled_out counting
                if neighbor in assignment:
                    continue
                # Get the overlap constraint positions
                overlap = self.crossword.overlaps[var, neighbor]
                if overlap is None:
                    # No actual overlap, so this word doesn't constrain that neighbor
                    continue

                x_index, y_index = overlap

                # For this neighbor, count how many of options would be ruled out (invalidated)
                for neighbor_word in self.domains[neighbor]:
                    if word[x_index] != neighbor_word[y_index]:
                        ruled_out += 1

            scores[word] = ruled_out

        # Sort the words in var's domain by how few neighbor values they kill
        return sorted(scores, key=lambda w: scores[w])


    def select_unassigned_variable(self, assignment: dict):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # Get variables that still need values
        unassigned_var = self.crossword.variables  - set(assignment.keys())
        # Put the unassigned variables into a list
        result = list(unassigned_var)
        # Sort using MRV (Minimum Remaining Values), then degree (higher better)
        result.sort(
            key=lambda x: (
                len(self.domains[x]), -len(self.crossword.neighbors(x)))
        )
        # Returns the best variable, after sorting, it is first in the list
        if result:
            return result[0]
        else:
            return None


    def backtrack(self, assignment: dict):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # Returns a final solution
        if self.assignment_complete(assignment):
            return assignment
        # Chooses which variable to assign next
        unassigned_var = self.select_unassigned_variable(assignment)
        # Tries each possible word for that variable
        for value in self.order_domain_values(unassigned_var, assignment):
            assignment[unassigned_var] = value
            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result is not None:
                    return result
            # If not consistent or recursion failed, undo and try next value
            del assignment[unassigned_var]
        # If no value worked, fail upward
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
