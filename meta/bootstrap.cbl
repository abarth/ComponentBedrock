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

  ]
}