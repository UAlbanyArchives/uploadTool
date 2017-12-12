import os
import subprocess
import wx
import argparse
import shutil
import sys
import tempfile
import configparser
from archives_tools import aspace as AS
from subprocess import Popen, PIPE

parser = argparse.ArgumentParser()
parser.add_argument("Files", help="Files to upload")
parser.add_argument("-p", help="Open files to preview them before uploading.", action='store_true')
args = parser.parse_args()

# get local_settings
__location__ = os.path.dirname(os.path.abspath(__file__))
configPath = os.path.join(__location__, "local_settings.cfg")
if not os.path.isfile(configPath):
	print ("ERROR: Could not find local_settings.cfg")
config = configparser.ConfigParser()
config.read(configPath)

uploadDir = config.get('uploadTool', 'uploadDir')
delete_path = config.get('uploadTool', 'delete_path')
repo = config.get('uploadTool', 'repository')

app = wx.App(False)


def deleteFile(fileCount, files):
	def dupFiles(oldName, movePath, newName, count):
		#print ("trying " + newName)
		if not os.path.exists(os.path.join(movePath, os.path.basename(newName))):
			shutil.move(oldName, os.path.join(movePath, os.path.basename(newName)))
		else:
			rootName, fileExt = os.path.splitext(os.path.basename(oldName))
			nextName = os.path.join(os.path.dirname(oldName), rootName + " [" + str(count) + "]" + fileExt)
			dupFiles(oldName, movePath, nextName, count + 1)
		
	if fileCount == 1:
		deleteMsg = "Do you want to delete this file?"
	else:
		deleteMsg = "Do you want to delete these files?"
	askDelete = wx.MessageDialog(None, deleteMsg, 'UploadTool', wx.YES_NO | wx.YES_DEFAULT | wx.ICON_WARNING | wx.STAY_ON_TOP)
	if askDelete.ShowModal() == wx.ID_YES:
		if fileCount == 1:
			dupFiles(files, delete_path, files, 1)
		else:
			if isinstance(files, list):
				for file in files:
					dupFiles(file, delete_path, file, 1)
			else:
				for file in files.split(" "):
					dupFiles(file, delete_path, file, 1)
				
					
	else:
		sys.exit()

def saveAs(fileCount, files):
	if fileCount == 1:
		ext = os.path.splitext(files)[1].lower()
		if ext == ".pdf":
			wildcard = "PDF (*.pdf)|*.pdf"
		elif ext == ".png":
			wildcard = "PNG (*.png)|*.png"
		elif ext == ".tif" or  ext == ".tiff":
			wildcard = "TIFF (*.tif)|*.tif"
		elif ext == ".jpg" or  ext == ".jpeg":
			wildcard = "JPG (*.jpg)|*.jpeg"
		else:
			wildcard = "*.*"
		saveDlg = wx.FileDialog(None, message="Save File as ...", defaultDir="", defaultFile="", wildcard=wildcard, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
		if saveDlg.ShowModal() == wx.ID_OK:
			output_path = saveDlg.GetPath()
			print ("Saving " + files + " to " + output_path)
			shutil.move(files, output_path)
			if os.name == "nt":
				openDirCmd = "start " + os.path.dirname(output_path)
			else:
				openDirCmd = "open " + os.path.dirname(output_path)
			openDir = Popen(openDirCmd, shell=True, stdout=PIPE, stderr=PIPE)
			stdout, stderr = openDir.communicate()
		else:
			startOver = wx.MessageDialog(None, "Do you want to start over?", 'UploadTool', wx.YES_NO | wx.YES_DEFAULT | wx.ICON_INFORMATION | wx.STAY_ON_TOP)
			if startOver.ShowModal() == wx.ID_YES:
				#restart upload too to try again
				args.p = None
				args.Files = files
				uploadFiles(args)
			else:
				deleteFile(fileCount, files)
	else:
		folderDlg = wx.DirDialog(None, "Choose a directory:", style=wx.DD_DEFAULT_STYLE)
		if folderDlg.ShowModal() == wx.ID_OK:
			output_path = folderDlg.GetPath()
			if not os.path.isdir(output_path):
				os.makedirs(output_path)
			for file in files.split(" "):
				print ("Saving " + file + " to " + output_path)
				shutil.move(file, output_path)
				if os.name == "nt":
					openDirCmd = "explorer " + output_path
					openDir = Popen(openDirCmd, shell=True, stdout=PIPE, stderr=PIPE)
					stdout, stderr = openDir.communicate()
		else:
			startOver = wx.MessageDialog(None, "Do you want to start over?", 'UploadTool', wx.YES_NO | wx.YES_DEFAULT | wx.ICON_INFORMATION | wx.STAY_ON_TOP)
			if startOver.ShowModal() == wx.ID_YES:
				#restart upload too to try again
				args.p = None
				args.Files = files
				uploadFiles(args)
			else:
				deleteFile(fileCount, files)
						
def checkOCR(args, pdfCount, fileCount):
	if pdfCount == 1:
		ocrMsg = "Has this file been OCRed?"
	else:
		ocrMsg = "Have all the PDF files been OCRed?"
	askOcr = wx.MessageDialog(None, ocrMsg, 'UploadTool', wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING | wx.STAY_ON_TOP)
	if askOcr.ShowModal() == wx.ID_NO:
		if fileCount == 1:
			openFile = Popen(args.Files, shell=True, stdout=PIPE, stderr=PIPE)
			stdout, stderr = openFile.communicate()
			if len(stdout) > 0:
				print (stdout)
			if len(stderr) > 0:
				print (stderr)
		else:
			for openFile in args.Files:
				if openFile.lower().endswith(".pdf"):
					openFile = Popen(openFile, shell=True, stdout=PIPE, stderr=PIPE)
					stdout, stderr = openFile.communicate()
		checkOCR(args, pdfCount, fileCount)
	else:
		return


def uploadFiles(args):
						
	fileCount = 0
	fileCheck = True
	if isinstance(args.Files, list):
		for file in args.Files:
			#print (file)
			fileCount += 1
			if not os.path.isfile(file):
				fileCheck = False
	else:
		fileCount = 1
		if not os.path.isfile(args.Files):
			fileCheck = False

	if not fileCheck == True:
		failedNotice = wx.MessageDialog(None, 'ERROR: Not all the files listed are available.', 'Input Error', wx.OK | wx.ICON_ERROR | wx.STAY_ON_TOP)
		failedNotice.ShowModal()
	else:

		if args.p:
			if fileCount == 1:
				openFile = Popen(args.Files, shell=True, stdout=PIPE, stderr=PIPE)
				stdout, stderr = openFile.communicate()
				if len(stdout) > 0:
					print (stdout)
				if len(stderr) > 0:
					print (stderr)
			else:
				for openFile in args.Files:
					openCmd = ("open " + openFile)
					openFile = Popen(openCmd, shell=True, stdout=PIPE, stderr=PIPE)
					stdout, stderr = openFile.communicate()

		dlg = wx.TextEntryDialog(None, 'Enter the ArchivesSpace ID, or Cancel to Save As...', 'Upload Tool')

		if dlg.ShowModal() != wx.ID_OK:
			dlg.Destroy()
			saveAs(fileCount, args.Files)
		else:
			
			refID = dlg.GetValue().strip()
			print (refID)
			session = AS.getSession()
			if session is None:
				failedNotice = wx.MessageDialog(None, 'ERROR: Could not connect to ArchivesSpace.', 'Failed to Connect', wx.OK | wx.ICON_ERROR | wx.STAY_ON_TOP)
				failedNotice.ShowModal()
				saveAs(fileCount, args.Files)
			else:
				record = AS.getArchObjID(session, repo, refID)
													

				if record is None:
					failedNotice = wx.MessageDialog(None, 'ERROR: Could not find ArchivesSpace record that matches that ID', 'Bad ID', wx.OK | wx.ICON_ERROR | wx.STAY_ON_TOP)
					failedNotice.ShowModal()
					saveAs(fileCount, args.Files)
				else:
				
					if fileCount == 1:
						msg = "Is this file representative of the whole ArchivesSpace record?"
					else:
						msg = "Are these files representative of the whole ArchivesSpace record?"

					askType = wx.MessageDialog(None, msg, 'UploadTool', wx.YES_NO | wx.YES_DEFAULT | wx.ICON_INFORMATION | wx.STAY_ON_TOP)
					if askType.ShowModal() == wx.ID_YES:
						filename = "whole"
					else:
						filename = "part"
						
					#get collection
					collection = AS.getResource(session, repo, record.resource.ref.split("/")[-1])
					
					recordDir = os.path.join(uploadDir, collection.id_0, refID)
					if not os.path.isdir(recordDir):
						os.makedirs(recordDir)
					#beDir =  os.path.join(recordDir, ".bulk_extractor")
					beDir =  os.path.join(recordDir, ".bulk_extractor")
											
					msg = "Is this the correct ArchivesSpace record?"
					msg = msg + "\n\n" + record.display_string
					msg = msg + "\n 		--> part of " + collection.title

					confirmRecord = wx.MessageDialog(None, msg, 'UploadTool', wx.YES_NO | wx.YES_DEFAULT | wx.ICON_INFORMATION | wx.STAY_ON_TOP)
					if confirmRecord.ShowModal() == wx.ID_NO:
						#restart upload too to try again
						args.p = None
						uploadFiles(args)
						
					else:
					
						#look for pdfs
						pdfCount = 0
						if fileCount == 1:
							if args.Files.lower().endswith(".pdf"):
								pdfCount = 1
						else:
							for pdfCheck in args.Files:
								if pdfCheck.lower().endswith(".pdf"):
									pdfCount += 1
								
						if pdfCount > 0:
							checkOCR(args, pdfCount, fileCount)					
							
							
						if fileCount == 1:
							print ("moving " +  args.Files +  " to " + recordDir)
							fileExt = os.path.splitext(args.Files)[1]
							shutil.move(args.Files, recordDir)
							os.rename(os.path.join(recordDir, os.path.basename(args.Files)), os.path.join(recordDir, filename + fileExt))
						else:
							fileNumber = 0
							for item in args.Files:
								print ("moving " +  item +  " to " + recordDir)
								fileNumber += 1
								fileExt = os.path.splitext(item)[1]
								shutil.move(item, recordDir)
								os.rename(os.path.join(recordDir, os.path.basename(item)), os.path.join(recordDir, filename + "-" + str(fileNumber) + fileExt))
								
						#run bulk_extractor
						print ("running bulk_extractor.exe")
						if not os.path.isdir(beDir):
							os.makedirs(beDir)
						beTemp = tempfile.mkdtemp()
						beCmd = ["bulk_extractor", "-o", beTemp, "-R", recordDir]
						#print (" ".join(beCmd))
						convert = Popen(beCmd, shell=True, stdout=PIPE, stderr=PIPE)
						stdout, stderr = convert.communicate()
						if len(stdout) > 0:
							print (stdout)
						if len(stderr) > 0:
							print (stderr)
						for tempFile in os.listdir(beTemp):
							tempPath = os.path.join(beTemp, tempFile)
							shutil.copy2(tempPath, beDir)
						shutil.rmtree(beTemp)
						

						successNotice = wx.MessageDialog(None, 'The file(s) have uploaded successfully', 'Upload Successful', wx.OK | wx.ICON_INFORMATION | wx.STAY_ON_TOP)
						successNotice.ShowModal()
						sys.exit()


#run uploadTool
if os.path.isdir(args.Files):
	fileList = []
	for subFile in os.listdir(args.Files):
		fileList.append(os.path.join(args.Files, subFile))
	args.Files = fileList
	uploadFiles(args)
else:
	uploadFiles(args)

app.MainLoop()






