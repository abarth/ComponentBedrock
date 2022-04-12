from shell import *
import json5
import threading
import os
import queue
import sys
import time


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
    (source_component, source_directory) = cf_component_find_src(component, source_component_name)

    source_capability_name = r.get('src_name', default_capability_name)

    dest_component_name = r['dst']
    (dest_component, dest_directory) = cf_component_find_dst(component, dest_component_name)

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

    if not cf_component_is_resolved(source_component) and not cf_component_is_eager(source_component):
        cap = cf_directory_lookup(source_directory, source_capability_name)
        return RouterServer(cap, source_component, source_capability_name)
    return None


# Most people will want this, but not everyone. suggestion: use the
# name `component` for something with opinion, built onto something more
# fundamental like `topology_node`.
def add_default_routes(component):
    for dest_component_name in cf_component_get_children(component):
        # TODO(geb): This should probably launch the RouterServer if necessary
        (_, source_directory) = cf_component_find_src(component, '#parent')
        (_, dest_directory) = cf_component_find_dst(component,
                                                    dest_component_name)
        source_capability_name = 'loader'
        dest_capability_name = 'loader'
        print(
            'routing default capability "loader" from #parent to component %s'
            % dest_component_name)
        cf_directory_route_capability(source_directory, source_capability_name,
                                      dest_directory, dest_capability_name)


# Idea: allow parsers to be chainable via transformers-
# TBD: Who is responsible for lazy resolving? parent or framework?
def resolve_component(component):
    url = cf_component_get_attribute(component, 'url')
    specification = load_component(component)
    cf_component_resolve(component)

    if bin := specification.get('bin'):
        with open(bin) as codefile:
            cf_component_set_program(component, codefile.read())

    # Add children, but don't resolve them yet
    for c in specification.get('children', []):
        child = cf_component_create()
        cf_component_set_attribute(child, 'url', c['url'])
        if c.get('eager') is not None and c['eager']:
            cf_component_set_attribute(child, 'eager', True)
        cf_component_add_child(component, c['name'], child)

    # Add routes
    router_servers = []
    for r in specification.get('routes', []):
        s = add_route(component, r)
        if s is not None:
            router_servers.append(s)

    # Add default routes
    add_default_routes(component)

    # Start all router servers for lazy routing
    for s in router_servers:
        s.start()

    # Now, resolve the eager children. This has to be done after adding routes so children
    # can access the loader.
    for name in cf_component_get_children(component):
        child = cf_component_get_child(component, name)
        if cf_component_is_eager(child):
            print('eagerly resolving component %s' % cf_component_get_attribute(child, 'url'))
            resolve_component(child)

    # Start the component if it's executable
    if bin:
        cf_component_start(component)


def load_component(component):
    incoming = cf_component_get_incoming(component)
    loader = cf_directory_open(incoming, 'loader')
    (res_sender, res_receiver) = cf_capability_create()
    url = cf_component_get_attribute(component, 'url')
    msg = LoadRequest(url, res_sender)
    cf_capability_send(loader, msg)
    res = cf_capability_recv(res_receiver)
    assert res.spec is not None
    return res.spec


class RouterServer(threading.Thread):
    def __init__(self, receiver, component, capability_name):
        super().__init__(daemon=True)
        self.receiver = receiver
        self.component = component
        self.capability_name = capability_name

    def run(self):
        # Wait for a message to arrive.
        cf_capability_watch(self.receiver)
        url = cf_component_get_attribute(self.component, 'url')
        print('lazily resolving component %s for %s' % (url, self.capability_name))
        resolve_component(self.component)
        # Either the receiver has arrived at its final destination, or control over it has been
        # handed off to the incoming dir of another unresolved component. Either way, there is
        # nothing more for this handler to do, so exit.


class LoadRequest(object):
    def __init__(self, url, res_sender):
        self.url = url
        self.res_sender = res_sender

class LoadResponse(object):
    def __init__(self, pkg, spec):
        self.pkg = pkg
        self.spec = spec

def run_loader(pkg_map, receiver):
    while True:
        msg = cf_capability_recv(receiver)
        (pkg_url, fragment) = msg.url.split('#')
        pkg = pkg_map.get(pkg_url)
        spec = cf_directory_open(pkg, fragment)
        cf_capability_send(msg.res_sender, LoadResponse(pkg, spec))

if __name__ == '__main__':
    print('\n=== START ===\n')
    pkg_map = make_pkg_map([
        'fuchsia-pkg://fuchsia.com/root#meta/root.cbl',
        'fuchsia-pkg://fuchsia.com/bootstrap#meta/bootstrap.cbl',
        'fuchsia-pkg://fuchsia.com/core#meta/core.cbl',
        'fuchsia-pkg://fuchsia.com/scenic#meta/scenic.cbl',
        'fuchsia-pkg://fuchsia.com/vulkan_loader#meta/vulkan_loader.cbl'
    ])
    (loader_sender, loader_receiver) = cf_capability_create()
    loader_thread = threading.Thread(target=run_loader, args=(pkg_map, loader_receiver),
                                       daemon=True)
    loader_thread.start()
    root = cf_component_create()
    cf_component_set_attribute(root, 'url', 'fuchsia-pkg://fuchsia.com/root#meta/root.cbl')
    cf_directory_add_child(cf_component_get_incoming(root), 'loader',
                           loader_sender)
    print('resolving root component')
    resolve_component(root)

    #bootstrap = cf_component_get_child(root, 'bootstrap')
    #bootstrap_incoming_namespace = cf_component_get_incoming_namespace(bootstrap)
    #bootstrap_pkg = cf_component_get_pkg_directory(bootstrap)
    #cf_directory_add_child(bootstrap_incoming_namespace, 'pkg', bootstrap_pkg)

    # Hacky sleep to give resolution time to complete
    time.sleep(0.1)
    print_tree(root)
