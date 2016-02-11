# -*- coding: utf-8 -*-
from flask import Flask, render_template, jsonify
import logging
import time
import ast
import os
import pigpio
from transmitter import Transmitter
from collections import namedtuple

app = Flask(__name__)
r = redis.StrictRedis(host='localhost', port=6379, db=0)
Switch = namedtuple('Switch', 'name on_code off_code')
logging.basicConfig(level=logging.DEBUG)

PIN=21

switches = [Switch('Lamp1', 333107, 333116),
            Switch('Unused', 333251, 333260),
            Switch('Kitchen', 333571, 333580),
            Switch('Humidifier', 335107, 335116),
            Switch('Lamp2', 341251, 341260)]

@app.route("/")
def home():
    return render_template('main.html', switches)

@app.route('/switch/:name/:action', methods=['POST'])
def switch(switch_name):
    switch = _find_switch(switch_name)
    if not switch:
        abort(404)
    if action.lower() not in ['on', 'off']:
        abort(400)
    if action.lower() == 'on':
        _send_code(switch.on)
    else:
        _send_code(switch.off)

def _send_code(code):
    pi = pigpio.pi()
    tx = Transmitter(pi, PIN)
    tx.send(code)
    time.sleep(1)
    tx.cancel()

def _find_switch(switch):
    next(sw for sw in switches if sw.name == switch)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
