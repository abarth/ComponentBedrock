{
  program: {
    bin: "bin/dyn_child.py",
  },
  routes: [
    {
      src: "#framework",
      src_name: "framework",
      dst: "#self",
      dst_name: "svc/framework",
    },
  ],
}