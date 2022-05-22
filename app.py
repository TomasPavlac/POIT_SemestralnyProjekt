from threading import Lock
from flask import Flask, render_template, session, request, jsonify, url_for
from flask_socketio import SocketIO, emit, disconnect
import MySQLdb       
import math
import time
import configparser as ConfigParser
import random
import math
import serial
import numpy as np

async_mode = None

app = Flask(__name__)


# config = ConfigParser.ConfigParser()
# config.read('config.cfg')
# myhost = config.get('mysqlDB', 'host')
# myuser = config.get('mysqlDB', 'user')
# mypasswd = config.get('mysqlDB', 'passwd')
# mydb = config.get('mysqlDB', 'db')
# print(myhost)


app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock() 

#Serial comunnication
ser = serial.Serial("/dev/ttyS0")

ser.baudrate = 9600
    
def background_thread(args):
    dataList = []  
    #db = MySQLdb.connect(host=myhost,user=myuser,passwd=mypasswd,db=mydb)          
    while True:
        read_ser = ser.readline()
        if args:
            temperature = dict(args).get('Temperature')
            luminosity = dict(args).get('Luminosity')
            humidity = dict(args).get('Humidity')
            dbV = dict(args).get('db_value')
        else:
            temperature = 1
            luminosity = 1
            humidity = 1
            dbV = 'nieco' 
        readSerialData = read_ser.decode()
        splitDataArr = readSerialData.split(",")
        lastElement = splitDataArr[2].replace("\r\n","")
        finalArr = np.array([splitDataArr[0],splitDataArr[1],lastElement])
        floatFinalArr = finalArr.astype(np.float)
        print(floatFinalArr)
        socketio.sleep(1.5)
#         if dbV == 'start':
#             dataDict = {
#             "Time": time.time(),
#             "Temperature": splitDataArr[0],
#             "Luminosity": splitDataArr[1],
#             "Humidity of Soil": splitDataArr[2]
#             }
#             dataList.append(dataDict)
#         else:
#             if len(dataList)>0:
#             print(str(dataList))
#             fuj = str(dataList).replace("'", "\"")
#             print(fuj)
#             cursor = db.cursor()
#             cursor.execute("SELECT MAX(id) FROM graph")
#             maxid = cursor.fetchone()
#             cursor.execute("INSERT INTO graph (id, hodnoty) VALUES (%s, %s)", (maxid[0] + 1, fuj))
#             db.commit()
#             dataList = []
#             dataCounter = 0
        if dbV == "start":
            socketio.emit('my_response',
                        {'Temperature': floatFinalArr[0],"Luminosity": floatFinalArr[1], 'Humidity': floatFinalArr[2]},
                        namespace='/test')
#     db.close()

@app.route('/',methods=['GET', 'POST'])
def tabs():
    return render_template('tabs.html',async_mode=socketio.async_mode)
#     
# @app.route('/db')
# def db():
#   db = MySQLdb.connect(host=myhost,user=myuser,passwd=mypasswd,db=mydb)
#   cursor = db.cursor()
#   cursor.execute('''SELECT  hodnoty FROM  graph WHERE id=1''')
#   rv = cursor.fetchall()
#   return str(rv)    
# 
# @app.route('/dbdata/<string:num>', methods=['GET', 'POST'])
# def dbdata(num):
#   db = MySQLdb.connect(host=myhost,user=myuser,passwd=mypasswd,db=mydb)
#   cursor = db.cursor()
#   print(num)
#   cursor.execute("SELECT hodnoty FROM  graph WHERE id=%s", num)
#   rv = cursor.fetchone()
#   return str(rv[0])
    
@socketio.on('my_event', namespace='/test')
def test_message(message):   
    session['Temperature'] = message['temp_value']
    session['Luminosity'] = message['lum_value']
    session['Humidity'] = message['hum_value']
    print(session['Humidity'])
    emit('my_response',
         {'Temperature': session['Temperature'], 'Luminosity': session['Luminosity'],'Humidity': session['Humidity']})
# 
@socketio.on('db_event', namespace='/test')
def db_message(message):   
    session['db_value'] = message['value']    
# 
@socketio.on('disconnect_request', namespace='/test')
def disconnect_request():
    emit('my_response',
         {'Temperature': 'Disconnected!'})
    disconnect()

@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread, args=session._get_current_object())

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=80, debug=True)