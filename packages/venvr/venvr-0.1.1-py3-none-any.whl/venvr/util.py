import os
from fyg.util import Named
from subprocess import getoutput

RTMP = """from optparse import OptionParser
parser = OptionParser("run.py [arg1] [arg2] ...")
args = parser.parse_args()[1]

%s
%s(*args)
"""

class Basic(Named):
	def out(self, cmd):
		self.log("out", cmd)
		out = getoutput(cmd)
		self.log(out)
		return out

	def based(self, fname):
		return os.path.join(self.path.base, fname)