import os
import configparser

# get local_settings
__location__ = os.path.dirname(os.path.abspath(__file__))
configPath = os.path.join(__location__, "local_settings.cfg")
if not os.path.isfile(configPath):
	print ("ERROR: Could not find local_settings.cfg")
config = configparser.ConfigParser()
config.read(configPath)

delete_path = config.get('uploadTool', 'delete_path')

for file in os.listdir(delete_path):
	filePath = os.path.join(delete_path, file)
	os.remove(filePath)