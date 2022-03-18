from bedrock import *

# Helper routines based on the bedrock APIs

def cf_component_route_capability(src_component, src_name, dst_component, dst_name, transformer=lambda x: x):
  src_directory = cf_component_get_outgoing(src_component)
  dst_directory = cf_component_get_incoming(dst_component)
  capability = transformer(cf_directory_open(src_directory, src_name))
  cf_directory_add_child(dst_directory, dst_name, capability)


def cf_directory_get_subdirectory(directory, path):
  # type check on opened node?
  return cf_directory_open(directory, path)


def cf_component_route_subdirectory(src_component, src_name, src_path, dst_component, dst_name):
  cf_component_route_capability(src_component, src_name, dst_component, dst_name,
                               transform=lambda capability: cf_directory_get_subdirectory(capability, src_path))


def cf_component_get_pkg_directory(component):
  return cf_package_get_directory(cf_component_get_package(component))

