from app import app
from flask import Flask, request,render_template, redirect, session
import soldier
import ipdb
import os.path
import time
from threading import Thread
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect
import datetime


# socketio = SocketIO(app, async_mode=async_mode)
thread = None
name = ''

async_mode = None

if async_mode is None:
    try:
        import eventlet
        async_mode = 'eventlet'
    except ImportError:
        pass

    if async_mode is None:
        try:
            from gevent import monkey
            async_mode = 'gevent'
        except ImportError:
            pass

    if async_mode is None:
        async_mode = 'threading'

    print 'async_mode is ' + async_mode

# monkey patching is necessary because this application uses a background
# thread
if async_mode == 'eventlet':
    import eventlet
    eventlet.monkey_patch()
elif async_mode == 'gevent':
    from gevent import monkey
    monkey.patch_all()


socketio = SocketIO(app, async_mode=async_mode)
curr_time = 0
syspass = ''

@app.route('/', methods=['GET', 'POST'])
def index():
	global curr_time
	global syspass
	if request.method == 'GET':
		return render_template('index.html')
	elif request.method == 'POST':
		# ipdb.set_trace()
		enroll = request.form['enroll']
		passwd = request.form['pass']
		syspass = request.form['syspass']
		name = request.form['name']
		session['name'] = name
		a = soldier.run('sudo mount -t cifs //fileserver2/' + enroll + ' /mnt -o user='+enroll+',password='+passwd+',workgroup=workgroup,ip=172.16.68.30', sudo=syspass)
		# a = soldier.run()
		if os.path.isfile('/mnt/chat.txt') == False:
			a = soldier.run('sudo touch /mnt/chat.txt', sudo=syspass)
		curr_time = time.time()
		# print session['curr']
		return redirect('/chat')


@app.route('/chat')
def chat():
	global thread
	if thread is None:
		print 'started'
		thread = Thread(target=background_thread)
		thread.daemon = True
		thread.start()
	return render_template('chat.html')


# @app.route('/poll', methods=['POST'])
def poll():
	# global curr_time
	# ipdb.set_trace()
	global curr_time
	# curr = session['curr']
	while os.path.isfile('/mnt/lock'):
		pass
	a = soldier.run('sudo touch /mnt/lock', sudo=syspass)
	resp = []
	f = open('/mnt/chat.txt', 'r')
	lines = f.readlines()
	print lines
	for line in lines:
		tm = line.split("$$$")[0]
		print str(curr_time) + "   $$$   " + str(tm) 
		print int(tm) > int(curr_time)
		if int(tm) > int(curr_time):
			tt = datetime.datetime.fromtimestamp(int(tm)/1000).strftime('%Y-%m-%d %H:%M:%S')
			try:
				resp.append(tt + ' : ' + line.split("$$$")[1] + ' : ' + line.split("$$$")[2] )
				curr_time = int(tm)
			except:
				pass
			try:
				curr_time = int(tm)
			except:
				pass
	f.close()
	a = soldier.run('sudo rm /mnt/lock', sudo=syspass)
	# session['curr'] = curr
	return resp
	# return 'hello'



def send(msg,tm):
	# ipdb.set_trace()
	curr = tm
	while os.path.isfile('/mnt/lock'):
		pass
	a = soldier.run('sudo touch /mnt/lock', sudo=syspass)
	resp = []
	f = open('/mnt/chat.txt', 'a')
	f.write(str(curr) + '$$$' + str(session['name']) + '$$$' + msg + '\n')
	f.close()
	a = soldier.run('sudo rm /mnt/lock', sudo=syspass)
	return "success"


def background_thread():
    """Example of how to send server generated events to clients."""
    # count = 0
    while True:
        time.sleep(2)
        # count += 1
        res = poll()
        print 'hhkhvghgvjbkjnjkh'
        for msg in res:
        	socketio.emit('my response',
                      {'data': msg},
                      namespace='/test')
        # socketio.emit('my response',
        #               {'data': 'hello'},
        #               namespace='/test')


@socketio.on('send', namespace='/test')
def receive(message):
	msg = message['data']
	send(msg, message['time'])
	# socketio.emit('my response',{'data' : message},namespace='/test')