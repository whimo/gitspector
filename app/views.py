from app import app
from flask import render_template, request, abort, jsonify
import os
from subprocess import check_output, STDOUT, TimeoutExpired, CalledProcessError
from datetime import datetime
from collections import defaultdict
from . import git_analysis


def _path_to_repo(repo_name, include_git=False):
    if include_git:
        return os.path.join(app.config['REPOS_DIR'], repo_name, '.git')
    else:
        return os.path.join(app.config['REPOS_DIR'], repo_name)


def _check_if_exists(repo_name):
    return os.path.exists(_path_to_repo(repo_name))


def _translate_interval(num, min1, max1, min2, max2):
    len1 = max1 - min1
    len2 = max2 - min2

    scaled = float(num - min1) / max(float(len1), 1)
    return min2 + (scaled * len2)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/repo_url', methods=['POST'])
def repo_url():
    if not request.get_json():
        abort(400)
    print(request.get_json())
    return jsonify({'status': 'SUCC sees'})


@app.route('/new_repo', methods=['POST'])
def new_repo():
    if not request.json or 'url' not in request.json:
        return jsonify({'status': 'error', 'error_text': 'You must specify .git of the repository'})

    repo_url = request.json['url']
    repo_name = repo_url.split('/')[-1][:-4]
    repo_name.replace('..', 'DEADBEEF')

    os.system('rm -rf {}'.format(_path_to_repo(repo_name, False)))

    try:
        output = check_output(['git', 'clone', repo_url, _path_to_repo(repo_name, False)],
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

    print(output)
    return jsonify({'status': 'error', 'error_text': 'Something went wrong. Please try again later.'})


@app.route('/repos/<repo_name>/contributors', methods=['GET'])
def get_contributors(repo_name):
    if not _check_if_exists(repo_name):
        return jsonify({'status': 'error', 'error_text': 'Repository does not exist.'})

    return jsonify({'status': 'ok',
                    'contributors': git_analysis.contributors(_path_to_repo(repo_name, True))})


@app.route('/repos/<repo_name>/stats', methods=['POST'])
def get_stats(repo_name):
    if not _check_if_exists(repo_name):
        return jsonify({'status': 'error', 'error_text': 'Repository does not exist.'})

    if 'username' not in request.json:
        return jsonify({'status': 'error',
                        'error_text': 'You must specify a username to collect statistics.'})

    try:
        from_date = datetime.strptime(request.json['from_date'], '%Y-%m-%d')
        to_date =   datetime.strptime(request.json['to_date'],   '%Y-%m-%d')

    except KeyError:
        return jsonify({'status': 'error',
                        'error_text': 'You must specify period start and end dates.'})

    except (ValueError, TypeError):
        return jsonify({'status': 'error',
                        'error_text': 'You must specify valid start and end dates.'})

    commits_by_type = defaultdict(list)
    commits_by_risk = defaultdict(list)

    commits = git_analysis.get_commits_period(from_date, to_date, _path_to_repo(repo_name, True))
    commits_info = [git_analysis.get_commit_info(commit, _path_to_repo(repo_name, True))
                    for commit in commits]

    commit_types, commit_risks = zip(*commits_info)
    commit_types = list(commit_types)
    commit_risks = list(commit_risks)
    min_risk, max_risk = min(commit_risks), max(commit_risks)

    for i, val in enumerate(commit_risks):
        risk_proj = _translate_interval(val, min_risk, max_risk, 0, 100)

        if risk_proj <= 33:
            commit_risks[i] = 'Low Risk'
        elif risk_proj <= 67:
            commit_risks[i] = 'Medium Risk'
        else:
            commit_risks[i] = 'High Risk'

    for i, commit in enumerate(commits):
        commit_description = git_analysis.get_description(commit, _path_to_repo(repo_name, True))
        info = {'sha': commit, 'description': commit_description}

        commits_by_type[commit_types[i]].append(info)
        commits_by_risk[commit_risks[i]].append(info)

    return jsonify({'status': 'ok',
                    'commits_by_type': dict(commits_by_type), 'commits_by_risk': dict(commits_by_risk)})
