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
    stack.push(child)
  return stack[-1]


def cf_component_create():
  return engine.Component()


def cf_component_add_child(component, name, child):
  component.add_child(name, child)

# def cf_component_resolve_moniker(component, moniker):
#   current = component
#   for part in moniker.split('/'):
