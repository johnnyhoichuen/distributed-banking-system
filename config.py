from enum import Enum, EnumMeta

read_topic = "read-only"
transaction_topic = "transaction"

mongoUrl = "mongodb://localhost:27017"

# API type
class APIType(Enum):
    ACC_INFO = b"acc_info"
    TRAN_HISTORY = b'tran_history'
    NEW_ACC = b'new_acc'
    ADD_FUND = b'add_fund'
    WITHDRAW_FUND = b'withdraw_fund'
    ERROR = b'error'

# examples of possible errors
ERROR_CODES = {
    '100': "Invalid currency",
    '101': "Invalid amount",
    '102': "Invalid user detail",
}

# support classes
class MetaEnum(EnumMeta):
    def __contains__(cls, item):
        try:
            cls(item)
        except ValueError:
            return False
        return True

# support classes
class BaseEnum(Enum, metaclass=MetaEnum):
    pass

# a set of acceptable currencies
class Currency(BaseEnum):
    BTC = "BTC"
    ETH = "ETH"
    USDT = "USDT"

