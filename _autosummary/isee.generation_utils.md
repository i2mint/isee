# isee.generation_utils

Generation utils for the isee package.

Main function:

- gen_semver: Generate a new semantic version based on git commit messages and tags.

Documentation generation used to live here too; it moved out to
`i2mint/epythet/actions/publish-github-pages`, which is what this repo’s own
CI uses.

### Functions

| [`gen_semver`](#isee.generation_utils.gen_semver)(\*[, dir_path, ...])       | Generate a new semantic version based on git commit messages and tags.                          |
|----------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------|
| [`get_new_version`](#isee.generation_utils.get_new_version)(\*[, work_tree, ...]) | Get the latest version from git tags and determine the new version based on the commit message. |

### isee.generation_utils.gen_semver(, dir_path=None, version_patch_prefix='', output_mode='auto')

Generate a new semantic version based on git commit messages and tags.

### Args

- dir_path (str): The directory path where the git repository is located.
  : If None, uses the current directory.
- version_patch_prefix (str): A prefix to be added to the patch version.
- output_mode (str): How to output the version:
  : - “auto”: Detect if running in GitHub Actions and adjust accordingly
    - “print”: Only print to stdout (for shell capture)
    - “return”: Only return (for Python API use)
    - “both”: Both print and return

### Returns

- str: The new version string if output_mode is “return” or “both”.
- None: If output_mode is “print”.

### isee.generation_utils.get_new_version(\*, work_tree='.', version_patch_prefix='', action_when_versions_not_valid=<built-in function warn>)

Get the latest version from git tags and determine the new version based on
the commit message.
