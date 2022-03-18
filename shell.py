from porcelain import *

_cwd = cf_directory_create()

def chroot(directory):
  _cwd = directory

def ls():
  for name in _cwd.list():
    print(name)

def cd(path):
  global _cwd
  directory = cf_directory_open(_cwd, path)
  if directory is None:
    print('No such file or directory.')
    return
  _cwd = directory
