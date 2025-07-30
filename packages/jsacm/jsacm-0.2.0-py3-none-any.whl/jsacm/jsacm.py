###jacoobsmodules###
# https://github.com/vinta/awesome-python?tab=readme-ov-file
# jmod.login
# jmod.greet
# jmod.calc
# jmod.agecalc
# jmod.gettime
# jmod.getdate
# jmod.getday
# jmod.createfile
# jmod.appendfile
# jmod.writefile
# jmod.deletefile
# jmod.readfile
# jmod.dbsearch
# jmod.dbedit
# jmod.rps
# jmod.createtodolist
# jmod.addtask
# jmod.checkofftask
# jmod.deletetask
# jmod.opentodolist
# jmod.fileconvert
# jmod.translate
# jsacm.aid
# jsacm.ewans
# jsacm.profitcalc
# jsacm.caesarcypher
# jsacm.namegen
# jsacm.convert
# jsacm.rickroll
# jsacm.ytplay
# jsacm.ytdownload
##################################################
# todo list:
# - sort out aid structure
# - add more features
# - add import string to req
##################################################
tasks = [""]
alphabet = ["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"]
numbers = ["0","1","2","3","4","5","6","7","8","9"]
keyboard = ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p','a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'z', 'x', 'c', 'v', 'b', 'n', 'm']
morse = ['.-','-...','-.-.','-..','.','..-.','--.','....','..','.---','-.-','.-..','--','-.','---','.--.','--.-','.-.','...','-','..-','...-','.--','-..-','-.--','--..']
##################################################
sortedfeatures = [
    [["Todo"],[
        'createtodolist = creates a todolist',
        'addtask = add a task to a todolist',
        'checkofftask = check task off todolist',
        'deletetask = deletes a task of the todolist',
        'opentodolist = reads the contents of the todolist'
               ]],
    [["File handling"],[
        'createfile = creates a new text file {filename}',
        'appendfile = appends a text file {filename, text}',
        'writefile = writes into a text file {filename, text}',
        'deletefile = deletes a text file {filename, overide}',
        'readfile = reads a text file {filename}'
            ]],
    [["Misc"],[
        'aid = lists all features in this release',
        'greeting = provides a greeting {name}'
            ]],
    [["Authentication"],[
        'login = login system (requires {username,password}'
            ]],
    [["Calculators"],[
        'calc = sophisticated calculator {equation}',
        'agecalc = age calculator {year}',
        'profitcalc = A simple profit calculator {net profit, costs}'
            ]],
    [["Get info"],[
        'gettime = prints the current time {rt}',
        'getdate = prints the current date {rt}',
        'getday = prints the current day {rt}'
            ]],
    [["Encryption"],[
        "ceasar.encrypt = ceasar cypher {phrase, 'random' or 'custom', cusotm key}",
        'asymetrical.encrypt = binary two step assymetrical encryption {binary}',
        'atbash.encrypt = simple abtash encryption {phrase}',
        'keyboard.encrypt = simple keyboard code encryption {phrase}'
            ]],
    [["Decryption"],[
        "ceasar.decrypt = ceasar cypher {encrypted msg, 'all' or 'custom', custom key}",
        'asymetrical.decrypt = binary two step assymetical decryption {encrypted binary, public key, private key}',
        'abtash.decrypt = simple abtash decryption {phrase}',
        'keyboard.decrypt = simple keyboard code decryption {phrase}'
        ]],
    [["Converstion"],[
        'convert = converts measurements between a wide range of units',
        'fileconvert = converts files to many different formats {current file type, convert to, filename}',
        'denary2binary = converts denary to binary {number}',
        'binary2denary = converts binary to denary {binary}',
        'denary2hexadecimal = converts denary to hexadecimal {number}',
        'denary2numeral = converts denary to roman numeral {number}',
        'numeral2denary = converts roman numeral to denary {numeral}',
        'english2morse = converts english to morse code {phrase}',
        'morse2english = converts morse code to english {morse}'
            ]],
    [["Translation"],[
        'translate = translates a phrase into any language {phrase, language}'
                      ]],
    [["Generation"],[
        'namegen = generates a random full name',
        'passgen = generates a random password {length}'
                     ]],
    [["You-Tube"],[
        'ytplay = plays a youtube video of choice from a url {url}',
        'ytdownload = downloads a youtube video form a url {url}'
            ]],
    [["Database handling"],[
        'dbsearch = searches an SQL databse',
        'dbedit = edits an SQL database'
            ]],
    [["Games"],[
        'rps = rock paper scissors'
            ]],
    [["Sorts"],[
        'sort.bubble = bubble sort {list}',
        'sort.bogo = bogo sort {list}',
        'sort.stalin = stalin sort {list}'
        ]],
    [["Searches"],[
        'search.linear = linear search {list, number}'
        ]]
    ]

###########################################help###
def aid(*argv):
    print("Avaliable features in this release are")
    for feature in sortedfeatures:
        feature_name = feature[0][0]
        feature_list = feature[1]
        
        print(f"\n=== {feature_name} ===")
        for item in feature_list:
            print(f"- {item}")
###########################################login###
def login(*argv):
    loop = 0
    check = False
    for arg in argv:
        check = True
        if loop == 0:
            usrname = arg
            loop = loop+1
        if loop == 1:
            passwrd = arg
    if check != True:
        usrname = "username"
        passwrd = "password"
    while True:
        usr = input("Enter username: ")
        if usr == usrname:
            break
        else:
            print("Incorrect username")
    while True:
        pas = input("Enter password: ")
        if pas == passwrd:
            print("You are now logged in")
            break
        else:
            print("Incorrect password")
        
        
################################################calc###        
        
import math
import sys
   
# String in the form above
# Using either, plus, add, minus, subtract, muplitply, times,  divide (operand is taken from first 2 letters)


#Converts the seperated 'int' characters that are as strings in elements into one string under operand
def calc_operand_collector(operand_list, numb_list):
    operand = "0"
    for n in range(operand_list.index(" ")):
        if operand_list[n] in numb_list:
            operand = operand + operand_list[n]
    return operand


#Turns word operators into integers
def calc_operator_collector(list):
    op = ""
    for n in range(len(list)):
        if list[n] == "p" and list[n + 1] == "l" or list[n] == "a" and list[n + 1] == "d":
            op = 0
        elif list[n] == "m" and list[n + 1] == "i" or list[n] == "s" and list[n + 1] == "u":
            op = 1
        elif list[n] == "m" and list[n + 1] == "u" or list[n] == "t" and list[n + 1] == "i":
            op = 2
        elif list[n] == "d" and list[n + 1] == "i":
            op = 3
    return op


#Main body subroutine
def calc(*argv):
    loop = 0
    check = False
    for arg in argv:
        check = True
        if loop == 0:
            string = arg
    if check != True:
        string = input("Enter your calculation: ")
    #Var & list declarations
    numb_list = ["0","1","2","3","4","5","6","7","8","9"]
    operand_list = []
    list = [*string]
    ans = 0


    #Finds what operation to do
    op = calc_operator_collector(list)


    #Creates a list of all the numbers in 'list' adding spaces to differentiate different operands    
    for n in range(len(list)):
        if list[n] in numb_list or list[n] == " ":
            operand_list.append(list[n])  
    operand_list.append(" ")
    #Makes the frst operand whole and integers again
    operand0 = int(calc_operand_collector(operand_list, numb_list))


    #Does stuff to make the next subroutine work
    for n in range(operand_list.index(" ") + 2):
        operand_list.pop(0)


    #Makes the second operand whole and integers again
    operand1 = int(calc_operand_collector(operand_list, numb_list))
   
    #Does the calculation
    if op == 0:
        ans = operand0 + operand1
    elif op == 1:
        ans = operand0 - operand1
    elif op == 2:
        ans = operand0 * operand1
    elif op == 3:
        ans = operand0 / operand1
    print(string,"is", ans)


  
############################################################greeting###
def greet(*argv):
    loop = 0
    check = False
    for arg in argv:
        check = True
        if loop == 0:
            name = arg
    if check != True:
        name = ""
    from datetime import datetime
    now = datetime.now()
    time = now.hour
    if time < 12:
        phr = "Good morning"
    elif time < 16:
        phr = "Good afternoon"
    elif time < 19:
        phr = "Good evening"
    else:
        phr = "Good night"
    print(phr,name)


############################################################time###
def gettime(*argv):
    import time
    phrase = ""
    loop = 0
    check = False
    for arg in argv:
        check = True
        if loop == 0:
            phrase = arg
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    if phrase == "rt":
        return current_time
    else:
        print(current_time)
    
    
############################################################date###
def getdate(*argv):
    from datetime import date
    loop = 0
    phrase = ""
    check = False
    for arg in argv:
        check = True
        if loop == 0:
            phrase = arg
    today = date.today()
    if phrase == "rt":
        return today
    else:
        print("Today's date:", today)
############################################################createfile###
def createfile(*argv): # can take: file name
    import os
    loop = 0
    check = False
    for arg in argv:
        check = True
        if loop == 0:
            file = arg
    if check != True:
        file = input("Choose a name for your new file: ")
    filen = "Created Files/"+file+".txt"
    if os.path.isfile(filen) == True:
        print("File with that name allready exists")
    else:
        newpath = r'Created Files' 
        if not os.path.exists(newpath):
            os.makedirs(newpath)
        f = open(filen, "x")
        print("File created")
        f.close()
############################################################appendfile###
def appendfile(*argv): # can take: file name, phrase
    import os
    loop = 0
    check = False
    for arg in argv:
        check = True
        if loop == 0:
            file = arg
            loop = loop+1
        if loop == 1:
            phrase = arg
    if check != True:
        file = input("enter file name: ")
        phrase = input("enter phrase to append into file: ")
    filen = "Created Files/"+file+".txt"
    if os.path.isfile(filen) == False:
        print("File with that name dosen't exist")
    else:
        phrase = phrase+". "
        f = open(filen, "a")
        f.write(phrase)
        print("Appended to file")
        f.close()
############################################################writefile###
def writefile(*argv): # can take: file name, phrase
    import os
    loop = 0
    check = False
    for arg in argv:
        check = True
        if loop == 0:
            file = arg
            loop = loop+1
        if loop == 1:
            phrase = arg
    if check != True:
        file = input("enter file name: ")
        phrase = input("enter phrase to write into file: ")
    phrase = phrase+". "
    filen = "Created Files/"+file+".txt"
    if os.path.isfile(filen) == False:
        print("File with that name dosen't exist")
    else:
        f = open(filen, "w")
        f.write(phrase)
        print("Written to file")
        f.close()
############################################################deletefile###
def deletefile(*argv): # can take: file name, overide
    import os
    loop = 0
    check = False
    for arg in argv:
        check1 = True
        if loop == 0:
            file = arg
            loop = loop +1
        if loop == 1:
            ovr = arg
    if check1 != True:
        file = input("enter file name: ")
    filen = "Created Files/"+file+".txt"
    if os.path.isfile(filen) == False:
        print("File with that name dosen't exist")
    else:
        if ovr == "overide":
            import os
            os.remove(filen)
            print("Deleted",filen,)
        else:
            check = input("Are you sure you want to delete this file? Y/N: ")
            if check == "Yes" or check == "Y" or check == "y" or check == "yes":
                os.remove(filen)
                print("Deleted",filen,)
            else:
                print("Canceling")
############################################################readfile###
def readfile(*argv): # can take: file name
    import os
    loop = 0
    check = False
    for arg in argv:
        check = True
        if loop == 0:
            file = arg
    if check != True:
        file = input("enter file name: ")
    filen = "Created Files/"+file+".txt"
    if os.path.isfile(filen) == False:
        print("File with that name dosen't exist")
    else:
        f = open(filen, "r")
        print(f.read())
        f.close

############################################################databasesearch###
def dbsearch(*argv):
    import sqlite3
    loop = 0
    check = False
    for arg in argv:
        check = True
        if loop == 0:
            dbchoice = arg
            loop = loop+1
        if loop == 1:
            tblchoice = arg
            loop = loop+1
        if loop == 2:
            find = arg
    if check != True:
        dbchoice = input("Enter name of database to be searched: ")
        tblchoice = input("Enter table name: ")
        column = input("Enter column to search: ")
        find = input("Enter what you want to search for: ")
    DATABASE = dbchoice+".db"
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    sqlt = "SELECT *"
    sqlc = " FROM "+str(tblchoice)
    sqln = " WHERE "+str(column)+" = "+str(find) 
    sql = str(sqlt)+str(sqlc)+str(sqln)
    cur.execute(sql)
    print(cur.fetchall())

############################################################dbedit###
def dbedit(*argv):
    import sqlite3
    loop = 0
    check = False
    for arg in argv:
        check = True
        if loop == 0:
            dbchoice = arg
            loop = loop+1
        if loop == 1:
            choicetable = arg
            loop = loop+1
        if loop == 2:
            choicecolumn = arg
            loop = loop+1
        if loop == 3:
            choicevalue = arg
            loop = loop+1
        if loop == 4:
            newvalue = arg
    if check != True:
        dbchoice = input("Enter name of database to be searched: ")
        choicetable = input("Enter table name: ")
        choicecolumn = input("Enter column: ")
        choicevalue = input("Enter old/existing value: ")
        newvalue = input("Enter new value: ")
    DATABASE = dbchoice+".db"
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    sqlt = "UPDATE "+str(choicetable)
    sqlc = " SET "+str(choicecolumn)
    sqln = "WHERE "+str(choicecolumn)
    sql = str(sqlt)+str(sqlc)+' = ? '+sqln+' = ?'
    print(sql)
    cursor.execute(sql, (newvalue,choicevalue) )
    conn.commit()
############################################################Rockpaperscissors###
    
def rps(*argv):
    import random
    print("sure lets see whos best")
    print("what have you chosen")
    usrchoice = input("...")
    print(usrchoice)
    choice = random.randint(1, 4)
    if choice == 1:
        print("I have chosen scissors")
        if usrchoice == "scissors":
            print("We have drawn")
        elif usrchoice == "rock":
            print("you won")
        elif usrchoice == "paper":
            print("you lost")
    elif choice == 2:
        print("I have chosen rock")
        if usrchoice == "rock":
            print("We have drawn")
        elif usrchoice == "paper":
            print("you won")
        elif usrchoice == "scissors":
            print("you lost")
    elif choice == 3:
        print("I have chosen paper")
        if usrchoice == "paper":
            print("We have drawn")
        elif usrchoice == "rock":
            print("you lost")
        elif usrchoice == "scissors":
            print("you won")

    else:
        print("error")


############################################################createtodolist###
def createtodolist(*argv):
    file = input("Choose name for your new todolist")
    filen = file+".txt"
    f = open(filen, "x")
    print("TODO list created")
    f.close()
    
############################################################opentotodolist###
def opentodolist(*argv):
    print("Tasks:")
    for index, task in enumerate(tasks):
        status = "Done" if task["done"] else ["Not Done"]
        print(f"{index + 1}. {task['task']} - {status}")

############################################################addtotodolist###
def addtask(*argv):
    print("Enter the new task")
    task = input("")
    tasks.append({"task": task, "done": False})
    print("Task added!")
    
############################################################checkofftodolist###
def checkofftask(*argv):
    task_index = int(input("Enter the task number to mark as done: ")) - 1
    if 0 <= task_index < len(tasks):
        tasks[task_index]["done"] = True
        print("Task marked as done!")
        
############################################################deletetodolist###
def deletetask(*argv):
    task_index = int(input("Enter the task number to be removed: ")) - 1
    if 0 <= task_index < len(tasks):
        tasks[task_index]["done"] = True
        print("Task Removed!")
        
############################################################age calculator###
def agecalc(*argv): # can take: year
    from datetime import datetime, timedelta
    now = datetime.now()
    loop = 0
    phrase = ""
    check = False
    for arg in argv:
        check = True
        if loop == 0:
            dob_input = arg
    if check != True:     
        print("Enter your date of birth (YYYY-MM-DD):")
        dob_input = input()
    birthday = datetime.strptime(dob_input, "%Y-%m-%d")
    difference = now - birthday
    age_in_years = difference.days // 365
    print(f"You are {age_in_years} years old.")
    
############################################################get day###
def getday(*argv): # can take: rt
    loop = 0
    phrase = ""
    check = False
    for arg in argv:
        check = True
        if loop == 0:
            phrase = arg
    import datetime
    now = datetime.datetime.now()
    if phrase == "rt":
        return now.strftime("%A")
    else:
        print("Today is",now.strftime("%A"))

############################################################file type converter###
def fileconvert(*argv): # can take: current file type, convert to, filename
    import aspose.words as aw
    loop = 0
    check = False
    for arg in argv:
        check = True
        if loop == 0:
            current = arg
            loop+= 1
        if loop == 1:
            operator = arg
            loop += 1
        if loop == 2:
            og = arg
    if check != True:
        print("Avaliable formats to convert are DOC - DOC - RTF - DOT - DOTX - DOTM - DOCM - ODT - OTT - PDF - XPS - OpenXPS - PostScript - JPG - PNG - TIFF - BMP - SVG - EMF - GIF - HTML - MHTML - EPUB - MOBI - Xaml - PCL - etc")
        current = input("current file type: ")
        operator = input("File type to convert to")
        og = input("Enter name of file to convert: ")
    oldname = str(og)+"."+str(current)
    newname = str(og)+"."+str(operator)
    doc = aw.Document(oldname)
    doc.save(newname)
    

############################################################translate###
def translate(*argv):
    from deep_translator import GoogleTranslator
    loop = 0
    check = False
    for arg in argv:
        check = True
        if loop == 0:
            phrase = arg
            loop = loop+1
        if loop == 1:
            lang = arg
    if check != True:
        phrase = input("Enter phrase to translate: ")
        lang = input("choose the language to translate into: ")
    translated = GoogleTranslator(source='auto', target= lang).translate(str(phrase))  # output -> Weiter so, du bist großartig
    print(translated)
    

############################################################password generator###
def passgen(*argv):
    loop = 0
    check = False
    for arg in argv:
        check = True
        if loop == 0:
            N = arg
    import random
    import string
    if check != True:
        N = input("enter how long you would like the password to be: ")
    passwrd =''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase + string.punctuation) for _ in range(int(N)))
    print(passwrd)

############################################################ewans module###
def ewans(*argv):
    print("Spam,Eggs and Ham")
    
    
############################################################profit calculator###
def profitcalc(*argv):
    loop = 0
    check = False
    for arg in argv:
        check = True
        if loop == 0:
            net_profit = arg
            loop = loop+1
        if loop == 1:
            costs = arg
    if check != True:
        net_profit = input("Enter the net profit: ")
        costs = input("Enter the total costs: ")
    print("The total profit is £"+str(int(net_profit)-int(costs)))
    

############################################################name generator###
def namegen(*argv):
    import names
    print(names.get_full_name())

############################################################unit converter###
def convert(*argv):
    factors = {
        "mm": 0.001,
        "cm": 0.01,
        "m": 1,
        "km": 1000,
        "in": 0.0254,
        "ft": 0.3048,
        "yd": 0.9144,
        "mi": 1609.34,
        "milimeters": 0.001,
        "centimeters": 0.01,
        "meters": 1,
        "kilometers": 1000,
        "inches": 0.0254,
        "feet": 0.3048,
        "yard": 0.9144,
        "miles": 1609.34
    }
    convert = []
    loop = 0
    check = False
    for arg in argv:
        check = True
        if loop == 0:
            convert.append(arg)
            loop = loop+1
        if loop == 1:
            convert.append(arg)
            loop = loop+1
        if loop == 2:
            convert.append(arg)
    loop1 = 0
    for i in convert:
        loop1 = loop1+1
        if loop1 == 3:
            value = int(i)
        if loop1 == 4:
            from_unit = str(i)
        if loop1 == 5:
            to_unit = str(i)
    if check != True:
        value = float(input("Enter the value: "))
        from_unit = str(input("Enter the unit to convert from (e.g., km, mi, ft): "))
        to_unit = str(input("Enter the unit to convert to: "))
    meters = value * factors[from_unit]
    result = meters / factors[to_unit]
    print(f"{value} {from_unit} is equal to {result:.4f} {to_unit}")


############################################################rickroll###
def rickroll(*argv):
    from os import startfile
    startfile("nggup.mp4")
    
############################################################ytplay###
def ytplay(*argv):
    from pytube import YouTube
    import webbrowser
    loop = 0
    check = False
    for arg in argv:
        check = True
        if loop == 0:
            video_url = arg
    if check != True:
        video_url = input("Enter url of video you want to play")
    yt = YouTube(video_url)
    video_title = yt.title
    thumbnail_url = yt.thumbnail_url
    webbrowser.open(video_url)
    
############################################################ytdownload###
def ytdownload(*argv):
    import os
    from pytubefix import YouTube
    from pytubefix.cli import on_progress
    loop = 0
    check = False
    for arg in argv:
        check = True
        if loop == 0:
            url = str(arg)
    if check != True:
        url = input("Enter Url of video to download")
     
    yt = YouTube(url, on_progress_callback = on_progress)
    print(yt.title)
    newpath = r'YTDOWNLOADS' 
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    ys = yt.streams.get_highest_resolution()
    ys.download("YTDOWNLOADS/")

############################################################denary to binary###
def denary2binary(*argv): # can take: number
    loop = 0
    check = False
    for arg in argv:
        check = True
        if loop == 0:
            x = int(arg)
    if check != True:
        x = int(input("Enter denary number:"))
    y = ""
    while x>0:
        y = str(x%2)+y
        x = x//2
    if check == True:
        return y
    else:
        print(y)
        
############################################################binary to denary###
def binary2denary(*argv): # can take: binary
    loop = 0
    check = False
    for arg in argv:
        check = True
        if loop == 0:
            x = arg
    if check != True:
        x = input("EDDIE:> enter binary number:\nUSER:>")
    y = []
    yy = []
    num = 0
    for i in x:
        y.append(i)
    num1 = len(y)-1
    for i in y:
        yy.append(y[num1])
        num1 -= 1
    nums = 0 
    for i in yy:
        if i == "1":
            num += (2**nums)
        nums += 1
    answer = ("Denary conversion is:",num)
    if check == True:
        return answer
    else:
        print(answer)
############################################################denary to hexadecimal###
def denary2hexadecimal(*argv): # can take: number
    hexc = ["1","2","3","4","5","6","7","8","9","A","B","C","D","C","E","F"]
    loop = 0
    check = False
    for arg in argv:
        check = True
        if loop == 0:
            x = int(arg)
    if check != True:
        x = int(input("Enter denary number:"))
    y = ""
    z = []
    ans = ""
    while x>0:
        y = str(x%2)+y
        x = x//2
    n = 4
    z = [y[i:i+n] for i in range(0, len(y), n)]
    for i in z:
        x = i
        y = []
        yy = []
        num = 0
        for i in x:
            y.append(i)
        num1 = len(y)-1
        for i in y:
            yy.append(y[num1])
            num1 -= 1
        nums = 0 
        for i in yy:
            if i == "1":
                num += (2**nums)
            nums += 1
        ans += (hexc[(num-1)])
    answer = ("Hex conversion is:",ans)
    if check == True:
        return answer
    else:
        print(answer)
############################################################denary to roman numerals###
def denary2numeral(*argv): # can take: number
    loop = 0
    check = False
    for arg in argv:
        check = True
        if loop == 0:
            number = int(arg)
    if check != True:
        number = int(input("Enter denary number to convert:"))
    roman_numerals = {
        1000: "M", 900: "CM", 500: "D", 400: "CD",
        100: "C", 90: "XC", 50: "L", 40: "XL",
        10: "X", 9: "IX", 5: "V", 4: "IV", 1: "I"
    }
    if 1 <= number <= 3999:
        result = ""
        for value, numeral in roman_numerals.items():
            while number >= value:
                result += numeral
                number -= value
        answer = (f"Roman numeral: {result}")
    else:
        print("Number out of range (1-3999)")
    if check == True:
        return answer
    else:
        print(answer)
############################################################roman numeral to denary###
def numeral2denary(*argv): # can take: roman numerals
    roman_numerals = {
        "M": 1000, "CM": 900, "D": 500, "CD": 400,
        "C": 100, "XC": 90, "L": 50, "XL": 40,
        "X": 10, "IX": 9, "V": 5, "IV": 4, "I": 1
    }
    loop = 0
    check = False
    for arg in argv:
        check = True
        if loop == 0:
            roman = arg
    if check != True:
        roman = input("Enter a Roman numeral:").upper()
    i = 0
    num = 0
    while i < len(roman):
        if i + 1 < len(roman) and roman[i:i+2] in roman_numerals:
            num += roman_numerals[roman[i:i+2]]
            i += 2
        else:
            num += roman_numerals[roman[i]]
            i += 1
    answer = (f"Denary number: {num}")
    if check == True:
        return answer
    else:
        print(answer)
###########################################################################################################################ASYMERTRICAL###
class asymetrical:
    ############################################################asymetrical encryption###
    def encrypt(*argv): # can take in binary input
            bininp = []
            loop = 0
            check = False
            for arg in argv:
                check = True
                if loop == 0:
                    bininp = str(arg)
            if check != True:
                bininp = input("Enter first binary number:")
            pubencry = []
            privencry = []
            pubxor = []
            privxor = []
            result = ""
            for i in range(len(bininp)):
                x = random.randint(0,1)
                pubxor += str(x)
            for i in range(len(bininp)):
                x = random.randint(0,1)
                privxor += str(x)
            pos = 0
            for i in bininp:
                if privxor[pos] == "1":
                    privencry.append("1")
                elif privxor[pos] == "0":
                    privencry.append(str(i))
                pos += 1
            pos1 = 0
            for i in privencry:
                if pubxor[pos1] == "1":
                    pubencry.append("1")
                elif pubxor[pos1] == "0":
                    pubencry.append(str(i))
                pos1 += 1
            result = "".join(pubencry)
            pubxor = int(''.join(map(str, pubxor)))
            privxor = int(''.join(map(str, privxor)))
            line1 = ("Public key:",pubxor," Private key:",privxor)
            line2 = ("\nOriginal:",bininp,"\nEncrypted:",result)
            answer = line1 + line2
            if check == True:
                return answer
            else:
                print(answer)
            
    ############################################################asymetrical decryption###
    def decrypt(*argv): # can take input of: encrypted binary, public key, private key
        loop = 0
        check = False
        for arg in argv:
            check = True
            if loop == 0:
                encry_key = str(arg)
                loop += 1
            if loop == 1:
                public_key = str(arg)
                loop += 1
            if loop == 2:
                private_key = str(arg)
                loop += 1
        if check != True:
            encry_bin = input("Enter the encrypted binary:")
            public_key = input("Enter public key:")
            private_key = input("Enter private key:")
        intermediate_result = []
        final_result = []
        for i in range(len(encry_bin)):
            if public_key[i] == "1":
                xor_result = int(encry_bin[i]) ^ int(private_key[i])
                intermediate_result.append(str(xor_result))
            elif public_key[i] == "0":
                intermediate_result.append(encry_bin[i])
        for i in range(len(intermediate_result)):
            xor_result = int(intermediate_result[i]) ^ int(private_key[i])
            final_result.append(str(xor_result))
        intermediate_binary = "".join(intermediate_result)
        decrypted_binary = "".join(final_result)
        answer = ("Intermediate binary after public key XOR:",intermediate_binary,"\nFinal decrypted binary after private key XOR:",decrypted_binary)
        if check == True:
            return answer
        else:
            print(answer)

###########################################################################################################################Caesar###
class ceasar:
    ############################################################ceasar encryption###
    def encrypt(*argv): # can take input of: phrase, "random" or "custom" shift, if custom also custom number
        ans = []
        loop = 0
        check = False
        for arg in argv:
            check = True
            if loop == 0:
                usrinp = str(arg)
                loop += 1
            if loop == 1:
                choi = str(arg)
                if choi == "custom":
                    loop += 1
            if loop == 2:
                n = int(arg)
        if check != True:
            usrinp = input("Enter phrase to input: ")
            choi = input("Would you like a random or a custom shift number?\n:>1) Random\n:>2) Custom")
        if choi == "1" or choi == "random":
            n = random.randint(1,25)
        elif choi == "2" or choi == "custom":
            if n == "":
                n = int(input("Enter your custom cypher shift number:"))
        alphabet = string.ascii_lowercase
        for i in range(len(usrinp)):
            ch = usrinp[i]
            if ch==" ":
                ans.append(" ")
            elif (ch.isupper()):
                ans.append(str(chr((ord(ch) + n-65) % 26 + 65)))      
            else:
                ans.append(str(chr((ord(ch) + n-97) % 26 + 97)))
                an = ''.join(ans)
        answer = ("Plain Text is : " + usrinp+"\nShift pattern is : " + str(n)+"\nCipher Text is : " + str(an))
        if check == True:
            return answer
        else:
            print(answer)
        
    ############################################################ceasar decryption###
    def decrypt(*argv): # can take input of: encrypted message, "all" or "custom" cypher key, if custom then also custom key
        import string
        alphabet = string.ascii_lowercase # "abcdefghijklmnopqrstuvwxyz"
        loop = 0
        check = False
        for arg in argv:
            check = True
            if loop == 0:
                encrypted_message = str(arg)
                loop += 1
            if loop == 1:
                choi = str(arg)
                if choi == "custom":
                    loop += 1
            if loop == 2:
                n = int(arg)
        if check != True:
            encrypted_message = input("Enter the message you would like to decrypt: \n").strip()
            choi = (input("Would you like to generate every cypher possible or a custom key? \n:>1) every cypher\n:>2) custom key"))
        if choi == "1" or choi == "all":
            loop = 1
            key = 1
        elif choi == "2" or choi == "custom":
            if key == "":
                key = int(input("Enter custom key:"))
            loop = 26
        answer = ""
        while loop <= 26:
            decrypted_message = ""
            for c in encrypted_message:

                if c in alphabet:
                    position = alphabet.find(c)
                    new_position = (position - key) % 26
                    new_character = alphabet[new_position]
                    decrypted_message += new_character
                else:
                    decrypted_message += c
            answ = ("\nshift pattern:"+str(key)+" decyphered message: "+decrypted_message)
            answer += answ
            key += 1
            loop += 1
        if check == True:
            return answer
        else:
            print(answer)
            
############################################################morse encryption###
def english2morse(*argv): # can take: phrase
    usrinp = []
    ans = ""
    loop = 0
    check = False
    for arg in argv:
        check = True
        if loop == 0:
            usrinp = arg
    if check != True:
        usrinp = input("Enter phrase to be translated\n")
    for i in usrinp:
        if i == " ":
            ans += "  "
        else:
            x = alphabet.index(i)
            y = morse[x]
            ans += str(f"{y} ")
    dhwi = (f"{ans}")
    if check == True:
        return dhwi
    else:
        print(dhwi)
############################################################morse decryption###
def morse2english(*argv): # can take: morse phrase
    usinp = []
    sortd = []
    loop = 0
    check = False
    for arg in argv:
        check = True
        if loop == 0:
            usrinp = arg
    if check != True:
        usrinp = input("Enter morse to be translated\n")
    sortd.split(" ")
    print(sortd)
    for i in sortd:
        if i == "  ":
            ans += " "
        else:
            x = morse.index(i)
            y = alphabet[x]
            ans += str("")
    xx = (f"{ans}")
    if check == True:
        return xx
    else:
        print(xx)

###########################################################################################################################ATBASH###
class atbash:
    ############################################################atbash encryption###
    def encrypt(*argv): # can take: phrase
        usrinp = []
        backwards = []
        ans = ""
        for i in alphabet:
            backwards.append(i)
        backwards.reverse()
        loop = 0
        check = False
        for arg in argv:
            check = True
            if loop == 0:
                usrinp = arg
        if check != True:
            usrinp = input("Enter the phrase you would like to encrypt:")
        for i in usrinp:
            if i == " ":
                ans += " "
            else:
                y = alphabet.index(i)
                x = backwards[y]
                ans += str(x) 
        if check == True:
            return ans
        else:
            print(ans)
            
    ############################################################atbash decryption###
    def decrypt(*argv): # can take: phrase
        usrinp = []
        backwards = []
        ans = ""
        for i in alphabet:
            backwards.append(i)
        backwards.reverse()
        loop = 0
        check = False
        for arg in argv:
            check = True
            if loop == 0:
                usrinp = arg
        if check != True:
            usrinp = input("Enter the phrase you would like to decrypt:")
        for i in usrinp:
            if i == " ":
                ans += " "
            else:
                y = backwards.index(i)
                x = alphabet[y]
                ans += str(x) 
        if check == True:
            return ans
        else:
            print(ans)

###########################################################################################################################KEYBOARD###
class keyboard:
    ############################################################keyboard code encryption###
    def encrypt(*argv):
        usrinp = []
        ans = ""
        loop = 0
        check = False
        for arg in argv:
            check = True
            if loop == 0:
                usrinp = arg
        if check != True:
            usrinp = input("EDDIE:> Enter phrase you would like to encrypt\nUSER:>")
        for i in usrinp:
            if i == " ":
                ans += " "
            else:
                y = alphabet.index(i)
                x = keyboard[y]
                ans += str(x)
        if check == True:
            return ans
        else:
            print(ans)

    ############################################################keyboard code decryption###
    def decrypt(*argv): # can take: phrase
        usrinp = []
        ans = ""
        loop = 0
        check = False
        for arg in argv:
            check = True
            if loop == 0:
                usrinp = arg
        if check != True:
            usrinp = input("Enter phrase you would like to decrypt:")
        for i in usrinp:
            if i == " ":
                ans += " "
            else:
                y = keyboard.index(i)
                x = alphabet[y]
                ans += str(x)
        if check == True:
            return ans
        else:
            print(ans)

###########################################################################################################################SORT CLASS###
class sort:
    def bogo(*argv): # can take: 
        import random
        data = []
        sorteddata = []
        loop = 0
        check = False
        for arg in argv:
            check = True
            if loop == 0:
                count = arg
        if check != True:
            count = int(input("enter data amt"))
        while count != 0:
            x = random.randint(1,100)
            data.append(x)
            sorteddata.append(x)
            count -= 1
        sorteddata.sort()
        amt = len(data)
        from time import sleep
        from tqdm import tqdm
        y = amt**amt
        for i in tqdm(range(y)):
            while sorteddata != data:
                r1 = random.randint(0,(amt-1))
                r2 = random.randint(0,(amt-1))
                id1 = data[r1]
                id2 = data[r2]
                data[r1] = id2
                data[r2] = id1
        if check == True:
            return data
        else:
            print(data)
            
    def bubble(*argv): # can take: list
        loop = 0
        lyst = []
        check = False
        for arg in argv:
            check = True
            if loop == 0:
                lyst = arg
        if check != True:
            while True:
                xx = input("Enter next nuber in list (press x and enter to finish):")
                if xx == "x":
                    break
                else:
                    lyst.append(int(xx))
        i = 0
        while True:
            try:
                if i == len(lyst):
                    i = 0
                elif lyst[i] > lyst[(i+1)]:
                    print("switch")
                    x = lyst[i]
                    y = lyst[(i+1)]
                    lyst[i] = y
                    lyst[(i+1)] = x
                    print(lyst)
                else:
                    print("non-switch")
                    print(lyst)
                print(i)
                i +=1
            except:
                i = 0
            finally:
                prev = 0
                solved = True
                for i in lyst:
                    if i > prev:
                        prev = i
                    else:
                        solved = False
                if solved == True:
                    break
        if check == True:
            return lyst
        else:
            print(lyst)
    
    def stalin(*argv): # can take: list
        not_sorted = []
        result = []
        import random
        loop = 0
        check = False
        for arg in argv:
            check = True
            if loop == 0:
                not_sorted = arg
        if check != True:
            while True:
                xx = input("Enter next nuber in list (press x and enter to finish):")
                if xx == "x":
                    break
                else:
                    not_sorted.append(int(xx))
        prev = 0
        for i in not_sorted:
            if i > prev:
                result.append(i)
                print(i,">",prev)
                prev = i
            else:
                print(i,"<",prev)
        print(result)

###########################################################################################################################SEARCH CLASS###
class search:
    def linear(*argv): # can take: list, number
        loop = 0
        lyst = []
        check = False
        for arg in argv:
            check = True
            if loop == 0:
                lyst = arg
                loop += 1
            if loop == 1:
                find = int(arg)
        if check != True:
            while True:
                xx = input("Enter next nuber in list (press x and enter to finish):")
                if xx == "x":
                    break
                else:
                    lyst.append(int(xx))
            find = int(input("Enter number to look for"))
        num = 0
        for i in lyst:
            num += 1
            if i == find:
                break
        if check == True:
            return num
        else:
            print("Found:",find,"at position:",num,"in list")
            
#######################################################################################################################################################
if __name__ == "__main__":
    supercheck = True
    
    
    
    
    
    
    
