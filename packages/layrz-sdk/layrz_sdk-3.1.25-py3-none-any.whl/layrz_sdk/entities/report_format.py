"""Report formats"""

import sys

if sys.version_info >= (3, 11):
  from enum import StrEnum
  from typing import Self
else:
  from typing_extensions import Self

  from layrz_sdk.backwards import StrEnum


class ReportFormat(StrEnum):
  """
  Report format definition.
  """

  MICROSOFT_EXCEL = 'MICROSOFT_EXCEL'
  JSON = 'JSON'
  PDF = 'PDF'

  def __str__(self: Self) -> str:
    """Readable property"""
    return self.name

  def __repr__(self: Self) -> str:
    """Readable property"""
    return f'ReportFormat.{self.value}'
