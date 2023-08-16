import os
from flask import send_from_directory
from flask import Flask, render_template
import time

from threading import Thread

import json
import datetime as dt
from site_parsing import main_parsing

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ONF UGATU forever'
last_update_dt = '08.14..00.31'
parse_interval = 5
log_name = "log.out"

try:
    with open("init_data/ours.json", mode="r", encoding="utf-8") as json_file:
        ours = json.load(json_file)
except Exception:
    ours = {}


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/robots.txt')
def robots():
    return ""


def site_parse():
    global last_update_dt
    while True:
        last_update = dt.datetime.strptime(last_update_dt, "%m.%d..%H.%M")
        if dt.datetime.now() - last_update > dt.timedelta(minutes=parse_interval):
            with open(log_name, "a", encoding="utf-8") as logout:
                print("Update on", dt.datetime.now(), "last", last_update, file=logout)
                try:
                    result = main_parsing(logout)
                    if result is not None:
                        last_update_dt = result
                except Exception as e:
                    print("Exception", e, file=logout)
        time.sleep(30)

thread = Thread(target=site_parse)
thread.start()

@app.route('/')
@app.route('/index')
def all_rating():
    with open("result_data/ratings_stacks.json", mode="r", encoding="utf-8") as stacks_file:
        stacks = json.load(stacks_file)
    return render_template('all_rating.html', stacks=stacks,
                           title="Статистика по направлениям УУНиТ",
                           header="Статистика по направлениям",
                           load_time=last_update_dt)


@app.route('/master')
@app.route('/index/master')
def all_rating_master():
    with open("result_data/ratings_stacks.json", mode="r", encoding="utf-8") as stacks_file:
        stacks = json.load(stacks_file)
    return render_template('all_rating_mag.html', stacks=stacks,
                           title="Статистика по направлениям УУНиТ",
                           header="Статистика по направлениям магистратуры",
                           load_time=last_update_dt)


@app.route('/<group_id>')
@app.route('/index/<group_id>')
def rating(group_id):
    with open("result_data/ratings_stacks.json", mode="r", encoding="utf-8") as stacks_file:
        stacks = json.load(stacks_file)
    header = ", ".join([stacks[0][group_id]["specialty_code"],
                        stacks[0][group_id]["profile"],
                        stacks[0][group_id]["institution_name"],
                        stacks[0][group_id]["education_form"],
                        stacks[0][group_id]["funding"],
                        stacks[0][group_id]["category"]])
    return render_template('rating.html', group_id=group_id, stacks=stacks,
                           title="Статистика по направлениям УУНиТ",
                           header="Статистика по направлению\n" + header,
                           load_time=last_update_dt, ours=ours)


@app.route('/applicants/<app_id>')
@app.route('/index/applicants/<app_id>')
def applicant(app_id):
    with open("result_data/ratings_stacks.json", mode="r", encoding="utf-8") as stacks_file:
        stacks = json.load(stacks_file)
    header = app_id
    if app_id in ours:
        header += "(" + ours[app_id] + ")"
    return render_template('applicant.html', app_id=app_id, stacks=stacks,
                           title="Статистика по направлениям УУНиТ",
                           header="Информация по поступающему \n" + header,
                           load_time=last_update_dt)



if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
    # app.run(port=27272, host='0.0.0.0')