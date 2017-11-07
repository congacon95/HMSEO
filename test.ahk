
f5::
reload
return
f2::
SendInput {Raw}get.best('', div='div', clas='class')
send {enter}
return
f3::
SendInput {Raw}get.bet('', div='div', clas='class')
send {enter}
return
f4::
SendInput {Raw}[root+i['href'] for i in get.bes('', div='div', clas='class')]
send {enter}
return
f6::
SendInput {Raw}get.log()
send {enter}
return
f7::
SendInput {Raw}for i, row in enumerate(rows):
send {enter}
SendInput {Raw}try:
send {enter}
send {enter}{Backspace}
SendInput {Raw}except: get.pe()
send {enter}{Backspace}{Backspace}
return
f8::
Click, 3
send {Backspace}
return
Clip(Text="", Reselect="") ; http://www.autohotkey.com/forum/viewtopic.php?p=467710 , modified February 19, 2013
{
	Static BackUpClip, Stored, LastClip
	If (A_ThisLabel = A_ThisFunc) {
		If (Clipboard == LastClip)
			Clipboard := BackUpClip
		BackUpClip := LastClip := Stored := ""
	} Else {
		If !Stored {
			Stored := True
			BackUpClip := ClipboardAll ; ClipboardAll must be on its own line
		} Else
			SetTimer, %A_ThisFunc%, Off
		LongCopy := A_TickCount, Clipboard := "", LongCopy -= A_TickCount ; LongCopy gauges the amount of time it takes to empty the clipboard which can predict how long the subsequent clipwait will need
		If (Text = "") {
			SendInput, ^c
			ClipWait, LongCopy ? 0.6 : 0.2, True
		} Else {
			Clipboard := LastClip := Text
			ClipWait, 10
			SendInput, ^v
		}
		SetTimer, %A_ThisFunc%, -700
		Sleep 20 ; Short sleep in case Clip() is followed by more keystrokes such as {Enter}
		If (Text = "")
			Return LastClip := Clipboard
		Else If (ReSelect = True) or (Reselect and (StrLen(Text) < 3000)) {
			StringReplace, Text, Text, `r, , All
			SendInput, % "{Shift Down}{Left " StrLen(Text) "}{Shift Up}"
		}
	}
	Return
	Clip:
	Return Clip()
}
^d::
SendInput {End}+{Home}
@ := Clip()
SendInput {End}{Enter}
Clip(@)
Return

`::
send {Shift}+{enter}
return
f10::
SendInput {Raw}from ptl import get
send {enter}
SendInput {Raw}get.setup(debug=True, driver=True)
send {enter}
SendInput {Raw}get.soup( , get.DR)
send {enter}
return