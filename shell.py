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

def print_component(component):
  print('children: ' +
        ', '.join(cf_component_get_children(component)))
  print('incoming: ' +
        ', '.join(cf_directory_list(cf_component_get_incoming(component))))
  print('outgoing: ' +
        ', '.join(cf_directory_list(cf_component_get_outgoing(component))))
  print('incoming_namespace: ' +
        ', '.join(cf_directory_list(cf_component_get_incoming_namespace(component))))
  print('outgoing_namespace: ' +
        ', '.join(cf_directory_list(cf_component_get_outgoing_namespace(component))))

