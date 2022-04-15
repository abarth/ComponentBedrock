from porcelain import *
import threading

# This type is known to components
class Namespace(object):
    def __init__(self, in_dir, out_dir):
        self.in_dir = in_dir
        self.out_dir = out_dir

def populate_namespace(runner_spec):
    in_dir = cf_directory_create()
    out_dir = runner_spec.outgoing_namespace
    incoming_namespace = runner_spec.incoming_namespace
    cf_directory_add_child(in_dir, 'svc', runner_spec.incoming_namespace)
    # cf_directory_add_child(in_dir, 'pkg', runner_spec.package)
    return Namespace(in_dir, out_dir)

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
        runner_spec = cf_component_will_run(component)
        bin = runner_spec.program.get('bin')
        with open(bin) as codefile:
            program = codefile.read()
        namespace = populate_namespace(runner_spec)
      
        def submain():
            exec(program, {'__NAMESPACE__': namespace})

        threading.Thread(target=submain, daemon=True).start()
        cf_capability_send(msg.res_sender, True)
