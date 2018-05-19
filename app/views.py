from app import app
from flask import render_template, request, abort, jsonify

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test', methods=['POST'])
def test():
    if not request.get_json():
        abort(400)
    print(request.get_json())
    return jsonify({'status': 'SUCC sees'})