
from shell import * 

root = cf_component_create()

# def cf_component_create_capability
# def cf_component_transform_capability
# def cf_component_install_capability


# TOOD: We should parse CML in order to create the topology.
def create_topology():
  cf_component_add_child(root, 'bootstrap', cf_component_create())
  bootstrap = 
  bootstrap_incoming_namespace = cf_component_get_incoming_namespace(bootstrap)
  bootstrap_pkg = cf_component_get_pkg_directory(bootstrap)
  cf_directory_add_child(bootstrap_incoming_namespace, 'pkg', bootstrap_pkg)
  
  core = cf_component_add_child(root, 'core', cf_component_create())
  cf_component_route_capability(bootstrap, 'dev', core, 'dev')
  return bootstrap

create_topology()
