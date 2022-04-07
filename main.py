from shell import *
import json5
import os


def read_specification(filename):
    with open(filename) as f:
        return json5.load(f)


def make_pkg_map(urls):
    pkg_map = {}
    for url in urls:
        (pkg_url, fragment) = url.split('#')
        pkg_map[pkg_url] = make_pkg_dir(fragment)
    return pkg_map


def make_pkg_dir(path):
    pkg_dir = cf_directory_create()
    meta_dir = cf_directory_create()
    (dirname, filename) = path.split('/')
    spec = read_specification(path)
    cf_directory_add_child(meta_dir, filename, spec)
    cf_directory_add_child(pkg_dir, dirname, meta_dir)
    return pkg_dir


def add_route(component, r):
    source_component_name = r['src']
    default_capability_name = r['name'] if 'name' in r else False
    source_directory = cf_component_resolve_src(component,
                                                source_component_name)

    source_capability_name = r.get('src_name', default_capability_name)

    dest_component_name = r['dst']
    dest_directory = cf_component_resolve_dst(component, dest_component_name)

    dest_capability_name = r.get('dst_name', default_capability_name)

    print('routing capability "%s" from component %s to component %s as "%s"' %
          (source_capability_name, source_component_name, dest_component_name,
           dest_capability_name))

    if r['src'] == '#parent':
        # Routing from a parent doesn't make a new capability, it takes an
        # existing one and gives it to a child.
        cf_directory_route_capability(source_directory, source_capability_name,
                                      dest_directory, dest_capability_name)
    elif r['dst'] == '#parent':
        # things routed to the parent are routed "backwards". The server end
        # is routed from the parent down to the child.
        cf_directory_route_capability(dest_directory, dest_capability_name,
                                      source_directory, source_capability_name)
    else:
        # TODO(hjfreyer): This doesn't quite work. If you create two routes with
        # the same source component and name, they'll clash with each other. A
        # potential fix would be to make each route between children have one
        # source and many destinations, or just aggregate by source first.
        #
        # TODO(hjfreyer): I broke `#self:incoming` and `#self:pkg`.
        sender, reciever = cf_capability_create()
        cf_directory_add_child(source_directory, source_capability_name,
                               reciever)
        cf_directory_add_child(dest_directory, dest_capability_name, sender)


# Most people will want this, but not everyone. suggestion: use the
# name `component` for something with opinion, built onto something more
# fundamental like `topology_node`.
def add_default_routes(component):
    for dest_component_name in cf_component_get_children(component):
        source_directory = cf_component_resolve_src(component, '#parent')
        dest_directory = cf_component_resolve_dst(component,
                                                  dest_component_name)
        source_capability_name = 'resolver'
        dest_capability_name = 'resolver'
        print(
            'routing default capability "resolver" from #parent to component %s'
            % dest_component_name)
        cf_directory_route_capability(source_directory, source_capability_name,
                                      dest_directory, dest_capability_name)


# Idea: allow parsers to be chainable via transformers-
# TBD: Who is responsible for lazy resolving? parent or framework?
def resolve_component(component, specification):
    print('resolving component %s' % component.url)
    cf_component_resolve(component)

    if bin := specification.get('bin'):
        with open(bin) as codefile:
            cf_component_set_program(component, codefile.read())

    # Add children, but don't resolve them yet
    for c in specification.get('children', []):
        child = cf_component_create(c['url'])
        cf_component_add_child(component, c['name'], child)

    # Add routes
    for r in specification.get('routes', []):
        add_route(component, r)

    # Add default routes
    add_default_routes(component)

    # Now, resolve the children. This has to be done after adding routes so children
    # can access the resolver.
    incoming = cf_component_get_incoming(component)
    resolver = cf_directory_lookup(incoming, 'resolver').open()
    for name in cf_component_get_children(component):
        child = cf_component_get_child(component, name)
        (_, child_spec) = resolver.resolve(child.url)
        assert child_spec is not None
        resolve_component(child, child_spec)

    if bin:
        cf_component_start(component)


class Resolver(object):
    def __init__(self, pkg_map):
        self.pkg_map = pkg_map

    def resolve(self, url):
        (pkg_url, fragment) = url.split('#')
        pkg = self.pkg_map.get(pkg_url)
        spec = cf_directory_open(pkg, fragment)
        return (pkg, spec)


class ResolverFactory(Capability):
    def open(self):
        pkg_map = make_pkg_map([
            'fuchsia-pkg://fuchsia.com/bootstrap#meta/bootstrap.cbl',
            'fuchsia-pkg://fuchsia.com/core#meta/core.cbl',
            'fuchsia-pkg://fuchsia.com/scenic#meta/scenic.cbl',
            'fuchsia-pkg://fuchsia.com/vulkan_loader#meta/vulkan_loader.cbl'
        ])
        return Resolver(pkg_map)


print('\n=== START ===\n')
# TODO: could call the resolver
specification = read_specification('meta/root.cbl')
root = cf_component_create(None)
cf_directory_add_child(cf_component_get_incoming(root), "resolver",
                       ResolverFactory())

resolve_component(root, specification)

bootstrap = cf_component_get_child(root, 'bootstrap')
bootstrap_incoming_namespace = cf_component_get_incoming_namespace(bootstrap)
bootstrap_pkg = cf_component_get_pkg_directory(bootstrap)
cf_directory_add_child(bootstrap_incoming_namespace, 'pkg', bootstrap_pkg)

print_tree(root)
