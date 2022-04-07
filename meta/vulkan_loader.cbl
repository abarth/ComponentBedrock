 {
  routes: [
    {
      src: "#self:pkg",
      src_name: "data",
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