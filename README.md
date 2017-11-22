# uploadTool
Tool to facilitate on-demand digitization with ArchivesSpace


## UAlbany Digitization Package Spec

* This is a standard container created by the uploadTool to facilitate automated on-demand digitization
* The package includes:
  * Digital surrogate(s)
  * If the surrogate is a PART or WHOLE of a file
  * A unique identifier to link with existing archival description
  * Output from [Bulk_Extractor](https://github.com/simsong/bulk_extractor)
* The package is designed to be as simple as possible, be platform-neutral, and be managed on a typical filesystem

### Requirements

1. Directory named with matching ArchivesSpace ref_id identifier
2. Subdirectory named `.bulk_extractor` with standard [Bulk_Extractor](https://github.com/simsong/bulk_extractor) output
3. Single files must be named `part` or `whole` to denote whether they are representative of the complete record
4. Multiple must be named `part` or `whole` to denote whether they are representative of the complete record, followed by `-` and an integer as a string which denotes the files' relative arrangement to each other
  * This does not refer to the files' arrangement with any other files outside the package
5. Accepted file extensions:
  * `pdf`
  * `png`
  * `jpg`
  * `tif`

### Example Package 1 (single file, representative of whole record)

		dcfc6f866316c0ef91a1e94474cb5283/
			| whole.pdf
			\--- .bulk_extractor/
				| domain.txt
				| url.txt
				| zip.txt
				| url_histogram.txt
				| report.xml
				| email.txt
				| exif.txt
				| email_histogram.txt
				...


### Example Package 2 (single file, not representative of whole record)

		6f450b827d05b3dca224bf13333c51b7/
			| part.pdf
			\--- .bulk_extractor/
				| domain.txt
				| url.txt
				| zip.txt
				| url_histogram.txt
				| report.xml
				| email.txt
				| exif.txt
				| email_histogram.txt
				...

### Example Package 3 (multiple files, representative of whole record, semantic arrangement)

		aaf3a6c428194189c01f084e2a2490ed/
			| whole-1.png
			| whole-2.png
			| whole-3.png
			| whole-4.png
			| whole-5.png
			| whole-6.png
			| whole-7.png
			| whole-8.png
			| whole-9.png
			| whole-10.png
			| whole-11.png
			\--- .bulk_extractor/
				| domain.txt
				| url.txt
				| zip.txt
				| url_histogram.txt
				| report.xml
				| email.txt
				| exif.txt
				| email_histogram.txt
				...

### Example Package 4 (multiple files,  not representative of whole record, semantic arrangement)

		aaf3a6c428194189c01f084e2a2490ed/
			| part-1.png
			| part-2.png
			| part-3.png
			\--- .bulk_extractor/
				| domain.txt
				| url.txt
				| zip.txt
				| url_histogram.txt
				| report.xml
				| email.txt
				| exif.txt
				| email_histogram.txt
				...


## Example workflow

1. User makes request through access system that supplies ArchivesSpace ref_id
2. Archivist assigns job to student and sends ArchivesSpace ref_id, instructs to digitize part or whole of record
3. Student pulls record and digitizes content according to UAlbany's scanning specs
  * Student consults with archivist when record is not as expected
4. Directory watcher script runs command to open uploadTool when scanner sends item to a computer
5. uploadTool displays sample image
  * Student Option A if scan is complete:
    1. Enter ArchivesSpace ref_id into text box
    2. Submit package
  * Student Option B if scan is not complete:
    1. Select "Save as" to save file to working directory
    2. Repeat as neccessary
    3. Process all files according to UAlbany's scanning specs
    4. Highlight all files and right click to run uploadTool
    5. Enter ArchivesSpace ref_id into text box
    6. Submit package
6. uploadTool runs `bulk_extractor.exe` and saves output to `.bulk_extractor` directory in package
7. uploadTool makes API call to get relevant descriptive metadata from ArchivesSpace
8. uploadTool makes API call to update ArchivesSpace record with unpublished digital object record
9. uploadTool makes API call to move package into repository
10. Repository ingest workflow displays Bulk Extractor output to archivist for review
11. Repository ingest workflow makes API call to publish ArchivesSpace digital object record after files are reviewed and ingest is complete



## Getting Started

This will help you get up and running to test uploadTool. The uploadTool script itself is cross-platform, but the monitoring script is a Windows-only Powershell script. I shouldn't be too hard to write a bash equivalent. 

### Prerequisites

* Python 2 or 3
* ArchivesSpace and API permissions
* [archives_tools](https://github.com/UAlbanyArchives/archives_tools), an experimental ArchivesSpace Python Library
* [wxPython](https://www.wxpython.org/pages/downloads/)
* argparse and configparser non-standard Python libraries



### Installing

1. Make sure Python is installed and get your ASpace API credentials
2. Install [bulk_extractor](http://downloads.digitalcorpora.org/downloads/bulk_extractor/) and make sure it's added to PATH
3. Install `archives_tools`



		git clone https://github.com/UAlbanyArchives/archives_tools
		cd archives_tools
		python setup.py install


4. Enter ArchivesSpace credentials with Python prompt



      python
      >>> from archives_tools import aspace as AS
      >>> AS.setURL("http://localhost:8089")
      URL path updated
      >>> AS.setUser("admin")
      User updated
      >>> AS.setPassword("admin")
      Password updated
      >>> session = AS.getSession()
      ASpace Connection Successful

5. Install other dependencies with pip



      pip install -U wxPython
      pip install configparser
      pip install argparse

6. Clone the uploadTool repo



      git clone https://github.com/UAlbanyArchives/uploadTool
      cd uploadTool

7. Create a config file called local_settings.cfg in the uploadTool directory
8. Enter config settings. `uploadDir` is a folder where packages will be sent. `delete_path` is a path where files are sent temporatily and deleted whenever `clearDeletedFiles.py` is scheduled. `repository` is the relvent ArchivesSpace repository id.


        [uploadTool]
        uploadDir:\\server\where\files\sent
        delete_path:C:\Users\me\deleted_files
        repository:2

9. Edit `monitor.ps1` to point to uploadTool, and directory to watch for new files
  * line 3 is directory to be watched for new files
  * line 10 is command to run uploadTool, so make sure its pointing to the uploadTool directory
  * line 13 is the path to a log file



    3| $watcher.Path = "C:\PDF"
     	...
    10 |python C:\Users\me\uploadTool\uploadTool.py -p $Event.SourceEventArgs.FullPath
      	...
    13 |Add-content "C:\Users\me\uploadTool\log.txt" -value $logline

10. Run `monitor.ps1` in background on boot
11. Schedule `clearDeletedFiles.py` whenever you want to clear the directory of deleted files
12. Edit registry to add a right-click to upload files not sent to watched directory
    * command is `python C:\[path]\uploadTool.py [files]`



## How it works

* `uploadTool.py` is a command line script that makes a wizard to connect to ArchivesSpace and make packages of digitized materials combined with links to description in ArchivesSpace



	python C:\path\uploadTool.py files.pdf to.jpg upload.tif

* An optional -p flag opens the files to preview them before the wizard starts
* In our workflow, one scanner drops files in a directory over a network connection, and another scanner is managed though Photoshop and files are saved locally
* `monitor.ps1` monitors the diectory where one scanner creates files and runs `uploadTool.py` when new files are created
* When a user created files with the second scanner, as files are ready to upload, they select all the files and right-click to run `uploadTool.py`



## Contributing and Sharing

uploadTool is designed to be specific to the workflow at the M.E. Grenander Department of Special Collections & Archives at the University at Albany, SUNY. However, any contributions are welcome, particularly feedback and comments on the workflow itself.

Any questions about how ArchivesSpace can be used for similar workflows at your repository are more than welcome.



## Authors

Gregory Wiedeman



## License

This project is funded by the State of New York though the University at Albany, SUNY and all new code developed is in the Public Domain