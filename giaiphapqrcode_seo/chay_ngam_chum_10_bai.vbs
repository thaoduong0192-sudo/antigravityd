Set WshShell = CreateObject("WScript.Shell") 
WshShell.Run chr(34) & "python" & Chr(34) & " " & chr(34) & "run_pillar_cluster_now.py" & Chr(34), 0
Set WshShell = Nothing
