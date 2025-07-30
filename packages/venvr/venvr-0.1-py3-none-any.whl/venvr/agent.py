from os.path import isdir, join as pjoin
from fyg import Config
from fyg.util import Named
from .runner import Runner
from .builder import Builder

class Agent(Named):
	def __init__(self, name, vstore, deps=[]):
		self.name = name
		self.vstore = vstore
		self.deps = deps
		self.setup()

	def run(self, funcname, *args, **kwargs):
		self.log("run", funcname, args, kwargs)
		return self.runner.run(funcname, *args, **kwargs)

	def register(self, func):
		name = self.builder.register(func)
		self.log("register", name)
		return name

	def setup(self):
		self.log("setup")
		self.setpaths()
		self.runner = Runner(self.name, self.path)
		self.builder = Builder(self.name, self.path, self.deps)
		isdir(self.path.base) or self.builder.build()

	def setpaths(self):
		base = pjoin(self.vstore, self.name)
		self.log("setpaths", base)
		venv = pjoin(base, "venv")
		binp = pjoin(venv, "bin")
		self.path = Config({
			"base": base,
			"venv": venv,
			"pip": pjoin(binp, "pip"),
			"py": pjoin(binp, "python"),
			"run": {}
		})