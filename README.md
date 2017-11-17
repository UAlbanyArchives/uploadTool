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
7. uploadTool makes API call to update ArchivesSpace record with unpublished digital object record
8. uploadTool makes API call to move package into repository
9. Repository ingest workflow displays Bulk Extractor output to archivist for review
10. Repository ingest workflow makes API call to publish ArchivesSpace digital object record after files are reviewed and ingest is complete