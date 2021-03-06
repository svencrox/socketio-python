#!/usr/bin/env python
async_mode = None

import time
from flask import Flask, render_template
import socketio
import random
import pika
import csvWrite as csv
from queue import Queue
import _thread
import counting as pc
import latestFile


sio = socketio.Server(logger=True, async_mode=async_mode)
app = Flask(__name__)
app.wsgi_app = socketio.WSGIApp(sio, app.wsgi_app)
app.config['SECRET_KEY'] = 'secret!'
thread = None
csv_queue_thread = None

# start a connection with localhost
credentials = pika.PlainCredentials('guest', 'guest')
connection = pika.BlockingConnection(pika.ConnectionParameters('172.17.9.74', 5672, '/', credentials))
channel = connection.channel()

queue_names = ["decibel_one", "decibel_two", "decibel_three", "decibel_four", 
"decibel_five", "decibel_six", "decibel_seven", "decibel_eight", "decibel_nine", "hello"]
csv_queue = Queue()

# declare queue here
for queue in queue_names:
    channel.queue_declare(queue=queue)

def callback(ch, method, properties, body):
    # print('body:', body)
    # print('ch: ', ch)
    # print('method: ', method.routing_key)
    # print('properties: ', properties)
    DECIBEL_DATA = body.decode()
    ROUTING_KEY = method.routing_key
    csv_queue.put({'data': DECIBEL_DATA, 'routing': ROUTING_KEY})
    sio.emit('my response', {'data': DECIBEL_DATA, 'routing': ROUTING_KEY},
                 namespace='/test')

def callback_camera(ch, method, properties, body):
    # print('body:', body)
    # print('ch: ', ch)
    # print('method: ', method.routing_key)
    # print('properties: ', properties)
    count = 0
    print('received video of size: ' + str(len(body)))
    #open the file that is received at the file location
    with open('./videos/' + str(time.time()) + '.mp4', 'wb') as f:
        f.write(body)

    lat = latestFile.latest()
    print("latest: " + lat)
    count = pc.main("./mobilenet_ssd/MobileNetSSD_deploy.prototxt", "./mobilenet_ssd/MobileNetSSD_deploy.caffemodel",
    lat , "./output/webcam_output.avi")
    print("Total= ", count)
    csv.cameraCount(count)
    sio.emit('my camera', {'data': count, 'routing': method.routing_key},
                 namespace='/test')

def print_csv_queue():
    while True:
        csv_data = csv_queue.get()
        print('CSV data: ', csv_data)
        csv.saveToFile(csv_data)


def background_thread():
    for queue in queue_names:
        if (queue=='hello'):
            channel.basic_consume(callback_camera,queue=queue,no_ack=True)
        else:
            channel.basic_consume(callback,queue=queue,no_ack=True)
    channel.start_consuming()


@app.route('/')
def index():
    global thread
    global csv_queue_thread
    if csv_queue_thread is None:
        csv_queue_thread = _thread.start_new_thread(print_csv_queue, ())
    if thread is None:
        thread = sio.start_background_task(background_thread)
    return render_template('index.html')

@sio.on('my event', namespace='/test')
def test_message(sid, message):
    sio.emit('my response', {'data': message['data']}, room=sid,
             namespace='/test')
    # prints i'm connected
    print('my event: ' + str(message['data']))

@sio.on('connect', namespace='/test')
def test_connect(sid, environ):
    sio.emit('my response', {'data': 'Connected', 'count': 0}, room=sid,
             namespace='/test')


@sio.on('disconnect', namespace='/test')
def test_disconnect(sid):
    print('Client disconnected')


# We kick off our server
if __name__ == '__main__':
    if sio.async_mode == 'threading':
        # deploy with Werkzeug
        app.run(threaded=True)
    elif sio.async_mode == 'eventlet':
         # deploy with eventlet
        import eventlet
        import eventlet.wsgi
        eventlet.wsgi.server(eventlet.listen(('', 5000)), app)
    elif sio.async_mode == 'gevent':
        # deploy with gevent
        from gevent import pywsgi
        try:
            from geventwebsocket.handler import WebSocketHandler
            websocket = True
        except ImportError:
            websocket = False
        if websocket:
            pywsgi.WSGIServer(('', 5000), app,
                              handler_class=WebSocketHandler).serve_forever()
        else:
            pywsgi.WSGIServer(('', 5000), app).serve_forever()
    elif sio.async_mode == 'gevent_uwsgi':
        print('Start the application through the uwsgi server. Example:')
        print('uwsgi --http :5000 --gevent 1000 --http-websockets --master '
              '--wsgi-file app.py --callable app')
    else:
        print('Unknown async_mode: ' + sio.async_mode)