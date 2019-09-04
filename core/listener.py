import glob
import os
import sys
import importlib
from core.helpers import help_option
from core.autocomplete import complete
from core.stagers.marvin import Marvin
class Listeners:
	array = ["list", "run", "generate","back", "help", "info"]

	def __init__(self):
		self.modules = []
		self.modules_folder = "./listeners"
		self.o_modules = []
		self.c_modules = 0

	def function(self,modules_count):
		print("\033[H\033[J") # Clear the screen
		print("\033[01;31m")
		print("Vortus")
		print("\033[00m")
		sys.stdout.write("\t  .:[ Listeners {}]:.\n\033[00m".format(modules_count))

	def shell(self):
		self.modules_get_list()
		self.function(len(self.o_modules))
		print()
		while True:
			try:
				complete(self.array)
				an = input("listeners >>> ") or "help"
				prompt = an.split()
				if not prompt:
					continue
				elif prompt[0] == "list":
					print("-----------\n"
                      "| listeners |\n"
                      "-----------"
                      "-----------------------------------\n"
                     "\t| ID  | Name | Version | Information |")
					for mod in self.o_modules:
						try:
							self.c_modules += 1
							m = importlib.import_module("listeners.%s" %(mod))
						except ImportError:
							print("\t>> %s - [ERROR ON LOAD]" %(mod))
						else:
							sys.stdout.write("\t")
							_ = len(m.MODULE_DE) + len(m.MODULE_VERSION) +30
							print("-" * _)
							print("\t| %d]. %s (%s) - %s\t|" %(self.c_modules, mod, m.MODULE_VERSION, m.MODULE_DE))
					sys.stdout.write("\t")
					print("-" * _)
				elif prompt[0] == "generate":
					a = Marvin()
					a.generate()
				elif prompt[0] == "help":
					help_option()
				elif prompt[0] == "back":
					break
			except Exception as e:
				raise e
	
	def modules_get_list(self):
		home = os.getcwd()
		os.chdir(self.modules_folder)
		self.modules = glob.glob("*.py")
		if not self.modules:
			print("No modules found.")
		else:
			os.chdir(home)
			for module in self.modules:
				module = module.split(".")[0]
				if module == "__init__":
					continue
				self.o_modules.append(module)