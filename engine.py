import re


class Directory(object):
    def is_valid_entry_name(name):
        return name != '' and name != '.' and name != '..' and not '/' in name

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

    # url may be None
    def __init__(self, url):
        self.parent = None
        self.url = url
        # private
        self._state = BaseState()


class BaseState(object):
    def __init__(self):
        # These must be part of BaseState so we can add routes without resolving the target component
        self.incoming = Directory()
        self.outgoing = Directory()


class ResolvedState(BaseState):
    def __init__(self, base_state):
        super().__init__()
        self.incoming = base_state.incoming
        self.outgoing = base_state.outgoing
        self.incoming_namespace = Directory()
        self.outgoing_namespace = Directory()
        self.package = Package()
        self.children = {}

    def add_child(self, name, child):
        assert Component.is_valid_child_name(name)
        assert not name in self.children
        child.parent = self
        self.children[name] = child

    # xxx - these looks very similar to directory
    def list_children(self):
        return self.children.keys()

    def lookup_child(self, name):
        return self.children.get(name)


# class RunningState(ResolvedState):
