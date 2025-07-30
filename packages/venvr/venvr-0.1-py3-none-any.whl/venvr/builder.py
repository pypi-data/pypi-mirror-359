import os, inspect
from .util import Basic, RTMP

class Builder(Basic):
	def __init__(self, name, path, deps=[]):
		self.name = name
		self.path = path
		self.dependencies = deps

	def build(self):
		self.log("build")
		self.dir()
		self.env()
		self.deps()

	def dir(self):
		self.log("dir", self.path.base)
		os.makedirs(self.path.base)

	def env(self):
		vp = self.path.venv
		self.log("env", vp)
		self.out("python3 -m venv %s"%(vp,))

	def deps(self):
		self.log("deps", *self.dependencies)
		for dep in self.dependencies:
			self.out("%s install %s"%(self.path.pip, dep))

	def register(self, func):
		fsrc = inspect.getsource(func)
		name = fsrc.split(" ", 1).pop(1).split("(", 1).pop(0)
		rp = self.based("%s.py"%(name,))
		self.path.run.update(name, rp)
		self.log("register", name, rp)
		with open(rp, "w") as f:
			f.write(RTMP%(fsrc, name))
		return name