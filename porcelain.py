from bedrock import *

# Helper routines based on the bedrock APIs

# TODO: should this be part of bedrock or porcelain?
# Constraint: capability must implement `Capability` class
# How would we enforce 'no dangling routes' invariant?
def cf_directory_route_capability(src_directory, src_name, dst_directory, dst_name, transformer=lambda x: x):
  # lazy routing: only open the source when the destination is opened
  class RoutedCapability(Capability):
    def __init__(self, src_directory, src_name):
      self.src_directory = src_directory
      self.src_name = src_name
  
    def open(self):
      return transformer(cf_directory_open(self.src_directory, self.src_name)).open()
      
  cf_directory_add_child(dst_directory, dst_name, RoutedCapability(src_directory, src_name))


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
  if name == '#self:pkg':
    return cf_component_get_pkg_directory(component)
  return cf_component_get_outgoing(cf_component_get_child(component, name))


def cf_component_resolve_dst(component, name):
  if name == '#self':
    return cf_component_get_incoming_namespace(component)
  if name == '#parent':
    return cf_component_get_outgoing(component)
  return cf_component_get_incoming(cf_component_get_child(component, name))

# abstract base class
class Capability(object):
  def open(self):
    pass