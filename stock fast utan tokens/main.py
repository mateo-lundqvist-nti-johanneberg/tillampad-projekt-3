import yfinance as yf
import smtplib, ssl
import sqlite3
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import imghdr
import schedule
import time
import re
import datetime
from threading import Thread
from datetime import datetime, timedelta
from email.message import EmailMessage #a lot of imports

con = sqlite3.connect("dbb.db", check_same_thread=False) #connects to database
cur = con.cursor() #creates cursor

sender_email = "altodiscordocount@gmail.com" #email that will be sending the mails

password = "jpazjdvnjkwaifxv" #password



port = 465 #gmail port

context = ssl.create_default_context() #creates default context


def main():
    print("""Hello welcome to stock thing, you want "info" or "signup"? """)
    action = input()
    if action == "info":
        info() #runs info function
    if action == "signup":
        print("what you wanna signup for, weekly report or notification") #what to signup for
        action2 = input()
        if action2 == "weekly":
            update() #runs update function
        if action2 == "notification":
            return "not done yet hahaha"
        
def update():
    print("write your email or write back to go back")
    mail = input()
    mailexists = True
    while mailexists: #input loop until condition is met
        if mail == "back":
            main() #sends you back to main if you want to leave
        cur.execute("SELECT mail FROM info") #fetches every mail in the dababase
        mailinfo = cur.fetchall()
        for x in mailinfo:
            if x[0] == mail:
                print("""Mail is already in use, please reenter mail or write "back" to go back to the menu""") #checks if mail is already in use
                mailexists = True
                mail = input() 
                break
            else:
                mailexists = False
    validMail = False #checks valid mail
    while validMail == False: #input loop again until condition is met
        if re.fullmatch(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', mail): #regex for valid mail
            validMail = True
        else:
            validMail = False
            print("Write a valid mail")
            mail = input()
        
    print("Write a ticker you want to get updates for")
    ticker = input() #Defines ticker
    tickernotexists = True
    while tickernotexists: #one more input loop
        tickertest = yf.Ticker(ticker)
        try:
            tickertest.info #tries to get info from the ticker
        except:
            print("Cannot get info of that ticker, it probably doesn't exist") #raise error if we get error 
            ticker = input()
        else:
            tickernotexists = False
    cur.execute("""INSERT INTO info (mail, ticker, wantweekly) VALUES (?, ?, ?)""", (mail, ticker, 1)) #adds to database
    con.commit()
    print("You have been added to daily updates")


def info():
    ticker = input("write ticker for company ")
    date = input("write date from-to in yyyy-mm-dd format ")
    mail = input("write your mail")
    dBefore = date.split(" ")[0]
    dAfter = date.split(" ")[1]
    stockInfo = yf.download(ticker, start=dBefore, end=dAfter, interval="1h")
    print(stockInfo['Open'])
    newarray = []
    for x in stockInfo['Open']:
        newarray.append(x)
    print(newarray)
    ypoints = np.array(newarray) #creates graph
    plt.plot(ypoints)
    plt.savefig('graph.png') #saves it as png
    
    newMessage = EmailMessage()
    newMessage['Subject'] = f"Information about tesla between {dBefore} and {dAfter}" #Defining email subject
    newMessage['From'] = sender_email  #Defining sender email
    newMessage['To'] = mail #Defining reciever email
    newMessage.set_content('test') #content of mail
    with open('graph.png', 'rb') as f: #opens graph
        image_data = f.read()
        image_type = imghdr.what(f.name)
        image_name = f.name
    newMessage.add_attachment(image_data, maintype='image', subtype=image_type, filename=image_name)
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server: #connects to smtp server
        server.login(sender_email, password)
        server.send_message(newMessage) #sends mail

main()