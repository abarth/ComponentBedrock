import re
import threading


class Directory(object):
    def is_valid_entry_name(name):
        return name != '' and name != '.' and name != '..' and not '/' in name

    def __init__(self):
        self._entries = {}

    def add_entry(self, name, object):
        assert not name in self._entries
        assert Directory.is_valid_entry_name(name), name
        self._entries[name] = object

    def list(self):
        return self._entries.keys()

    def lookup(self, name):
        return self._entries.get(name)

    def __repr__(self):
        return repr(self._entries)


class Sender(object):
    def __init__(self, queue):
        self._queue = queue

    def send(self, msg):
        self._queue.put(msg)


class Reciever(object):
    def __init__(self, queue):
        self._queue = queue

    def recieve(self):
        return self._queue.get()

    def send(self, msg):
        self._queue.put(msg)



class Package(object):
    def __init__(self):
        self.directory = Directory()


class Component(object):
    def is_valid_child_name(name):
        return re.fullmatch('[-a-zA-Z_.]{1,100}', name)

    # url may be None
    def __init__(self, url, incoming, outgoing):
        self.parent = None
        self.url = url
        # private
        self._state = BaseState(incoming, outgoing)

    def start(self):
        assert isinstance(self._state, ResolvedState)
        self._state = RunningState(self._state)

        def submain():
            exec(self._state.program, {'__HANDLE__': self})

        threading.Thread(target=submain).start()


class BaseState(object):
    def __init__(self, incoming, outgoing):
        # These must be part of BaseState so we can add routes without resolving the target component
        self.incoming = incoming
        self.outgoing = outgoing


class ResolvedState(BaseState):
    def __init__(self, base_state):
        super().__init__(base_state.incoming, base_state.outgoing)
        self.incoming_namespace = Directory()
        self.outgoing_namespace = Directory()
        self.package = Package()
        self.program = None
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


class RunningState(ResolvedState):
    def __init__(self, resolved_state):
        self.incoming = resolved_state.incoming
        self.outgoing = resolved_state.outgoing
        self.incoming_namespace = resolved_state.incoming_namespace
        self.outgoing_namespace = resolved_state.outgoing_namespace
        self.package = resolved_state.package
        self.program = resolved_state.program
        self.children = resolved_state.children
