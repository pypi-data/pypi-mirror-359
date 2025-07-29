"""Chart Data type"""

import sys

if sys.version_info >= (3, 11):
  from enum import StrEnum
  from typing import Self
else:
  from strenum import StrEnum
  from typing_extensions import Self


class ChartDataType(StrEnum):
  """
  Chart Data Type
  """

  STRING = 'STRING'
  DATETIME = 'DATETIME'
  NUMBER = 'NUMBER'

  def __str__(self: Self) -> str:
    """Readable property"""
    return self.name

  def __repr__(self: Self) -> str:
    """Readable property"""
    return f'ChartDataType.{self.name}'
