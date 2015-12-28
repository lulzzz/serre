from flask import Flask, request, render_template
import json

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def ping():
    if request.method == 'POST':
        pass
    elif request.method == 'GET':
        return render_template('index.html')
    else:
        pass

if __name__ == '__main__':
    app.run()
