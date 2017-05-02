import socket
from flask import Flask, render_template, request, jsonify, session, redirect
import os
import datetime
import time
import pandas as pd
from celery import Celery

def make_celery(app):
    celery = Celery(app.import_name, backend=app.config['CELERY_RESULT_BACKEND'], broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return  TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
host = '127.0.0.1'
port = 1518
sock1.bind(('127.0.0.1', 1516))
sock2.bind(('127.0.0.1', 1519))
app = Flask(__name__)
app.config['SECRET KEY'] = 'secret!'
app.secret_key = os.urandom(24)
app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='redis://localhost:6379'
)
celery = make_celery(app)
@app.route('/')
def index():
    if 'username' in session:
        return render_template('index.html', username=session['username']) 
    else:
        return render_template('auth.html') 


@celery.task(name="runScript")
def runScript(fromTime, toTime):
    if datetime.datetime.now() == fromTime:
        while datetime.datetime.now() <= toTime:
            data = sock2.recv(1024)
            result = {i: int.from_bytes(data[24 + i * 4:27 + (i) * 4], byteorder='little') for i in range(0, 180)}
            df = pd.DataFrame.from_dict(result, orient='index')
            if not os.path.isdir(f"{datetime.datetime.now().strftime('%d.%m.%y')}"):
                os.makedirs(f"{datetime.datetime.now().strftime('%d.%m.%y')}")
            df = df.transpose()
            df.to_csv(f"{datetime.datetime.now().strftime('%d.%m.%y')}/{datetime.datetime.now().strftime('%H_%M_%S')}.txt", index=False, header=True, sep='\t', mode='a+')
            time.sleep(1)

@app.route('/signup', methods=["POST"])
def signUp():
    if request.method == 'POST':
        regData = request.get_json(silent=True)['data']
        username = regData[0]
        password = regData[1]
        print(regData)
        with open('users.txt', 'a+') as users:
            users.write(f"{username} {password}\n")
        return redirect('/')
    return jsonify({'message': 'Неверные данные'}), 400
  



@app.route('/signin', methods=["POST"])
def signIn():
    if request.method == 'POST':
        authData = request.get_json(silent=True)['data']
        users_dict = {}
        with open('users.txt', 'r') as users:
            for line in users:
                users_dict[line.split()[0]] = line.split()[1]
        if authData[0] in users_dict and users_dict[authData[0]] == authData[1]:
            session['username'] = authData[0]
            return jsonify(text='success')
    return jsonify(text='sucess')



@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/send', methods=["POST"])
def sendMassage():
    res = request.get_json(silent=True)['data']
    data = [int(x) for x in res[1:-5]]
    bytes_ = [[0,0],[0,0],[0,0],[0,0],[0,0],0,0,0]
    for i in range(0, len(data)):
        if data[i] == -15:
            bytes_[i//2][not i%2] = '0000'
        if data[i] == -14:
            bytes_[i//2][not i%2] = '1000'
        if data[i] ==  -13:
            bytes_[i//2][not i%2] = '0100'
        if data[i] == -12:
            bytes_[i//2][not i%2] = '1100'
        if data[i] == -11:
            bytes_[i//2][not i%2] = '0010'
        if data[i] == -10:
            bytes_[i//2][not i%2] = '1010'
        if data[i] == -9:
            bytes_[i//2][not i%2] = '0110'
        if data[i] == -8:
            bytes_[i//2][not i%2] = '1110'
        if data[i] == -7:
            bytes_[i//2][not i%2] = '0001'
        if data[i] == -6:
            bytes_[i//2][not i%2] = '1001'
        if data[i] == -5:
            bytes_[i//2][not i%2] = '0101'
        if data[i] == -4:
            bytes_[i//2][not i%2] = '1101'
        if data[i] == -3:
            bytes_[i//2][not i%2] = '0011'
        if data[i] == -2:
            bytes_[i//2][not i%2] = '1011'
        if data[i] == -1:
            bytes_[i//2][not i%2] = '0111'
        if data[i] == 0:
            bytes_[i//2][not i%2] = '1111'

    result = [int(''.join(x),2) for x in bytes_[0:-3]]
    result.extend([0,0,0])
    tmp = [x for x in bin(result[-3])[2::].zfill(8)]
    if res[-2] == 1:
        tmp[0] = '1'
    if res[-3] == 1:
        tmp[4] = '1'
    if res[-4] == 1:
        tmp[3] = '1'
    if res[-5] == 1:
        tmp[2] = '1'
    tmp[5::] = bin(int(res[-1]))[2::].zfill(3)
    result[-3] = int(''.join(tmp), 2)
    result[-1] = abs(int((float(res[0])+15.5)*2))
    setState = bytearray(16)
    setState[0] = 3
    setState[4:7] = (1517).to_bytes(4, byteorder='little')
    setState[8::] = result
    sock.sendto(setState, ('127.0.0.1', 1517))
    return jsonify({'message': 'success'})


@app.route('/get')
def getMessage():
    result = []
    setState = bytearray(16)
    setState[0] = 1
    setState[4:7] = (1516).to_bytes(4, byteorder='little')
    sock1.sendto(setState, ('127.0.0.1', 1517))
    recieve = [bin(x)[2::].zfill(8) for x in sock1.recv(1024)]
    tmp = [[x[4::], x[0:4]] for x in recieve[8::]]
    data = [[0,0],[0,0],[0,0],[0,0],[0,0],0] 
    for i in range(0, len(tmp) - 3):
        for j in range(0,2):
            if tmp[i][j] == '0000':
                data[i][j] = -15
            elif tmp[i][j] == '1000':  
                data[i][j] = -14
            elif tmp[i][j] == '0100':  
                data[i][j] = -13
            elif tmp[i][j] == '1100':  
                data[i][j] = -12
            elif tmp[i][j] == '0010':  
                data[i][j] = -11
            elif tmp[i][j] == '1010':  
                data[i][j] = -10
            elif tmp[i][j] == '0110':  
                data[i][j] = -9
            elif tmp[i][j] == '1110':  
                data[i][j] = -8
            elif tmp[i][j] == '0001':  
                data[i][j] = -7
            elif tmp[i][j] == '1001':  
                data[i][j] = -6
            elif tmp[i][j] == '0101':  
                data[i][j] = -5
            elif tmp[i][j] == '1101':  
                data[i][j] = -4
            elif tmp[i][j] == '0011':  
                data[i][j] = -3
            elif tmp[i][j] == '1011':  
                data[i][j] = -2
            elif tmp[i][j] == '0111':  
                data[i][j] = -1
            elif tmp[i][j] == '1111':  
                data[i][j] = 0   
    data[-1] = int(recieve[-1], 2) / 2 - 15.5
    for n in range(1,len(data) - 1):
        data[n] = data[n-1] + data[n]    
    result.append(data[-1])
    result.extend(data[-2])  
    status = [0,0,0,0]
    status[0] = recieve[-3][2] == '1'  
    status[1] = recieve[-3][3] == '1'
    status[2] = recieve[-3][4] == '1'
    status[3] = recieve[-3][0] == '1'
    syncRange = int(recieve[-3][-3::], 2)
    return jsonify({'data': result, 'status': status, 'syncRange': syncRange})

@app.route('/graph')
def graphData():
    data = sock2.recv(1024)
    result = [int.from_bytes(data[24+i*4:27+(i)*4], byteorder='little') for i in range(0,180)]
    return jsonify({'data': result})

@app.route('/save', methods=["POST"])
def saveData():
    data = request.get_json()['data']   
    for k in data.keys():
        data[k] = [{item['x']: item['y']} for item in sorted(data[k], key=lambda x: x['x'])]
        data[k] = dict((key, d[key]) for d in data[k] for key in d).items()
        data[k] = ["%d %d" %(item[0], item[1]) for item in data[k]]
    
    df = pd.DataFrame.from_dict(data, orient='index')

    if not os.path.isdir(f"{datetime.datetime.now().strftime('%d.%m.%y')}"):
        os.makedirs(f"{datetime.datetime.now().strftime('%d.%m.%y')}")
    df = df.transpose()
    df.to_csv(f"{datetime.datetime.now().strftime('%d.%m.%y')}/{datetime.datetime.now().strftime('%H_%M_%S')}.txt", index=False, header=True, sep='\t')
    return jsonify({'message': 'Success'})


@app.route("/run", methods=["POST"])
def run():
    data = request.get_json(silent=True)
    fromTime = pd.to_datetime(data['from'])
    toTime = pd.to_datetime(data['to'])
    app.config.update(
        CELERYBEAT_SCHEDULE={
            'add-every-minute': {
                'task': 'runScript',
                'schedule': datetime.timedelta(seconds=10)
            },
        }
    )
    runScript(fromTime, toTime)
    return jsonify({'message': 'Success'})

if __name__ == '__main__':
    app.run(debug=False, use_reloader=False)
