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
	if fileCount == 1:
		deleteMsg = "Do you want to delete this file?"
	else:
		deleteMsg = "Do you want to delete these files?"
	askDelete = wx.MessageDialog(None, deleteMsg, 'UploadTool', wx.YES_NO | wx.YES_DEFAULT | wx.ICON_WARNING | wx.STAY_ON_TOP)
	if askDelete.ShowModal() == wx.ID_YES:
		if fileCount == 1:
			shutil.move(files, delete_path)
		else:
			for file in files:
				shutil.move(file, delete_path)
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
		saveDlg = wx.FileDialog(None, message="Save File as ...", defaultDir="", defaultFile="", wildcard=wildcard, style=wx.SAVE|wx.OVERWRITE_PROMPT)
		if saveDlg.ShowModal() == wx.ID_OK:
			output_path = saveDlg.GetPath()
			print ("Saving " + files + " to " + output_path)
			shutil.move(files, output_path)
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
			for file in files:
				print ("Saving " + file + " to " + output_path)
				shutil.move(file, output_path)
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
			for openFile in args.Files.split(" "):
				if openFile.lower().endswith(".pdf"):
					openCmd = ("open " + openFile)
					openFile = Popen(openCmd, shell=True, stdout=PIPE, stderr=PIPE)
					stdout, stderr = openFile.communicate()
		checkOCR(args, pdfCount, fileCount)
	else:
		return


def uploadFiles(args):
						
	fileCount = 0
	fileCheck = True
	for file in args.Files.split(" "):
		fileCount += 1
		if not os.path.isfile(file):
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
				for openFile in args.Files.split(" "):
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
						for pdfCheck in args.Files.split(" "):
							if pdfCheck.lower().endswith(".pdf"):
								pdfCount += 1
								
						if pdfCount > 0:
							checkOCR(args, pdfCount, fileCount)					
							
							
						print ("moving " +  args.Files +  " to " + recordDir)
						if fileCount == 1:
							fileExt = os.path.splitext(args.Files)[1]
							os.rename(args.Files, os.path.join(recordDir, filename + fileExt))
						else:
							fileNumber = 0
							for item in args.Files.split(" "):
								fileNumber += 1
								fileExt = os.path.splitext(item)[1]
								os.rename(item, os.path.join(recordDir, filename + fileExt))
								
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
uploadFiles(args)

app.MainLoop()






