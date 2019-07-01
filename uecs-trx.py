#! /usr/bin/python3
#coding: utf-8
#
# Ver: 0.01
# Date: 2019/07/01
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
PORT = 16529
PORT = 16520
#config = configparser.ConfigParser()
#config.read('/etc/uecs/config.ini')

def menu_about():
    messagebox.showinfo('ABOUT','UECS送受信機 Version: 0.02')

def btn_quit():
    quit()

rxp = tk.Tk()
rxp.title("受信機")
rxp.geometry("1280x770")
mainFrame = tk.Frame(rxp)
rxmenu = tk.Menu(rxp)
rxp.configure(menu=rxmenu)

rxmenu_file   = tk.Menu(rxmenu,tearoff=False)
rxmenu_format = tk.Menu(rxmenu,tearoff=False)
rxmenu_help   = tk.Menu(rxmenu,tearoff=False)

rxmenu.add_cascade(label='File',   underline=0, menu=rxmenu_file)
rxmenu.add_cascade(label='Format', underline=0, menu=rxmenu_format)
rxmenu.add_cascade(label='Help',   underline=0, menu=rxmenu_help)
#
rxmenu_file.add_command(label='ABOUT',command=menu_about)
rxmenu_file.add_separator()
rxmenu_file.add_command(label='QUIT',command=btn_quit)
#
addtod = tk.IntVar()
rxmenu_format.add_checkbutton(label='ADD TOD',onvalue=1, offvalue=0, variable=addtod)
rxmenu_help.add_command(label='ABOUT',command=menu_about)
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

dport = tk.Checkbutton(optionFrame,variable=dpd,text="16520")
cport = tk.Checkbutton(optionFrame,variable=cpd,text="16529")

optlbl1.pack(side=tk.LEFT)
dport.pack()
cport.pack()
optionFrame.grid(column=0,row=1)

textFrame = tk.Frame(mainFrame,width=1270,height=250)
textFrame.grid()
rtext = tk.Text(textFrame,bg='white',width=180,height=30,relief="groove")
rtext.pack(side=tk.LEFT,padx=(3,0),pady=(3,3))
scrollbar = tk.Scrollbar(textFrame,orient=tk.VERTICAL,command=rtext.yview)
scrollbar.pack(side=tk.RIGHT,fill="y")
rtext["yscrollcommand"] = scrollbar.set

class ServerThread(threading.Thread):
    def __init__(self, PORT):
        threading.Thread.__init__(self)
        self.data = 'hoge'
        self.kill_flag = False
        # line information
        self.HOST = ""
        self.PORT = PORT
        self.BUFSIZE = 512
        self.ADDR = (gethostbyname(self.HOST), self.PORT)
        # bind
        self.udpServSock = socket(AF_INET, SOCK_DGRAM)
        self.udpServSock.setsockopt(SOL_SOCKET,SO_REUSEADDR|SO_BROADCAST,1)
        self.udpServSock.bind(self.ADDR) # HOST, PORTでbinding
        # Get Network information by myself
        self.ipaddress = netifaces.ifaddresses('enp3s0')[netifaces.AF_INET][0]['addr']
        self.node = uuid.getnode()
        self.mac = uuid.UUID(int=self.node)
        self.macaddr = self.mac.hex[-12:].upper()

    def run(self):
        while True:
            a=datetime.datetime.now()
            s="{0:4d}/{1:02d}/{2:02d} {3:2d}:{4:02d}:{5:02d}"\
                .format(a.year,a.month,a.day,a.hour,a.minute,a.second)

            # try:
            data, self.addr = self.udpServSock.recvfrom(self.BUFSIZE) # データ受信
            self.data = data.decode('utf-8').rstrip("\n")
            if (addtod.get()==0):
                txt = "{0}".format(self.data)
            else:
                txt = "{0} {1}".format(s,self.data)
            rtext.insert('end',txt+'\n')
            rtext.see('end')
            print(txt)
            print("cport={0}  dport={1}".format(cpd.get(),dpd.get()))
            root = ET.fromstring(self.data)
            for c1 in root:
                sp = c1.tag
                print("SPd=:{0}:".format(sp))
                for c2 in c1.attrib:
                    print(c2)

#                 if ( sp == 'NODESCAN' ):
#                     self.sdata = "{0}{1}<NODE><NAME>{2}</NAME><VENDER>{3}</VENDER>"\
#                                  "<UECSID>{4}</UECSID><IP>{5}</IP><MAC>{6}</MAC></UECS>".\
#                                  format(XML_HEADER,UECS_HEADER,config['NODE']['name'],config['NODE']['vender'],\
#                                         config['NODE']['uecsid'],self.ipaddress,self.macaddr)
#                     self.udpServSock.sendto(self.sdata.encode('utf-8'),self.addr)

#                 # CCMSCAN
#                 elif ( sp == 'CCMSCAN' ):
#                     ccm = ET.parse(config['NODE']['xmlfile'])
#                     ccmroot = ccm.getroot()
#                     maxx    = len(ccmroot)
#                     maxy    = int((maxx+1)/2)
#                     cpag    = int(c1.attrib['page'])
#                     curx    = int(cpag-1)*2
#                     ccmt    = ccmroot[curx]
#                     ccmnum  = curx+1
#                     if (ccmnum < maxx):
#                         ccmcount = 2
#                     else:
#                         ccmcount = 1
#                     ccmtt   = config[ccmt.text]
#                     ccmdata = "{0}{1}<CCMNUM page=\"{2}\" total=\"{3}\">{4}</CCMNUM>"\
#                               "<CCM No=\"{5}\" room=\"{6}\" region=\"{7}\" order=\"{8}\" "\
#                               "priority=\"{9}\" cast=\"{10}\" unit=\"{11}\" SR=\"{12}\" "\
#                               "LV=\"{13}\">{14}</CCM>"\
#                               .format(XML_HEADER,UECS_HEADER,cpag,maxy,ccmcount,
#                                       ccmnum,ccmtt['room'],ccmtt['region'],ccmtt['order'],
#                                       ccmtt['priority'],ccmt.attrib['cast'],ccmt.attrib['unit'],ccmt.attrib['SR'],
#                                       ccmt.attrib['LV'],ccmt.text)
#                     curx   += 1
#                     ccmnum  = curx+1
#                     if (curx < maxx):
#                         if (ccmroot[curx]!=""):
#                             ccmt  = ccmroot[curx]
#                             ccmtt = config[ccmt.text]
#                             ccmdata += "<CCM No=\"{0}\" room=\"{1}\" region=\"{2}\" order=\"{3}\" "\
#                                        "priority=\"{4}\" cast=\"{5}\" unit=\"{6}\" SR=\"{7}\" "\
#                                        "LV=\"{8}\">{9}</CCM>"\
#                                        .format(ccmnum,ccmtt['room'],ccmtt['region'],ccmtt['order'],
#                                                ccmtt['priority'],ccmt.attrib['cast'],ccmt.attrib['unit'],ccmt.attrib['SR'],
#                                                ccmt.attrib['LV'],ccmt.text)
#                     ccmdata += "</UECS>"
#                     self.udpServSock.sendto(ccmdata.encode('utf-8'),self.addr)
#                 else:
#                     pass
# #            except:
# #                pass


if __name__ == '__main__':
    th = ServerThread(PORT)
    th.setDaemon(True)
    th.start()
    itv = 0     # Interval Counter
    rxp.mainloop()

    while True:
        if not th.data:
            pass
        # print(th.data)
       # time.sleep(0.1)
            
