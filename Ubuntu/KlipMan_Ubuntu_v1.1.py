from __future__ import division
import pygame
from pyxhook import HookManager
import pyperclip
# import thread
from   threading import Thread
from   copy import deepcopy
import time, sys
import commands
import re
import pickle
import os


# needs pyhook.py from https://github.com/herherher/python-keylogger in the same folder to work
# Major variables are var10, var11, var20, var21
# var10 - Array of strings directly copied from clipboard
# var11 - Array corresponding to var10, but each element maybe a string like of var10
#         or maybe an array of strings seperated by newline
# var20 and var21 have the same logic as above, but these store the list for 'one after other'
# undo and redo are 2 dimenional lists, in which first collumn indicates what action happend
# second collumn stores the value seleted or added, to recover into original variable later

Print = False # enable disable all print commands
Title       = "KlipMan_v1.1"
Win_name    = "KlipMan_v1.1"
tim, con_at = 0, 0

cagr_m, cagr_n, cagr_t  = (0, -1, -1),(0,-1,-1), 0 # for calculating CAGR , from m to n
value = 0.0
c_gettime = False
c_gettime_char = ''

# z,x,c = False,False,False
var10, var11, var20, var21  = [] , [] , [] , []
last_var10, last_var20 = [],[]
clipa,sclipa = "", "" # stores the processed (ready to render- newline managed) version of ptimary and secondary clipboards
sc1, sc2 = [],[]
drag,drag1,drag2 = False,False,False

con, shi, alt,capl = False,False,False,False
con1 = False
toKill = False # useful to communicate quit message across threads, if multithreading
c2c = False # click to copy
oao = False # one after other 
app = False # to append
onn = False # always on top
to_restart = False
last_game = False
mm = False
cha = True
cagr = False
morghuled = []
mor = 350
last_save, last_load = 0,0
names, name_list = [], []
load_name = False
get_name = False
save_name = ""
current_name = ""
autosave = time.time() - 20 # to give offset of 20 seconds before first save
                            # so you get 1 minute to load the previous version 
                            # from autosave if you want to
saved_data = {}

just_clicked,last_click = False, False
# f0,f1,f2,f3,f4 = 13,10,10,12,12  # font sizes
f0,f1,f2,f3,f4 = 10,7,7,9,9  # font sizes - Lucida - 2

ldown , rdown  = False, False # mouse buttons down 
white = (255,255,255)
black = (0,0,0)
grey  = (200,200,200)
green = (0,255,0)
blue  = (0,0,255)
cyan  = (0,255,255)
red   = (255,0,0)

def constrain(val, mi, ma):
  # if Print: print "old,new:", val
  val = max(val, mi)  
  val = min(val, ma)
  if Print: print val
  return val

# some coordinates
x_en, x_cl, x_rs, x_ex = 2, 130, 192, 217 # x coordinates of some displayed words
# Enable, Clear, rst, Exit respectively

sx , sy = 300, 270 # stores current screen size
v_div = (0.2, 0.6) # the respective fractions of vertical screen indicating the 
                   # positions of first and second setting panes respectively

di1 , di2, id1, id2 = {}, {}, {}, {}

start1y    = int(sy*v_div[0])                                     # y for first settings line
start2y    = int(sy*v_div[1])                                     # y for second settings line
start1y    = constrain(start1y,40,start2y)
start2y    = constrain(start2y,start1y, sy-(2*(f0+1)) )

e1, e2, e3 = (x_en, start1y), (x_en , start2y), (x_en, sy-17)      # x,y of the three Enables
c1, c2     = (x_cl, start1y), (x_cl, start2y)                      # x,y of the two clears
r1, r2, r3 = (x_rs, start1y), (x_rs, start2y), (sx-16, start1y-20) # x,y of the three resets
a1, vm     = (150, sy-17),    (x_ex + 200, start1y)                # x,y of append and (vm)
s1, ex1    = (x_ex,start2y),  (x_ex+25,start1y)                    # x,y of start oao and exit
o1, d1     = (x_ex, start1y), (sx-30, sy-17)                       # x,y of 

clip_div = 0.6            # how much % of x should primary and secondary clipboard display take
cl1 = (20,start1y + 15)   # starting point of clipboard list
cl2 = (20,start2y + 15)   # starting point of one after other list
cl0, scl0 = (3, 3), (sx*clip_div, 3)  # starting point of primary and econdary clipboard respectively


last_clip, last_sclip = "", "" # last value of primary and secondary clipboard
                               # useful to know when value changes, hence, to update
# cen = (0, 240)
copied = False
to_copy = "" # when Ctrl+C is detected, Clipboard is copied in this string for further processing
undo, redo = [], [] # for storing undo and redo arrays 

def ur_limit(): # cannot define constants in python, hence this way
  return 3 # limit for undo and redo

sdev1x,sdev1y,sdev2x,sdev2y = 0,0,0,0 # list of scroll coordinates ....
sdev3x,sdev3y,sdev4x,sdev4y = 0,0,0,0 # .... keeps track of how much scrolled


nor = ['1','2','3','4','5','6','7','8','9','0','-','=',',','.','/',';',"'",'[',']','\\']
nos = ['!','@','#','$','%','^','&','*','(',')','_','+','<','>','?',':','"','{','}', '|']
ABC = ['Q','W','E','R','T','Y','U','I','O','P','A','S','D','F','G','H','J','K','L','Z','X','C','V','B','N','M']
abc = ['q','w','e','r','t','y','u','i','o','p','a','s','d','f','g','h','j','k','l','z','x','c','v','b','n','m']

# num = ['0','1','2','3','4','5','6','7','8','9']
# if you have a Keyboard with numpad doubling as other special keys 
# and whenver you press a numkey, the special key shows up, map them here
# from 0 - 9 
spe = ['P_Insert','P_End','P_Down','P_Next','P_Left','P_Begin','P_Right','P_Home','P_Up','P_Page_Up']


app_chr, appended = "", "" # for append mode
to_app   = False # for append mode
p_cl, s_cl, clip_now = "", "" , "" # primary, secondary clipboard
last_onn = False

def hasNumbers(inputString):
    return bool(re.search(r'\d', inputString))

# def hasNumbers(inputString):
     # return any(char.isdigit() for char in inputString)

def rreplace(s, old, new, occurrence): # replace 'occurance' number of last occurances of 'old' with 'new'
    li = s.rsplit(old, occurrence)
    return new.join(li)

def isString(variable): # checks whether the given value is string or not
  answer = False
  try:
    testing = variable.find(' ')
    answer = True
  except AttributeError as e:
    answer = False
  return answer

def get_caps():
    cap = commands.getoutput('xset -q | grep Caps') # get CAPS LOCK state
    i1  = cap.find('Caps')
    i2  = cap.find('Num' )
    cap2 = cap[i1:i2]
    if 'Off' in cap2 or 'off' in cap2:
      return False
    if 'On' in cap2 or 'on' in cap2:
      return True
    return False


def get_cagr(cm, cn, ct):
    # you can replace it with any other custom formula
    # and make according changes in the code
    val = ( (((cn/cm)**(1/ct))-1) * 100 ) # formula for cagr
    return val


# load save autosave walkthrough:
# autosaves current clippings every 40 seconds into autosave.klip
# load: Ctrl+L       to load from autosave file (will work only for 1 minute until bootup)
#                    as after 1 minute, the file will be overwritten by the autosave 
#                    of the current version
#       Ctrl+Shift+L to load any other clippings, displays the available .klip files
#                    then click on any one of the files to open it
#                    the loaded file will then become the current file
#
# save: Ctrl+S       to save the current status, if there exists a current file, 
#                    it will save into it, else will save in autosave
#       Ctrl+Shift+S save as, type the name you want to save the current clippings as,
#                    and press enter. it will save into the typed name 
#                    and then this will become the current file

def save_data(data, tosave):
  global var10, var20, clip_now, s_cl, last_save,Title,current_name,Win_name
  not_allowed = ['/']

  if time.time() - last_save > 1.5:
    if tosave == '':
      try:
          output = open('autosave.klip', 'wb')
      except IOError as e:
          if Print: print "file N/A"
          return False
      except :
        return False

    else:
      for nott in not_allowed:
        if nott in tosave:
          # if Print: print "nott:", nott
          tosave = tosave.replace(nott,'')
      try:
          output = open(tosave + '.klip', 'wb')
          current_name = tosave
      except IOError as e:
          if Print: print "file N/A"
          return False
      except :
        return False

    pickle.dump(data, output)
    output.close()
    if current_name != "":
      Title = Win_name + '-' + current_name
      pygame.display.set_caption(Title)

    if Print: print "saved:"
    if Print: print var10
    if Print: print var20
    if Print: print clip_now
    if Print: print s_cl
    last_save = time.time()

def load_data(toload):
  global var10, var20, var11, var21, clip_now, s_cl, last_load, Title, current_name, Win_name
  if time.time() - last_load > 1.5:
    data1 = {}
    pkl_file = 0
    if toload == '':
      try:
        pkl_file = open('autosave.klip', 'rb')
      except IOError as e:
        if Print: print "file N/A"
        return False
      except :
        return False
    else:
      try:
        pkl_file = open(toload+'.klip', 'rb')
      except IOError as e:
        if Print: print "file N/A"
        return False
      except :
        return False

      current_name = toload

    try:
        data1 = pickle.load(pkl_file)
    except:
        return False
    if Print: print data1

    # data2 = pickle.load(pkl_file)
    # if Print: print data2

    pkl_file.close()

    un = []
    un.append("loaded")
    unn = []
    unn.append(data1['v1'])
    unn.append(data1['v2'])
    unn.append(data1['v3'])
    unn.append(data1['v4'])
    unn.append(pyperclip.paste())
    unn.append(s_cl)
    unn.append(len(var10))
    unn.append(len(var20))

    un.append(unn)
    undo.append(un)
    if len(undo) > ur_limit():
        undo.pop(0)



    var10.extend(data1['v1'])
    var20.extend(data1['v2'])
    clip_now = data1['v3']
    s_cl     = data1['v4']

    if current_name != "":
        Title = Win_name + '-' + current_name
        pygame.display.set_caption(Title)

    if Print: print "loaded:"
    if Print: print var10
    if Print: print var20
    if Print: print clip_now
    if Print: print s_cl
    var11, var21 = [], []
    for v in var10:
      var11.append(manage_nl(v))
    for v in var20:
      var21.append(manage_nl(v))
    pyperclip.copy(clip_now)
    clipa   = manage_nl(clip_now)
    sclipa  = manage_nl(s_cl)
    last_load = time.time()

def manage_nl(stri): 
# newline characters are not properly processed and appear as a box in the pygame display 
# this functions finds newline characters if any, and replaces them with '~'
# also splits the string into an array of strings, representing different lines after newline characters
# to display all the lines, for pygame.
# if no newline founs, returns the original string
# \t is not processed as tab by pygane, hence it is replaced by 4 spaces ("    ") for display 


    st = ""
    tem2, tem3 = [], []
    coun = 0
    stri = stri.replace('\t', "    ")
    stlist = list(stri)
    ll = len(stlist)
    jk = 0 
    while jk < ll :
      chrr = stlist[jk]
      coun += 1
      if coun == ll:
        if chrr != '\n' and chrr != '\r':
          st += chrr
        else:
          if len(tem2) > 0:
            st = st + '~'
          else:
            stri = stri[:-1] + '~'
        if len(tem2) > 0:
          tem2.append(st)
          st = ""
      elif (chrr == '\r' and jk + 1< ll and stlist[jk+1] == '\n') or (chrr == '\n' and jk + 1< ll and stlist[jk+1] == '\r'):
        tem2.append(st+'~')
        st = ""
        coun += 1 
        jk += 1
      elif chrr == '\n' or chrr == '\r':
        tem2.append(st+'~')
        st = ""
      else:
        st += chrr
      jk += 1
    if len(tem2) > 0: 
      return tem2
    else:
      return stri 

tem = pyperclip.paste() 
if tem != "" :
    var10.append(tem) # adds the initial value into the array var10
    out = manage_nl(tem)
    var11.append(out)
    if Print: print "yooo"

def test():

    # if Print: print "wtf"
# def test():
    pygame.init()
    pygame.font.init()
    # if Print: print "wtf now"
    
    # Globalization
    global sx, sy, f1, f2, f3, f4, Title, cha, clipa, sclipa,clip_now
    global white,black,grey, blue, green, red
    global e1,e2,e3,c1,c2,r1,r2,s1,e1,cl1,cl2,cl0,ex1,r3,a1,o1,scl0,drag,drag1,drag2
    global tim, last_clip, last_sclip, to_restart, to_copy, p_cl, s_cl
    global di1,di2,id1,id2,spe, nor, nos, abc, ABC, onn, last_onn, toKill, d1
    global c2c, oao, app, to_app, app_chr, appended, mm, copied,just_clicked,last_click
    global sdev2x, sdev1x, sdev1y, sdev2y, sdev3x, sdev3y, sdev4x,sdev4y
    global var10, var11, var20 ,var21, undo, redo, last_game, mor, morghuled, v_div
    global ldown, rdown, con, con_at, con1, clip_div, last_var10, last_var20
    global cagr_m,cagr_n,cagr_t,cagr,value,c_time,c_gettime,c_gettime_char,cs_time,cs_type,c_scr
    global autosave, saved_data, get_name, save_name, load_name, names, name_list
    global start1y, start2y
 

    fon1 = None
    fon2 = 'Comic Sans MS'
    fon3 = 'Arial'
    fon4 = 'roboto' 
    fon5 = 'Calibri'
    fon6 = 'Lucida Console'
    fon  = fon6
    # if Print: print fo
    fon0 = pygame.font.SysFont(fon,f0)     # Default font for Instructions / Buttons. Not changable
    fo10 = pygame.font.SysFont(fon,f1)     # Font for Clipboard list (single line items)
    fo11 = pygame.font.SysFont(fon,f1 - 1) # Font for Clipboard list (multi  line items)
    fo20 = pygame.font.SysFont(fon,f2)     # Font for one after other list (single line items)
    fo21 = pygame.font.SysFont(fon,f2 - 1) # Font for one after other list (multi  line items)
    fo30 = pygame.font.SysFont(fon,f3)     # Font for primary clipboard display (single line items)
    fo31 = pygame.font.SysFont(fon,f3 - 1) # Font for primary clipboard display (multi  line items)
    fo40 = pygame.font.SysFont(fon,f4)     # Font for secondary clipboard display (single line items)
    fo41 = pygame.font.SysFont(fon,f4 - 1) # Font for secondary clipboard display (multi  line items)

    # Intializing some fixed texts
    text1  = fon0.render("Exit", 10, cyan)
    text2  = fon0.render("Enable 1 click copy", 10, cyan)
    text3  = fon0.render("Disable 1 click copy", 10, cyan)
    text4  = fon0.render("Enable 1 after other", 10, cyan)
    text5  = fon0.render("Disable 1 after other", 10, cyan)
    text6  = fon0.render("Start oao", 10, cyan)
    text7  = fon0.render("Clear", 10, cyan)
    text8  = fon0.render("rst", 10, cyan)
    text09 = fon0.render("Enable Append", 10, cyan)
    text10 = fon0.render("Disable Append", 10, cyan)
    text11 = fon0.render("Done", 10, cyan)
    text12 = fon0.render("non", 10, cyan)
    text13 = fon0.render("on", 10, cyan)
    text14 = fon0.render("Valar Morghulis", 10, red)
    text15 = fon0.render("time?", 10, cyan)
    text16 = fon0.render("type..", 10, cyan)
    text17 = fon0.render("name:", 10, cyan)
    text18 = fon0.render("click to load:", 10, cyan)
    # text15 = fon0.render("Undo", 10, cyan)

    # Screen set-up
    pygame.display.set_caption(Title)
    screen = pygame.display.set_mode((sx,sy),pygame.RESIZABLE)
    if Print: print "pygame started"
    pygame.mouse.set_visible(1)
    background = pygame.Surface(screen.get_size())    
    background = background.convert()
    background.fill((250,250,250))
    background.fill((0,0,0))

    screen.blit(background, (0,0))
    pygame.display.flip()
    
    exx1  = screen.blit(text1, ex1) # Exit
     
    ec2c  = screen.blit(text2 , e1)  # Enable  c2c
    dc2c  = screen.blit(text3 , e1)  # Disable c2c
    eoao  = screen.blit(text4 , e2)  # Enable  oao
    doao  = screen.blit(text5 , e2)  # Disable oao

    soao  = screen.blit(text6 , s1)  # Start oao
    clr1  = screen.blit(text7 , c1)  # Clear for clipboard list
    clr2  = screen.blit(text7 , c2)  # Clear one after other list
    rst1  = screen.blit(text8 , r1)  # Reset for clipboard list
    rst2  = screen.blit(text8 , r2)  # Reset for one after other list
    onn1  = screen.blit(text12, o1)  # Disable Always on Top
    onn2  = screen.blit(text13, o1)  # Enable Always on top
      
    dapp  = screen.blit(text10, e3)  # Disable append
    eapp  = screen.blit(text09, e3)  # Enable append
    don   = screen.blit(text11, d1)  # Done (append purposes)
    app2  = fon0.render(app_chr, 1, white)
    app1  = screen.blit(app2, a1)    # Appending character
    rapp1 = pygame.draw.rect(screen, blue, app1 ) 
    app1  = screen.blit(app2, a1)
    onn1  = screen.blit(text12, o1)  # Enable Always on top
    onn2  = screen.blit(text13, o1)  # Disable Always on top
    rst3  = screen.blit(text8 , r3 ) # Reset for primary and secondary clipboard 
    nam   = screen.blit(text17, ( sx-30, r2[1] - f0 ) ) 

    cs_time = screen.blit(text15,d1) # Text to click when need to enter time 
                                     # manually for calculating CAGR
    cs_type = screen.blit(text16,d1) # Text to click when finished typing time^

    len1, len2 = '[' + str(len(var10)) + ']', '[' + str(len(var20)) +']'
    l1    = fon0.render(len1 , 10, cyan)
    l2    = fon0.render(len2 , 10, cyan)
    le1   = screen.blit(l1, (c1[0] + 30, c1[1]) ) # length of var1
    le2   = screen.blit(l2, (c2[0] + 30, c2[1]) ) # length of var2

    pcir  = pygame.draw.circle(screen, cyan, (3,3), 4)
    scir  = pygame.draw.circle(screen, cyan, (sx-3,3), 4)
    cir1  = pygame.draw.circle(screen, cyan, (sx-3, r1[1]), 4)
    cir2  = pygame.draw.circle(screen, cyan, (sx-3, r2[1]), 4)


    rc2c  = pygame.draw.rect(screen, black, (0, e1[1], sx, f0+1) ) 
    roao  = pygame.draw.rect(screen, black, (0, e2[1], sx, f0+1) ) 
    rapp  = pygame.draw.rect(screen, black, (0, e3[1], sx, f0+1) ) 

    pygame.display.flip()

    timn  = time.time()
    count = 0

    tim = time.time()
    if Print: print "tim is", tim
    # pygame.event.set_grab(False)
 
    # Sometimes, the key return maybe same in case of pressing a key with or without Shift or CAPS Lock
    # so, here is a dictionary used to map characters to their respective 'shift' versions
    # input may also differ if the function call is processed by pythoncom or by pygame
    di1=dict(zip(nos,nor))
    id1=dict(zip(nor,nos))
    di2=dict(zip(abc,ABC))
    id2=dict(zip(ABC,abc))
    # if Print: print di1, di2

    
    while True :
        time.sleep(0.001)
        
        screen.fill(black)
        if con1 and con and time.time() - 0.05 > con_at:
        # sometimes if you press Ctrl+C or Ctrl+V and remove the fingers quickly, there is a chance
        # that the C or V keydown might be registered after Ctrl keyup is registered
        # hence, this snippet gives us an additional 30ms after Ctrl keyup is registered
          con = False
          if Print: print "con is", con
          con1 = False

        if copied: # to give time to fill the clipboard # increase if you frequently copy very large data or for slower systems
          time.sleep(0.08)
          to_copy = pyperclip.paste()
          copied  = False

        if to_copy != "":  
          # When an item is copied using Ctrl+C, it is copied in this variable and
          # processed here, instead of procesing in the function
          tem = to_copy
          var10.append(tem)
          out = manage_nl(tem)
          var11.append(out)
          
          un = []
          un1 = "to var1 " # prepare string for undo
          sdev3x,sdev3y = 0,0 # resets scrolls (deviations) for clipboard whenever a new item is copied

          if oao: # if oao is on, appends to var2
            var20.append(tem)
            var21.append(out)
            un1 += "and var2 "
            pyperclip.copy(var20[0])

          if app and not to_app:
            appended += (tem + app_chr)
            pyperclip.copy(appended)
            un1 += "and app "
          if app and to_app:
            app_chr += tem

          un1 += "added"
          un.append(un1)
          un.append(tem)
          undo.append(un)
          redo = []
          redo.append(un)
          if len(undo) > ur_limit():
            undo.pop(0)
          to_copy = ""

          # code for Secondary Clipboard using middle click
          # no need in Ubuntu as it already provides one
          # Still, if you want this, you can disable that 
          # uncomment this

        if mm:                    # when middle clicked
          if con:                   # if control is pressed, it copies the selected item
            p_cl = pyperclip.paste()  # takes backup of clipboard
            # shell.SendKeys("^(c)")    # sends Ctrl+C
            cap = commands.getoutput('xdotool key "control+c"')
            time.sleep(0.06)          # waits for 60 ms for things to take effect
            s_cl = pyperclip.paste()  # transfers copied item into secondary clipboard variable
            var10.append(s_cl)        # appends to array ....
            out = manage_nl(s_cl)     # ....
            var11.append(out)         # ....
            pyperclip.copy(p_cl)      # restores primary clipboard from backup
            sdev4x,sdev4y = 0,0       # resets scrolls (deviations) for clipboard whenever a new item is copied

          else :                   # if Control is not pressed, it pastes the item in secondary clipboard
            p_cl = pyperclip.paste()  # takes backup of clipboard
            pyperclip.copy(s_cl)      # transfers secondary clipboard variable into clipboard
            time.sleep(0.05)          # waits for 50 ms for things to take effect
            cap = commands.getoutput('xdotool key "control+v"')
            # shell.SendKeys("^(v)")    # sends Ctrl+V
            time.sleep(0.05)          # waits for 50 ms for things to take effect
            pyperclip.copy(p_cl)      # restores primary clipboard from backup
          
          mm = False
          # if Print: print p_cl
          # if Print: print s_cl


        ncir = pygame.draw.circle(screen, cyan, (0,0), 0) # A null circle for use later
        
        # t1 = time.time()
        # when something changes, then only the pygamme window is refreshed 
        # channge indicated when the variable is true

        if time.time() - autosave > 40: # autosaves in every 40 seconds
            now_data = {
            'v1' : var10,
            'v2' : var20,
            'v3' : clip_now,
            'v4' : s_cl
            }
            if saved_data != now_data:
              save_data(now_data, '')
              saved_data = now_data
              if Print: print "saved"
            else:
              if Print: print "no need to save"
            autosave = time.time()



        if cha:
          texx, sc1 = [], []
          # if a particular element in the var11 is an array, it goes through the array to display each line nearby
          # else if it is a string, it displays the string
          time.sleep(0.001)
          screen.unlock()
          copy_var11 = deepcopy(var11) # copy made as orignal var11 can get changed in 
                                       # the main loop while this loop is being executed
          vspace = 3
          xx, yy = cl1[0] + sdev1x, cl1[1] + sdev1y

          for ii in range(len(copy_var11)):
            if not isString(copy_var11[ii]): 
              n1 = len(copy_var11[ii])
              tex2, sc_temp2= [], []
              yy += f1/(vspace/3)
              for i2 in range(n1):
                yy += f1/vspace
                wid = fo11.size(copy_var11[ii][i2])[0]
                if wid > sx - xx: # if whole horizontal text doesnt fit in the screen...
                  bre = int(((sx - xx) * len(copy_var11[ii][i2])) / wid )
                else :
                  bre = None
                try: 
                    tt = fo11.render(copy_var11[ii][i2][:bre], 1, grey) # ...render only the text that will
                except pygame.error as e: # sometimes, a too big font can throw this exception
                    f1 -= 1               # hence, decrease the font in case of such exceptions
                  # f1 = max(8, f1)
                    fo10 = pygame.font.SysFont(fon,int(f1))
                    fo11 = pygame.font.SysFont(fon,int(f1) - 1)
                tex2.append(tt)
                if yy + f1 < e2[1] and yy > c1[1]: # render only the allowed text lines with proper y coordinate 
                  time.sleep(0.0002)
                  try:
                    sc_temp = screen.blit(tex2[-1], (xx,yy))
                  except pygame.error as e:
                    if Print: print "pg:" , e
                    sc_temp = ncir
                  sc_temp2.append(sc_temp)
                else:                              # no need of rendering text lines that will be below the last allowed line 
                  sc_temp = ncir                   # instead, populate the array with null circles, to preserve the correspondance between sc1 and var1
                  sc_temp2.append(sc_temp)
                yy += f1/vspace                    # to add vertical spcace in between adjacent lines
              yy += f1/vspace                      # to add vertical spcace in between adjacent lines
  
              sc1.append(sc_temp2)
              texx.append(tex2)
            
            else: # if string 
              yy += f1/(vspace/3)
              # if Print: print "copy_var11:", copy_var11[ii]
              wid = fo10.size(copy_var11[ii])[0]
              if wid > sx - xx: # if whole text doesnt fit in the screen...
                bre = int(((sx - xx) * len(copy_var11[ii])) / wid)
              else:
                bre = None
              try:
                  tt = fo10.render(copy_var11[ii][:bre], 1, white) # ...render only the text that will
              except pygame.error as e: # sometimes, a too big font can throw this exception
                  f1 -= 1
                  # f1 = max(8, f1)
                  fo10 = pygame.font.SysFont(fon,int(f1))
                  fo11 = pygame.font.SysFont(fon,int(f1) - 1)
              texx.append(tt)
              # if yy + f1 < e2[1] and yy + f1/1.2 > c1[1]:
              if yy + f1 < e2[1] and yy > c1[1]: # render only the line only if it has  proper y coordinate 
                  time.sleep(0.0002)
                  try:
                    sc_temp = screen.blit(texx[-1], (xx,yy))
                  except pygame.error as e:
                    if Print: print "pg:" , e
                    sc_temp = ncir

                  sc1.append(sc_temp)
              else:
                  sc_temp = ncir
                  sc1.append(sc_temp)
              yy += f1/(vspace/2)               # to add vertical spcace in between adjacent lines
  
          texx2, sc2 = [], []
          xx, yy = cl2[0] + sdev2x, cl2[1] + sdev2y
          
          time.sleep(0.001)
          copy_var21 = deepcopy(var21)

          for ii in range(len(copy_var21)):
            if not isString(copy_var21[ii]):
              n1 = len(copy_var21[ii])
              tex2, sc_temp2 = [], []
              yy += f2/(vspace/3)
              for i2 in range(n1):
                yy += f2/vspace
                wid = fo21.size(copy_var21[ii][i2])[0]
                if wid > sx - xx: # if whole text doesnt fit in the screen...
                  bre = int(((sx - xx) * len(copy_var21[ii][i2])) / wid )
                else :
                  bre = None
                try:
                    tt = fo21.render(copy_var21[ii][i2][:bre], 1, grey) # ...render only the text that will
                except pygame.error as e: # sometimes, a too big font can throw this exception
                  f2 -= 1
                  # f1 = max(8, f1)
                  fo20 = pygame.font.SysFont(fon,int(f2))
                  fo21 = pygame.font.SysFont(fon,int(f2) - 1)
                tex2.append(tt)
                if yy > c2[1] and yy < e3[1]:
                  try:  
                    sc_temp = screen.blit(tex2[-1], (xx,yy))
                    sc_temp2.append(sc_temp)
                  except pygame.error as e:
                     if Print: print "pg:" , e
                     sc_temp = ncir
                yy += f2/vspace           # to add vertical spcace in between adjacent lines
              yy += f2/vspace             # to add vertical spcace in between adjacent lines
  
              sc2.append(sc_temp2)
              texx2.append(tex2)
            else:
              yy += f2/(vspace/3)
              # if Print: print copy_var21[ii]
              wid = fo20.size(copy_var21[ii])[0]
              if wid > sx - xx: # if whole text doesnt fit in the screen...
                bre = int(((sx - xx) * len(copy_var21[ii])) / wid)
              else:
                bre = None
              try:
                  tt = fo20.render(copy_var21[ii][:bre], 1, white) # ...render only the text that will
              except pygame.error as e: # sometimes, a too big font can throw this exception
                  f2 -= 1
                  # f1 = max(8, f1)
                  fo20 = pygame.font.SysFont(fon,int(f2))
                  fo21 = pygame.font.SysFont(fon,int(f2) - 1)
              texx2.append(tt)
              if yy  > c2[1] and yy < e3[1]:
                try:
                  sc_temp = screen.blit(texx2[-1], (xx,yy))
                except pygame.error as e:
                   if Print: print "pg:" , e
                   sc_temp = ncir                  
                sc2.append(sc_temp)
              yy += f2/(vspace/2)

        
        # display current clipboard
        # bigb = pygame.draw.rect(screen, black, (0, 0, 480, cl1[1]) ) 
        
        # if Print: print "t2:", time.time() - t1
        # t1 = time.time()


        if cha:
          tex2, sct, scc = [], [], []
          xx, yy = scl0[0] + sdev4x, scl0[1] + sdev4y
  
        # if s_cl != "":
          # Secondary Clipboard          
          if not isString(sclipa):
            copy_sclipa = deepcopy(sclipa)
            for ii in range(len(copy_sclipa)):
              tex2, sct= [], []
              yy += f4/(vspace/2)
              rawtext = copy_sclipa[ii]
              txt = []
              cond = False
              timmm = time.time()
              while not cond and time.time() - 0.05 < timmm :
                wid = fo41.size(rawtext)[0]
                if wid > sx - xx: # if whole text doesnt fit in the screen...
                  bre = int(((sx - xx) * len(rawtext) ) / wid) # ...find only the text that will
                  last_space = rawtext.rfind(' ', 0, bre) # ...then find the last space before that
                  # if Print: print wid, sx, xx, len(rawtext), bre, last_space
                  
                  if last_space != -1:
                    try:
                        ttt = fo41.render(rawtext[:last_space], 1 , grey)
                    except pygame.error as e:
                        f4 -= 1
                        # f1 = max(8, f1)
                        fo40 = pygame.font.SysFont(fon,int(f3))
                        fo41 = pygame.font.SysFont(fon,int(f3) - 1)
                    # if Print: print rawtext[:last_space]
                    rawtext = rawtext[last_space+1:]
                    if yy + f4 < e1[1] :
                      yy += f4/vspace
                      time.sleep(0.0002)
                      try:
                        sc_temp  = screen.blit(ttt, (xx,yy))
                      except pygame.error as e:
                        if Print: print "pg:" , e
                        sc_temp = ncir
                      sct.append(sc_temp)
                      yy += f4/vspace
                  
                  else: # when space not found .... 
                    try:
                        ttt = fo41.render(rawtext[:bre-2], 1 , grey) # ....render only the text that will 
                    except pygame.error as e:
                        f4 -= 1
                        # f1 = max(8, f1)
                        fo40 = pygame.font.SysFont(fon,int(f4))
                        fo41 = pygame.font.SysFont(fon,int(f4) - 1)
                    # if Print: print rawtext[:last_space]
                    rawtext = rawtext[bre-2:]  
                    if yy + f4 < e1[1] :
                      yy += f4/vspace
                      time.sleep(0.0002)
                      try: 
                        sc_temp  = screen.blit(ttt, (xx,yy))
                      except pygame.error as e:
                        if Print: print "pg:" , e
                        sc_temp = ncir

                      sct.append(sc_temp)
                      yy += f4/vspace
                else:
                    try:
                        ttt = fo41.render(rawtext, 1 , grey)
                    except pygame.error as e:
                        f4 -= 1
                        # f1 = max(8, f1)
                        fo40 = pygame.font.SysFont(fon,int(f4))
                        fo41 = pygame.font.SysFont(fon,int(f4) - 1)
                    # if Print: print rawtext
                    if yy + f4 < e1[1] :
                      yy += f4/vspace
                      time.sleep(0.0002)
                      try:  
                        sc_temp  = screen.blit(ttt, (xx,yy))
                      except pygame.error as e:
                        if Print: print "pg:" , e
                        sc_temp = ncir

                      sct.append(sc_temp)
                      yy += f4/vspace
  
                    # if Print: print "\n\t\tcond met"
                    cond = True
              # texx.append(tex2)
          else:  
              rawtext = sclipa
              # if Print: print "r=" , rawtext
              cond = False
              timmm = time.time()
              while not cond and time.time() - 0.05 < timmm :
                yy += f4/vspace
                wid = fo40.size(rawtext)[0]
                if wid > sx - xx:
                  bre = int(((sx - xx) * len(rawtext) ) / wid)
                  last_space = rawtext.rfind(' ', 0, bre)
                  # if Print: print wid, sx, xx, len(rawtext), bre, last_space
                  if last_space != -1:
                    ttt = fo40.render(rawtext[:last_space], 1 , white)
                    # if Print: print rawtext[:last_space]
                    rawtext = rawtext[last_space+1:]
                    if yy + f4 < e1[1] :
                      yy += f4/vspace
                      time.sleep(0.0002)
                      try:
                        sc_temp  = screen.blit(ttt, (xx,yy))
                      except pygame.error as e:
                        if Print: print "pg:" , e
                        sc_temp = ncir
                      sct.append(sc_temp)
                      yy += f4/vspace

                  else:
                    ttt = fo40.render(rawtext[:bre-2], 1 , white)
                    # if Print: print rawtext[:last_space]
                    rawtext = rawtext[bre-2:]
                    if yy + f4 < e1[1] :
                      yy += f4/vspace
                      time.sleep(0.0002)
                      try:
                        sc_temp  = screen.blit(ttt, (xx,yy))
                      except pygame.error as e:
                        if Print: print "pg:" , e
                        sc_temp = ncir
                      sct.append(sc_temp)
                      yy += f4/vspace
  
                else:
                    # if Print: print wid, sx, xx
                    ttt = fo40.render(rawtext, 1 , white)
                    # if Print: print rawtext
                    if yy + f4 < e1[1] :
                      yy += f4/4
                      time.sleep(0.0002)
                      try:
                        sc_temp  = screen.blit(ttt, (xx,yy))
                      except pygame.error as e:
                        if Print: print "pg:" , e
                        sc_temp = ncir

                      sct.append(sc_temp)
                      yy += f4/(vspace/2)
                    # if Print: print "\n\t\tcond met"
                    cond = True
                    # if Print: print "\n\t\tcond met"
                    break
  
  
          rcli  = pygame.draw.rect(screen, black, (0, 0, scl0[0], e1[1]) ) 
          if s_cl != "":
            rcli2 = pygame.draw.rect(screen, cyan , (scl0[0], 0, 5, 7) ) 
  
  # Primary Clipboard
          time.sleep(0.001)
          tex2, sct, scc = [], [], []
          xx, yy = cl0[0] + sdev3x, cl0[1] + sdev3y

          if not isString(clipa):
            copy_clipa = clipa
            for ii in range(len(copy_clipa)):
              tex2, sct= [], []
              yy += f3/(vspace/2)
              rawtext = copy_clipa[ii]
              txt = []
              cond = False
              timmm = time.time()
              while not cond and time.time() - 0.05 < timmm :
                wid = fo31.size(rawtext)[0]
                if wid > scl0[0] - xx:
                  bre = int(((scl0[0] - xx) * len(rawtext) ) / wid)
                  last_space = rawtext.rfind(' ', 0, bre)
                  # if Print: print wid, sx, xx, len(rawtext), bre, last_space
                  if last_space != -1:
                    try:
                        ttt = fo31.render(rawtext[:last_space], 1 , grey)
                    except pygame.error as e:
                        f3 -= 1
                        # f1 = max(8, f1)
                        fo30 = pygame.font.SysFont(fon,int(f3))
                        fo31 = pygame.font.SysFont(fon,int(f3) - 1)
                    # if Print: print rawtext[:last_space]
                    rawtext = rawtext[last_space+1:]
                    if yy + f3 < e1[1] :
                      yy += f3/vspace
                      time.sleep(0.0002)
                      try:
                        sc_temp  = screen.blit(ttt, (xx,yy))
                      except pygame.error as e:
                        if Print: print "pg:" , e
                        sc_temp = ncir
                      sct.append(sc_temp)
                      yy += f3/vspace
                  else:
                    try:
                        ttt = fo31.render(rawtext[:bre-2], 1 , grey)
                    except pygame.error as e:
                        f3 -= 1
                        # f1 = max(8, f1)
                        fo30 = pygame.font.SysFont(fon,int(f3))
                        fo31 = pygame.font.SysFont(fon,int(f3) - 1)
                    # if Print: print rawtext[:last_space]
                    rawtext = rawtext[bre-2:]
                    if yy + f3 < e1[1] :
                      yy += f3/vspace
                      time.sleep(0.0002)
                      try:
                        sc_temp  = screen.blit(ttt, (xx,yy))
                      except pygame.error as e:
                        if Print: print "pg:" , e
                        sc_temp = ncir
                      sct.append(sc_temp)
                      yy += f3/vspace
                else:
                    try:
                        ttt = fo31.render(rawtext, 1 , grey)
                    except pygame.error as e:
                        f3 -= 1
                        # f1 = max(8, f1)
                        fo30 = pygame.font.SysFont(fon,int(f3))
                        fo31 = pygame.font.SysFont(fon,int(f3) - 1)
                    # if Print: print rawtext
                    if yy + f3 < e1[1] :
                      yy += f3/vspace
                      time.sleep(0.0002)
                      try:
                        sc_temp  = screen.blit(ttt, (xx,yy))
                      except pygame.error as e:
                        if Print: print "pg:" , e
                        sc_temp = ncir
                      sct.append(sc_temp)
                      yy += f3/vspace
  
                    # if Print: print "\n\t\tcond met"
                    cond = True
              # texx.append(tex2)
          else:
              rawtext = clipa
              # if Print: print "r=" , rawtext
              cond = False
              timmm = time.time()
              while not cond and time.time() - 0.05 < timmm :
                yy += f3/vspace
                wid = fo30.size(rawtext)[0]
                if wid > scl0[0] - xx:
                  bre = int(((scl0[0] - xx) * len(rawtext) ) / wid)
                  last_space = rawtext.rfind(' ', 0, bre)
                  # if Print: print wid, sx, xx, len(rawtext), bre, last_space
                  if last_space != -1:
                    ttt = fo30.render(rawtext[:last_space], 1 , white)
                    # if Print: print rawtext[:last_space]
                    rawtext = rawtext[last_space+1:]
                    if yy + f3 < e1[1] :
                      yy += f3/vspace
                      time.sleep(0.0002)
                      try:
                        sc_temp  = screen.blit(ttt, (xx,yy))
                      except pygame.error as e:
                        if Print: print "pg:" , e
                        sc_temp = ncir
                      sct.append(sc_temp)
                      yy += f3/vspace
                  else:
                    ttt = fo30.render(rawtext[:bre-2], 1 , white)
                    # if Print: print rawtext[:last_space]
                    rawtext = rawtext[bre-2:]
                    if yy + f3 < e1[1] :
                      yy += f3/vspace
                      time.sleep(0.0002)
                      try:
                        sc_temp  = screen.blit(ttt, (xx,yy))
                      except pygame.error as e:
                        if Print: print "pg:" , e
                        sc_temp = ncir
                      sct.append(sc_temp)
                      yy += f3/vspace
  
                else:
                    # if Print: print wid, sx, xx
                    ttt = fo30.render(rawtext, 1 , white)
                    # if Print: print rawtext
                    if yy + f3 < e1[1] :
                      yy += f3/4
                      time.sleep(0.0002)
                      try:
                        sc_temp  = screen.blit(ttt, (xx,yy))
                      except pygame.error as e:
                        if Print: print "pg:" , e
                        sc_temp = ncir
                      sct.append(sc_temp)
                      yy += f3/(vspace/2)
                    # if Print: print "\n\t\tcond met"
                    cond = True
                    # if Print: print "\n\t\tcond met"
                    break
    
              time.sleep(0.001)

          # create black rectangles beneath some permanent texts so that 
          # scrolled text will go behind it and not interfere with the texts 
          rc2c = pygame.draw.rect(screen, black, (0, e1[1], sx, f0+1) ) 
          roao = pygame.draw.rect(screen, black, (0, e2[1], sx, f0+1) ) 
          rapp = pygame.draw.rect(screen, black, (0, e3[1], sx, f0+1) ) 
  
          time.sleep(0.001)

          if c2c:
            dc2c  = screen.blit(text3, e1 )
          else:
            ec2c  = screen.blit(text2, e1 )
  
          if oao:
            doao  = screen.blit(text5, e2 )
          else:
            eoao  = screen.blit(text4, e2 )
  
          if app:
            dapp  = screen.blit(text10, e3)
          else:
            eapp  = screen.blit(text09, e3)
  
          if to_app:
            don   = screen.blit(text11, d1)
  
          if app:
            app2 = fon0.render(app_chr, 1, white)
            app1 = screen.blit(app2, a1)
            rapp1= pygame.draw.rect(screen, blue, app1 ) 
            app1 = screen.blit(app2, a1)
          
          if onn:
            onn1 = screen.blit(text12, o1)
          else:
            onn2 = screen.blit(text13, o1)

          if cagr and not app:
            # if cagr_t <= 0 :
            if c_gettime:
              cs_type = screen.blit(text16,(d1[0] - 5, d1[1] - (f0+1) ) )
              rcs_type= pygame.draw.rect(screen, black, cs_type)
              cs_type = screen.blit(text16,(d1[0] - 5, d1[1] - (f0+1) ) )
              c_char  =  fon0.render("t: " + c_gettime_char, 1, white)
              cs_char = screen.blit(c_char,(d1[0]-30,d1[1]-(2*f0+1) ))
              rcs_char= pygame.draw.rect(screen, black, cs_char)
              cs_char = screen.blit(c_char,(d1[0]-30,d1[1]-(2*f0+1) ))
            else:
              cs_time = screen.blit(text15,(d1[0] - 5, d1[1] - (f0+1) ) )
              rcs_time= pygame.draw.rect(screen, black, cs_time)
              cs_time = screen.blit(text15,(d1[0] - 5, d1[1] - (f0+1) ) )

            c_str  =  format(cagr_m[0], '.3f') + "  " +  format(cagr_n[0], '.3f') + "   " + str(cagr_t) + "   " + format(value, '.3f')
            c_ren  =  fon0.render(c_str, 1, white)
            c_scr  =  screen.blit(c_ren, (a1[0] - 60, a1[1] - (f0+1) ))
            rc_scr =  pygame.draw.rect(screen, blue, c_scr ) 
            c_scr  =  screen.blit(c_ren, (a1[0] - 60, a1[1] - (f0+1) ))

          # cyan circles to clear the primary and secondary clpboards respectively
          pcir = pygame.draw.circle(screen, cyan, (3,3), 4)
          scir = pygame.draw.circle(screen, cyan, (sx-3,3), 4)
          cir1  = pygame.draw.circle(screen, cyan, (sx-3, int(r1[1]+f0/2)), 4)
          cir2  = pygame.draw.circle(screen, cyan, (sx-3, int(r2[1]+f0/2)), 4)
  
          soao  = screen.blit(text6, s1 )        
          rst1  = screen.blit(text8, r1 )
          rst2  = screen.blit(text8, r2 )
  
          rst3  = screen.blit(text8, r3 )
          drst3 = pygame.draw.rect(screen, black, rst3 )
          rst3  = screen.blit(text8, r3 )
  
          clr1  = screen.blit(text7, c1 )
          clr2  = screen.blit(text7, c2 )
  
          len1, len2 = '[' + str(len(var10)) + ']', '[' + str(len(var20)) +']'
          l1    = fon0.render(len1 , 10, cyan)
          le1   = screen.blit(l1, (c1[0] + 30, c1[1]) )
          
          l2    = fon0.render(len2 , 10, cyan)
          le2   = screen.blit(l2, (c2[0] + 30, c2[1]) )
  
          exx1  = screen.blit(text1, ex1 )
          if sx > x_ex + mor:
            valar = screen.blit(text14, vm )
          if get_name:
            nam   = screen.blit(text17, ( sx-120, r2[1] - f0*1.5 ) )
            namf  = fon0.render(save_name, 10, cyan)
            namm  = screen.blit(namf, ( sx-90, r2[1] - f0*1.5 ) )

          if load_name:
            names = []
            vspace = 3
            xx, yy = sx - 120 + cl1[0] + sdev1x, cl1[1] + sdev1y
            loads  = screen.blit(text18, (xx,yy))
            rloads = pygame.draw.rect(screen, black, loads ) 
            loads  = screen.blit(text18, (xx,yy))

            yy += f0/(vspace/5)
            for dis in name_list:
              nfont   = fon0.render(dis, 10, cyan)
              disfont = screen.blit(nfont, (xx,yy))
              rdisfont = pygame.draw.rect(screen, black, disfont ) 
              disfont  = screen.blit(nfont, (xx,yy))
              
              names.append(disfont)
              yy += f0/(vspace/4)

          pygame.display.flip()
          # if Print: print time.time()

        # pygame.event.set_blocked(pygame.KEYDOWN)
        # pygame.event.set_blocked(pygame.KEYUP)
        # cha = False


        # if last_game:
        pygame.event.pump()
 
        # pygame.event.pump()
        # checks if the variables have changed.. if yes, turn cha on to refresh display in next loop
        clip_now = pyperclip.paste()
        if last_clip != clip_now:
          clipa = manage_nl(clip_now)
          cha = True
          # if Print: print "kidhar", cha
        last_clip = clip_now

        if last_sclip != s_cl:
          cha = True
          sclipa = manage_nl(s_cl)
          if s_cl == "":
            scl0 = (sx,3)
          else:
            scl0 = (int(sx*clip_div), 3)
          last_sclip = s_cl
        # if Print: print "here"

        # if last_var10 != var10 or last_var20 != var20:
        #   cha = True
        #   # if Print: print "idhar"
        # last_var10 = var10
        # last_var20 = var20
        if toKill:
          sys.exit()

        for event in pygame.event.get():
            cha = True # any event on pygame's display will turn 'cha' True for faster response
            if event.type == pygame.QUIT:
                toKill = True
                sys.exit()
                # quit()
            pos = pygame.mouse.get_pos() # gets mouse position as tuple
            # if Print: print "e:", event
            if event.type == 5: # scroll event 

              tsend = (time.time() - tim) 
              #  tsend keeps track of loop time to adjust sensitivity of scroll porportionally
              # cha = True
              sens, fsens = (tsend**0.333)*100, 0.8  # scroll sensitivity and font change sensitivity
              # sens, fsens = 6, tsend*80 # sensitivity
              # if Print: print 'p:', pos, cl1[1], cl2[1]

              if pos[1] >= 5+c1[1] and pos[1] < 5+c2[1] and (len(var10) > 0 or load_name):
                  # changes font size when control is pressed, else just scrolls
                  # font size is constrained between 5 and 50
                  # scrolls sideways if alt is pressed while vertical scrolling
                  # event buttons 4,5,6,7 corresponds to scrolls:
                  # up / down / right / left

                if event.button == 4:
                  if con:
                      f1 += fsens
                      f1 = min(50, f1)
                      fo10 = pygame.font.SysFont(fon,int(f1))
                      fo11 = pygame.font.SysFont(fon,int(f1) - 1)
                  elif alt:
                      sdev1x += sens
                  else:
                      sdev1y += sens
                  # if Print: print "sup1"
                elif event.button == 5:
                  if con:
                      f1 -= fsens
                      f1 = max(5, f1)
                      fo10 = pygame.font.SysFont(fon,int(f1))
                      fo11 = pygame.font.SysFont(fon,int(f1) - 1)
                  elif alt:
                      sdev1x -= sens
                  else:
                      sdev1y -= sens
                elif event.button == 6:
                  sdev1x += sens
                elif event.button == 7:
                  sdev1x -= sens


              elif pos[1] >= 5+c2[1] and len(var20) > 0:
                if event.button == 4:
                  if con:
                      f2 += fsens
                      f2 = min(50, f2)
                      fo20 = pygame.font.SysFont(fon,int(f2))
                      fo21 = pygame.font.SysFont(fon,int(f2) - 1)
                  elif alt:
                      sdev2x += sens
                  else:
                      sdev2y += sens
                elif event.button == 5:
                  if con:
                      f2 -= fsens
                      f2 = max(5, f2)
                      fo20 = pygame.font.SysFont(fon,int(f2))
                      fo21 = pygame.font.SysFont(fon,int(f2) - 1)
                  elif alt:
                      sdev2x -= sens
                  else:
                      sdev2y -= sens
                if event.button == 6:
                    sdev2x += sens
                elif event.button == 7:
                    sdev2x -= sens

              elif pos[1] < 5+c1[1] :
                if event.button == 4:
                  if con:
                    if clip_now != "" and pos[0] <= scl0[0]:
                      f3 += fsens
                      f3 = min(50, f3)
                      fo30 = pygame.font.SysFont(fon,int(f3))
                      fo31 = pygame.font.SysFont(fon,int(f3) - 1)

                    elif s_cl != "" and pos > scl0[0]:
                      f4 += fsens
                      f4 = min(50, f4)
                      fo40 = pygame.font.SysFont(fon,int(f4))
                      fo41 = pygame.font.SysFont(fon,int(f4) - 1)

                  elif alt and pos[0] > scl0[0] and s_cl != "":
                      sdev4x += sens
                  elif pos[0] > scl0[0] and s_cl != "":
                      sdev4y += sens
                  elif alt and pos[0] <= scl0[0] and clip_now != "":
                      sdev3x += sens
                  elif clip_now != "":
                      sdev3y += sens
                
                elif event.button == 5:
                  if con:
                    if clip_now != "" and pos[0] <= scl0[0]:
                      f3 -= fsens
                      f3 = max(5, f3)
                      fo30 = pygame.font.SysFont(fon,int(f3))
                      fo31 = pygame.font.SysFont(fon,int(f3) - 1)

                    elif s_cl != "" and pos > scl0[0]:
                      f4 -= fsens
                      f4 = max(5, f4)
                      fo40 = pygame.font.SysFont(fon,int(f4))
                      fo41 = pygame.font.SysFont(fon,int(f4) - 1)

                  elif alt and pos[0] > scl0[0] and s_cl != "":
                      sdev4x -= sens
                  elif pos[0] > scl0[0] and s_cl != "":
                      sdev4y -= sens
                  elif alt and pos[0] <= scl0[0] and clip_now != "":
                      sdev3x -= sens
                  elif clip_now != "":
                      sdev3y -= sens

                if event.button == 6:
                  if pos[0] > scl0[0] and s_cl != "":
                    sdev4x += sens
                  elif pos[0] <= scl0[0] and clip_now != "":
                    sdev3x += sens
                elif event.button == 7:
                  if pos[0] > scl0[0] and s_cl != "":
                    sdev4x -= sens
                  elif pos[0] <= scl0[0] and clip_now != "":
                    sdev3x -= sens

            elif event.type==pygame.VIDEORESIZE:
              # when window is resized 
              # if Print: print 'h' #, pygame.VIDEORESIZE#, event.dict['size']
              time.sleep(0.08)
              try:
                screen=pygame.display.set_mode(event.dict['size'],pygame.RESIZABLE)
                # screen=pygame.display.set_mode(event.dict['size'], pygame.RESIZABLE | pygame.HWSURFACE | pygame.DOUBLEBUF)
              except :
              # except exception as e:
                if Print: print "err:", e         
              # screen=pygame.display.set_mode(event.dict['size'],pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE)
              # screen.blit(pygame.transform.scale(pic,event.dict['size']),(0,0))
              time.sleep(0.005)
              background = pygame.Surface(screen.get_size())    
              background = background.convert()
              background.fill((250,250,250))
              background.fill((0,0,0))
              screen.blit(background, (0,0))
              pygame.display.flip()
              # get screen size 
              sx = screen.get_size()[0]
              sy = screen.get_size()[1]

              start1y    = int(sy*v_div[0])
              start2y    = int(sy*v_div[1])                               # y of second pane
              start1y    = constrain(start1y,40,start2y)
              start2y    = constrain(start2y,start1y+(2*(f0+1)), sy-(3*(f0+1)) )

              e1, e2, e3 = (x_en, start1y), (x_en , start2y), (x_en, sy-17)      # x,y of the three Enables
              c1, c2     = (x_cl, start1y), (x_cl, start2y)                      # x,y of the two clears
              r1, r2, r3 = (x_rs, start1y), (x_rs, start2y), (sx-16, start1y-20) # x,y of the three resets
              a1, vm     = (150, sy-17),    (x_ex + 200, start1y)                # x,y of append and (vm)
              s1, ex1    = (x_ex,start2y),  (x_ex+25,start1y)                    # x,y of start oao and exit
              o1, d1     = (x_ex, start1y), (sx-30, sy-17)                       # x,y of 
              
              # clip_div = 0.6            # how much % of x should primary and secondary clipboard display take
              cl1 = (20,start1y + 15)   # starting point of clipboard list
              cl2 = (20,start2y + 15)   # starting point of one after other list
              cl0, scl0 = (3, 3), (sx*clip_div, 3)  # starting point of primary and econdary clipboard respectively

              if s_cl == "":
                scl0 = (sx, 3)
              else:
                scl0 = (int(sx*clip_div), 3)

              if Print: print "Size is", screen.get_size(), '\tsy is ', sx
              cha = True
              pygame.display.flip()

            # if Print: print event.type, "\t\t", event.button

            if (1,0,0) == pygame.mouse.get_pressed():
                # collidepoint inidicates if mouse position lies in the surface of corresponding object
                # if Print: print "click", pos
                # cha = True
                # reset resets the scrolls 
                if not last_click:
                  just_clicked = True
                else:
                  just_clicked = False
                last_click = True

                if rst1.collidepoint(pos):
                  sdev1x = 0
                  sdev1y = 0
                elif rst2.collidepoint(pos):
                  sdev2x = 0
                  sdev2y = 0
                elif rst3.collidepoint(pos):
                  sdev3x = 0
                  sdev3y = 0
                  sdev4y = 0
                  sdev4x = 0
                elif pcir.collidepoint(pos) and clip_now != "": # clears primary clipboard
                  un = []
                  un.append("from clip deleted ")
                  un.append(pyperclip.paste())
                  undo.append(un)
                  redo = []
                  redo.append(un)                  
                  if len(undo) > ur_limit():
                    undo.pop(0)
                  pyperclip.copy('')
                  appended = ""
                  # if Print: print un
                  clip_now = pyperclip.paste()

                elif s_cl != "" and rcli2.collidepoint(pos):
                  if not drag and just_clicked:
                    drag = True
                elif cir1.collidepoint(pos):
                  if not drag1 and not drag2 and just_clicked:
                    drag1 = True
                elif cir2.collidepoint(pos):
                  if not drag2 and not drag1 and just_clicked:
                    drag2 = True

                elif scir.collidepoint(pos) and s_cl != "": # clears secondary clipboard
                  un = []
                  un.append("from sec deleted ")
                  un.append(s_cl)
                  undo.append(un)
                  redo = []
                  redo.append(un)
                  if len(undo) > ur_limit():
                    undo.pop(0)
                  s_cl =  ''
                  # if Print: print un
                if c2c and not shi: # when click to copy is enabled , 
                  for jj in range(len(sc1)):
                    sc4 = sc1[jj]
                    try:
                      j1 = len(sc4)
                      if j1 > 0:
                        jk = len(sc4[0])
                        for j2 in range(j1):
                          if sc4[j2].collidepoint(pos):
                            if con:
                              s_cl = var10[jj]
                            else:
                              pyperclip.copy(var10[jj])
                            break
                    except TypeError, e: # if there is an array in the element of sc1
                      if sc1[jj].collidepoint(pos):
                        if con:
                          s_cl = var10[jj]
                        else:
                          pyperclip.copy(var10[jj])
                if load_name:
                  for na in range(len(names)):
                    if names[na].collidepoint(pos):
                      load_data(name_list[na])
                      load_name = False
                      sdev1x, sdev1y = 0,0

                if drag : # changing the division of display spaces of primary and secondary clipboard
                    clip_div = pos[0]/sx
                    scl0 = (int(sx*clip_div), 3)
                    # if Print: print "dragging"

                if drag1: # changing the display space of clipboard list
                  pyy        = constrain(pos[1], 40, sy*v_div[1]-(3*(f0+1)))
                  v_div      = (pyy / sy, v_div[1])
                  start1y    = int(sy*v_div[0])
                  start1y    = constrain(start1y,40,start2y-(2*(f0+1)))

                  e1, e2, e3 = (x_en, start1y), (x_en, start2y), (x_en, sy-17)      # x,y of the three Enables
                  c1, c2     = (x_cl, start1y), (x_cl, start2y)                      # x,y of the two clears
                  r1, r2, r3 = (x_rs, start1y), (x_rs, start2y), (sx-16, start1y-20) # x,y of the three resets
                  a1, vm     = (150, sy-17),    (x_ex + 200, start1y)                # x,y of append and (vm)
                  s1, ex1    = (x_ex,start2y),  (x_ex+25,start1y)                    # x,y of start oao and exit
                  o1, d1     = (x_ex, start1y), (sx-30, sy-17)                       # x,y of 
                  
                  cl1 = (20,start1y + 15) # starting point of clipboard list
                  cl2 = (20,start2y + 15) # starting point of one after other list
                  cl0 = (3, 3)            # starting point of primary and econdary clipboard respectively
                  # if Print: print "dragging1"


                if drag2: # changing the display space for one after other mode
                  pyy        = constrain(pos[1],  sy*v_div[0], sy - (2*(f0+1)))
                  v_div      = (v_div[0] , pyy/ sy)
                  start2y    = int(sy*v_div[1])                               
                  start2y    = constrain(start2y,start1y+(2*(f0+1)), sy-(3*(f0+1)) )

                  e1, e2, e3 = (x_en, start1y), (x_en, start2y), (x_en, sy-17)      # x,y of the three Enables
                  c1, c2     = (x_cl, start1y), (x_cl, start2y)                      # x,y of the two clears
                  r1, r2, r3 = (x_rs, start1y), (x_rs, start2y), (sx-16, start1y-20) # x,y of the three resets
                  a1, vm     = (150, sy-17),    (x_ex + 200, start1y)                # x,y of append and (vm)
                  s1, ex1    = (x_ex,start2y),  (x_ex+25,start1y)                    # x,y of start oao and exit
                  o1, d1     = (x_ex, start1y), (sx-30, sy-17)                       # x,y of 
                  
                  cl1 = (20,start1y + 15) # starting point of clipboard list
                  cl2 = (20,start2y + 15) # starting point of one after other list
                  cl0 = (3, 3)            # starting point of primary and econdary clipboard respectively
                  # if Print: print "dragging2"


                if shi: # when shift is pressed, for cagr
                  for jj in range(len(sc1)):
                    sc4 = sc1[jj]
                    try:
                      j1 = len(sc4)
                      if j1 > 0:
                        jk = len(sc4[0])
                        for j2 in range(j1):
                          if sc4[j2].collidepoint(pos):
                            strr = var11[jj][j2]
                            if hasNumbers(strr):
                              width = pos[0] - sdev1x - cl1[0]
                              wid = fo11.size(strr)[0]
                              # if Print: print width, wid
                              le  = (int(len(strr)*width/wid))
                              # if Print: print strr[le]
                              # extracting nearest numbers from the clicked part of  text
                              if not strr[le].isdigit() and strr[le] != '.' and strr[le] != '-':
                                  ind = le
                                  ind1,ind2 = le,le
                                  while ind1 > 0 or ind2 < len(strr): # crawl back and forth till the nearest number is completely found
                                      if ind1 > 0:
                                          dig1 = strr[ind1]
                                          if dig1.isdigit() or dig1 == '-' or dig1 == '.':
                                              le = ind1
                                              break
                                      if ind2 < len(strr):
                                          dig2 = strr[ind2]
                                          if dig2.isdigit() or dig2 == '-' or dig2 == '.':
                                              le = ind2
                                              break
                                      ind1 -= 1
                                      ind2 += 1                     

                              in1, in2 = le,le
                            
                              while in1 > 0:
                                if not strr[in1].isdigit() and not strr[in1] == '-'and not strr[in1] == '.' and not strr[in1] == ',' :
                                  break
                                in1 -= 1
                              while in2 < len(strr) :
                                if not strr[in2].isdigit() and not strr[in2] == '-' and not strr[in2] == '.' and not strr[in2] == ',':
                                  break
                                in2 += 1
                              if not strr[in1].isdigit() and strr[in1] != '-':
                                in1 += 1
                              if Print: print "num:", strr[in1:in2]

                              cagr = True
                              try:
                                cagr_m = (float(strr[in1:in2].replace(',','')), jj, j2, in1) # remove commas in the string if any
                              except ValueError as e:
                                if Print: print "cannot be converted"
                                cagr_m = (0,-1,-1,-1)
 
                              if (cagr_m[1] == cagr_n[1] != -1 and cagr_m[2] == cagr_n[2] != -1):
                                cagr_t = var11[cagr_m[1]][cagr_m[2]][cagr_m[3]:cagr_n[3]].count("    ")
                                if Print: print cagr_m[0], cagr_n[0], cagr_t
                              else:
                                # cagr_t = -1
                                if Print: print "time not found"
                              if cagr_m[0] > 0 and cagr_t > 0:
                                value = get_cagr(cagr_m[0], cagr_n[0], cagr_t)
                                if Print: print value
                              else:
                                value = 0
                                if Print: print "improper values"
                            else:
                              if Print: print "no number detected"
                            break
                    except TypeError, e:
                      if sc1[jj].collidepoint(pos):
                        strr = var11[jj]
                        if hasNumbers(strr):
                            width = pos[0] - sdev1x - cl1[0]
                            wid = fo10.size(strr)[0]
                            # if Print: print width, wid
                            le  = (int(len(strr)*width/wid))
                            # if Print: print strr[le]
                            if not strr[le].isdigit() and strr[le] != '.' and strr[le] != '-':
                                ind = le
                                ind1,ind2 = le,le
                                while ind1 > 0 or ind2 < len(strr):
                                    if ind1 > 0:
                                        dig1 = strr[ind1]
                                        if dig1.isdigit() or dig1 == '-' or dig1 == '.':
                                            le = ind1
                                            break
                                    if ind2 < len(strr):
                                        dig2 = strr[ind2]
                                        if dig2.isdigit() or dig2 == '-' or dig2 == '.':
                                            le = ind2
                                            break
                                    ind1 -= 1
                                    ind2 += 1                     

                            in1, in2 = le,le
                            
                            while in1 > 0:
                              if not strr[in1].isdigit() and not strr[in1] == '-'and not strr[in1] == '.' and not strr[in1] == ',':
                                break
                              in1 -= 1
                            while in2 < len(strr) :
                              if not strr[in2].isdigit() and not strr[in2] == '-' and not strr[in2] == '.' and not strr[in2] == ',':
                                break
                              in2 += 1

                            if not strr[in1].isdigit() and strr[in1] != '-':
                              in1 += 1
                            if Print: print "num:", strr[in1:in2]
                            cagr = True
                            try:
                              cagr_m = (float(strr[in1:in2].replace(',','')), jj, -1, in1) # remove commas in the string if any
                            except ValueError as e:
                              if Print: print "cannot be converted"
                              cagr_m = (0,-1,-1,-1)
                            if (cagr_m[1] == cagr_n[1] != -1 and cagr_m[2] == cagr_n[2] == -1):
                              cagr_t = var11[cagr_m[1]][cagr_m[3]:cagr_n[3]].count("    ")
                              if Print: print cagr_m[0], cagr_n[0], cagr_t
                            else:
                              # cagr_t = -1
                              if Print: print "time not found"
                            if cagr_m[0] > 0 and cagr_t > 0:
                              value = get_cagr(cagr_m[0], cagr_n[0], cagr_t)
                              if Print: print value
                            else:
                              value = 0
                              if Print: print "improper values"
                        else:
                            if Print: print "no number detected"


 
                ldown = True
            
            if ldown and (0,0,0) == pygame.mouse.get_pressed(): # when left click released
                ldown = False
                last_click = False                
                if Print: print "released"
                if sx > x_ex + mor and valar.collidepoint(pos): 
                  morghuled.append(var10)
                  morghuled.append(var11)
                  morghuled.append(var20)
                  morghuled.append(var21)
                  morghuled.append(pyperclip.paste())
                  morghuled.append(s_cl)
                  morghuled.append(cagr_m)
                  morghuled.append(cagr_n)
                  morghuled.append(cagr_t)
                  morghuled.append(value)
                  morghuled.append(c_gettime_char)
                  morghuled.append(cagr)

                  # Clicking Valar Morghulis will kill all the values
                  # Fortunately, you can bring all of them back due to grace of Lord of the Light

                  un = []
                  un.append("Valar Morghuled")
                  un.append([])
                  undo.append(un)
                  if len(undo) > ur_limit():
                    undo.pop(0)
                  
                  var10 = []
                  var11 = []
                  var20 = []
                  var21 = []
                  s_cl  = ""
                  cagr_m = (0,0,0,0)
                  cagr_n = (0,0,0,0)
                  cagr_t = 0
                  value  = 0
                  c_gettime_char = ''
                  cagr = False
                  c_gettime = False
                  pyperclip.copy('')

                if exx1.collidepoint(pos): # exit
                    toKill = True
                    cap = commands.getoutput("xdotool key 'Escape'")
                    # the keylogger function being in different thread, and called
                    # only when there is a key press, one is imulated by pressing Escape
                    sys.exit()
                    # quit()  

                if drag:
                  drag = False
                if drag1:
                  drag1 = False
                if drag2:
                  drag2 = False

                if not c2c and ec2c.collidepoint(pos):
                    # if Print: print "click to copy enabled"
                    c2c = True
                elif c2c and dc2c.collidepoint(pos):
                    # if Print: print "click to copy disabled"
                    c2c = False
            
                if not oao and eoao.collidepoint(pos):
                    # if Print: print "1 after other enabled"
                    oao = True
                elif oao and doao.collidepoint(pos):
                    # if Print: print "1 after other disabled"
                    oao = False
                
                if oao and soao.collidepoint(pos): # first element of one after other list will be copied into clipboard
                                                   # so that you can resuming using the one after other mode
                  if len(var20)>0:
                    pyperclip.copy(var20[0]) 
                    # first element of click to copy list is made
                    # if Print: print "started"
                  # else:
                    # print"empty"
                # elif not oao and soao.collidepoint(pos):
                    # to_restart = True # for trial basis
                if cagr:
                  if c_scr.collidepoint(pos):
                    pyperclip.copy(format(value,'.3f'))
                  if not c_gettime and cs_time.collidepoint(pos): # enable gettime
                    c_gettime = True               # gettime is when you manually want to enter time for calculating cagr
                  elif c_gettime and cs_type.collidepoint(pos): # when you finished entering time and click on type..
                    if Print: print c_gettime_char
                    c_gettime = False
                    if c_gettime_char != "":
                      # if c_gettime_char.count('/') == 1: 
                      # time entered can be 1/12 or 3.5/25.5, it will automatically converted into corresponding decimal value
                      if '/' in c_gettime_char:
                        fra = c_gettime_char.split('/')
                        c_gettime_char = format(float(fra[0])/float(fra[1]), '.3f')
          
                      cagr_t = float(c_gettime_char)
                      if cagr_m[0] > 0 and cagr_t > 0:
                        value = get_cagr(cagr_m[0], cagr_n[0], cagr_t)
                        if Print: print value
                      else:
                        value = 0
                        if Print: print "improper values"   

                if onn and onn1.collidepoint(pos):
                  # if Print: print "always on top turned off"
                  onn = False
                  # if Print: print onn2
                  last_onn = True
                elif not onn and onn2.collidepoint(pos):
                  # if Print: print "always on top turned on"
                  onn = True
                  # if Print: print onn


                if to_app and  don.collidepoint(pos):
                    to_app = False
                    # if Print: print "final to append:", app_chr
                    # Finalizes characters to append in the append mode

                if not app and eapp.collidepoint(pos):
                    # if Print: print "Append enabled"
                    app = True
                    to_app = True
                elif app and dapp.collidepoint(pos):
                    # if Print: print "Append disabled"
                    to_app = False
                    app_chr = ""
                    app = False
                    appended = ""

                if clr2.collidepoint(pos) or le2.collidepoint(pos):
                  if len(var20) > 0:
                    un = []
                    un.append("from var2 deleted all")
                    un.append(var20)
                    undo.append(un)
                    redo = []
                    # redo.append(un)
                    if len(undo) > ur_limit():
                      undo.pop(0)
                  var20 = []
                  var21 = []
                  # if Print: print "Cleared var2"
                if clr1.collidepoint(pos) or le1.collidepoint(pos):
                  if len(var10) > 0:
                    un = []
                    un.append("from var1 deleted all")
                    un.append(var10)
                    undo.append(un)
                    redo = []
                    # redo.append(un)
                    if len(undo) > ur_limit():
                      undo.pop(0)
                  var10 = []
                  var11 = []
                  # if Print: print "Cleared var1"

            if (0,0,1) == pygame.mouse.get_pressed():
                rdown = True
                if shi: # when shift is pressed, for cagr
                  for jj in range(len(sc1)):
                    sc4 = sc1[jj]
                    try:
                      j1 = len(sc4)
                      if j1 > 0:
                        jk = len(sc4[0])
                        for j2 in range(j1):
                          if sc4[j2].collidepoint(pos):
                            strr = var11[jj][j2]
                            if hasNumbers(strr):
                              width = pos[0] - sdev1x - cl1[0]
                              wid = fo11.size(strr)[0]
                              # if Print: print width, wid
                              le  = (int(len(strr)*width/wid))
                              # find the index of character which was clicked
                              # if Print: print strr[le]
                              if not strr[le].isdigit() and strr[le] != '.' and strr[le] != '-':
                                  ind = le
                                  ind1,ind2 = le,le
                                  while ind1 > 0 or ind2 < len(strr):
                                    # running loop to get the number which was clicked or nearest to the clicked point
                                      if ind1 > 0:
                                          dig1 = strr[ind1]
                                          if dig1.isdigit() or dig1 == '-' or dig1 == '.':
                                              le = ind1
                                              break
                                      if ind2 < len(strr):
                                          dig2 = strr[ind2]
                                          if dig2.isdigit() or dig2 == '-' or dig2 == '.':
                                              le = ind2
                                              break
                                      ind1 -= 1
                                      ind2 += 1                     

                              in1, in2 = le,le
                              
                              while in1 > 0:
                                if not strr[in1].isdigit() and not strr[in1] == '-'and not strr[in1] == '.' and not strr[in1] == ',':
                                  break
                                in1 -= 1
                              while in2 < len(strr) :
                                if not strr[in2].isdigit() and not strr[in2] == '-' and not strr[in2] == '.' and not strr[in2] == ',':
                                  break
                                in2 += 1
                              if not strr[in1].isdigit() and strr[in1] != '-':
                                in1 += 1
                              if Print: print "num:", strr[in1:in2]
                              cagr = True
                              try:
                                cagr_n = (float(strr[in1:in2].replace(',','')), jj, j2, in1)
                              except ValueError as e:
                                if Print: print "cannot be converted"
                                cagr_n = (0,-1,-1,-1)
                              if (cagr_m[1] == cagr_n[1] != -1 and cagr_m[2] == cagr_n[2]):
                                cagr_t = var11[cagr_m[1]][cagr_m[2]][cagr_m[3]:cagr_n[3]].count("    ")
                                # find time interval by calculating number of tabs in between the numbers
                                # good for when the data is tab-seperated i.e. has been copied from excel/sheets/tables
                                if Print: print cagr_m[0], cagr_n[0], cagr_t
                                # cagr_m and cagr_n are tuples(a,b,c,d) corresponding to the two numbers 
                                # and store value and indices in array for of the values to find the number
                                # of tabs in between 

                              else:
                                if Print: print "time not found"
                                # cagr_t = -1
                              if cagr_m[0] > 0 and cagr_t > 0:
                                value = get_cagr(cagr_m[0], cagr_n[0], cagr_t)
                                # finding value of CAGR in %
                                if Print: print value
                              else:
                                value = 0  
                                if Print: print "improper values"
                            else:
                              if Print: print "no number detected"
                            break
                    except TypeError, e:
                      if sc1[jj].collidepoint(pos):
                        strr = var11[jj]
                        if hasNumbers(strr):
                            width = pos[0] - sdev1x - cl1[0] # total width of the line
                            wid = fo10.size(strr)[0]
                            # if Print: print width, wid
                            le  = (int(len(strr)*width/wid))
                            # find the index of character which was clicked
                            # if Print: print strr[le]
                            if not strr[le].isdigit() and strr[le] != '.' and strr[le] != '-' :
                                ind = le
                                ind1,ind2 = le,le
                                while ind1 > 0 or ind2 < len(strr):
                                    # running loop to get the number which was clicked or nearest to the clicked point
                                    if ind1 > 0:
                                        dig1 = strr[ind1]
                                        if dig1.isdigit() or dig1 == '-' or dig1 == '.':
                                            le = ind1
                                            break
                                    if ind2 < len(strr):
                                        dig2 = strr[ind2]
                                        if dig2.isdigit() or dig2 == '-' or dig2 == '.':
                                            le = ind2
                                            break
                                    ind1 -= 1
                                    ind2 += 1                     

                            in1, in2 = le,le
                            
                            while in1 > 0:
                              if not strr[in1].isdigit() and not strr[in1] == '-'and not strr[in1] == '.' and not strr[in1] == ',':
                                break
                              in1 -= 1
                            while in2 < len(strr) :
                              if not strr[in2].isdigit() and not strr[in2] == '-' and not strr[in2] == '.' and not strr[in2] == ',':
                                break
                              in2 += 1
                            if not strr[in1].isdigit() and strr[in1] != '-':
                              in1 += 1
                            if Print: print "num:", strr[in1:in2]
                            cagr = True
                            if Print: print cagr_m[0], cagr_n[0], cagr_t
                            # cagr_m and cagr_n are tuples(a,b,c,d) corresponding to the two numbers 
                            # and store value and indices in array for of the values to find the number
                            # of tabs in between 
                            try:
                              cagr_n = (float(strr[in1:in2].replace(',','')), jj, -1, in1)
                            except ValueError as e:
                              if Print: print "cannot be converted"
                              cagr_m = (0,-1,-1,-1)
                            if (cagr_m[1] == cagr_n[1] != -1 and cagr_m[2] == cagr_n[2] == -1):
                              cagr_t = var11[cagr_m[1]][cagr_m[3]:cagr_n[3]].count("    ")
                              # finding time interval by calculating number of tabs in between the numbers
                              # good for when the data is tab-seperated i.e. has been copied from excel/sheets/tables

                              if Print: print cagr_m[0], cagr_n[0], cagr_t
                            else:
                              # cagr_t = -1
                              if Print: print "time not found"
                            if cagr_m[0] > 0 and cagr_t > 0:
                              value = get_cagr(cagr_m[0], cagr_n[0], cagr_t)
                                # finding value of CAGR in %
                              if Print: print value
                            else:
                              value = 0
                              if Print: print "improper values"
                        else:
                            if Print: print "no number detected"


            if (0,1,0) == pygame.mouse.get_pressed(): 
                # middle click
                if c2c:
                  for jj in range(len(sc1)):
                    sc4 = sc1[jj]
                    try: # if the element is an array
                      j1 = len(sc4)
                      if j1 > 0:
                        jk = len(sc4[0])
                        for j2 in range(j1):
                          if sc4[j2].collidepoint(pos):
                              s_cl = var10[jj]
                              break
                    except TypeError, e: # if the element is not an array
                      if sc1[jj].collidepoint(pos):
                          s_cl = var10[jj]

          
            if rdown and (0,0,0) == pygame.mouse.get_pressed(): # when right click released
              rdown = False
              if c_gettime:
                if cs_type.collidepoint(pos):
                  cagr = False
              else:
                if cs_time.collidepoint(pos):
                  cagr = False
              if c1[1] < pos[1] < c2[1] and not shi:
                var0 = deepcopy(var11) 
                if c2c:
                  for jj in range(len(sc1)):
                    sc3 = sc1[jj]
                    try: # if the element is an array
                      j1 = len(sc3)
                      if j1 > 0:
                        jk = sc3[0][1]
                        for j2 in range(j1):
                          if sc3[j2].collidepoint(pos):
                            # ind = var11.index(var0[jj])
                            ind = jj
                            # if Print: print ind
                            un = []
                            un.append("from var1 deleted " + str(ind))
                            un.append(var10[ind])
                            undo.append(un)
                            redo = []
                            # redo.append(un)
                            var10.pop(ind)
                            var11.pop(ind)
                            if len(undo) > ur_limit():
                              undo.pop(0)
                            break
                    except TypeError, e: # if the element is not an array
                      if sc3.collidepoint(pos):
                        ind = var11.index(var0[jj])
                        # if Print: print ind
                        un = []
                        un.append("from var1 deleted " + str(ind))
                        un.append(var10[ind])
                        undo.append(un)
                        
                        var10.pop(ind)
                        var11.pop(ind)

                        if len(undo) > ur_limit():
                          undo.pop(0)
                        break

        # texx, sc1, texx2, sc2 = [], [], [], []
        time.sleep(0.001)
        count +=1
        if time.time() - 1 > timn :
          if Print: print "count:", count #  prints the number of loops running per second
          count = 0
          timn = time.time()
        tim = time.time()


class Keylogger:

  def __init__(self):
    global toKill
    if toKill:
      # quit()
      sys.exit()
    if Print: print "0"
    self.klg = HookManager()
    if Print: print "1"
    self.klg.KeyDown = self.OnKeyboardEvent
    if Print: print "2"
    self.klg.KeyUp = self.OnKeyboardEvent
    if Print: print "3"
    self.klg.HookKeyboard()
    if Print: print "4"
    self.klg.MouseAllButtonsUp = self.OnMouseEvent
    if Print: print "5"
    self.klg.HookMouse()
    # watch for all mouse events
    # self.klg.MouseAll = self.OnMouseEvent
    # self.klg.HookMouse()`
    self.klg.start()
    if Print: print "5"



  def OnMouseEvent(self, event):
        # called when mouse events are received
        # if Print: print event.MessageName
        
        global mm,toKill
        if toKill:
          sys.exit()
        # if Print: print event
        em = event.MessageName
        ew = event.WindowName
        # if Print: print em
        if "up" in em and "middle" in em and ew != Title:
            mm = True
        # return True


  def OnKeyboardEvent(self, event):    # called when keyboard events are received
    # if Print: print "b1"
    # if Print: print "event2 is:", event
    time_req = time.time()
    k  = event.Key
    l  = event.MessageName
    cc = event.Ascii
    ew = event.WindowName

    global toKill, Print
    if toKill:
      sys.exit()
    if cc == 96 or cc == 126:
      if Print: print "quitting"     
      toKill = True
      # quit()
      sys.exit()
      # self.klg.stop()


    # if Print: print "e2:", event
    global con,shi,alt, di1,di2,id1,id2,spe, con_at,con1,clip_now
    global var10,var20,var11,var21, to_copy,last_game
    global mm, s_cl,p_cl, cha, morghuled, undo, redo
    global app_chr, to_app, appended,sdev3x,sdev3y, copied
    global c_time,c_gettime,c_gettime_char,value,cagr_t,cagr_m,cagr_n,value,c_gettime_char
    global get_name, save_name, load_name, name_list,current_name

    # if Print: print cc, k
    if k == "space": 
      k = " "
    if ew == Title:
      last_game = True
    else:
      last_game = False
    # if Print: print "lg:", last_game
    # if k == "grave" or k == 'Oem_3':

    # if Print: print "k is:", k, ':\tl is ', l, "\tcc is:", cc, '\tw:', event.WindowName
        # if Print: print 'KeyID:', event.KeyID

    if con is False and (k == "Control_L" or k == "Control_R") and "down" in l :
      con = True
      if Print: print "con is", con
    elif con and (k == "Control_L" or k == "Control_R") and "up" in l :
      con_at = time.time()
      con1 = True
  
    if shi is False and (k == "Shift_L" or k == "Shift_R") and "down" in l :
      shi = True
      # if Print: print "shi is ", shi
    elif shi and (k == "Shift_L" or k == "Shift_R") and "up" in l :
      shi = False
      # if Print: print "shi is", shi

    if (k == "Alt_L" or k == "Alt_R") and "down" in l :
      alt = True
      # if Print: print "alt is ", alt
    elif (k == "Alt_L" or k == "Alt_R") and "up" in l :
      alt = False
      # if Print: print "alt is ", alt

    if con and ((k == 'c' or k == "C") or(k == 'x' or k == "X")) and "up" in l:
      # if Print: print "copied or cut"
      cha = True
      if mm:
        # Ctrl + middle click sends Ctrl+C which gets detected here
        time.sleep(0.020)
        # s_cl = pyperclip.paste`()
        # pyperclip.copy(p_cl)`
        # if Print: print "mm in copy"
        # if Print: print p_cl
        # if Print: print s_cl
      else:
        # to_copy = pyperclip.paste()
        copied = True
      # if Print: print "var1 and var2 are\n", var10, "\n", var20
    
    if con and (k == 'v' or k == "V") and "up" in l:
      # if Print: print "pasted"
      cha = True
      if oao and not mm:
        if len(var20) > 0:
          un = []
          un.append("from var2 deleted " )
          un.append(var20[0])
          undo.append(un)
          var20.pop(0)
          var21.pop(0)
          redo = []
          if len(undo) > ur_limit():
            undo.pop(0)
        if len(var20) > 0:
          pyperclip.copy(var20[0])

    if (k == 'x' or k == "X") and "up" in l:
        if Print: print "u:", undo
        if Print: print "r:", redo

    if con and (k == 'L' or k == 'l') and "up" in l and Title == ew:
      if shi:
        pat = os.getcwd()
        lss = os.listdir(pat)
        name_list = []
        for nn in lss:
          if ".klip" in nn:
            name_list.append(nn[:-5])
        if Print: print name_list
        load_name = True
      else:
        load_data('')

    if con and (k == 'S' or k == 's') and "up" in l and Title == ew:
      now_data = {
      'v1' : var10,
      'v2' : var20,
      'v3' : clip_now,
      'v4' : s_cl
      }
      if shi:
        get_name = True
      else:
        # save_data(now_data)
        save_data(now_data, current_name)

    if get_name and k == "Escape" and "up" in l:
      get_name = False
      save_name = ""
    if load_name and k == "Escape" and "up" in l:
      load_name = False


    if get_name and "up" in l and not con:
      cha = True
      kk = ''
      if cc > 32 :
        capl = get_caps()

        if "P_" in k: # Ex. output is 'Numpad5'
          try:
            numm = spe.index(k)
            if numm != -1:
              kk = numm
              if Print: print "1kk:", kk
              # if kk.isdigit():
              c_gettime_char += str(kk)
          except ValueError:
            if Print: print "val error"

        if 64 < cc < 91 or 96 < cc < 123:
          # if not shi ^ capl:
          kk = chr(cc)
          # else:
            # kk = di2[chr(cc)]
          if Print: print "orig and next", chr(cc), kk 
        else:
          # if shi:
          kk = chr(cc)
          # else:
            # kk = di1[chr(cc)]
          if Print: print "orig and next", chr(cc), kk

        # kk = chr(cc)
      elif "Numpad" in k: # Ex. output is 'Numpad5'
        kk = k[-1]
      elif k == " " or k == 'space' or k == 'Space' or k == 'SPACE':
        kk = ' '
      elif k == "Return" or k == 'Enter':
        now_data = {
        'v1' : var10,
        'v2' : var20,
        'v3' : clip_now,
        'v4' : s_cl
        }
        save_data(now_data, save_name)
        get_name = False     
      elif k == "BackSpace":
        if len(save_name) > 0:
          save_name = save_name[:-1]

      save_name += kk
      if Print: print save_name




    # undo/redo walkthorugh:
    # implementing undo/redo can be tricky
    # I've tried to make it the final result work similary to how it works in MS Office
    # whenever an action is done, it is noted to the undo and redo variable
    # and whenever undo/redo is called, it is processed differently (oppositely) 
    # also, whenever undo is called, it adds a string in redo corresponding to the action and vice versa


    if con and (k == 'Z' or k == "z") and "up" in l and Title == ew: # for undo
      # if Print: print "w:", event.Window
      # if Print: print "wn:", event.WindowName
      # cha = True
      if Print: print "u:", undo, '\n'
      # for num in undo:
        # if Print: print num
      if len(redo) > 0:
        len_redo = len(redo)
        # for redd in range(len(redo_copy):
        ij = 0
        while ij < len(redo):
          if "undo" not in redo[ij][0]:
            if Print: print "popping:",ij, redo[ij]
            redo.pop(ij)
          else:
            ij += 1
            
      if len(undo) > 0:
        str1 = undo[-1][0]
        if str1.find("Valar") != -1:
          var10  = morghuled[0]
          var11  = morghuled[1]
          var20  = morghuled[2]
          var21  = morghuled[3]
          pyperclip.copy(morghuled[4])
          s_cl   = morghuled[5]
          cagr_m = morghuled[6]
          cagr_n = morghuled[7]
          cagr_t = morghuled[8]
          value  = morghuled[9]
          c_gettime_char = morghuled[10]
          cagr   = morghuled[11]

          undo.pop()
          morghuled = []

        elif str1.find("loaded") != -1:
            re,ree = [], []
            re.append("(undo) loaded")
            ree.append(undo[-1][1][0])
            ree.append(undo[-1][1][1])
            ree.append(undo[-1][1][2])
            ree.append(undo[-1][1][3])
            ree.append(pyperclip.paste())
            ree.append(s_cl)
            re.append(ree)
            redo.append(re)
            pyperclip.copy(undo[-1][1][4])
            s_cl     =     undo[-1][1][5]
            todel = undo[-1][1][6]
            del var10[todel:]
            del var11[todel:]
            todel = undo[-1][1][7]
            del var20[todel:]
            del var21[todel:]
            if len(redo) > ur_limit:
                redo.pop(0)
            undo.pop()


        elif str1.find("from ") != -1:
          re = []
          # if len(redo) > 0:
            # len_redo = len(redo)
            # # for redd in range(len(redo_copy):
            # ij = 0
            # while ij < len(redo):
            #   if "undo" not in redo[ij][0]:
            #     if Print: print "popping:",ij, redo[ij]
            #     redo.pop(ij)

          res = "(undo) from" 
          varr = str1[ str1.find("from ") : str1.find("deleted") ]
          if "clip" in varr:
            res += " clip "
            pyperclip.copy(undo[-1][1])
            res += "deleted "
            ret = undo[-1][1]
            re.append(res)
            re.append(ret)
            redo.append(re)
            undo.pop()
          elif "sec" in varr:
            res += " sec "
            s_cl = undo[-1][-1]
            res += "deleted "
            ret = undo[-1][1]
            re.append(res)
            re.append(ret)
            redo.append(re)

            undo.pop()
          elif "var1" in varr:
            if "all" in str1:
              # res += "var1"
              var10 = undo[-1][1]
              for stt in var10:
                var11.append(manage_nl(stt))
              # if Print: print "var1 and var2 are\n", var10, "\n", var20
              re = []
              re.append("(undo) from var1 deleted all")
              re.append(var10)
              redo.append(re)
              if len(redo) > ur_limit():
                redo.pop(0)
              undo.pop()
            else :
              inde = int(str1[str1.find("deleted ")+8:])
              # if inde == 0:
              var10.insert(inde,undo[-1][-1])
              var11.insert(inde,manage_nl(var10[inde]))
              re = []
              re.append("(undo) from var1 deleted " + str(inde))
              re.append("")
              redo.append(re)
              if len(redo) > ur_limit():
                redo.pop(0)
              # if Print: print "var1 and var2 are\n", var10, "\n", var20
              undo.pop()
          elif "var2" in varr:
            if "all" in str1:
              var20 = undo[-1][1]
              for stt in var20:
                var21.append(manage_nl(stt))
              # if Print: print "var1 and var2 are\n", var10, "\n", var20
              pyperclip.copy(var20[0])
              re = []
              re.append("(undo) from var2 deleted all")
              re.append(var20)
              redo.append(re)
              if len(redo) > ur_limit():
                redo.pop(0)
              undo.pop()
            else :
              # inde = int(str1[str1.find("deleted ")+8:])
              # if inde == 0:
              var20.insert(0,undo[-1][-1])
              var21.insert(0,manage_nl(var20[0]))
              if oao:
                pyperclip.copy(var20[0])
              # if Print: print "var1 and var2 are\n", var10, "\n", var20
              re = []
              re.append("(undo) from var2 deleted 0")
              re.append(undo[-1][1])
              if Print: print "appending2:", re
              redo.append(re)
              if len(redo) > ur_limit():
                redo.pop(0)
              undo.pop()


        elif str1.find("to ") != -1:
          varr = str1[ str1.find("to ") : str1.find("added") ]
          re = []
          # if len(redo) > 0:
          #   len_redo = len(redo)
          #   # for redd in range(len(redo_copy):
          #   ij = 0
          #   while ij < len(redo):
          #     if "undo" not in redo[ij][0]:
          #       if Print: print "popping:",ij, redo[ij]
          #       redo.pop(ij)
          #     else:
          #       ij += 1
                # redo
          res = "(undo) to" 
          if "var1" in varr:
            res += " var1 "
            ret = undo[-1][1]
            # ret = var10[-1]
            if len(var10) > 0:
              var10.pop()
              var11.pop()
              # if Print: print "var10 asked to pop"
              if len(var10) > 0:
                pyperclip.copy(var10[-1])
            
            # redo.append(re)
            if len(redo) > ur_limit():
              redo.pop(0)

            if str1.find("added") - str1.find("var1") < 6:
              undo.pop()

          if "var2" in varr:
            res += "and var2 "
            ret = undo[-1][1]
            # ret = var20[-1]
            if len(var20) > 0:
              var20.pop()
              var21.pop()
              # if Print: print "var20 asked to pop"
            if str1.find("added") - str1.find("var2") < 6:
              undo.pop()
            if oao and  len(var20) > 0:
              pyperclip.copy(var20[0])

          if "app" in varr:
            res += "and app "
            ret = undo[-1][1]
            # if Print: print "pre:", appended
            appended = rreplace(appended, app_chr, '', 1)
            appended = rreplace(appended, undo[-1][1], '', 1)

            if str1.find("added") - str1.find("app") < 6:
              undo.pop()
            # if Print: print "post:", appended
            pyperclip.copy(appended)

          res += "added"
          re.append(res)
          re.append(ret)
          # if Print: print "appending1:", re
          redo.append(re)
          if len(redo) > ur_limit():
            redo.pop(0)

    if con and (k == 'Y' or k == "y") and "up" in l and ew == Title: # for redo
      if Print: print "r:", redo, '\n'
      # cha = True
      if len(redo) > 0:
        str2 = redo[-1][0]

        if str2.find("loaded") != -1:
            un,unn = [], []
            un.append("loaded")
            unn.append(redo[-1][1][0])
            unn.append(redo[-1][1][1])
            unn.append(redo[-1][1][2])
            unn.append(redo[-1][1][3])
            unn.append(pyperclip.paste())
            unn.append(s_cl)
            pyperclip.copy(redo[-1][1][4])
            s_cl     =     redo[-1][1][5]
            unn.append(len(var10))
            unn.append(len(var20))            
            un.append(unn)
            undo.append(un)

            var10.extend(redo[-1][1][0])
            var11.extend(redo[-1][1][1])


            var11, var21 = [], []
            for v in var10:
              var11.append(manage_nl(v))
            for v in var20:
              var21.append(manage_nl(v))

            if len(undo) > ur_limit:
                undo.pop(0)
            redo.pop()

  
        elif str2.find("to ") != -1:
          varr = str2[ str2.find("to ") : str2.find("added") ]
          ure = []
          ures = "(undo) to"
          uret = []

          if "var1" in varr:
            var10.append(redo[-1][-1])
            var11.append(manage_nl(var10[-1]))
            pyperclip.copy(var10[-1])
            ures += " var1 "
            uret = redo[-1][1]

            if str2.find("added") - str2.find("var1") < 6 and "undo" in str2:
              redo.pop()

          if "var2" in varr:
            var20.append(redo[-1][-1])
            var21.append(manage_nl(var20[-1]))
            ures += " var2 "
            uret = redo[-1][1]

            if str2.find("added") - str2.find("var2") < 6 and "undo" in str2:
              redo.pop()
            if oao:
              pyperclip.copy(var20[0])
            # pyperclip.copy(var10[-1])

          if "app" in varr:
            # if Print: print "pre:", appended
            appended += redo[-1][1]
            appended += app_chr
            ures += "and app "
            uret = redo[-1][1]

            if str2.find("added") - str2.find("app") < 6 and "undo" in str2:
              redo.pop()
            # if Print: print "post:", appended
            pyperclip.copy(appended)
          ures += "added"

          ure.append(ures)
          ure.append(uret)
          undo.append(ure)
          # redo.pop()
          if len(undo) > ur_limit():
            undo.pop(0)

        elif str2.find("from") != -1:
          varr = str2[ str2.find("from ") : str2.find("deleted") ]
          ure = []
          ures = "from"
          uret = []
          if Print: print "str2:", str2
          if "clip" in varr:
            ures += " clip deleted "
            uret = redo[-1][1]
            pyperclip.copy('')
            if str2.find("deleted") - str2.find("clip") < 6 and "undo" in str2:
              redo.pop()          

          if "sec" in varr:
            ures += " sec deleted "
            uret = redo[-1][1]
            s_cl = ''

            if str2.find("deleted") - str2.find("sec") < 6 and "undo" in str2:
              redo.pop()          
          if "var1" in varr:
            if "all" in str2:
              # print
              ures += " var1 all "
              if len(var10) > 0:
                uret = var10
                if len(undo) > ur_limit():
                  undo.pop(0)
                var10 = []
                var11 = []
              else:
                # ures += " var1 all"
                uret = redo[-1][1]
                if len(undo) > ur_limit():
                  undo.pop(0)
              ures += "deleted"

            else:
              inde = int(str2[str2.find("deleted ")+8:])
              if Print: print inde
              ures += " var1 "
              if inde == -1:
                uret = var10[-1]
                var10.pop()
                var11.pop()
                ures += "deleted -1" 

                if len(var10) > 0:
                  pyperclip.copy(var10[-1])
              elif inde < len(var10):
                uret = var10[inde]
                var10.pop(inde)
                var11.pop(inde)
                ures += "deleted " + str(inde)

            if len(redo) > ur_limit():
              redo.pop(0)

            if str2.find("deleted") - str2.find("var1") < 6 and "undo" in str2:
              if Print: print "popping:", redo.pop()


          if "var2" in varr:
            if "all" in str2:
              if len(var20) > 0:
                ures += " var2 all"
                uret = var20
                if len(undo) > ur_limit():
                  undo.pop(0)
              var20 = []
              var21 = []
            else:
              inde = int(str2[str2.find("deleted ")+8:])
              ures += " var2 "
              if inde == -1:
                uret = var20[-1]
                var20.pop()
                var21.pop()
                ures += "deleted 0"

              elif inde < len(var20) :
                uret = var20[inde]
                var20.pop(inde)
                var21.pop(inde)
                ures += "deleted " + str(inde)
                if oao and len(var20) > 0:
                  pyperclip.copy(var20[0])

            if str2.find("deleted") - str2.find("var2") < 6 and "undo" in str2:
              redo.pop()

          if "app" in varr:
            ures += "and app "
            uret = undo[-1][1]
            # if Print: print "pre:", appended
            appended = rreplace(appended, app_chr, '', 1)
            appended = rreplace(appended, undo[-1][1], '', 1)
            if str2.find("deleted") - str2.find("app") < 6:
              redo.pop()
            # if Print: print "post:", appended
            pyperclip.copy(appended)

          # ures += "deleted"
          if "deleted" in ures:
            ure.append(ures)
            ure.append(uret)
            undo.append(ure)
          # redo.pop()
          if len(undo) > ur_limit():
            undo.pop(0)

        else:
          redo.pop()

    if to_app and k == "BackSpace" and "up" in l: # deletes last char while typing characters to append
      cha = True
      if Print: print "deleting char"
      # if Print: print "pre:", app_chr
      if len(app_chr) > 0:
        app_chr = app_chr[:-1]
      # if Print: print "post:", app_chr
    # if app  and 

    if c_gettime and "up" in l:
      # when manually entering time for CAGR calculation
      # formats accepted: '2', '5/12', '3.5', '4.5/12.5'
      # it porcesses these formats to get the proper time entered...      
      kk = ''
      if Print: print "k:", k,cc
      if "P_" in k: # Ex. output is 'Numpad5'
        
        # kk = k[-1]
        try:
          numm = spe.index(k)
          if numm != -1:
            kk = numm
            if Print: print "1kk:", kk
            # if kk.isdigit():
            c_gettime_char += str(kk)
        except ValueError:
          if Print: print "val error"

      if (k == '/' or k == '?' or "Divide" in k or cc == 63 or cc == 47) :
        if '/' not in c_gettime_char and len(c_gettime_char) > 0:
          c_gettime_char += '/'
      elif (k == '.' or k == '>' or cc == 46 or cc == 62 or "_Delete" in k or "Period" in k) and len(c_gettime_char) > 0:
        if '/' in c_gettime_char:
          fra = c_gettime_char.split('/')
          if '.' not in fra[1]:
            c_gettime_char += '.'
        elif '.' not in c_gettime_char:
          c_gettime_char += '.'
      elif 47 < cc < 58:
        kk = chr(cc)
        if Print: print "2kk:", kk
        if kk.isdigit():
          c_gettime_char += kk
      elif chr(cc) in nos:
        kk = di1[chr(cc)]
        if Print: print "3kk:", kk
        if kk.isdigit():
          c_gettime_char += kk
      elif k == "Back" or k == "BackSpace":
        if Print: print "deleting char"
        if len(c_gettime_char) > 0:
          c_gettime_char = c_gettime_char[:-1]
      if k == "Return" or k == 'Enter' or k == 'P_Enter':
          if Print: print c_gettime_char
          if c_gettime_char != "":
            # if c_gettime_char.count('/') == 1: 
            if '/' in c_gettime_char:
              fra = c_gettime_char.split('/')
              if float(fra[1]) > 0:
                c_gettime_char = format(float(fra[0])/float(fra[1]), '.3f')
              else: c_gettime_char = "0"

            cagr_t = float(c_gettime_char)
            c_gettime = False
            if cagr_m[0] > 0 and cagr_t > 0:
              value = get_cagr(cagr_m[0], cagr_n[0], cagr_t)
              if Print: print value
            else:
              value = 0
              if Print: print "improper values"        


    if to_app and not con and "up" in l: # type to add characters to append
      cha = True
      if cc > 32 :
        capl = get_caps()

        if "P_" in k: # Ex. output is 'Numpad5'
          try:
            numm = spe.index(k)
            if numm != -1:
              kk = numm
              if Print: print "1kk:", kk
              # if kk.isdigit():
              c_gettime_char += str(kk)
          except ValueError:
            if Print: print "val error"

        if 64 < cc < 91 or 96 < cc < 123:
          # if not shi ^ capl:
          kk = chr(cc)
          # else:
            # kk = di2[chr(cc)]
          if Print: print "orig and next", chr(cc), kk 
        else:
          # if shi:
          kk = chr(cc)
          # else:
            # kk = di1[chr(cc)]
          if Print: print "orig and next", chr(cc), kk

        # kk = chr(cc)
      elif "Numpad" in k: # Ex. output is 'Numpad5'
        kk = k[-1]
      elif k == "tab" or k == 'Tab' or k == 'TAB':
        kk = '\t'
      elif k == "Return" or k == 'Enter':
        kk = '\n'
      elif k == " " or k == 'space' or k == 'Space' or k == 'SPACE':
        kk = ' '
      # if cc != 0 :
    # if len(k) == 1:
      else:
        kk=''
      if Print: print "k:", k, " kk:", kk
      app_chr += kk
      if Print: print "total:", app_chr
    # time.sleep(0.002)
    # if time.time() - time_req > 0.15:
      # to_restart = True
    # return True

# new = KeyL()
# if Print: print "end"

class Thr1(Thread):
    def __init__(self):
        Thread.__init__(self)


    def run(self):
      if Print: print "Starting First"
      new = Keylogger()

class Thr2(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        if Print: print 'Starting Second'
        test()

if __name__ == '__main__':
    a = Thr1()
    b = Thr2()

    a.start()
    b.start()        

if Print: print "boo"