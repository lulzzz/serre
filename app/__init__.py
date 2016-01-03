from flask import Flask, request, render_template, jsonify
import json
from pymongo import MongoClient
from datetime import datetime, timedelta

app = Flask(__name__)
client = MongoClient()
db = client['test']
posts = db['posts']
queue = db['queue']

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = request.json
        _id = posts.insert(request.json)
        uid = data['uid']
        q = queue.find_one({'uid' : uid})
        if q is not None:
            print 'pushing action to node, removing action from queue'
            queue.delete(q['_id'])
        # queue.delete_many()
        response = {
            "_id" : str(_id),
            "status" : "ok",
            "action" : q
        }
        return jsonify(response)
    elif request.method == 'GET':
        return render_template('index.html')
    else:
        return None

@app.route('/node/<node_id>')
def show_node_summary(node_id):
    return render_template('node.html', node_id=node_id)

"""
API Functions
"""
@app.route('/api/update_queue', methods=['GET', 'POST'])
def update_queue():
    if request.method == "POST":
        data = request.form.to_dict()
        if data is not None:
            print data
            status = "ok"
        else:
            status = "bad"
        # _id = queue.insert(data)
    else:
        status = "awful"
    response = {
        "status" : status
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run()
