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
  source_directory = cf_component_resolve_src(component, source_component_name)
  
  source_capability_name = r.get('src_name', default_capability_name)
  
  dest_component_name = r['dst']
  dest_directory = cf_component_resolve_dst(component, dest_component_name)
    
  dest_capability_name = r.get('dst_name', default_capability_name)
    
  print('routing capability "%s" from component %s to component %s as "%s"' %
       (source_capability_name, source_component_name,
         dest_component_name, dest_capability_name))
  cf_directory_route_capability(source_directory, source_capability_name,
                                dest_directory, dest_capability_name)

# Most people will want this, but not everyone. suggestion: use the
# name `component` for something with opinion, built onto something more
# fundamental like `topology_node`.
def add_default_routes(component):
  for dest_component_name in cf_component_get_children(component):
    source_directory = cf_component_resolve_src(component, '#parent')
    dest_directory = cf_component_resolve_dst(component, dest_component_name)
    source_capability_name = 'resolver'
    dest_capability_name = 'resolver'
    print('routing default capability "resolver" from #parent to component %s' %
      dest_component_name)
    cf_directory_route_capability(source_directory, source_capability_name,
                                  dest_directory, dest_capability_name)

# Idea: allow parsers to be chainable via transformers-
# TBD: Who is responsible for lazy resolving? parent or framework?
def resolve_component(component, specification, incoming_above_root):
  print('resolving component %s' % component.url)
  cf_component_resolve(component)

  # Bootstrap root's incoming
  incoming = cf_component_get_incoming(component)
  for (name, cap) in incoming_above_root.items():
    incoming.add_entry(name, cap)

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
  resolver = cf_directory_lookup(incoming, 'resolver').open()
  for name in cf_component_get_children(component):
    child = cf_component_get_child(component, name)
    (_, child_spec) = resolver.resolve(child.url)
    assert child_spec is not None
    resolve_component(child, child_spec, {})

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
    pkg_map = make_pkg_map(
      ['fuchsia-pkg://fuchsia.com/bootstrap#meta/bootstrap.cbl',
       'fuchsia-pkg://fuchsia.com/core#meta/core.cbl',
       'fuchsia-pkg://fuchsia.com/scenic#meta/scenic.cbl',
       'fuchsia-pkg://fuchsia.com/vulkan_loader#meta/vulkan_loader.cbl']
    )
    return Resolver(pkg_map)

print('\n=== START ===\n')
incoming = {"resolver": ResolverFactory()}
# TODO: could call the resolver
specification = read_specification('meta/root.cbl')
root = cf_component_create(None)
resolve_component(root, specification, incoming)

bootstrap = cf_component_get_child(root, 'bootstrap')
bootstrap_incoming_namespace = cf_component_get_incoming_namespace(bootstrap)
bootstrap_pkg = cf_component_get_pkg_directory(bootstrap)
cf_directory_add_child(bootstrap_incoming_namespace, 'pkg', bootstrap_pkg)

print_tree(root)