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
   