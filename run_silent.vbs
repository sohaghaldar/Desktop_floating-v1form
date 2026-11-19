Set FSO = CreateObject("Scripting.FileSystemObject")
ScriptFolder = FSO.GetParentFolderName(WScript.ScriptFullName)
Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = ScriptFolder
PythonwPath = "C:\Python314\pythonw.exe"
If Not FSO.FileExists(PythonwPath) Then
    PythonwPath = "pythonw.exe"
End If
WshShell.Run Chr(34) & PythonwPath & Chr(34) & " " & Chr(34) & ScriptFolder & "\desktop_spider.py" & Chr(34), 0, False
