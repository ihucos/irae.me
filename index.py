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

    return html


if __name__ == "__main__":
    app.run()
