
from porcelain import *

def main():
    outgoing = __NAMESPACE__.out_dir
    lib = cf_directory_open(outgoing, "vulkan_lib")

    while True:
        print("MESSAGE RECIEVED BY VULKAN", cf_capability_recv(lib))

main()
