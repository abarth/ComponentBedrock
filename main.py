from shell import *
from runner import run_component, run_runner
from framework import *
import json5
import threading
import os
import queue
import sys
import time


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
     

if __name__ == '__main__':
    print('\n=== START ===\n')
    pkg_map = make_pkg_map([
        'fuchsia-pkg://fuchsia.com/root#meta/root.cbl',
        'fuchsia-pkg://fuchsia.com/bootstrap#meta/bootstrap.cbl',
        'fuchsia-pkg://fuchsia.com/core#meta/core.cbl',
        'fuchsia-pkg://fuchsia.com/dyn_child#meta/dyn_child.cbl',
        'fuchsia-pkg://fuchsia.com/scenic#meta/scenic.cbl',
        'fuchsia-pkg://fuchsia.com/vulkan_loader#meta/vulkan_loader.cbl'
    ])
    (loader_sender, loader_receiver) = cf_capability_create()
    loader_thread = threading.Thread(target=run_loader,
                                     args=(pkg_map, loader_receiver),
                                     daemon=True)
    loader_thread.start()
    (runner_sender, runner_receiver) = cf_capability_create()
    runner_thread = threading.Thread(target=run_runner,
                                     args=(runner_receiver,),
                                     daemon=True)
    runner_thread.start()
    root = cf_component_create()
    add_framework_service(root)
    cf_component_set_attribute(root, 'url', 'fuchsia-pkg://fuchsia.com/root#meta/root.cbl')
    cf_directory_add_child(cf_component_get_incoming(root), 'loader',
                           loader_sender)
    cf_directory_add_child(cf_component_get_incoming(root), 'runner', runner_sender)
    print('resolving root component')
    resolve_component(root)

    #bootstrap = cf_component_get_child(root, 'bootstrap')
    #bootstrap_incoming_namespace = cf_component_get_incoming_namespace(bootstrap)
    #bootstrap_pkg = cf_component_get_pkg_directory(bootstrap)
    #cf_directory_add_child(bootstrap_incoming_namespace, 'pkg', bootstrap_pkg)

    # Hacky sleep to give resolution time to complete
    time.sleep(0.2)
    print_tree(root)
