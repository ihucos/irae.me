#!/usr/bin/env python3
from flask import Flask, session, request, redirect
import flask
import os
import atexit
import mmap
import subprocess
from urllib.request import urlopen
import datetime
import json

MASTER_PWD = 'irae ist der beste'
DBFILE = '/tmp/dbfile'

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'xxx')


def get_ip_info(ip):
    resp = session.get(ip)
    if not resp:
        url = 'http://ip-api.com/json/{}'.format(ip)
        resp = urlopen(url).read()
        session[ip] = resp

    return json.loads(resp)

def get_now_repr():
    return datetime.datetime.now().date().isoformat()

def write_msg(ip, nick, msg):
    ip_info = get_ip_info(ip)
    nick = nick.replace('\n', '')
    msg = msg.replace('\n', '')
    with open(DBFILE, 'a') as f:
        f.write('{ip: <16} |{isp: <8} |{time: <8} |{city: <8} |{nick: >12} |{msg}\n'.format(
            ip=ip,
            isp=ip_info['isp'][:8],
            city=ip_info['city'][:8],
            nick=nick[:12],
            time=get_now_repr(),
            msg=msg))


@app.route("/msgs")
def msgs():
    resp_content = subprocess.check_output(['tail', '-n', '100',
                                            DBFILE]).decode()
    resp_content = '\n'.join(reversed(resp_content.splitlines()))
    resp = flask.Response(resp_content)
    resp.headers['Refresh'] = '1; url=/msgs'
    resp.headers['Content-Type'] = 'text'
    return resp


@app.route("/", methods=['GET', 'POST'])
def index():

    nick = request.form.get('nick')
    if nick:
        session['nick'] = nick

    msg = request.form.get('msg')
    if msg:
        write_msg('92.200.58.48' or request.remote_addr,
                  session.get('nick', 'niemand'), msg)

    html = '<html>'

    html += '''<form action="/" method=POST>
        <input autofocus name="msg"" placeholder='deine naricht' size=24 id=focus>
        <input name="nick" placeholder='dein name' size=8>
        <input type="submit" value="press Enter">
        </form>'''

    html += '''<html>
             <iframe src="/msgs" width="100%" height="80%">
               Dein browser ist doof
             </iframe>
        '''
    #html +=    '''<script>
    #    window.scrollTo(0,document.body.scrollHeight);
    #    document.getElementById("focus").focus();
    #    setTimeout(function () { document.location.href = '/' }, 1000);
    #    </script>'''

    return html


if __name__ == "__main__":
    app.run()
"""

@app.route("/login", methods=['GET', 'POST'])
def login():
    if session.get('authenticated') == '1':
        return redirect('/', code=302)
        
    secret = request.form.get('secret')
    if not secret:
        return '''<html>
        <form action="/login" method=POST>
        <input name="secret" type="password" placeholder='Password'>
        <input type="submit" value="Login">
        </form>'''
    elif secret != MASTER_PWD:
        return 'DIGGER, man oh man, wie kann man nur den password vergessen. <a href="/login">versuche es nochmal</a>'
    elif secret == MASTER_PWD:
        session['authenticated'] = '1'
        return redirect('/', code=302)
    else:
        return 'du hast die seite kaputt gemacht'

@app.route("/logout")
def logout():
    session.clear()
    return 'ausgelogt'


@app.route("/msgs", methods=['GET', 'POST'])
def index():

    ###
    # that block is inmportant
    ###
    if not session.get('authenticated') == '1':
        return redirect('/login', code=302)

    with open(DBFILE, 'r') as f:


@app.route("/", methods=['GET', 'POST'])
def index():

    ###
    # that block is inmportant
    ###
    if not session.get('authenticated') == '1':
        return redirect('/login', code=302)


    msg = request.form.get('msg')
    if msg:
        nick = request.form.get('nick', '').replace('\n', '').replace('\0', '')[:8]
        if nick:
            session['nick'] = nick
        msg = msg.replace('\n', '').replace('\0', '')
        with open(DBFILE, 'a') as f:
            f.write('\0'.join([request.remote_addr, session['nick'], msg]) + '\n')

    html = '''<html>
        '''

    html += '<br /><br /><br />'

    html += '''<table border=1>
    <tr><th>ip</th><th>wer</th><th>naricht</th></tr>'''
    for ip, nick, msg in getentries():
        html += '<tr><td>{}</td><td>{}</td><td>{}</td></tr>'.format(
            flask.escape(ip), flask.escape(nick), flask.escape(msg))
    html += '</table>'

    html += '''<form action="/" method=POST>
        <input name="nick" placeholder='wer bist du' size=9>
        <input name="msg"" placeholder='was hast du zu sagen' size=24 id=focus>
        <input type="submit" value="press Enter">
        </form>'''


    html +=    '''<script>
        window.scrollTo(0,document.body.scrollHeight);
        document.getElementById("focus").focus();
        setTimeout(function () { document.location.href = '/' }, 1000);
        </script>'''

    return html

def getentries():
    try:
        with open(DBFILE, 'r') as f:
            while True:
                line = f.readline()
                if not line:
                    break
                yield line.split('\0')
    except FileNotFoundError as exc:
        yield ('file', 'not', 'found')
 
if __name__ == "__main__":
    app.run()

"""
