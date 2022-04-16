
from porcelain import *
import secrets

def main():
    svc = cf_directory_open(__NAMESPACE__.in_dir, "svc")
    assert svc is not None
    framework = cf_directory_open(svc, "framework")
    assert framework is not None
    name = "child-%s" % secrets.randbelow(100)
    print("Adding child with name %s" % name)

    # Direct bedrock interaction
    child = cf_component_create()
    cf_component_set_attribute(child, "url", "fuchsia-pkg://fuchsia.com/grandchild#meta/grandchild.cbl")

    # Mediated
    (send, recv) = cf_capability_create()
    cf_capability_send(framework,
                       {"action": "add_child",
                        "name": name,
                        "child": child,
                        "response": send})
    assert(cf_capability_recv(recv))

main()