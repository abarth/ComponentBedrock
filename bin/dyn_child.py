
from porcelain import *
import secrets

def main():
    incoming_services = cf_directory_open(__NAMESPACE__.in_dir, "svc")
    add_child_svc = cf_directory_open(incoming_services, "framework")
    name = "child-%s" % secrets.randbelow(100)
    print("Adding child with name %s" % name)
    child = cf_component_create()
    cf_component_set_attribute(child, "url", "fuchsia-pkg://fuchsia.com/grandchild#meta/grandchild.cbl")
    (send, recv) = cf_capability_create()
    cf_capability_send(add_child_svc,
                       {"action": "add_child",
                        "name": name,
                        "child": child,
                        "response": send})
    assert(cf_capability_recv(recv))

main()