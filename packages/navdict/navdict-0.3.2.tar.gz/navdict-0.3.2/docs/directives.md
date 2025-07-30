# How directives work

## What are directives?

- a string matching `r"^([a-zA-Z]\w+)[\/]{2}(.*)$"` where group 1 is the 
  directive and group 2 is the value

- when the value is a filename or path, it can be absolute or relative
  - absolute: use as is
  - relative: depending on the parent
