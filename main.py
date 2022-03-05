from shell import * 

root = cf_component_create()

# TOOD: We should parse CML in order to create the topology.
def create_topology():
  cf_component_add_child(root, 'bootstrap', cf_component_create())
  cf_component_add_child(root, 'core', cf_component_create())

create_topology()
