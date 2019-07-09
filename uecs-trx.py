#! /usr/bin/python3
#coding: utf-8
#
# Ver: 0.03
# Date: 2019/07/08
# Author: horimoto@holly-linux.com
#
import datetime
import time
import configparser
import netifaces
import threading
import xml.etree.ElementTree as ET
import uuid
from socket import *
import tkinter as tk
from tkinter import messagebox
#import tkinter.ttk as ttk

XML_HEADER  = "<?xml version=\"1.0\"?>"
UECS_HEADER = "<UECS ver=\"1.00-E10\">"
HOST = netifaces.ifaddresses('enp3s0')[netifaces.AF_INET][0]['addr']
ADDRESS = netifaces.ifaddresses('enp3s0')[netifaces.AF_INET][0]['broadcast']
print("HOST,ADDRESS={0},{1}".format(HOST,ADDRESS))
CPORT = 16529
DPORT = 16520
#config = configparser.ConfigParser()
#config.read('/etc/uecs/config.ini')

def menu_about():
    messagebox.showinfo('ABOUT','UECS送受信機 Version: 0.03')

def btn_quit():
    quit()

rxp = tk.Tk()
rxp.title("受信機")
rxp.geometry("1280x600")
mainFrame = tk.Frame(rxp)
rxmenu = tk.Menu(rxp)
rxp.configure(menu=rxmenu)

rxmenu_file   = tk.Menu(rxmenu,tearoff=False)
rxmenu_format = tk.Menu(rxmenu,tearoff=False)
rxmenu_help   = tk.Menu(rxmenu,tearoff=False)

rxmenu.add_cascade(label='ファイル', underline=0, menu=rxmenu_file)
rxmenu.add_cascade(label='出力書式', underline=0, menu=rxmenu_format)
rxmenu.add_cascade(label='ヘルプ',   underline=0, menu=rxmenu_help)
#
rxmenu_file.add_command(label='このプログラムについて',command=menu_about)
rxmenu_file.add_separator()
rxmenu_file.add_command(label='終了',command=btn_quit)
#
addtod = tk.BooleanVar()
shorttext = tk.BooleanVar()
shortesttext = tk.BooleanVar()
hidencnd = tk.BooleanVar()
addtod.set(False)
shorttext.set(False)
shortesttext.set(False)
hidencnd.set(False)

rxmenu_format.add_checkbutton(label='日付を追加する',variable=addtod)
rxmenu_format.add_checkbutton(label='短縮表示',variable=shorttext)
rxmenu_format.add_checkbutton(label='極超短縮表示',variable=shortesttext)
rxmenu_format.add_checkbutton(label='cndを表示しない',variable=hidencnd)
#

rxmenu_help.add_command(label='このプログラムについて',command=menu_about)
mainFrame.grid()

titleFrame = tk.Frame(mainFrame)
label1 = tk.Label(titleFrame,text="UECS通信機 受信電文")
label1.pack(side=tk.TOP)
titleFrame.grid(column=0,row=0)

optionFrame = tk.Frame(mainFrame)
optlbl1 = tk.Label(optionFrame,text="受信PORT")
dpd = tk.BooleanVar()
dpd.set(True)
cpd = tk.BooleanVar()
cpd.set(True)

cb_dport = tk.Checkbutton(optionFrame,variable=dpd,text="16520")
cb_cport = tk.Checkbutton(optionFrame,variable=cpd,text="16529")

optlbl1.pack(side=tk.LEFT)
cb_dport.pack()
cb_cport.pack()
optionFrame.grid(column=0,row=1)

textFrame = tk.Frame(mainFrame,width=1270,height=200)
textFrame.grid()
rtext = tk.Text(textFrame,bg='white',width=180,height=20,relief="groove")
rtext.pack(side=tk.LEFT,padx=(3,0),pady=(3,3))
scrollbar = tk.Scrollbar(textFrame,orient=tk.VERTICAL,command=rtext.yview)
scrollbar.pack(side=tk.RIGHT,fill="y")
rtext["yscrollcommand"] = scrollbar.set

class DataUDP(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.data = 'hoge'
        self.kill_flag = False
        # line information
        self.HOST = HOST
        #self.HOST = "0.0.0.0"
        self.DPORT = DPORT
        self.BUFSIZE = 512
        #self.DADDR = (gethostbyname(self.HOST), self.DPORT)
        self.DADDR = (self.HOST,self.DPORT)
        print("HOST={0}".format(gethostbyname(self.HOST)))
        # bind
        # DATA PORT
        self.udpDSock = socket(AF_INET, SOCK_DGRAM)
        #self.udpDSock.setsockopt(SOL_SOCKET,SO_REUSEADDR|SO_BROADCAST,1)
        self.udpDSock.setsockopt(SOL_SOCKET,SO_REUSEPORT|SO_BROADCAST,1)
        self.udpDSock.bind(self.DADDR) # HOST, PORTでbinding
        # Get Network information by myself
        self.ipaddress = netifaces.ifaddresses('enp3s0')[netifaces.AF_INET][0]['addr']
        self.node = uuid.getnode()
        self.mac = uuid.UUID(int=self.node)
        self.macaddr = self.mac.hex[-12:].upper()

    def run(self):
        v = {}
        while True:
            a=datetime.datetime.now()
            s="{0:4d}/{1:02d}/{2:02d} {3:02d}:{4:02d}:{5:02d}"\
                .format(a.year,a.month,a.day,a.hour,a.minute,a.second)

            # try:
            ddata, self.daddr = self.udpDSock.recvfrom(self.BUFSIZE) # データ受信
            dtext = ddata.decode('utf-8')
            self.ddata = dtext.rstrip("\n")
            root = ET.fromstring(self.ddata)
            for c1 in root:
                sp = c1.tag
                v[sp] = c1.text
                #print("{0}={1}".format(sp,v[sp]))
                for c2 in c1.attrib:
                    v[c2] = c1.attrib[c2]
                    #print("c2[{0}]={1}".format(c2,v[c2]))
            shtype = v['type'][0:3]
            if (dpd.get()):
                if (hidencnd.get() and (shtype=='cnd')):
                    pass
                else:
                    if (not shortesttext.get()):
                        if (shorttext.get()):
                            dtext = dtext.replace(XML_HEADER+UECS_HEADER,"")
                            dtext = dtext.replace("</UECS>","")
                    else:
                        dtext = "{0},{1},{2},{3},{4},{5},{6}"\
                                .format(v['type'],v['room'],v['region'],v['order'],\
                                        v['priority'],v['DATA'],v['IP'])
                        
                    if (addtod.get()):
                        txt = "{0} {1}".format(s,dtext)
                    else:
                        txt = "{0}".format(dtext)
                    rtext.insert('end',txt+'\n')
                    rtext.see('end')
                
            print(txt)
            print("dport={0}".format(dpd.get()))

class CtrlUDP(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.data = 'hoge'
        self.kill_flag = False
        # line information
        self.HOST = ""
        self.CPORT = CPORT
        self.BUFSIZE = 512
        self.CADDR = (gethostbyname(self.HOST), self.CPORT)
        # bind
        # CONTROL PORT
        self.udpCSock = socket(AF_INET, SOCK_DGRAM)
        self.udpCSock.setsockopt(SOL_SOCKET,SO_REUSEPORT,1)
        self.udpCSock.bind(self.CADDR) # HOST, PORTでbinding
        # Get Network information by myself
        self.ipaddress = netifaces.ifaddresses('enp3s0')[netifaces.AF_INET][0]['addr']
        self.node = uuid.getnode()
        self.mac = uuid.UUID(int=self.node)
        self.macaddr = self.mac.hex[-12:].upper()

    def run(self):
        v = {}
        while True:
            a=datetime.datetime.now()
            s="{0:4d}/{1:02d}/{2:02d} {3:02d}:{4:02d}:{5:02d}"\
                .format(a.year,a.month,a.day,a.hour,a.minute,a.second)

            # try:
            ddata, self.daddr = self.udpCSock.recvfrom(self.BUFSIZE) # データ受信
            dtext = ddata.decode('utf-8')
            self.ddata = dtext.rstrip("\n")
            # root = ET.fromstring(self.ddata)
            # for c1 in root:
            #     sp = c1.tag
            #     v[sp] = c1.text
            #     #print("{0}={1}".format(sp,v[sp]))
            #     for c2 in c1.attrib:
            #         v[c2] = c1.attrib[c2]
            #         #print("c2[{0}]={1}".format(c2,v[c2]))
            # shtype = v['type'][0:3]
            # if (hidencnd.get() and (shtype=='cnd')):
            #     pass
            # else:
            if (cpd.get()):
                if (not shortesttext.get()):
                    if (shorttext.get()):
                        dtext = dtext.replace(XML_HEADER+UECS_HEADER,"")
                        dtext = dtext.replace("</UECS>","")
                else:
                    dtext = "{0},{1},{2},{3},{4},{5},{6}"\
                            .format(v['type'],v['room'],v['region'],v['order'],\
                                    v['priority'],v['DATA'],v['IP'])
                
                if (addtod.get()):
                    txt = "{0} {1}".format(s,dtext.rstrip("\n"))
                else:
                    txt = "{0}".format(dtext.rstrip("\n"))
                rtext.insert('end',txt+'\n')
                rtext.see('end')
                
            print(txt)
            print("cport={0}  dport={1}".format(cpd.get(),dpd.get()))


if __name__ == '__main__':
    dtudp = DataUDP()
    dtudp.setDaemon(True)
    dtudp.start()
    ctudp = CtrlUDP()
    ctudp.setDaemon(True)
    ctudp.start()
    rxp.mainloop()

    while True:
        if not dtudp.data:
            pass
        # print(th.data)
       # time.sleep(0.1)
            
