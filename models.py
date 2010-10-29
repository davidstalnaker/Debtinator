from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import re
import random
import string
import hashlib



def parseMoney(amount):
	if type(amount) == int or type(amount) == float:
		return int(amount * 100)
	else:
		pattern = re.compile('[^\d\.]+')
		return int(float(pattern.sub('', amount)) * 100)
		
def printMoney(intAmount):
	return '$%d.%.2d' % (intAmount / 100, intAmount % 100)
	
def addDebt(owee, ower, amount, db_session):
	print("adding debt")
	# If the owee already is owed money, just add to the debt
	debt = Debt.query.filter(Debt.owee == owee).filter(Debt.ower == ower).first()
	if debt:
		print("  adding to existing")
		print("  debt is %s" % debt)
		debt.amount += parseMoney(amount)
	else:
		# If the owee is already in debt, subtract from it and reverse if necessary
		debt = Debt.query.filter(Debt.owee == ower).filter(Debt.ower == owee).first()
		if debt:
			print("  subtracting from existing")
			print("  debt is %s" % debt)
			debt.amount -= parseMoney(amount)
			if(debt.amount < 0):
				debt.amount = -1 * debt.amount
				debt.owee = owee
				debt.ower = ower
		else:
			print("  creating new")
			#if no debt exists between these users, make one
			debt = Debt(amount, ower, owee)
			db_session.add(debt)
	print("  debt now %d" % debt.amount)
	return debt


bill_participants = Table('bill_participants', Base.metadata,
	Column('user_id', Integer, ForeignKey('users.id')),
	Column('bill_id', Integer, ForeignKey('bills.id'))
)

class User(Base):
	__tablename__ = 'users'
	id = Column(Integer, primary_key=True)
	name = Column(String)
	salt = Column(String)
	password = Column(String)
	
	def __init__(self, name, password):
		self.name = name
		self.salt = self.generateSalt(8)
		self.password = self.hashPassword(password)
	
	def __repr__(self):
		return "<User('%s','%s')>" % (self.name, self.password)

	def validate(self):
		errors = [];
		if self.name == None or self.name == "":
			errors.append("Invalid username")
		if self.password == None or self.password == "" or self.password == self.hashPassword(""):
			errors.append("Invalid password")
		if User.query.filter(User.name == self.name).count() != 0:
			errors.append("Username unavailable")
		return (len(errors) == 0, errors)
		
	def hashPassword(self, password):
		return hashlib.sha1(password + self.salt).hexdigest()
		
	def testPassword(self, testPass):
		return self.hashPassword(testPass) == self.password
		
	def generateSalt(self, length = 8):
		chars = string.letters + string.digits
		return ''.join([random.choice(chars) for i in range(length)])
		
class Bill(Base):
	__tablename__ = 'bills'
	id = Column(Integer, primary_key = True)
	amount = Column(Integer)
	participants = relationship('User', secondary=bill_participants, backref='bills')
	payer_id = Column(Integer, ForeignKey('users.id'))
	payer = relationship('User', backref='paidBills')
	
	def __init__(self, amount, participants, payer):
		self.amount = parseMoney(amount)
		self.participants = participants
		self.payer = payer
		
	def __repr__(self):
		return "Bill for %s with participants: %s and paid by %s" % \
		(printMoney(self.amount), ", ".join(map(lambda p: p.name, self.participants)), self.payer.name)

class Debt(Base):
	__tablename__ = 'debts'
	id = Column(Integer, primary_key = True)
	amount = Column(Integer)
	ower_id = Column(Integer, ForeignKey('users.id'))
	ower = relationship('User', backref='debtsTo', primaryjoin='debts.c.ower_id == User.id')
	owee_id = Column(Integer, ForeignKey('users.id'))
	owee = relationship('User', backref='debtsFrom', primaryjoin='debts.c.owee_id == User.id')
	
	def __init__(self, amount, ower, owee):
		self.amount = parseMoney(amount)
		self.ower = ower
		self.owee = owee
		
	def __repr__(self):
		return "%s owes %s %s" % \
		(self.ower.name, self.owee.name, printMoney(self.amount))
   