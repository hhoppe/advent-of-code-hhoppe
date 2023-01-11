#!/usr/bin/env python3
# -*- fill-column: 100; -*-
"""Tests for advent_of_code_hhoppe module."""

import advent_of_code_hhoppe

BASE_URL = 'https://github.com/hhoppe/advent-of-code-hhoppe/raw/main/testdata'
INPUT_URL = f'{BASE_URL}/{{year}}_{{day:02d}}_input.txt'
ANSWER_URL = f'{BASE_URL}/{{year}}_{{day:02d}}{{part_letter}}_answer.txt'


def test_creation() -> None:
  """Test creation of Advent object."""
  advent = advent_of_code_hhoppe.Advent(year=2017, input_url=INPUT_URL, answer_url=ANSWER_URL)
  puzzle = advent.puzzle(day=1)
  assert len(puzzle.input) == 2119
  puzzle.verify(1, lambda s: 1044)
  puzzle.verify(2, lambda s: 1054)
