import os
import subprocess
import wx
import argparse
import shutil
from archives_tools import aspace as AS
from subprocess import Popen, PIPE

parser = argparse.ArgumentParser()
parser.add_argument("Files", help="Files to upload")
parser.add_argument("-p", help="Open files to preview them before uploading.", action='store_true')
args = parser.parse_args()

#settings
uploadDir = "\\\\romeo\\SPE\\uploads"
repo = "2"

app = wx.App(False)
#aa38f45243b46d8c476e109e681e5806


def saveAs(fileCount, files):
	if fileCount == 1:
		saveDlg = wx.FileDialog(None, message="Save File as ...", defaultDir="", defaultFile= "", wildcard="*.*", style=wx.SAVE|wx.OVERWRITE_PROMPT)
		if saveDlg.ShowModal() == wx.ID_OK:
			output_path = saveDlg.GetPath()
			print ("Saving " + files + " to " + output_path)
			shutil.move(files, output_path)
			saveDlg.Destroy()
		else:
			saveDlg.Destroy()
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
			print "TEST this isn't working"
			askDelete = wx.MessageDialog(None, msg, 'UploadTool', wx.YES_NO | wx.YES_DEFAULT | wx.ICON_INFORMATION | wx.STAY_ON_TOP)
			if askDelete.ShowModal() == wx.ID_YES:
				if fileCount == 1:
					os.remove(files)
				else:
					for file in files:
						os.remove(file)


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
			if fileCount == 1:
				deleteMsg = "Do you want to delete this file?"
			else:
				deleteMsg = "Do you want to delete these files?"
			askDelete = wx.MessageDialog(None, deleteMsg, 'UploadTool', wx.YES_NO | wx.YES_DEFAULT | wx.ICON_WARNING | wx.STAY_ON_TOP)
			if askDelete.ShowModal() == wx.ID_YES:
				if fileCount == 1:
					os.remove(args.Files)
				else:
					for deleteFile in args.Files.split(" "):
						os.remove(deleteFile)
									

			if record is None:
				failedNotice = wx.MessageDialog(None, 'ERROR: Could not find ArchivesSpace record that matches that ID', 'Bad ID', wx.OK | wx.ICON_ERROR | wx.STAY_ON_TOP)
				failedNotice.ShowModal()
				saveAs(fileCount, args.Files)
			else:
			
				if fileCount == 1:
					msg = "Is this file representative of the whole ASpace record?"
				else:
					msg = "Are these files representative of the whole ASpace record?"

				askType = wx.MessageDialog(None, msg, 'UploadTool', wx.YES_NO | wx.YES_DEFAULT | wx.ICON_INFORMATION | wx.STAY_ON_TOP)
				if askType.ShowModal() == wx.ID_YES:
					filename = "whole"
				else:
					filename = "part"
				
				recordDir = os.path.join(uploadDir, refID)
				if not os.path.isdir(recordDir):
					os.makedirs(recordDir)
				beDir =  os.path.join(recordDir, ".bulk_extractor")
					
				#get collection
				collection = AS.getResource(session, repo, record.resource.ref.split("/")[-1])
				
				msg = "Is this the correct ASpace record?"
				msg = msg + "\n\n" + record.display_string
				msg = msg + "\n 	part of " + collection.title

				confirmRecord = wx.MessageDialog(None, msg, 'UploadTool', wx.YES_NO | wx.YES_DEFAULT | wx.ICON_INFORMATION | wx.STAY_ON_TOP)
				if confirmRecord.ShowModal() == wx.ID_NO:
					print ("Wrong record")
					
				else:
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
					beCmd = ["bulk_extractor", "-R", recordDir, "-o", beDir]
					convert = Popen(beCmd, shell=True, stdout=PIPE, stderr=PIPE)
					stdout, stderr = convert.communicate()
					if len(stdout) > 0:
						print (stdout)
					if len(stderr) > 0:
						print (stderr)
					

			successNotice = wx.MessageDialog(None, 'The file(s) have uploaded successfully', 'Upload Successful', wx.OK | wx.ICON_INFORMATION | wx.STAY_ON_TOP)
			successNotice.ShowModal()


app.MainLoop()






