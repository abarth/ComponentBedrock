
from porcelain import *

def main():
    outgoing_services = cf_directory_open(__NAMESPACE__.out_dir, "svc")
    lib = cf_directory_open(outgoing_services, "vulkan_lib")

    while True:
        print("MESSAGE RECIEVED BY VULKAN", cf_capability_recv(lib))

main()
