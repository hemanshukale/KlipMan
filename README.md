# KlipMan
A Clipboard Manager with some pretty unique features

All code is here, while the executables are up for grab in https://sourceforge.net/projects/klipman/

Hello All, 


There are many clipboard managers available on the internet, some even better than this, however, I've tried to put some very unique features in this..   

**Alternate clipboard:**  
Paste by Middle click or winkey +v and copy by Ctrl+Middle click or winkey + c), which is totally seperate from your primary clipboard. However, the winkey + c and winkey + v doesnt work when c or v are pressed. it works when c or v are/were pressed then you stop pressing winkey

**One after other mode:**  
In which, you can just copy stuff one after other in rapid succession with Ctrl+C and then rapidly paste all the stuff in the same order you copied, just by pressing series of Ctrl+V   

**Append Mode:**  
You can choose some characters, known as 'appending characters', then, whatever string you copy, these characters will be apppended to it, at the end it. The next you string you copy, gets appended after that and again the appending characters get appended, and so on..  

**CAGR Calculator:**  
There is a very easy way to calculate CAGRs rapidly if needed and if the data (numbers) are tab seperated.
Suppose you want to calculate CAGR between 'm' and 'n', eliffor a time interval 't':
Shift + Left click to select m, Shift + Right Click to select n. if both numbers are valid, it directly finds the t by finding number of tabs in between and subsequently finds CAGR. In case you want to enter time manually, click 'time?' at the bottom right then type the time you want. Accepted formats: '2', '5/12', '3.5', '4.5/12.5'.
Then press Enter or click on 'type...'
To close the mode right click on 'time?'
If numbers are not tab seperated, m and n can be selected by the method explained above and time can be entered manually.


**Top Black Space (TBS) -**  
● Left : Shows the current content of clipboard, the content that will be pasted whenever you press Ctrl+V  
● Right : Shows the content of secondary clipboard, this content will (ideally) be pasted whenever you Middle click somewhere  
To copy an item into secondary clipboard, select the item and Ctrl+Middle click.
If it is not getting pasted, try long clicking, or try pasting to notepad to see if it’s working
properly.  
If not getting directly copy or pasted on a cell, try alternates like opening the cell.  


**Middle Black Space (MBS) -**  
Maintains a clipboard ‘history’, keeps a track of all the contents ever copied to the clipboard by using Ctrl+C, (Currently does not work with Right Click + Copy )  

**Bottom Black Space (BBS) -**
Useful for the special mode of ‘one after other’.  
When this mode is enabled, copy all you want to, in succession, using Ctrl+C.  
Then paste all in succession using Ctrl+V.  

**Penultimate line:**  Temporary, shows CAGR stats, in following order: m , n , t (calculating from m to n with interval t)

**Extreme bottom Line:**  
Append Mode: Select some characters or words, which will get added to the end of whatever you are copying.

**Ex.**  
* Select the word (appending character) to append as: “ Seeds, “  
* Copy 3 words in this order: “Apple”, “Orange”, “Mango”  
* Final output: “Apple Seeds, Orange Seeds, Mango Seeds”  

* Click on Enable Append to start this mode. Done will appear on the bottom right of screen.  

* Type the words you want to set as appending characters or select the words somewhere and copy them with **Ctrl+C**, it will take them automatically. You can use Backspace in case of mistakes. Press Done when done.  

* Some keyboards provide different inputs, so, if typing to enter the characters, either try typing outside the ClipMan window or try inside. One of the mode should work properly for you.

Now as this mode is started, just copy the words in the required order, the s/w will automatically append all the required words with the appending characters and the final string will be ready to use in clipboard.

The mouse / keyboard input may get slow if very large amounts of data is copied while you are actively using the GUI. I am trying to solve the issue.

There are also and undo and redo functions. I have tried to made their working as similar to their working in MS Word. So, do play around some with undo and redo to get to know their limitations, before starting any serious stuff.


**Button / Key (valid in )** |  **Action**
---------- | ----------
Left Click on any item (MBS) | Copy it into clipboard.
Right Click on any item (MBS) | Delete the item
Middle Click on any item (MBS) | Copy it to Secondary Clipboard
Ctrl + Left Click on any item (MBS) | Copy it to Secondary Clipboard
Clear (MBS and BBS) | Clear all the items in the corresponding space
Cyan dot at top, extreme left | Clears clipboard.
Cyan dot at top, extreme right | Clears secondary clipboard
rst (MBS and BBS and TBS) | Brings the items back to default position if accidently scrolled beyond recovery.
non / on | Turns off or turns on Always on Top mode, respectively
Shift + Left Click near a number (MBS)| Extracts number for the 'from' for CAGR. 
Shift + Right Click near a number (MBS)| Extracts number for the 'to' for CAGR. 
Left Click on "time?" | Enables manual time entry for CAGR calculation (only when CAGR mode is on)
Right Click on "time?" | Disables CAGR mode
Left Click on "type?" | Accepts the written time or Enter (only when CAGR mode is on)
Drag the 2 cyan dots at right | to change size of respective spaces
Drag the cyan rectangle at top | change the display sizes of primary and secondary clipboard
Ctrl + Z | Undo (currently limited at 3, changable)
Ctrl + Y | Redo (currently limited at 3, changable)
Ctrl Shift + L | Load a file from the given options, click on the option (all the klip files in the folder)
Ctrl + L | Loads from the autosave.klip file if present in the folder
Ctrl + Shift + S | Save As, type the name you want to save the current file as. (without .klip)
Ctrl + S | Saves | Saves the current klippings in the current file (displayed in the title). If no current file is selected, will save in autosave.klip
Esc. | Back from the mode of Save As or Load File


If the copied selection consists of multiple lines, the font of the corresponding display becomes gray and 1 unit smaller to better distinguish it from other items in the list.
A **‘~’** character in such a font indicates a new line  

There are some **major differences** for the scripts for Ubuntu and Windows:  

* In Ubuntu, the loop which calls the OnKeyboardEvent function is already in another thread, according to the way pyxhook was created. Hence, all the pygame stuff and Keylogger stuff is in different threads.
However, in Windows, the loop calling of the OnKeyboardEvent is either procesed by pythoncom or by pygame.event. Putting these commands in different threads crashes the whole program. Also, you cannot put lot of commands in the OnKeyboardEvent function. When any mouse/keyboard event is detected by Windows, the event is sent to the python script. Only when the script returns True, is the event sent to other programs. If the OnKeyBoardEvent takes too much time before retruning True, it will result in an OS-wide slowdown of Mouse and Keyboard, which is soon detected by Windows and then it will stop sending events to the script and bypass it instead.  
Also, your main loop can also not be very slow, as the above effect holds in case when the OnKeyboardEvent takes too much time or is called very less frequently compared to actual speed of events. This arises when the mainloop has very high execution time resulting in the pygane.event or pythoncom commands getting called very less frequently.  
Hence, The processes that took most time (text processing and display commands) have been put into another function, disp (display), and this function is executed in another thread. A boolean variable 'cha' takes care that two instances of disp may not run at the same time.  

* Ubuntu doesn't have an alternate of the library I used for Windows - pyHook  
Hence, I got this file from the pyhook project: https://github.com/herherher/python-keylogger  (Thanks to herherher)
Just keep the file in the same folder anf then you wil be able to compile it.  


**Planned updates:**  
* Keys/clicks recording and fast replaying for repetitive and boring tasks 
* High processing usage in Ubuntu, and unexpectedly large file size. I will see what I can do to trim both down
* Set hotkeys for for some klippings or for some actions (Like double shift will paste current date/time)
* Hideable klippings especially for passwords (they will be replaced with stars in the display)
* Code will be made more efficient
* You can also choose some other window to be always on top, using this software
* Text searching within klippings
* Image Support
* Dran n drop

**Applications:**

* For booking tickets, you can store all the required data beforehand and you can fill all the textboxes rapidly by pressing **Ctrl + V** in succesion. (One after other mode)
* If you need to copy 10 diifferent things from 10 different tabs into a file, no need to (copy + change window + paste)x10, you would just need (copy)x10 + change window + (paste)x10, it will paste in the same order you copied(One after other mode)
* For repetitive tasks, suppose sending a lot of mails, you can keep a template of klippings of most used phrases ready. You would just need to click on the klipping and paste it wherever you want. You can also middle click on the klipping to copy into secondary clipboard and then press middle click at the required place to paste. 
* Calculation of CAGR needs just two clicks (good for analysts), and to copy the output, just click on it. You can replace the formula for CAGR by something else if you have some different needs.
* For developers: you already have a framework, you can now easily make a lot of changes to more suit your need. Ex. you can directly change the data you copy, internally. You can replace some words with preset once etc.


**Note:**  

I've also attached a readme pdf for instructions with images.  

This software tracks all your keystrokes. Though it doesn't record them, it maybe enough of a reason to get paranoid. You are free to check the whole code and compile your own. All is open source. Also, this keylogging can be tweaked and used for some not so legal stuff, so, be careful and use it wisely. 




**PS:**  
This might have some bugs, Do let me know (hemanshu.kale@gmail.com) in case of any random problems / bugs  

Enjoy :)

