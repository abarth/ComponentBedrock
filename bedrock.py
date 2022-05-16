import engine
from queue import Queue


def cf_directory_create():
    return engine.Directory()


def cf_directory_open(directory, path):
    stack = [directory]
    for part in path.split('/'):
        if part == '' or part == '.':
            continue
        if part == '..':
            stack.pop()
            if not stack:
                return None
            continue
        child = stack[-1].lookup(part)
        if child is None:
            return None
        stack.append(child)
    return stack[-1]


def cf_directory_add_child(directory, name, object):
    directory.add_entry(name, object)


def cf_directory_list(directory):
    return directory.list()


def cf_directory_lookup(directory, name):
    return directory.lookup(name)


def cf_is_directory(object):
    return isinstance(object, engine.Directory)


def cf_component_create():
    component = engine.Component()
    component._state = engine.BaseState()
    return component


def cf_component_set_attribute(component, attr, val):
    component.attributes[attr] = val


def cf_component_get_attribute(component, attr):
    return component.attributes.get(attr)


def cf_component_will_resolve(component):
    with component.lock:
        assert isinstance(component._state, engine.BaseState)
        component._state = engine.ResolvedState(component._state)
        assert isinstance(component._state, engine.ResolvedState)

def cf_component_get_state(component):
    with component.lock:
        if isinstance(component._state, engine.RunningState):
            return 'running'
        elif isinstance(component._state, engine.ResolvedState):
            return 'resolved'
        elif isinstance(component._state, engine.StoppedState):
            return 'stopped'
        else:
            return 'unresolved'

def cf_component_is_resolved(component):
    with component.lock:
        return isinstance(component._state, engine.ResolvedState)


def cf_component_add_child(component, name, child):
    with component.lock:
        component._state.add_child(name, child)


def cf_component_get_incoming(component):
    with component.lock:
        return component._state.incoming


def cf_component_get_outgoing(component):
    with component.lock:
        return component._state.outgoing


def cf_component_get_incoming_namespace(component):
    with component.lock:
        assert isinstance(component._state, engine.ResolvedState)
        return component._state.incoming_namespace


def cf_component_get_outgoing_namespace(component):
    with component.lock:
        assert isinstance(component._state, engine.ResolvedState)
        return component._state.outgoing_namespace


def cf_component_get_children(component):
    with component.lock:
        assert isinstance(component._state, engine.ResolvedState)
        return component._state.list_children()


def cf_component_get_child(component, name):
    with component.lock:
        assert isinstance(component._state, engine.ResolvedState)
        return component._state.lookup_child(name)


def cf_component_get_package(component):
    with component.lock:
        assert isinstance(component._state, engine.ResolvedState)
        return component._state.package


def cf_component_get_program(component):
    with component.lock:
        assert isinstance(component._state, engine.ResolvedState)
        return component._state.program


def cf_component_set_program(component, program):
    with component.lock:
        assert isinstance(component._state, engine.ResolvedState)
        component._state.program = program


def cf_component_will_run(component):
    with component.lock:
        assert isinstance(component._state, engine.ResolvedState) or isinstance(component._state, engine.StoppedState)
        component._state = engine.RunningState(component._state)


def cf_component_did_stop(component):
    with component.lock:
        assert isinstance(component._state, engine.RunningState)
        component._state = engine.StoppedState(component._state)


def cf_package_get_directory(package):
    return package.directory


def cf_capability_create():
    """Returns a (sender/client_end, reciever/server_end) pair."""
    queue = engine.WatchableQueue()
    return engine.Sender(queue), engine.Receiver(queue)


def cf_capability_send(capability, message):
    capability.send(message)


def cf_capability_recv(capability):
    return capability.recv()


def cf_capability_watch(capability):
    capability.watch()
