
from porcelain import *

def main():
    svc = cf_directory_open(__NAMESPACE__.in_dir, "svc")
    assert svc is not None
    vulkan_loader = cf_directory_open(svc, "vulkan_loader")
    assert vulkan_loader is not None
    print('SCENIC SENDING MESSAGE')
    cf_capability_send(vulkan_loader, "hello world")

main()
