from .manager import Manager

vstore = "venvrs"
manny = None

def setvstore(vs):
	global vstore
	vstore = vs
	print("set vstore to", vs)

def getman():
	global manny
	if not manny:
		manny = Manager(vstore)
	return manny

def getagent(name, deps=[]):
	return getman().agent(name, deps)

def run(envname, deps, func, *args, **kwargs):
	agent = getagent(envname, deps)
	return agent.run(agent.register(func), *args, **kwargs)