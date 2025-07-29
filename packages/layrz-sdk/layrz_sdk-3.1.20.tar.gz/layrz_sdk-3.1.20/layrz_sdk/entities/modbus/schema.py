import sys

if sys.version_info >= (3, 11):
  from enum import StrEnum
else:
  from strenum import StrEnum


class ModbusSchema(StrEnum):
  """Modbus schema enumeration"""

  SINGLE = 'SINGLE'
  """ Defines a single Modbus request. """
  MULTIPLE = 'MULTIPLE'
  """ Defines multiple Modbus requests. """
