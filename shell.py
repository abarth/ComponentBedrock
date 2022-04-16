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

def print_directory_tree(directory, prefix=''):
    for name in cf_directory_list(directory):
      print(prefix + '* %s' % name)
      node = cf_directory_lookup(directory, name)
      if cf_is_directory(node):
        print_directory_tree(node, prefix + '  ')

def print_component(component, prefix=''):
    print(prefix + 'url: ' + cf_component_get_attribute(component, 'url'))
    print(prefix + 'state: ' + cf_component_get_state(component))
    print(prefix + 'incoming: ' +
          ', '.join(cf_directory_list(cf_component_get_incoming(component))))
    print(prefix + 'outgoing: ' +
          ', '.join(cf_directory_list(cf_component_get_outgoing(component))))
    print(prefix + 'eager: %s' % cf_component_is_eager(component))
    if cf_component_is_resolved(component):
        print(prefix + 'children: ' +
              ', '.join(cf_component_get_children(component)))
        print(prefix + 'incoming_namespace: ')
        print_directory_tree(cf_component_get_incoming_namespace(component), prefix + '  ')
        print(prefix + 'outgoing_namespace: ')
        print_directory_tree(cf_component_get_outgoing_namespace(component), prefix + '  ')



def print_tree(component, prefix=''):
    print_component(component, prefix)
    if cf_component_is_resolved(component):
        for c in cf_component_get_children(component):
            print(prefix + 'child: ' + c)
            print_tree(cf_component_get_child(component, c), prefix + '  ')
