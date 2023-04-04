from dataclasses import dataclass

# account holder
# transaction

# account

@dataclass
class Address():
	line_1: str
	line_2: str
	city: str
	state: str
	zip_code: str
	country: str

@dataclass
class AccountHolder():
	name: str
	email: str
	phone_number: str
	address: Address

@dataclass(frozen=True)
class Transaction():
	transaction_id: str
	transaction_type: str
	description: str
	amount: int
	timestamp: str

# for adding funds
@dataclass
class Credit():
	amount: int
	currency: str
	description: str = "Deposit"

# for withdrawing
@dataclass
class Debit():
	amount: int
	currency: str
	description: str = "Withdrawal"