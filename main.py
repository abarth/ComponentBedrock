from shell import * 
import json5

def read_specification(filename):
  print('reading manifest %s' % filename)
  with open(filename) as f:
    return json5.load(f)

def parse_component(filename):
  component = cf_component_create()
  specification = read_specification(filename)
  for c in specification.get('children', []):
    child = parse_component(c['url'])
    cf_component_add_child(component, c['name'], child)

  # TODO - need to separate parsing and resolution so we can resolve from parent.
  for r in specification.get('routes', []):
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
  
  return component

root = parse_component('meta/root.cbl')
   
bootstrap = cf_component_get_child(root, 'bootstrap')
bootstrap_incoming_namespace = cf_component_get_incoming_namespace(bootstrap)
bootstrap_pkg = cf_component_get_pkg_directory(bootstrap)
cf_directory_add_child(bootstrap_incoming_namespace, 'pkg', bootstrap_pkg)

print_tree(root)
