import sys

if sys.version_info >= (3, 11):
  from enum import StrEnum
  from typing import Self
else:
  from strenum import StrEnum
  from typing_extensions import Self


class MapCenterType(StrEnum):
  """Map Chart center type"""

  FIXED = 'FIXED'
  CONTAIN = 'CONTAIN'

  def __str__(self: Self) -> str:
    """Readable property"""
    return self.name

  def __repr__(self: Self) -> str:
    """Readable property"""
    return f'MapCenterType.{self.name}'
