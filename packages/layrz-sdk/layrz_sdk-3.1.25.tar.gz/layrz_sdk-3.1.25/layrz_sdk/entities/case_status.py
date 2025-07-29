import sys

if sys.version_info >= (3, 11):
  from enum import StrEnum
  from typing import Self
else:
  from typing_extensions import Self

  from layrz_sdk.backwards import StrEnum


class CaseStatus(StrEnum):
  """Case status enum"""

  PENDING = 'PENDING'
  FOLLOWED = 'FOLLOWED'
  CLOSED = 'CLOSED'

  def __str__(self: Self) -> str:
    """Readable property"""
    return self.name

  def __repr__(self: Self) -> str:
    """Readable property"""
    return f'CaseStatus.{self.name}'
