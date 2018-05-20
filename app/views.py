from app import app
from flask import render_template, request, abort, jsonify
import os
from subprocess import check_output, STDOUT, TimeoutExpired, CalledProcessError
from datetime import datetime
from collections import defaultdict
from . import git_analysis


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
        return jsonify({'status': 'error', 'error_text': 'You must specify .git of the repository'})

    repo_url = request.json['url']
    repo_name = repo_url.split('/')[-1][:-4]
    repo_name.replace('..', 'DEADBEEF')

    os.system('rm -rf {}'.format(_path_to_repo(repo_name)))

    try:
        output = check_output(['git', 'clone', repo_url, _path_to_repo(repo_name)],
                              timeout=app.config['CLONE_TIMEOUT'], stderr=STDOUT)
        output = output.decode()

    except CalledProcessError as e:
        output = str(e.output)

    except TimeoutExpired:
        return jsonify({'status': 'error', 'error_text': 'Timed out on git clone.'})

    if 'not found' in output:
        return jsonify({'status': 'error', 'error_text': 'Repository not found.'})
    elif 'Cloning into' in output:
        return jsonify({'status': 'ok'})

    return jsonify({'status': 'error', 'error_text': 'Something went wrong. Please try again later.'})


@app.route('/repos/<repo_name>/contributors', methods=['GET'])
def get_contributors(repo_name):
    if not _check_if_exists(repo_name):
        return jsonify({'status': 'error', 'error_text': 'Repository does not exist.'})

    return jsonify({'status': 'ok',
                    'contributors': str(git_analysis.contributors(_path_to_repo(repo_name)))})


@app.route('/repos/<repo_name>/stats', methods=['GET'])
def get_stats(repo_name):
    if not _check_if_exists(repo_name):
        return jsonify({'status': 'error', 'error_text': 'Repository does not exist.'})

    if 'username' not in request.json:
        return jsonify({'status': 'error',
                        'error_text': 'You must specify a username to collect statistics.'})

    try:
        from_date = datetime.strptime(request.args.get('from_date'), '%Y-%m-%d')
        to_date =   datetime.strptime(request.args.get('to_date'),   '%Y-%m-%d')

    except KeyError:
        return jsonify({'status': 'error',
                        'error_text': 'You must specify period start and end dates.'})

    except (ValueError, TypeError):
        return jsonify({'status': 'error',
                        'error_text': 'You must specify valid start and end dates.'})

    commits_by_type = defaultdict(list)
    commits_by_risk = defaultdict(list)

    commits = git_analysis.get_commits_period(from_date, to_date)

    for commit in commits:
        commit_description = git_analysis.get_description(commit)
        commit_type, commit_risk = git_analysis.get_commit_info(commit)
        info = {'sha': commit, 'description': commit_description}

        commits_by_type[commit_type].append(info)
        commits_by_risk[commit_risk].append(info)

    return jsonify({'status': 'ok',
                    'commits_by_type': dict(commits_by_type), 'commits_by_risk': dict(commits_by_risk)})
