{
  bin: 'bin/vulkan_loader.py',
  routes: [
    {
      src: "#self",
      src_name: "vulkan_lib",
      dst: "#parent",
      dst_name: "vulkan_lib"
    },
    // or
    //{
    //  src: "#framework",
    //  src_name: "pkg",
    //  dst: "#parent",
    //  dst_name: "vulkan_lib"
    //},
    // or:
    //{
    //  src: "#self:framework",
    //  src_name: "pkg/data/lib",
    //  dst: "#parent",
    //  dst_name: "vulkan_lib"
    //},
  ]
}