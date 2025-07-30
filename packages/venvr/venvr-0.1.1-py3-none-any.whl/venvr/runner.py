from .util import Basic

class Runner(Basic):
	def __init__(self, name, path):
		self.name = name
		self.path = path

	def run(self, func, *args, **kwargs):
		rp = self.path.run[func]
		self.log("run", rp, *args, **kwargs)
		return self.out("%s %s %s"%(self.path.py, rp,
			" ".join(['"%s"'%(a,) for a in args])))