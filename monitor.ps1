### SET FOLDER TO WATCH + FILES TO WATCH + SUBFOLDERS YES/NO
    $watcher = New-Object System.IO.FileSystemWatcher
    $watcher.Path = "C:\PDF"
    $watcher.Filter = "*.*"
    $watcher.IncludeSubdirectories = $true
    $watcher.EnableRaisingEvents = $true  

	### EVENTS TO BE WATCHED 
		Register-ObjectEvent $watcher "Created" -Action {
			python C:\Users\spestudent\uploadTool\uploadTool.py -p $Event.SourceEventArgs.FullPath
			$changeType = $Event.SourceEventArgs.ChangeType
			$logline = "$(Get-Date), $changeType, $path"
			Add-content "C:\Users\spestudent\uploadTool\log.txt" -value $logline
		}
		while ($true) {sleep 1}
