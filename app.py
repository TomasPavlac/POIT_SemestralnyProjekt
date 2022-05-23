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

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()

#Serial comunnication
ser = serial.Serial("/dev/ttyS0")

ser.baudrate = 9600
    
def background_thread(args):
    dataList = []
    count = 0           
    while True:
        read_ser = ser.readline()
        if args:
            temperature = dict(args).get('Temperature')
            luminosity = dict(args).get('Luminosity')
            humidity = dict(args).get('Humidity')
            dbV = dict(args).get('db_value')
            btnV = dict(args).get('btn_value')
        else:
            temperature = 1
            luminosity = 1
            humidity = 1
            btnV = 'nieco'
            dbV = 'nieco'
        count += 0.5
        readSerialData = read_ser.decode()
        splitDataArr = readSerialData.split(",")
        lastElement = splitDataArr[2].replace("\r\n","")
        finalArr = np.array([splitDataArr[0],splitDataArr[1],lastElement])
        floatFinalArr = finalArr.astype(np.float)
        t = time.asctime(time.localtime(time.time()))
        print(floatFinalArr)
        if btnV == "start":
            socketio.emit('my_response',
                        {'Temperature': floatFinalArr[0],"Luminosity": floatFinalArr[1], 'Humidity': floatFinalArr[2],"Count": count},
                        namespace='/test')

        socketio.sleep(1.5)

@app.route('/',methods=['GET', 'POST'])
def tabs():
    return render_template('tabs.html',async_mode=socketio.async_mode)
  
@socketio.on('my_event', namespace='/test')
def test_message(message):   
    session['Temperature'] = message['temp_value']
    session['Luminosity'] = message['lum_value']
    session['Humidity'] = message['hum_value']
    print(session['Humidity'])
    emit('my_response',
         {'Temperature': session['Temperature'], 'Luminosity': session['Luminosity'],'Humidity': session['Humidity']})

@socketio.on('btn_event', namespace='/test')
def value_message(message):   
    session['btn_value'] = message['value'] 
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