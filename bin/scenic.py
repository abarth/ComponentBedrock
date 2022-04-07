
from porcelain import *

def main():
    incoming = cf_component_get_incoming_namespace(__HANDLE__)
    lib = cf_directory_open(incoming, "vulkan_loader")
    print('SCENIC SENDING MESSAGE')
    cf_capability_send(lib, "hello world")

main()
