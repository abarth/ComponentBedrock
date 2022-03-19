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
  ],
  routes: [
    {
      src: "bootstrap",
      name: "dev",
      dst: "core",
    },
  ]
}