import string, re

class Money(object):
	amount = 0
	
	def __init__(self, amount = 0, centValue = False):
		if type(amount) == Money:
			self.amount = amount.amount
		else:
			if centValue:
				self.amount = amount
			else:
				self.amount = parseMoney(amount)
			
	def __add__(self, other):
		if type(other) == Money:
			return Money(self.amount + other.amount, centValue = True)
		else:
			return Money(self.amount + parseMoney(other), centValue = True)
		
	def __sub__(self, other):
		if type(other) == Money:
			return Money(self.amount - other.amount, centValue = True)
		else:
			return Money(self.amount - parseMoney(other), centValue = True)

	def __rsub__(self, other):
		
		if type(other) == Money:
			return Money(other.amount - self.amount, centValue = True)
		else:
			return Money(parseMoney(other) - self.amount, centValue = True)
		
	def __mul__(self, other):
		return Money(self.amount * other, centValue = True)
		
	def __floordiv__(self, other):
		return Money(self.amount // other, centValue = True)
		
	__div__ = __floordiv__
	__radd__ = __add__
	__rmul__ = __mul__
	
	def dollars(self):
		return self.amount / 100
		
	def cents(self):
		return self.amount % 100
		
	def floatValue(self):
		return float(self.amount) / 100
		
	def intValue(self):
	    return self.amount
		
	def __repr__(self):
		return '$%d.%.2d' % (self.dollars(), self.cents())

def parseMoney(amount):
	if type(amount) == int or type(amount) == float:
		return int(amount * 100)
	else:
		pattern = re.compile('[^\d\.]+')
		return int(float(pattern.sub('', amount)) * 100)