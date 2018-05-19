from ast import literal_eval
import os
from collections import defaultdict


def get_all_dependencies(directory, language='python'):
    if language == 'python':
        return literal_eval('[' + os.popen('sfood {}'.format(directory)).read().replace('\n', ',') + ']')
    elif language == 'cpp':
        return literal_eval('[' + os.popen('cfood {}'.format(directory)).read().replace('\n', ',') + ']')


def get_dependencies_dict(directory, language='python'):
    dependencies_list = get_all_dependencies(directory, language)
    dependencies_dict = defaultdict(list)
    for child, parent in dependencies_list:
        try:
            if directory in parent[0]:
                dependencies_dict['/'.join(child)].append('/'.join(parent))
        except TypeError:
            pass

    return dependencies_dict
