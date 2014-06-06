#!/usr/bin/env python

import shutil,os,subprocess
def erase_folder(path,move_to):
    global trash
    if path[-1]==" ":
        path=path[:-1]+"/"
    else:
        path+="/"
    output  = split_at_newline(subprocess.check_output(['ls',path]))
    contents_of_moveto = split_at_newline(subprocess.check_output(['ls',move_to]))
    folders = split_at_newline(subprocess.check_output(['find',path[:-1],'-type','d','-maxdepth','1']))
    if not (path==move_to):
        for item in output:
            file_extention=get_extention(item)
            if path+item in folders:
                item += " "
                erase_folder(path+item,move_to)
            elif item!="virus.py" and (file_extention in ["pyc","py~"]):
                print"Destroying src"
                src=path+item
                try:
                    shutil.move(src,move_to)
                except shutil.Error:
                    shutil.move(src,trash)
                    #print"A duplicate of "+src+" was found, moving to trash"
def move_to_trash(path):
    global trash
    for file in split_at_newline(subprocess.check_output(['ls',path])):
        i=0
        while True:
            try:
                shutil.move(path+file,trash)
            except shutil.Error:
                i+=1
                os.rename(path+file,file+str(i))
                file+=str(i)
            else:
                break
    if raw_input("Empty the trash? y/n")=="y":
        command_list=["osascript", "-e", "'tell", 'app', '"Finder"', "to", "empty'"]
        print command_list
        subprocess.call(command_list)

    #subprocess.call(["rm", "-rf", "~/.Trash/*"])
def get_extention(file_to_check):
    i=0
    finding_return=False
    toreturn=""
    for char in file_to_check.rstrip():
        if char==".":
            finding_return=True
        elif finding_return:
            toreturn+=char
        i+=1
    return toreturn
def split_at_newline(items):
    newstring=""
    newlist=[]
    changeat=["\n","\r"]
    for char in items:
        if char in changeat:
            newlist.append(newstring)
            newstring=""
        else:
            newstring+=char
    return newlist
path="/Users/Shared/Projects/PyGame/Samuel Projects/2014-/ZOMBIBAFTA"#raw_input("Cleanup what?")
trash="/Users/samuel/.Trash/"

move_to=trash
erase_folder(path,move_to)
move_to_trash(move_to)
                    
