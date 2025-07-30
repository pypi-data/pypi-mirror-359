from fyg.util import Loggy
from .agent import Agent

class Manager(Loggy):
	def __init__(self, vstore):
		self.vstore = vstore
		self.venvrs = {} # detect?

	def subsig(self):
		return self.vstore

	def agent(self, name, deps=[]):
		if name not in self.venvrs:
			self.venvrs[name] = Agent(name, self.vstore, deps)
		return self.venvrs[name]