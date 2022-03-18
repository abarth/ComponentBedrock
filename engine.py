import re

class Directory(object):
  def is_valid_entry_name(name):
    return name != '' and name != '.' and name != '..'

  def __init__(self):
    self._entries = {}

  def add_entry(self, name, object):
    assert not name in self._entries
    assert Directory.is_valid_entry_name(name)
    self._entries[name] = object

  def list(self):
    return self._entries.keys()

  def lookup(self, name):
    return self._entries.get(name)


class Package(object):
  def __init__(self):
    self.directory = Directory()


class Component(object):
  def is_valid_child_name(name):
    return re.fullmatch('[-a-zA-Z_.]{1,100}', name)
  
  def __init__(self):
    self.outgoing = Directory()
    self.incoming = Directory()
    self.incoming_namespace = Directory()
    self.outgoing_namespace = Directory()
    self.package = Package()
    self._children = {}
    self.parent = None

  def add_child(self, name, child):
    assert Component.is_valid_child_name(name)
    assert not name in self._children
    assert child.parent is None
    self._children[name] = child
    child.parent = self
