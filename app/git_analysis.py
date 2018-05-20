from subprocess import check_output, CalledProcessError
import re
from datetime import datetime, timedelta


def show_author_of_line(file, line_off, line, prev_sha):
    cmd = ['git', 'blame', '{}^'.format(prev_sha), '{}'.format(file),
           '-L{},{}'.format(line_off + line, line_off + line)]

    try:
        output = check_output(cmd).decode('utf-8')
        r_author = r'\(([a-zA-Z0-9 ]*) ([0-9\-\ \:]*\+[0-9]{4,4}) ' + \
                   str(line + line_off) + r'\)'

        captures = re.search(r_author, output)
        return captures.group(1), captures.group(2)  # author, time
    except CalledProcessError:
        return (None, None)


def stats_for_commit(sha1):
    print('lasalca here')
    commit = sha1
    cmd = ['git', 'diff', '{}^'.format(commit), '{}'.format(commit)]
    output = check_output(cmd).decode('utf-8')

    diffs = []

    line_a = 0
    offset = 0
    filename = ''
    stage = 0
    del_off = 0
    skip_new_file_idx = 0
    skip_new_file_iter = 0

    for line in output.split('\n'):
        if line.startswith(r'\ No newline at end of file'):
            continue

        if line.startswith('deleted file'):
            continue

        if skip_new_file_idx < 0:
            if not line.startswith('@@'):
                continue
            else:
                r_skip = r'\@\@ [\-\+][0-9]*,[0-9]* [\-\+][0-9]*,([0-9]*) \@\@'
                skip_new_file_idx = int(re.search(r_skip, line).group(1))
                skip_new_file_iter = 0
                continue

        if skip_new_file_idx > 0:  # new file loop
            if skip_new_file_iter < skip_new_file_idx:
                skip_new_file_iter += 1
                diffs.append(('+', (None, None)))
                continue
            stage = 0

        if stage == 1:
            if line.startswith('new file'):
                skip_new_file_idx = -1  # jump to new file loop
            stage += 1
            continue

        if stage == 2:
            line += '\n'  # to match end of line

            # e.g. '--- a/path/to/file.ext'
            r_path = r'[\-\+]{3,3} a\/([^\0]*)\n'

            filename = re.search(r_path, line).group(1)
            stage = 0
            continue

        if line.startswith('@@'):

            # e.g. '<sha-1> (<name> <date> line)\n'
            r_lines = r'\@\@ [\-\+]([0-9]*),[0-9]* [\-\+]([0-9]*),[0-9]* \@\@'

            diff_start = re.search(r_lines, line)
            line_a = int(diff_start.group(1))
            offset = 0
            del_off = 0
            continue

        if line.startswith('diff'):
            stage = 1
            continue

        if line.startswith('+') and not line.startswith('+++'):
            if del_off < 0:
                diffs.append(('?', (None, None)))
            else:
                diffs.append(('+', (None, None)))

        elif line.startswith('-') and not line.startswith('---'):
            diffs.append(('-', show_author_of_line(filename,
                                                   offset + del_off,
                                                   line_a,
                                                   '{}'.format(commit))))
            del_off -= 1

        offset += 1

    return diffs


def changes_in_files_in_commit(commit):
    cmd = 'git diff {sha}^ {sha} --stat'.format(sha=commit)
    stats = check_output(cmd.split())
    for line in stats.split('\n')[:-1]:
        r_stat = r'([^\0]*) | ([0-9]+) [\-\+]*'
        stat = re.search(r_stat, line)
        yield (stat.group(1), stat.group(2))


def get_commits_period(from_date, to_date):
    cmd = ['git', 'rev-list',
           '--since="{}"'.format(from_date.strftime('%Y-%m-%d')),
           '--before="{}"'.format(to_date.strftime('%Y-%m-%d')),
           '--all', '--no-merges']

    return check_output(cmd).decode('utf-8').split()


ISO8601 = '%Y-%m-%d %H:%M:%S %z'


def get_description(sha):
    cmd = f'git log --format=%B -n 1 {sha}'
    return check_output(cmd.split()).decode('utf-8')


def get_diff_count(sha):
    cmd = f'git diff {sha}^ {sha} --stat'.split()
    stat = check_output(cmd).decode('utf-8').split('\n')[:-2]

    r_change = r'.* (|) *([0-9]+).*'
    changes = 0

    for line in stat:
        print(repr(line))
        changes += int(re.search(r_change, line).group(2))
    return changes


def get_time(sha):
    cmd = f'git log --format=%ai -n 1 {sha}'.split()
    return check_output(cmd).decode('utf-8').replace('\n', '')


def is_deleting_old_code(stats, date):
    date = datetime.strptime(date, ISO8601) - timedelta(days=30)
    changed_elder_than_month = 0
    deletes = 0
    for stat in stats:
        if stat[0] == '-':
            deletes += 1
            if datetime.strptime(stat[1][1], ISO8601) <= date:
                changed_elder_than_month += 1

    if float(changed_elder_than_month) / float(deletes) > 0.8:
        return True

    return False


def is_helping_others(stats, me):
    deletes = 0
    helps = 0
    for stat in stats:
        if stat[0] == '-':
            deletes += 1
            if stat[1][0] != me:
                helps += 1

    if float(helps) / float(deletes) > 0.8:
        return True

    return False


def is_churning(stats, date, me):
    date = datetime.strptime(date, ISO8601) - timedelta(days=7)
    changed_newer_than_week = 0
    deletes = 0
    for stat in stats:
        if stat[0] == '-':
            deletes += 1
            if datetime.strptime(stat[1][1], ISO8601) >= date:
                if stat[1][0] == me:
                    changed_newer_than_week += 1

    if float(changed_newer_than_week) / float(deletes) > 0.8:
        return True

    return False


def get_commit_info(sha):
    cmd = ['git', 'log', '--format=%an', '-n', '1', sha]
    me = check_output(cmd).decode('utf-8').replace('\n', '')

    commit_stats = stats_for_commit(sha)

    minus = 0
    add = 0
    change = 0
    total = len(commit_stats)
    for stat in commit_stats:
        if stat[0] == '+':
            add += 1
        elif stat[0] == '-':
            minus += 1
        else:
            change += 1

    if float(add + change) / float(total) > 0.8:
        c_type = 'New Work'

    elif is_deleting_old_code(commit_stats, get_time(sha)):
        c_type = 'Refactoring'

    elif is_helping_others(commit_stats, me):
        c_type = 'Helping Others'

    elif is_churning(commit_stats, get_time(sha), me):
        c_type = 'Code Churn'

    else:
        c_type = 'Other'

    get_files = f'git diff {sha}^ {sha} --name-only'.split()
    files = check_output(get_files).decode('utf-8').split('\n')[:-1]

    return c_type, files


def get_counts_period(from_date, to_date):
    commits = get_commits_period(from_date, to_date)
    activity = {'New Work': 0,
                'Refactoring': 0,
                'Helping Others': 0,
                'Code Churn': 0}
    for commit in commits:
        c_type, _ = get_commit_info(commit)
        amount = get_diff_count(commit)
        activity[c_type] += amount

    return activity
