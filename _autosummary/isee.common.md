# isee.common

This module contains common functions that are used in multiple modules.

Functions:

- git: Execute a git command and return the output.
- get_env_var: Get the value of an environment variable.
- get_file_path: Get the file path of a file in a directory.

### Functions

| [`get_env_var`](#isee.common.get_env_var)(key)                  | Get the value of an environment variable.    |
|------------------------------------------------------------------------------------|----------------------------------------------|
| `get_file_path`(filename, root_path)                                               |                                              |
| [`git`](#isee.common.git)(\*args[, work_tree, git_dir]) | Execute a git command and return the output. |

### isee.common.get_env_var(key)

Get the value of an environment variable.
If the variable is not defined or is empty, raise a RuntimeError.

* **Parameters:**
  **key** – The name of the environment variable.
* **Returns:**
  The value of the environment variable.
* **Raises:**
  [**RuntimeError**](https://docs.python.org/3/builtins/exceptions.html#RuntimeError) – If the environment variable is not defined or is empty.

```pycon
>>> import os
>>> os.environ['TEST'] = 'test'
>>> get_env_var('TEST')
'test'
```

```pycon
>>> get_env_var('TEST2')
Traceback (most recent call last):
...
RuntimeError: TEST2 is not defined or is empty!
```

```pycon
>>> os.environ['TEST3'] = ''
>>> get_env_var('TEST3')
Traceback (most recent call last):
...
RuntimeError: TEST3 is not defined or is empty!
```

### isee.common.git(\*args, work_tree='.', git_dir=None)

Execute a git command and return the output.

```pycon
>>> git('status')
On branch master
Your branch is up to date with 'origin/master'.

nothing to commit, working tree clean
```
