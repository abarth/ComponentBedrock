from porcelain import *

_cwd = cf_directory_create()


def chroot(directory):
    global _cwd
    _cwd = directory


def ls():
    global _cwd
    print(', '.join(cf_directory_list(_cwd)))


def cd(path):
    global _cwd
    directory = cf_directory_open(_cwd, path)
    if directory is None:
        print('No such file or directory.')
        return
    _cwd = directory


def print_component(component, prefix=''):
    print(prefix + 'children: ' +
          ', '.join(cf_component_get_children(component)))
    print(prefix + 'incoming: ' +
          ', '.join(cf_directory_list(cf_component_get_incoming(component))))
    print(prefix + 'outgoing: ' +
          ', '.join(cf_directory_list(cf_component_get_outgoing(component))))
    print(prefix + 'incoming_namespace: ' + ', '.join(
        cf_directory_list(cf_component_get_incoming_namespace(component))))
    print(prefix + 'outgoing_namespace: ' + ', '.join(
        cf_directory_list(cf_component_get_outgoing_namespace(component))))


def print_tree(component, prefix=''):
    print_component(component, prefix)
    for c in cf_component_get_children(component):
        print(prefix + 'child: ' + c)
        print_tree(cf_component_get_child(component, c), prefix + '  ')
