from porcelain import *
import threading

# This type is known to components
class Namespace(object):
    def __init__(self, in_dir, out_dir):
        self.in_dir = in_dir
        self.out_dir = out_dir


def run_component(component):
    incoming = cf_component_get_incoming(component)
    runner = cf_directory_open(incoming, 'runner')
    assert runner is not None
    (res_sender, res_receiver) = cf_capability_create()
    msg = RunnerRequest(component, res_sender)
    cf_capability_send(runner, msg)
    res = cf_capability_recv(res_receiver)
    assert res


class RunnerRequest(object):
    def __init__(self, component, res_sender):
        self.component = component
        self.res_sender = res_sender


def run_runner(receiver):
    while True:
        msg = cf_capability_recv(receiver)
        component = msg.component
        bin = cf_component_get_program(component).get('bin')
        with open(bin) as codefile:
            program = codefile.read()

        in_dir = cf_component_get_incoming_namespace(component)
        out_dir = cf_component_get_outgoing_namespace(component)
        namespace = Namespace(in_dir, out_dir)
      
        def submain():
            exec(program, {'__NAMESPACE__': namespace})
            cf_component_did_stop(component)
        
        cf_component_will_run(component)
        threading.Thread(target=submain, daemon=True).start()
        cf_capability_send(msg.res_sender, True)
