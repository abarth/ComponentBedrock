// Equivalent to create_topology() in Component Bedrock Language (pseudo-cml)
{
  children: [
    {
      name: "bootstrap",
      url: "meta/bootstrap.cbl",
    },
    {
      name: "core",
      url: "meta/core.cbl",
    },
    {
      name: "vulkan_loader",
      url: "meta/vulkan_loader.cbl",
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