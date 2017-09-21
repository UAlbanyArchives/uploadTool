import os
import subprocess
import wx
import argparse
import shutil
from archives_tools import aspace as AS

parser = argparse.ArgumentParser()
parser.add_argument("Files", help="Files to upload")
args = parser.parse_args()

#settings
uploadDir = "\\\\romeo\\SPE\\uploads"

app = wx.App(False)
#aa38f45243b46d8c476e109e681e5806


def saveAs(fileCount, files):
	if fileCount == 1:
		saveDlg = wx.FileDialog(None, message="Save File as ...", defaultDir="", defaultFile= "", wildcard="*.*", style=wx.SAVE|wx.OVERWRITE_PROMPT)
		if saveDlg.ShowModal() == wx.ID_OK:
			output_path = saveDlg.GetPath()
			print "Saving " + files + " to " + output_path
			#shutil.move(files, output_path)
			saveDlg.Destroy()
		else:
			saveDlg.Destroy()
	else:
		folderDlg = wx.DirDialog(None, "Choose a directory:", style=wx.DD_DEFAULT_STYLE)
        if folderDlg.ShowModal() == wx.ID_OK:
			output_path = folderDlg.GetPath()
			#if not os.path.isdir(output_path):
				#os.makedirs(output_path)
			for file in files:
				print "Saving " + file + " to " + output_path
				#shutil.move(file, output_path)
        folderDlg.Destroy()


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
	dlg = wx.TextEntryDialog(None, 'Enter the ArchivesSpace ID, or Cancel to Save As...', 'Upload Tool')

	if dlg.ShowModal() != wx.ID_OK:
		dlg.Destroy()
		saveAs(fileCount, args.Files)
	else:
		
		refID = dlg.GetValue()
		print refID
		session = AS.getSession()
		if session is None:
			failedNotice = wx.MessageDialog(None, 'ERROR: Could not connect to ArchivesSpace.', 'Failed to Connect', wx.OK | wx.ICON_ERROR | wx.STAY_ON_TOP)
			failedNotice.ShowModal()
			saveAs(fileCount, args.Files)
		else:
			record = AS.getArchObjID(session, "2", refID)
			
			dlg.Destroy()
			AS.pp(record)
			if record is None:
				failedNotice = wx.MessageDialog(None, 'ERROR: Could not find ArchivesSpace record that matches that ID', 'Bad ID', wx.OK | wx.ICON_ERROR | wx.STAY_ON_TOP)
				failedNotice.ShowModal()
				saveAs(fileCount, args.Files)
			else:
			
				recordDir = os.path.join(uploadDir, refID)
				beDir =  os.path.join(uploadDir, refID, "be")
				#if not os.path.isdir(recordDir):
					#os.makedirs(recordDir)
				
				if fileCount == 1:
					msg = "Is this file representative of the whole ASpace record?"
				else:
					msg = "Are these files representative of the whole ASpace record?"

				askType = wx.MessageDialog(None, msg, 'UploadTool', wx.YES_NO | wx.YES_DEFAULT | wx.ICON_INFORMATION | wx.STAY_ON_TOP)
				if askType.ShowModal() == wx.ID_YES:
				
					print "moving " +  args.Files +  " to " + recordDir
					#shutil.move(args.Files, recordDir)
				else:
					print "no?"
						
				#run Bulk Extractor
				print "Running Bulk Extractor"
					

			successNotice = wx.MessageDialog(None, 'The file(s) have uploaded successfully', 'Upload Successful', wx.OK | wx.ICON_INFORMATION | wx.STAY_ON_TOP)
			successNotice.ShowModal()


app.MainLoop()






