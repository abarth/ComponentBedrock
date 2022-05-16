import threading
from porcelain import *
from runner import run_component

class FrameworkService(threading.Thread):
    def __init__(self, receiver, component):
        super().__init__(daemon=True)
        self.receiver = receiver
        self.component = component

    def run(self):
        while True:
            request = cf_capability_recv(self.receiver)
            if request["action"] == "add_child":
                cf_component_add_child(self.component, request["name"], request["child"])
                cf_capability_send(request["response"], True)
            else:
                cf_capability_send(request["respond"], "unknown")


def add_framework_service(component):
    framework_dir = cf_directory_create()
    (send, recv) = cf_capability_create()
    cf_directory_add_child(framework_dir, "framework", send)
    FrameworkService(recv, component).start()
    cf_component_set_attribute(component, "framework", framework_dir)

# Most people will want this, but not everyone. suggestion: use the
# name `component` for something with opinion, built onto something more
# fundamental like `topology_node`.
def add_default_routes(component):
    for dest_component_name in cf_component_get_children(component):
        for default_capability_name in ['loader', 'runner']:
            # TODO(geb): This should probably launch the RouterServer if necessary
            (_, source_directory) = cf_component_find_src(component, '#parent')
            (_, dest_directory) = cf_component_find_dst(component,
                                                        dest_component_name)
            source_capability_name = default_capability_name
            dest_capability_name = default_capability_name
            print(
                'routing default capability "%s" from #parent to component %s'
                % (default_capability_name, dest_component_name))
            cf_directory_route_capability(source_directory, source_capability_name,
                                          dest_directory, dest_capability_name)


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
        sender = cf_directory_open(source_directory, source_capability_name)
        if sender is None:
            new_sender, receiver = cf_capability_create()
            cf_path_add_child(source_directory,
                              source_capability_name,
                              receiver)
            sender = new_sender

        cf_path_add_child(dest_directory, dest_capability_name, sender)

    if source_component and not cf_component_is_resolved(source_component) and not cf_component_is_eager(source_component):
        cap = cf_directory_lookup(source_directory, source_capability_name)
        return RouterServer(cap, source_component, source_capability_name)
    return None

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

# Idea: allow parsers to be chainable via transformers
def resolve_component(component):
    url = cf_component_get_attribute(component, 'url')
    specification = load_component(component)
    cf_component_will_resolve(component)

    if program := specification.get('program'):
        cf_component_set_program(component, program)

    # Add children, but don't resolve them yet
    for c in specification.get('children', []):
        child = cf_component_create()
        add_framework_service(child)
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

    # Start the component if it has a 'program' specification
    if program:
        run_component(component)


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
