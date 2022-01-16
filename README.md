# Module `advent_of_code_hhoppe`

Python library to process Advent-of-Code puzzles in a Jupyter notebook.
See [a complete example](https://colab.research.google.com/github/hhoppe/advent_of_code_2021/blob/main/advent_of_code_2021.ipynb).

Usage summary:

- The **preamble** optionally specifies reference inputs and answers for the puzzles:
  ```
    BASE_URL = 'https://github.com/hhoppe/advent_of_code_2021/blob/main/data/google.Hugues_Hoppe.965276/'
    INPUT_URL = BASE_URL + '2021_{day:02}_input.txt'
    ANSWER_URL = BASE_URL + '2021_{day:02}{part_letter}_answer.txt'
    advent = advent_of_code_hhoppe.Advent(
        year=2021, input_url=INPUT_URL, answer_url=ANSWER_URL)
  ```


- For **each day** (numbered 1..25), the first notebook cell defines a `puzzle` object:

  ```
    puzzle = advent.puzzle(day=1)
  ```
  The puzzle input string is automatically read into the attribute `puzzle.input`.
  This input string is unique to each Advent participant.

  For each of the two puzzle parts, a function (e.g. `process1`) takes an input string and returns a string or integer answer.
  Using calls like the following, we time the execution of each function and verify the answers:
  ```
    puzzle.verify(part=1, func=process1)
    puzzle.verify(part=2, func=process2)
  ```

- At the end of the notebook, a table summarizes **timing** results.

## Alternative ways to specify puzzle inputs/answers

- The puzzle inputs and answers can be more efficiently downloaded using a single ZIP file:
  ```
    PROFILE = 'google.Hugues_Hoppe.965276'
    ZIP_URL = f'https://github.com/hhoppe/advent_of_code_2021/raw/main/data/{PROFILE}.zip'
    !if [[ ! -d {PROFILE} ]]; then wget -q {ZIP_URL} && unzip -q {PROFILE}; fi
    INPUT_URL = f'{PROFILE}/{{year}}_{{day:02d}}_input.txt'
    ANSWER_URL = f'{PROFILE}/{{year}}_{{day:02d}}{{part_letter}}_answer.txt'
    advent = advent_of_code_hhoppe.Advent(
        year=2021, input_url=INPUT_URL, answer_url=ANSWER_URL)
  ```

- The puzzle inputs and answers can be obtained  directly from adventofcode.com using a web-browser session cookie and the `advent-of-code-data` PyPI package:

  ```
    !pip install -q advent-of-code-data
    import aocd
    # Fill-in the session cookie in the following:
    mkdir -p ~/.config/aocd && echo 53616... >~/.config/aocd/token
    advent = advent_of_code_hhoppe.Advent(year=2021)
  ```
