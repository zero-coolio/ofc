from enum import Enum

class TxType(str, Enum):
    credit = "credit"
    debit = "debit"
