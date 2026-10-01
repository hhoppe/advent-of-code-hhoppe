#!/usr/bin/env python3
# -*- fill-column: 100; -*-
"""Tests for advent_of_code_hhoppe module."""

import functools
import io
import pathlib
import tarfile
import unittest.mock
from typing import Any

import pytest

import advent_of_code_hhoppe

BASE_URL = 'https://github.com/hhoppe/advent-of-code-hhoppe/raw/main/testdata'
INPUT_URL = f'{BASE_URL}/{{year}}_{{day:02d}}_input.txt'
ANSWER_URL = f'{BASE_URL}/{{year}}_{{day:02d}}{{part_letter}}_answer.txt'
TESTDATA = pathlib.Path(__file__).parent / 'testdata'
LOCAL_INPUT_URL = f'{TESTDATA.as_posix()}/{{year}}_{{day:02d}}_input.txt'
LOCAL_ANSWER_URL = f'{TESTDATA.as_posix()}/{{year}}_{{day:02d}}{{part_letter}}_answer.txt'


def test_creation() -> None:
  """Test creation of Advent object."""
  advent = advent_of_code_hhoppe.Advent(
      year=2017, input_url=INPUT_URL, answer_url=ANSWER_URL, use_aocd=False
  )
  puzzle = advent.puzzle(day=1)
  assert len(puzzle.input) == 2119
  puzzle.verify(1, lambda s: 1044)
  puzzle.verify(2, lambda s: 1054)


def _make_advent(**kwargs: Any) -> advent_of_code_hhoppe.Advent:
  return advent_of_code_hhoppe.Advent(year=2017, use_aocd=False, **kwargs)


def test_creation_from_local_files() -> None:
  """Test reading the puzzle input and the answers from local files."""
  advent = _make_advent(input_url=LOCAL_INPUT_URL, answer_url=LOCAL_ANSWER_URL)
  puzzle = advent.puzzle(day=1)
  assert advent.puzzles == {1: puzzle}
  assert puzzle.input.rstrip('\r\n') == (TESTDATA / '2017_01_input.txt').read_text().rstrip('\r\n')
  assert puzzle.parts[1].answer == '1044'
  assert puzzle.parts[2].answer == '1054'


def test_missing_answer_files() -> None:
  """Test that a missing answer file leaves the answer unknown."""
  missing_url = f'{TESTDATA.as_posix()}/missing_{{part}}.txt'
  advent = _make_advent(input_url=LOCAL_INPUT_URL, answer_url=missing_url)
  puzzle = advent.puzzle(day=1)
  assert puzzle.parts[1].answer is None and puzzle.parts[2].answer is None


def test_missing_input() -> None:
  """Test that a puzzle without any input is an error."""
  advent = _make_advent(input_url=f'{TESTDATA.as_posix()}/missing.txt')
  with pytest.raises(ValueError, match='cannot be determined'):
    advent.puzzle(day=1)


def test_verify_correct_and_incorrect() -> None:
  """Test verify() with correct and incorrect results, of type `str` and `int`."""
  advent = _make_advent(input_url=LOCAL_INPUT_URL, answer_url=LOCAL_ANSWER_URL)
  puzzle = advent.puzzle(day=1)
  puzzle.verify(1, lambda s: 1044)
  puzzle.verify(2, lambda s: '1054')
  with pytest.raises(ValueError, match="Result '1045' != expected '1044'"):
    puzzle.verify(1, lambda s: 1045)
  with pytest.raises(ValueError, match='is not type'):
    puzzle.verify(1, lambda s: 1044.0)


def test_verify_records_unknown_answer(capsys: pytest.CaptureFixture[str]) -> None:
  """Test that without a stored answer, the first result becomes the answer."""
  puzzle = _make_advent().puzzle(day=1, input='1122\n')
  assert puzzle.parts[1].answer is None
  puzzle.verify(1, lambda s: 3)
  assert puzzle.parts[1].answer == '3'
  assert "Obtained result '3'." in capsys.readouterr().out
  with pytest.raises(ValueError):
    puzzle.verify(1, lambda s: 4)


def test_verify_function_day_check() -> None:
  """Test that a function named for another day is rejected, also through `functools.partial`."""
  puzzle = _make_advent().puzzle(day=1, input='1122\n')

  def day2(s: str, factor: int = 1) -> int:
    return len(s) * factor

  with pytest.raises(ValueError, match='looks incompatible'):
    puzzle.verify(1, day2)
  with pytest.raises(ValueError, match='looks incompatible'):
    puzzle.verify(1, functools.partial(day2, factor=2))

  def day1(s: str) -> int:
    return len(s)

  puzzle.verify(1, day1)


def test_timing_and_show_times(capsys: pytest.CaptureFixture[str]) -> None:
  """Test the timing of `repeat` calls and the summary table."""
  advent = _make_advent()
  puzzle = advent.puzzle(day=1, input='1122\n')
  assert puzzle.parts[1].elapsed_time == 0.0  # Negative zero, as it never ran.
  func = unittest.mock.Mock(return_value=3, __name__='day1')
  puzzle.verify(1, func, repeat=3)
  assert func.call_count == 3
  assert puzzle.parts[1].elapsed_time >= 0.0
  assert '(Part 1:' in capsys.readouterr().out
  advent.show_times(recompute=True, repeat=2)
  assert func.call_count == 5
  lines = capsys.readouterr().out.splitlines()
  assert lines[0] == '(Computing min times over 2 calls.)'
  assert lines[1].startswith('day_1    part_1:') and 'part_2:-0.000' in lines[1]
  assert lines[2].startswith('Total time:')


def test_compute_silent_suppresses_output(capsys: pytest.CaptureFixture[str]) -> None:
  """Test that `silent=True` hides the output of the function."""
  puzzle = _make_advent().puzzle(day=1, input='1122\n')
  puzzle.verify(1, lambda s: 3)
  capsys.readouterr()

  def noisy(unused_s: str) -> int:
    print('noisy')
    return 3

  puzzle.parts[1].func = noisy
  puzzle.parts[1].compute(puzzle.input, silent=True)
  assert capsys.readouterr().out == ''


def test_print_summary_outside_notebook(capsys: pytest.CaptureFixture[str]) -> None:
  """Test the summary of the input and answers, with the Markdown display mocked."""
  puzzle = _make_advent().puzzle(day=1, input=''.join(f'{i}\n' for i in range(20)))
  with unittest.mock.patch('IPython.display.display') as display:
    puzzle.print_summary()
  texts = [call.args[0].data for call in display.call_args_list]
  url = 'https://adventofcode.com/2017/day/1'
  assert texts[0] == f'For [day 1]({url}), `puzzle.input` has 20 lines:'
  assert texts[1] == 'The stored answers are: `{1: None, 2: None}`'
  assert capsys.readouterr().out == '0\n1\n2\n3\n4\n5\n6\n7\n ...\n16\n17\n18\n19\n'


def test_print_summary_single_long_line(capsys: pytest.CaptureFixture[str]) -> None:
  """Test the summary of an input consisting of a single long line."""
  puzzle = _make_advent().puzzle(day=1, input='x' * 200 + '\n')
  with unittest.mock.patch('IPython.display.display') as display:
    puzzle.print_summary()
  assert display.call_args_list[0].args[0].data.endswith('a single line of 200 characters:')
  assert capsys.readouterr().out == 'x' * 80 + ' ... ' + 'x' * 35 + '\n'


def test_tar_url(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
  """Test the extraction of inputs and answers from a local .tar.gz file into ./data."""
  buffer = io.BytesIO()
  with tarfile.open(fileobj=buffer, mode='w:gz') as tf:
    for name in ('2017_01_input.txt', '2017_01a_answer.txt', '2017_01b_answer.txt'):
      tf.add(TESTDATA / name, arcname=f'profile/{name}')
  (tmp_path / 'profile.tar.gz').write_bytes(buffer.getvalue())
  monkeypatch.chdir(tmp_path)
  advent = _make_advent(tar_url='profile.tar.gz')
  assert (tmp_path / 'data/profile/2017_01_input.txt').is_file()
  puzzle = advent.puzzle(day=1)
  puzzle.verify(1, lambda s: 1044)
  puzzle.verify(2, lambda s: 1054)
  with pytest.raises(ValueError, match='must have suffix'):
    _make_advent(tar_url='profile.zip')


def test_use_aocd_default(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
  """Test that `use_aocd` defaults to whether an aocd token file exists."""
  monkeypatch.setenv('HOME', str(tmp_path))
  monkeypatch.setenv('USERPROFILE', str(tmp_path))
  assert not advent_of_code_hhoppe.Advent(year=2017).use_aocd
  (tmp_path / '.config/aocd').mkdir(parents=True)
  (tmp_path / '.config/aocd/token').write_text('dummy', newline='\n')
  assert advent_of_code_hhoppe.Advent(year=2017).use_aocd


def test_aocd_submit_mocked() -> None:
  """Test the submission path with aocd mocked, so that nothing reaches adventofcode.com."""
  advent = _make_advent()
  puzzle = advent.puzzle(day=1, input='1122\n')
  advent.use_aocd = True
  fake_puzzle = unittest.mock.Mock(answered_a=True, answer_a='3')
  with (
      unittest.mock.patch('aocd.submit') as submit,
      unittest.mock.patch('aocd.models.Puzzle', return_value=fake_puzzle),
  ):
    puzzle.verify(1, lambda s: 3)
  submit.assert_called_once_with('3', year=2017, day=1, part='a', reopen=False)
  assert puzzle.parts[1].answer == '3'


def test_answer_file_with_trailing_newline(tmp_path: pathlib.Path) -> None:
  """Test that a trailing newline in an answer file is ignored."""
  (tmp_path / '2017_01a_answer.txt').write_text('3\n', newline='\n')
  answer_url = f'{tmp_path.as_posix()}/{{year}}_{{day:02d}}{{part_letter}}_answer.txt'
  advent = _make_advent(answer_url=answer_url)
  advent.puzzle(day=1, input='1122\n').verify(1, lambda s: 3)


def test_aocd_rejected_answer_raises() -> None:
  """Test that a result rejected by adventofcode.com is a loud failure (submitted only once)."""
  advent = _make_advent()
  puzzle = advent.puzzle(day=1, input='1122\n')
  advent.use_aocd = True
  fake_puzzle = unittest.mock.Mock(answered_a=False, spec=['answered_a'])
  with (
      unittest.mock.patch('aocd.submit') as submit,
      unittest.mock.patch('aocd.models.Puzzle', return_value=fake_puzzle),
      pytest.raises(ValueError, match='not accepted'),
  ):
    puzzle.verify(1, lambda s: 5, repeat=3)
  submit.assert_called_once()


def test_verify_rejects_bool_result_and_zero_repeat() -> None:
  """Test that a `bool` result (although an int subclass) and `repeat=0` are errors."""
  puzzle = _make_advent().puzzle(day=1, input='1122\n')
  with pytest.raises(ValueError, match='is not type'):
    puzzle.verify(1, lambda s: True)
  with pytest.raises(AssertionError):
    puzzle.verify(1, lambda s: 3, repeat=0)
