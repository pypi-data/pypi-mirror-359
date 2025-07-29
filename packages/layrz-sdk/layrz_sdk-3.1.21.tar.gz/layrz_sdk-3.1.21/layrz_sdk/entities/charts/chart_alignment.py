"""Chart alignment"""

import sys

if sys.version_info >= (3, 11):
  from enum import StrEnum
  from typing import Self
else:
  from strenum import StrEnum
  from typing_extensions import Self


class ChartAlignment(StrEnum):
  """
  Chart Alignment
  """

  CENTER = 'center'
  LEFT = 'left'
  RIGHT = 'right'

  def __str__(self: Self) -> str:
    """Readable property"""
    return self.name

  def __repr__(self: Self) -> str:
    """Readable property"""
    return f'ChartAlignment.{self.name}'
