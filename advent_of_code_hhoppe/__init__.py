#!/usr/bin/env python3
"""Library for Advent of Code -- Hugues Hoppe."""

from __future__ import annotations

__docformat__ = 'google'
__version__ = '1.0.5'
__version_info__ = tuple(int(num) for num in __version__.split('.'))

from collections.abc import Callable
import contextlib
import dataclasses
import io
import numbers
import pathlib
import re
import tarfile
import time
from typing import Any
import unittest.mock
import urllib.error
import urllib.request

import aocd  # https://github.com/wimglenn/advent-of-code-data
import IPython
import IPython.display


def _read_contents(path_or_url: str, /) -> bytes:
  if path_or_url.startswith(('http://', 'https://')):
    with urllib.request.urlopen(path_or_url) as response:
      data: bytes = response.read()
    return data
  return pathlib.Path(path_or_url).read_bytes()


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
    # Could set: quiet=True.
    aocd.submit(result, year=self.advent.year, day=self.day, part=self.part, reopen=False)
    puz = aocd.models.Puzzle(year=self.advent.year, day=self.day)
    if self.part == 1:
      if puz.answered_a:
        answer: str = puz.answer_a
        return answer
    elif self.part == 2:
      if puz.answered_b:
        answer = puz.answer_b
        return answer
    else:
      raise ValueError(self.part)
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
      puz = aocd.models.Puzzle(year=self.advent.year, day=self.day)
      self.input = puz.input_data
      if not self.input.endswith('\n'):
        self.input += '\n'
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
  tar_url: str = ''
  input_url: str = ''
  answer_url: str = ''
  puzzles: dict[int, Puzzle] = dataclasses.field(default_factory=dict)  # [day]
  use_aocd: bool = False

  def __post_init__(self) -> None:
    if self.tar_url:
      assert not self.input_url and not self.answer_url
      data_dir = pathlib.Path('./data')
      if not data_dir.is_dir():
        data_dir.mkdir()
      if match := re.search(r'([^/]+)\.tar\.gz$', self.tar_url):
        data_name = match.group(1)
      else:
        raise ValueError(f'{self.tar_url=} must have suffix .tar.gz')
      if not (data_dir / data_name).is_dir():
        with tarfile.open(fileobj=io.BytesIO(_read_contents(self.tar_url)), mode='r:gz') as tf:
          tf.extractall(path=data_dir)  # Python 3.11.4: use filter='data' for security.
      self.input_url = f'{data_dir}/{data_name}/{{year}}_{{day:02d}}_input.txt'
      self.answer_url = f'{data_dir}/{data_name}/{{year}}_{{day:02d}}{{part_letter}}_answer.txt'

    self.use_aocd = pathlib.Path('~/.config/aocd/token').expanduser().exists()

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
