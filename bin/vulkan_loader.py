
from porcelain import *

def main():
    outgoing = cf_component_get_outgoing_namespace(__HANDLE__)
    lib = cf_directory_open(outgoing, "vulkan_lib")

    while True:
        print("MESSAGE RECIEVED BY VULKAN", cf_capability_recv(lib))

main()
