import threading
from porcelain import *

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
