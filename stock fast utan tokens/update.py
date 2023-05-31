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
from email.message import EmailMessage

con = sqlite3.connect("dbb.db", check_same_thread=False)
cur = con.cursor()

sender_email = "altodiscordocount@gmail.com"
password = "jpazjdvnjkwaifxv"



port = 465

context = ssl.create_default_context()

def sendUpdate():
    cur.execute("SELECT * FROM info")
    data = cur.fetchall()
    for x in data:
        mail = x[0]
        ticker = x[1]
        today = datetime.now() - timedelta(days = 1) #sets dates
        yearnow = today.strftime("%Y")
        monthnow = today.strftime("%m")
        daynow = today.strftime("%d")
        weekago = datetime.now() - timedelta(days = 7)
        yearbefore = weekago.strftime("%Y")
        monthbefore = weekago.strftime("%m")
        daybefore = weekago.strftime("%d")
        timenow = f"{yearnow}-{monthnow}-{daynow}"
        timebefore = f"{yearbefore}-{monthbefore}-{daybefore}"
        print(timenow)
        stockInfo = yf.download(ticker, start=timebefore, end=timenow, interval="1h") #downloads stock information
        print(stockInfo['Open'])
        newarray = []
        for x in stockInfo['Open']:
            newarray.append(x) #creates array with only the open market data
        print(newarray)
        ypoints = np.array(newarray)
        plt.plot(ypoints)
        plt.savefig('graph.png') #makes it into graph and saves as png

        newMessage = EmailMessage()
        newMessage['Subject'] = f"Weekly report for {ticker}" #Defining email subject
        newMessage['From'] = sender_email  #Defining sender email
        newMessage['To'] = mail
        with open('graph.png', 'rb') as f:
            image_data = f.read()
            image_type = imghdr.what(f.name)
            image_name = f.name
            newMessage.add_attachment(image_data, maintype='image', subtype=image_type, filename=image_name)
        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.login(sender_email, password)
            server.send_message(newMessage)

schedule.every().wednesday.at("11:02", "Europe/Amsterdam").do(sendUpdate) #sets a schedule to send out the mail

def updateCheck():
    while True:
        schedule.run_pending() #checks for schedule
        time.sleep(1)

updateCheck()