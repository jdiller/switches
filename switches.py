# -*- coding: utf-8 -*-
from flask import Flask, render_template, abort
import logging
import time
import pigpio
from transmitter import Transmitter
from collections import namedtuple

app = Flask(__name__)
Switch = namedtuple('Switch', 'name on_code off_code')
logging.basicConfig(level=logging.DEBUG)

PIN = 21

switches = [Switch('Bookshelf', 333107, 333116),
            Switch('Tube', 333251, 333260),
            Switch('Kitchen', 333571, 333580),
            Switch('Humidifier', 335107, 335116),
            Switch('Floor', 341251, 341260)]

switch_groups = {
        'Living Room': [switches[0], switches[1], switches[4]],
        'TV' : [switches[0],switches[4]],
        'All' : [switches[0], switches[1], switches[2], switches[4]]
}

@app.route("/")
def home():
    return render_template('main.html', switches=switches)


@app.route('/switch/<switch_name>/<action>', methods=['POST'])
def switch(switch_name, action):
    switch = _find_switch(switch_name)
    if not switch:
        logging.debug("Couldn't find switch called " + switch_name)
        abort(404)
    if action.lower() not in ['on', 'off']:
        abort(400)
    if action.lower() == 'on':
        _send_code(switch.on_code)
    else:
        _send_code(switch.off_code)
    return 'ok'

@app.route('/group/<group_name>/<action>', methods=['POST'])
def group(group_name, action):
    switch_group = switch_groups.get(group_name)
    if not switch_group:
        abort(404)
    for switch in switch_group:
        if action.lower() == 'on':
            _send_code(switch.on_code)
        else:
            _send_code(switch.off_code)
    return 'ok'


def _send_code(code):
    pi = pigpio.pi()
    tx = Transmitter(pi, PIN)
    tx.send(code)
    time.sleep(1)
    tx.cancel()


def _find_switch(switch):
    switch = switch.replace('the ', '')
    return next(sw for sw in switches if lower(sw.name.lower() == switch.lower())

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)
