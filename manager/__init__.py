from flask import Flask, request, render_template, jsonify
import json
from pymongo import MongoClient
from datetime import datetime, timedelta
import os, sys

app = Flask(__name__)
client = MongoClient()
db = client['test']
posts = db['posts']
tasks_queue = db['queue']

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = request.json
        print 'NODE: ' + str(data)
        doc_id = posts.insert(request.json)
        print 'DOC_ID: ' + str(doc_id)

        # Check if there is any recent tasks
        uid = data['uid']        
        task = tasks_queue.find_one({'uid' : uid})
        if task is not None:
            tasks_queue.remove({'_id' : task['_id']}) # remove action from queue
            task.pop('_id', None)
        else:
            task = None
        print 'TASK: ' + str(task)

        # Push tasks to node
        response = {
            "status" : "ok",
            "doc_id" : str(doc_id),
            "task" : task #!TODO: send task to node
        }        
        print 'RESPONSE: ' + str(response)
        return jsonify(response)
    elif request.method == 'GET':
        return render_template('index.html')
    else:
        return None

@app.route('/node/')
def show_nodes():
    return render_template('index.html')   

@app.route('/node/<node_id>')
def show_node_summary(node_id):
    dt = timedelta(hours=1)
    time_a = datetime.now()
    time_b = datetime.now() - dt
    doc_template = {
        "uid" : node_id,
        "time" : {"$lt": time_b, "$gt": time_a} #!TODO search by time frame
    }
    docs = posts.find(doc_template)
    d = docs.limit(1) #!TODO ensure that only
    print d
    watering_time = 60
    cycle_time = 90
    lights = 100
    snapshot = [d for d in docs]
    return render_template('node.html', node_id=node_id, snapshot=snapshot, watering_time=watering_time, cycle_time=cycle_time, lights=lights)

"""
API Functions
"""
@app.route('/api/update_queue', methods=['GET', 'POST'])
def update_queue():
    if request.method == "POST":
        try:
            data = request.form.to_dict()
            if data is not None:
                _id = tasks_queue.insert(data)
                status = "ok"
            else:
                status = "bad"
        except Exception as error:
            print str(error)
    else:
        status = "awful"
    response = {
        'status' : status    
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run()
