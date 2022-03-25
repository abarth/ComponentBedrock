from bedrock import *

# Helper routines based on the bedrock APIs

def cf_directory_route_capability(src_directory, src_name, dst_directory, dst_name, transformer=lambda x: x):
  capability = transformer(cf_directory_open(src_directory, src_name))
  cf_directory_add_child(dst_directory, dst_name, capability)


def cf_component_route_capability(src_component, src_name, dst_component, dst_name, transformer=lambda x: x):
  src_directory = cf_component_get_outgoing(src_component)
  dst_directory = cf_component_get_incoming(dst_component)
  cf_directory_route_capability(src_directory, src_name, dst_directory, dst_name)


def cf_directory_get_subdirectory(directory, path):
  # type check on opened node?
  return cf_directory_open(directory, path)


def cf_component_route_subdirectory(src_component, src_name, src_path, dst_component, dst_name):
  cf_component_route_capability(src_component, src_name, dst_component, dst_name,
                               transform=lambda capability: cf_directory_get_subdirectory(capability, src_path))


def cf_component_get_pkg_directory(component):
  return cf_package_get_directory(cf_component_get_package(component))


def cf_component_resolve_src(component, name):
  if name == '#self' or name == '#self:outgoing':
    return cf_component_get_outgoing_namespace(component)
  if name == '#self:incoming':
    return cf_component_get_incoming_namespace(component)
  if name == '#parent':
    return cf_component_get_incoming(component)
  return cf_component_get_outgoing(cf_component_get_child(component, name))


def cf_component_resolve_dst(component, name):
  if name == '#self':
    return cf_component_get_incoming_namespace(component)
  if name == '#parent':
    return cf_component_get_outgoing(component)
  return cf_component_get_incoming(cf_component_get_child(component, name))
