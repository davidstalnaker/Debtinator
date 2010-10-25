from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import random
import string
import hashlib

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
	
	def __init__(self, amount, participants):
		self.amount = amount
		self.participants = participants
		
	def __repr__(self):
		return "Bill for $%s with participants: %s" % (self.amount, ", ".join(map(lambda p: p.name, self.participants)))
