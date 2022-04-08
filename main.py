from shell import *
import json5
import threading
import os
import queue
import sys


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
    resolver = cf_directory_lookup(incoming, 'resolver')
    for name in cf_component_get_children(component):
        child = cf_component_get_child(component, name)
        (res_sender, res_receiver) = cf_capability_create()
        msg = ResolveInput(child.url, res_sender)
        cf_capability_send(resolver, msg)
        res = cf_capability_recv(res_receiver)
        assert res.spec is not None
        resolve_component(child, res.spec)

    if bin:
        cf_component_start(component)


class ResolveInput(object):
    def __init__(self, url, res_sender):
        self.url = url
        self.res_sender = res_sender

class ResolveOutput(object):
    def __init__(self, pkg, spec):
        self.pkg = pkg
        self.spec = spec

class ResolverThread(threading.Thread):
    def __init__(self, pkg_map, receiver):
        super().__init__(daemon=True)
        self.pkg_map = pkg_map
        self.receiver = receiver

def run_resolver(pkg_map, receiver):
    while True:
        msg = cf_capability_recv(receiver)
        (pkg_url, fragment) = msg.url.split('#')
        pkg = pkg_map.get(pkg_url)
        spec = cf_directory_open(pkg, fragment)
        cf_capability_send(msg.res_sender, ResolveOutput(pkg, spec))

if __name__ == '__main__':
    print('\n=== START ===\n')
    pkg_map = make_pkg_map([
        'fuchsia-pkg://fuchsia.com/bootstrap#meta/bootstrap.cbl',
        'fuchsia-pkg://fuchsia.com/core#meta/core.cbl',
        'fuchsia-pkg://fuchsia.com/scenic#meta/scenic.cbl',
        'fuchsia-pkg://fuchsia.com/vulkan_loader#meta/vulkan_loader.cbl'
    ])
    (resolver_sender, resolver_receiver) = cf_capability_create()
    resolver_thread = threading.Thread(target=run_resolver, args=(pkg_map, resolver_receiver),
                                       daemon=True)
    resolver_thread.start()
    root = cf_component_create(None)
    cf_directory_add_child(cf_component_get_incoming(root), "resolver",
                           resolver_sender)
    # TODO: could call the resolver to load the root spec instead
    specification = read_specification('meta/root.cbl')
    resolve_component(root, specification)

    bootstrap = cf_component_get_child(root, 'bootstrap')
    bootstrap_incoming_namespace = cf_component_get_incoming_namespace(bootstrap)
    bootstrap_pkg = cf_component_get_pkg_directory(bootstrap)
    cf_directory_add_child(bootstrap_incoming_namespace, 'pkg', bootstrap_pkg)

    print_tree(root)
