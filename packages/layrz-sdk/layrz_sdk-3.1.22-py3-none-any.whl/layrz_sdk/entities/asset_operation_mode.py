"""Asset Operation Mode"""

import sys

if sys.version_info >= (3, 11):
  from enum import StrEnum
  from typing import Self
else:
  from strenum import StrEnum
  from typing_extensions import Self


class AssetOperationMode(StrEnum):
  """
  Asset Operation mode definition
  It's an enum of the operation mode of the asset.
  """

  SINGLE = 'SINGLE'
  MULTIPLE = 'MULTIPLE'
  ASSETMULTIPLE = 'ASSETMULTIPLE'
  DISCONNECTED = 'DISCONNECTED'
  STATIC = 'STATIC'
  ZONE = 'ZONE'

  def __str__(self: Self) -> str:
    """Readable property"""
    return self.name

  def __repr__(self: Self) -> str:
    """Readable property"""
    return f'AssetOperationMode.{self.name}'
