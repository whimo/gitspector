from ast import literal_eval
import os
from collections import defaultdict


def get_all_dependencies(directory, language='python'):
    if language == 'python':
        return literal_eval('[' + os.popen('sfood {}'.format(directory)).read().replace('\n', ',') + ']')
    elif language == 'cpp':
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
