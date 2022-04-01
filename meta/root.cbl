// Equivalent to create_topology() in Component Bedrock Language (pseudo-cml)
{
  children: [
    {
      name: "bootstrap",
      url: "fuchsia-pkg://fuchsia.com/bootstrap#meta/bootstrap.cbl",
    },
    {
      name: "core",
      url: "fuchsia-pkg://fuchsia.com/core#meta/core.cbl",
    },
    {
      name: "vulkan_loader",
      url: "fuchsia-pkg://fuchsia.com/vulkan_loader#meta/vulkan_loader.cbl",
    }
  ],
  routes: [
    {
      src: "bootstrap",
      name: "dev",
      dst: "core",
    },
    {
      src: "vulkan_loader",
      name: "vulkan_lib",
      dst: "core",
    }
  ]
}