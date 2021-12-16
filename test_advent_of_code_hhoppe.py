import advent_of_code_hhoppe

PROFILE = 'google.Hugues_Hoppe.965276'
INPUT_URL = f'https://github.com/hhoppe/advent_of_code_{{year}}/raw/main/data/{PROFILE}/{{year}}_{{day:02d}}_input.txt'
ANSWER_URL = f'https://github.com/hhoppe/advent_of_code_{{year}}/raw/main/data/{PROFILE}/{{year}}_{{day:02d}}{{part_letter}}_answer.txt'

def test_creation() -> None:
  advent = advent_of_code_hhoppe.Advent(year=2020, input_url=INPUT_URL, answer_url=ANSWER_URL)
  puzzle = advent.puzzle(day=1)
  assert len(puzzle.input) > 100
  puzzle.verify(1, lambda x: 651651)
  puzzle.verify(2, lambda x: 214486272)
