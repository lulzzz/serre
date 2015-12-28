from flask import Flask, request, render_template
import json

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        pass
    elif request.method == 'GET':
        return render_template('index.html')
    else:
        pass

@app.route('/node/<node_id>')
def show_node_summary(node_id):
    return render_template('node.html', node_id=node_id)

if __name__ == '__main__':
    app.run()
