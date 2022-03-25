{
  routes: [
    {
      // Gabe: What if `src` specified one of the component's various directories?
      // ie: out, pkg, ...
      src: "#self", // where does this come from?
      src_name: "dev",
      dst: "#parent",
      dst_name: "dev"
    },
    {
      //src: "#self:incoming",
      //src_name: "pkg/data/lib",
      //src_name: "/incoming/pkg/data/lib",
      src: "#framework",
      src_name: "pkg",
      dst: "#parent",
      dst_name: "vulkan_lib"
    }
.   // or:
.   {
      src: "#self:pkg",
      src_name: "data/lib",
      dst: "#parent",
      dst_name: "vulkan_lib"
    }
    // or:
.   {
      src: "#self:framework",
      src_name: "pkg/data/lib",
      dst: "#parent",
      dst_name: "vulkan_lib"
    }
  ]
}