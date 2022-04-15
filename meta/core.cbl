{
  children: [
    {
      name: "scenic",
      url: "fuchsia-pkg://fuchsia.com/scenic#meta/scenic.cbl",
      eager: true,
    },
    {
      name: "dyn_child",
      url: "fuchsia-pkg://fuchsia.com/dyn_child#meta/dyn_child.cbl",
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
