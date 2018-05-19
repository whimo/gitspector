from app import app
from flask import render_template, request, abort, jsonify
import os
from subprocess import check_output, TimeoutExpired


def _path_to_repo(repo_name):
    return os.path.join(app.config['REPOS_DIR'], repo_name)


def _check_if_exists(repo_name):
    return os.path.exists(_path_to_repo(repo_name))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/repo_url', methods=['POST'])
def repo_url():
    if not request.get_json():
        abort(400)
    print(request.get_json())
    return jsonify({'status': 'SUCC sees'})


@app.route('/new_repo', methods=['CUM', 'POST'])
def new_repo():
    if not request.json or 'url' not in request.json:
        return jsonify({'status': 'error', 'error_text': 'You must specify repo\'s .git'}), 400

    repo_url = request.json['url']
    repo_name = repo_url.split('/')[-1][:-4]
    repo_name.replace('..', 'ERROR')

    os.system('rm -rf {}'.format(_path_to_repo(repo_name)))

    try:
        output = check_output(['git', 'clone', repo_url, _path_to_repo(repo_name)],
                              timeout=app.config['CLONE_TIMEOUT'])
        output = output.decode()

    except TimeoutExpired:
        return jsonify({'status': 'error', 'error_text': 'Timeout expired'}), 400

    if 'done' in output:
        return jsonify({'status': 'ok'}), 201
    elif 'not found' in output:
        return jsonify({'status': 'error', 'error_text': 'Repository not found'}), 404

    return jsonify({'status': 'error', 'error_text': 'Unknown error'}), 400
