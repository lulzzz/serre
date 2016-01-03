from flask import Flask, request, render_template, jsonify
import json
from pymongo import MongoClient
from datetime import datetime, timedelta

app = Flask(__name__)
client = MongoClient()
db = client['test']
col = db['samples']

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        _id = col.insert(request.json)
        response = {
            "_id" : str(_id),
            "status" : "ok"
        }
        return jsonify(response)
    elif request.method == 'GET':
        return render_template('index.html')
    else:
        return None

@app.route('/node/<node_id>')
def show_node_summary(node_id):
    return render_template('node.html', node_id=node_id)

if __name__ == '__main__':
    app.run()
