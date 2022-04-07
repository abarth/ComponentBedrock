{
  bin: "bin/scenic.py",
  routes: [
    {
      src: "#parent",
      name: "vulkan_loader",
      dst: "#self",
    },
  ]
}