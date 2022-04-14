
from porcelain import *

def main():
    incoming_services = cf_directory_open(__NAMESPACE__.in_dir, 'svc')
    lib = cf_directory_open(incoming_services, "vulkan_loader")
    print('SCENIC SENDING MESSAGE')
    cf_capability_send(lib, "hello world")

main()
