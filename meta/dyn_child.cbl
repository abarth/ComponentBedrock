{
  program: {
    bin: "bin/dyn_child.py",
  },
  routes: [
    {
      src: "#framework",
      name: "framework",
      dst: "#self",
    },
  ],
}