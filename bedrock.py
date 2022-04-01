import engine

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

def cf_component_create(url):
  component = engine.Component(url)
  component._state = engine.BaseState()
  return component

def cf_component_resolve(component):
  assert isinstance(component._state, engine.BaseState)
  component._state = engine.ResolvedState(component._state)

def cf_component_add_child(component, name, child):
  assert isinstance(component._state, engine.ResolvedState)
  component._state.add_child(name, child)

def cf_component_get_incoming(component):
  return component._state.incoming

def cf_component_get_outgoing(component):
  return component._state.outgoing

def cf_component_get_incoming_namespace(component):
  assert isinstance(component._state, engine.ResolvedState)
  return component._state.incoming_namespace

def cf_component_get_outgoing_namespace(component):
  assert isinstance(component._state, engine.ResolvedState)
  return component._state.outgoing_namespace

def cf_component_get_children(component):
  assert isinstance(component._state, engine.ResolvedState)
  return component._state.list_children()

def cf_component_get_child(component, name):
  assert isinstance(component._state, engine.ResolvedState)
  return component._state.lookup_child(name)

def cf_component_get_package(component):
  assert isinstance(component._state, engine.ResolvedState)
  return component._state.package

def cf_package_get_directory(package):
  return package.directory 
  
# def cf_component_resolve_moniker(component, moniker):
#   current = component
#   for part in moniker.split('/'):
