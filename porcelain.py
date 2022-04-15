from bedrock import *
import threading

# Helper routines based on the bedrock APIs


def cf_directory_route_capability(src_directory,
                                  src_name,
                                  dst_directory,
                                  dst_name,
                                  transformer=lambda x: x):
    cap = transformer(cf_directory_lookup(src_directory, src_name))
    cf_directory_add_child(dst_directory, dst_name, cap)


def cf_directory_get_subdirectory(directory, path):
    # type check on opened node?
    return cf_directory_open(directory, path)


def cf_directory_route_subdirectory(src_directory, src_name, src_path,
                                    dst_directory, dst_name):
    cf_component_route_capability(
        src_directory,
        src_name,
        dst_directory,
        dst_name,
        transform=lambda capability: cf_directory_get_subdirectory(
            capability, src_path))


def cf_component_get_pkg_directory(component):
    return cf_package_get_directory(cf_component_get_package(component))


def cf_component_find_src(component, name):
    if name == '#self' or name == '#self:outgoing':
        return (component, cf_component_get_outgoing_namespace(component))
    if name == '#self:incoming':
        return (component, cf_component_get_incoming_namespace(component))
    if name == '#parent':
        return (component, cf_component_get_incoming(component))
    if name == '#self:pkg':
        return (component, cf_component_get_pkg_directory(component))
    if name == '#framework':
        return (None, cf_component_get_attribute(component, "framework"))
    child = cf_component_get_child(component, name)
    return (child, cf_component_get_outgoing(child))


def cf_component_find_dst(component, name):
    if name == '#self':
        return (component, cf_component_get_incoming_namespace(component))
    if name == '#parent':
        return (component, cf_component_get_outgoing(component))
    child = cf_component_get_child(component, name)
    return (child, cf_component_get_incoming(child))

def cf_component_is_eager(component):
    eager = cf_component_get_attribute(component, 'eager')
    if eager is not None:
        return eager
    else:
        return False
