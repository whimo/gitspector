from ast import literal_eval
import os
from collections import defaultdict

SUPPORTED_EXTENSIONS = {'py': 'python',
                        'c': 'c', 'h': 'c', 'cc': 'c', 'hh': 'c',
                        'C': 'c', 'H': 'c', 'cpp': 'c', 'hpp': 'c', 'cxx': 'c', 'hxx': 'c'}
SUPPORTED_LANGUAGES = ('python', 'c')


def get_all_dependencies(directory, language='python'):
    if language == 'python':
        return literal_eval('[' + os.popen('sfood {}'.format(directory)).read().replace('\n', ',') + ']')
    elif language == 'c':
        return literal_eval('[' + os.popen('cfood {}'.format(directory)).read().replace('\n', ',') + ']')


def get_forward_dependencies_dict(directory, language='python'):
    dependencies_list = get_all_dependencies(directory, language)
    dependencies_dict = defaultdict(set)
    for child, parent in dependencies_list:
        try:
            if directory in parent[0]:
                dependencies_dict['/'.join(child)].add('/'.join(parent))
        except TypeError:
            pass

    return dependencies_dict


def get_backward_dependencies_dict(directory, language='python'):
    dependencies_list = get_all_dependencies(directory, language)
    dependencies_dict = defaultdict(set)
    for child, parent in dependencies_list:
        try:
            if directory in parent[0]:
                dependencies_dict['/'.join(parent)].add('/'.join(child))
        except TypeError:
            pass

    return dependencies_dict


def _process_trans_dependency(dependencies_dict, file, already_processed):
    if file not in dependencies_dict:
        return set()

    ret = set()

    for dependency in dependencies_dict[file]:
        if dependency not in already_processed:
            already_processed.add(dependency)
            ret.add(dependency)
            ret.update(_process_trans_dependency(dependencies_dict, dependency, already_processed))

    return ret


def get_backward_trans_dependencies(directory, language='python', only_lens=True):
    dependencies_dict = dict(get_backward_dependencies_dict(directory, language))

    for key in dependencies_dict.keys():
        dependencies_dict[key] = _process_trans_dependency(dependencies_dict, key, set(key))

    if only_lens:
        for key in dependencies_dict.keys():
            dependencies_dict[key] = len(dependencies_dict[key])

    return dependencies_dict


def get_risk(directory, commit, files):
    os.system('git --git-dir={}/.git checkout {}'.format(directory, commit))
    file_deps = []
    deps_bylang = {lang: None for lang in SUPPORTED_LANGUAGES}

    for file in files:
        dependers = 0

        ext = file[0].split('.')[-1]
        if ext in SUPPORTED_EXTENSIONS:
            lang = SUPPORTED_EXTENSIONS[ext]
            if deps_bylang[lang] is None:
                deps_bylang[lang] = get_backward_trans_dependencies(directory, lang)
                print(deps_bylang[lang])

            for parent in deps_bylang[lang].keys():
                if file[0] in parent:
                    dependers = deps_bylang[lang][parent]
                    break

        file_deps.append(max(1, dependers) * file[1])

    os.system('git --git-dir={}/.git checkout master'.format(directory))
    return sum(file_deps) * len(files) * 0.1
