#!/usr/bin/env python3
"""Library for Advent of Code -- Hugues Hoppe."""

from __future__ import annotations

__docformat__ = 'google'
__version__ = '0.8.3'
__version_info__ = tuple(int(num) for num in __version__.split('.'))

from collections.abc import Callable
import contextlib
import dataclasses
import numbers
import pathlib
import re
import sys
import time
from typing import Any
import unittest.mock
import urllib.error
import urllib.request

import IPython
import IPython.display


def _read_contents(path_or_url: str, /) -> bytes:
  if path_or_url.startswith(('http://', 'https://')):
    with urllib.request.urlopen(path_or_url) as response:
      data: bytes = response.read()
    return data
  with open(path_or_url, 'rb') as f:
    return f.read()


@dataclasses.dataclass
class PuzzlePart:
  """Part (1 or 2) of a daily puzzle."""

  advent: Advent = dataclasses.field(repr=False)
  day: int
  part: int
  answer: str | None = None
  func: Callable[[str], str | int] | None = None
  elapsed_time: float = -0.0  # Negative zero to show that it never ran.

  def _aocd_submit(self, result: str) -> str | None:
    """Submit a result to adventofcode.com and return the answer."""
    import aocd  # pylint: disable=import-error, import-outside-toplevel

    puz = aocd.models.Puzzle(year=self.advent.year, day=self.day)
    if self.part == 1:
      puz.answer_a = result  # Submit.
      if puz.answered_a:
        return puz.answer_a
    elif self.part == 2:
      puz.answer_b = result
      if puz.answered_b:
        return puz.answer_b
    else:
      raise AssertionError()
    return None

  def compute(self, input_: str, /, *, silent: bool = False, repeat: int = 1) -> None:
    """Run the stored function on the selected input."""
    assert self.func
    elapsed_times = []
    for _ in range(repeat):
      with contextlib.ExitStack() as stack:
        if silent:
          for f in ('sys.stdout', 'sys.stderr', 'IPython.display.display'):
            stack.enter_context(unittest.mock.patch(f))
        start_time = time.monotonic()
        raw_result = self.func(input_)
        if not isinstance(raw_result, (str, numbers.Integral)):
          raise ValueError(f'Result {raw_result!r} is not type `str` or `int`.')
        result = str(raw_result)
        elapsed_times.append(time.monotonic() - start_time)
      if self.answer is not None:
        if result != self.answer:
          raise ValueError(f'Result {result!r} != expected {self.answer!r}')
      else:
        print(f'Obtained result {result!r}.')
        if self.advent.use_aocd:
          self.answer = self._aocd_submit(result)
        else:
          self.answer = result
    self.elapsed_time = min(elapsed_times)
    if not silent:
      print(f'(Part {self.part}: {self.elapsed_time:#5.3f} s)', flush=True)


@dataclasses.dataclass
class Puzzle:
  """Daily puzzle consisting of an input and two problems to solve."""

  advent: Advent = dataclasses.field(repr=False)
  day: int
  input: str = ''
  parts: dict[int, PuzzlePart] = dataclasses.field(default_factory=dict)  # 1..2

  def __post_init__(self) -> None:
    self.advent.puzzles[self.day] = self
    if not self.input and self.advent.input_url:
      url = self.advent.input_url.format(year=self.advent.year, day=self.day)
      with contextlib.suppress(urllib.error.HTTPError, FileNotFoundError):
        self.input = _read_contents(url).decode()
    if not self.input and self.advent.use_aocd:
      import aocd  # pylint: disable=import-error, import-outside-toplevel

      puz = aocd.models.Puzzle(year=self.advent.year, day=self.day)
      self.input = puz.input_data
    if not self.input:
      raise ValueError('The puzzle input cannot be determined.')
    for part in (1, 2):
      puzzle_part = self.parts[part] = PuzzlePart(self.advent, self.day, part)
      if self.advent.answer_url:
        url = self.advent.answer_url.format(
            year=self.advent.year, day=self.day, part=part, part_letter='ab'[part - 1]
        )
        with contextlib.suppress(urllib.error.HTTPError, FileNotFoundError):
          puzzle_part.answer = _read_contents(url).decode()
      if puzzle_part.answer is None and self.advent.use_aocd:
        import aocd  # pylint: disable=import-error, import-outside-toplevel

        puz = aocd.models.Puzzle(year=self.advent.year, day=self.day)
        if part == 1 and puz.answered_a:
          puzzle_part.answer = puz.answer_a
        if part == 2 and puz.answered_b:
          puzzle_part.answer = puz.answer_b
    if IPython.get_ipython():  # type: ignore
      self.print_summary()

  def print_summary(self) -> None:
    """Shows the puzzle input (possibly abbreviated) and any stored answers."""

    def display_markdown(text: str) -> None:
      IPython.display.display(IPython.display.Markdown(text))  # type: ignore

    lines = [
        (line[:80] + ' ... ' + line[-35:] if len(line) > 120 else line)
        for line in self.input.splitlines()
    ]
    url = f'https://adventofcode.com/{self.advent.year}/day/{self.day}'
    s = f'For [day {self.day}]({url}), `puzzle.input` has '
    if len(lines) != 1:
      s += f'{len(lines):_} lines:'
    else:
      line = self.input.rstrip('\n')
      s += f'a single line of {len(line):_} characters:'
    display_markdown(s)
    lines2 = lines[:8] + [' ...'] + lines[-4:] if len(lines) > 13 else lines
    print('\n'.join(lines2))
    answers = {part: self.parts[part].answer for part in (1, 2)}
    display_markdown(f'The stored answers are: `{answers}`')

  def verify(self, part: int, func: Callable[[str], str | int], /, *, repeat: int = 1) -> None:
    """Runs `func` on the puzzle input and check the answer for the part."""
    func2: Any = getattr(func, 'func', func)  # For `functools.partial`.
    func_name: str | None = getattr(func2, '__name__', None)
    if func_name:
      if match := re.match(r'day(\d+)', func_name):
        func_day = int(match.group(1))
        if func_day != self.day:
          raise ValueError(f'Function {func_name} looks incompatible for day {self.day}.')
    puzzle_part = self.parts[part]
    puzzle_part.func = func
    puzzle_part.compute(self.input, repeat=repeat)


@dataclasses.dataclass
class Advent:
  """Annual advent-of-code consisting of 25 daily puzzles."""

  year: int
  input_url: str = ''
  answer_url: str = ''
  puzzles: dict[int, Puzzle] = dataclasses.field(default_factory=dict)  # [day]

  def __post_init__(self) -> None:
    self.use_aocd = (
        'aocd' in sys.modules and pathlib.Path('~/.config/aocd/token').expanduser().exists()
    )

  def puzzle(self, *args: Any, **kwargs: Any) -> Puzzle:
    """Obtain a daily puzzle."""
    return Puzzle(self, *args, **kwargs)

  def show_times(self, *, recompute: bool = False, repeat: int = 1) -> None:
    """Prints the execution times of all puzzle parts."""
    if recompute and repeat > 1:
      print(f'(Computing min times over {repeat} calls.)')
    total = 0.0
    for day, puzzle in sorted(self.puzzles.items()):
      s = f'day_{day:<2}'
      for part in (1, 2):
        s += f'   part_{part}:'
        puzzle_part = puzzle.parts.get(part)
        if not puzzle_part:
          s += '  n/a '
          continue
        if recompute and puzzle_part.func:
          puzzle_part.compute(puzzle.input, silent=True, repeat=repeat)
        s += f'{puzzle_part.elapsed_time:#6.3f}'
        total += puzzle_part.elapsed_time
      print(s)
    print(f'Total time:{total:#7.3f} s')


# Local Variables:
# fill-column: 100
# End:
