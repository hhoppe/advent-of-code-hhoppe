# Package `advent-of-code-hhoppe`

[![CI](https://img.shields.io/github/actions/workflow/status/hhoppe/advent-of-code-hhoppe/main.yml?branch=main&label=CI)](https://github.com/hhoppe/advent-of-code-hhoppe/actions/workflows/main.yml)
[![PyPI](https://img.shields.io/pypi/v/advent-of-code-hhoppe)](https://pypi.org/project/advent-of-code-hhoppe/)
[![Python](https://img.shields.io/pypi/pyversions/advent-of-code-hhoppe)](https://pypi.org/project/advent-of-code-hhoppe/)
[![License](https://img.shields.io/github/license/hhoppe/advent-of-code-hhoppe)](https://github.com/hhoppe/advent-of-code-hhoppe/blob/main/LICENSE)

Python library to process Advent-of-Code puzzles in a Jupyter notebook.
See [a complete example](https://colab.research.google.com/github/hhoppe/advent_of_code/blob/main/2021/advent_of_code_2021.ipynb).

Install it using `pip install advent-of-code-hhoppe`.

Usage summary:

- The **preamble** optionally specifies reference inputs and answers for the puzzles, here using a
  `.tar.gz` file that is downloaded and extracted into the directory `./data`:
  ```
    YEAR = 2021
    PROFILE = 'google.Hugues_Hoppe.965276'
    TAR_URL = f'https://github.com/hhoppe/advent_of_code/raw/main/{YEAR}/data/{PROFILE}.tar.gz'
    advent = advent_of_code_hhoppe.Advent(year=YEAR, tar_url=TAR_URL)
  ```


- For **each day** (numbered 1..25, or 1..12 starting in 2025), the first notebook cell defines a `puzzle` object:

  ```
    puzzle = advent.puzzle(day=1)
  ```
  The puzzle input string is automatically read into the attribute `puzzle.input`.
  This input string is unique to each Advent participant.

  For each of the two puzzle parts, a function (e.g. `process1`) takes an input string and returns a string or integer answer.
  Using calls like the following, we time the execution of each function and verify the answers:
  ```
    puzzle.verify(1, process1)
    puzzle.verify(2, process2)
  ```

- At the end of the notebook, `advent.show_times()` prints a table of the **timing** results.

## Alternative ways to specify puzzle inputs/answers

- The puzzle inputs and answers can be read from individual files (or URLs), specified using
  patterns with the fields `year`, `day`, `part`, and `part_letter`:
  ```
    INPUT_URL = 'data/{year}_{day:02d}_input.txt'
    ANSWER_URL = 'data/{year}_{day:02d}{part_letter}_answer.txt'
    advent = advent_of_code_hhoppe.Advent(
        year=2021, input_url=INPUT_URL, answer_url=ANSWER_URL)
  ```

- The puzzle inputs and answers can be obtained directly from adventofcode.com using a web-browser session cookie and the `advent-of-code-data` PyPI package (a dependency of this package):

  ```
    # Fill in the session cookie in the following:
    !mkdir -p ~/.config/aocd && echo 53616... >~/.config/aocd/token
    advent = advent_of_code_hhoppe.Advent(year=2021)
  ```
  If the token file exists, `use_aocd` defaults to `True`, and the results for parts without a
  known answer are submitted to adventofcode.com automatically (pass `use_aocd=False` to prevent
  this).
