from subprocess import check_output, CalledProcessError
import re


def show_author_of_line(file, line_off, line, prev_sha):
    cmd = f'git blame {prev_sha}^ {file} -L{line_off + line},{line_off + line}'.split()
    try:
        output = check_output(cmd).decode('utf-8')
        r_author = r'\(([a-zA-Z0-9 ]*) ([0-9\-\ \:]*\+[0-9]{4,4}) ' + str(line + line_off) + r'\)'
        captures = re.search(r_author, output)
        return captures.group(1), captures.group(2)  # author, time
    except CalledProcessError:
        return (None, None)


def stats_for_commit(sha1):
    print('lasalca here')
    commit = sha1
    cmd = f'git diff {commit}^ {commit}'.split(' ')
    d = check_output(cmd).decode('utf-8')

    diffs = []

    line_a = 0
    line_b = 0
    offset = 0
    filename = ''
    stage = 0
    del_off = 0
    skip_new_file_idx = 0
    skip_new_file_iter = 0

    for line in d.split('\n'):

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
            r_path = r'[\-\+]{3,3} a\/([^\0]*)\n'  # e.g. '--- a/path/to/file.ext'
            filename = re.search(r_path, line).group(1)
            stage = 0
            continue

        if line.startswith('@@'):
            r_lines = r'\@\@ [\-\+]([0-9]*),[0-9]* [\-\+]([0-9]*),[0-9]* \@\@'  # e.g. '<sha-1> (<name> <date> line)\n'
            diff_start = re.search(r_lines, line)
            line_a = int(diff_start.group(1))
            line_b = int(diff_start.group(2))
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
            diffs.append(('-', show_author_of_line(filename, offset + del_off, line_a, f'{commit}')))
            del_off -= 1

        offset += 1

    return diffs


def get_commits_period(from_date, to_date):
    cmd = f'git rev-list\
            --since="{from_date.strftime('%Y-%m-%d')}" --before="{to_date.strftime('%Y-%m-%d')}"\
            --all --no-merges'.split(' ')
    return check_output(cmd).decode('utf-8').split()
