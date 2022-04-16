{
  program: {
    bin: "bin/scenic.py",
  },
  routes: [
    {
      src: "#parent",
      src_name: "vulkan_loader",
      dst: "#self",
      dst_name: "svc/vulkan_loader"
    },
  ],
}