{
  children: [
    {
      name: "scenic",
      url: "fuchsia-pkg://fuchsia.com/scenic#meta/scenic.cbl",
      eager: true,
    }
  ],
  routes: [
    {
      src: "#parent",
      name: "vulkan_loader",
      dst: "scenic",
    },
  ]
}
