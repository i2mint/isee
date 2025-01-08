# Introduction
Python continuous integration (CI) support tools.

To install:	```pip install isee```

[Documentation here](https://i2mint.github.io/isee/index.html).

1. [Introduction](#introduction)
2. [Goal](#goal)
3. [Workflow](#workflow)
4. [Results and Logs](#results-and-logs)
5. [Versioning](#versioning)
6. [Skip CI](#skip-ci)
7. [Hosting](#hosting)
8. [How to setup CI](#how-to-setup-ci)
    * [For a GitHub repository](#for-a-github-repository)
    * [For a GitLab repository](#for-a-gitlab-repository)
9. [Useful resources](#useful-resources)
10. [Troubleshooting](#troubleshooting)
    * [Common non fatal error during publishing](#common-non-fatal-error-during-publishing)
    * [Github token problems (e.g. tagging)](#github-token-problems-eg-tagging)
    * [Vesion tag misalignment](#vesion-tag-misalignment)


# Goal
The goal of CI is to automate code formatting, validation, deployment and publishing of packages. 

# Workflow
A CI pipeline is triggered when new code is pushed to a remote repository.
Every CI pipeline does at least:
1. Code formatting
    * Apply automated linting on source code
    * Push back the formatted code to the remote repository
2. Code validation
    * Testing (unit tests, integration tests, doctests)
    * Docstring validation (only for frameworks)
3. Deployment to an integration environment for applications / Publishing for frameworks -- (only on *master* and only if the *Validation* step succeeded)
    * Semi-automated versioning (see the [Versioning](#versioning) section) + Tag the repository with the new generated version number
    * Packaging
    * Deployment / Publishing

# Results and Logs
You can see your CI pipeline's result and logs:
* From your **GitLab project page &rarr; CI/CD &rarr; Pipelines**
* From your **GitHub project page &rarr; Actions &rarr; Continuous Integration**

# Versioning
Versioning is semi-automatically resolved: if you want the major or minor part to be bumped, you only have to add ***[bump major]*** or ***[bump minor]*** to your commit message on *master* (versioning is not applied to other branches).

Example, the current version number is **1.0.5**.
If you commit with the following message:
```
Added some new stuff.
```
the new version number will be **1.0.6**.
But if you commit with the following message:
```
Added some great new stuff! [bump minor]
```
the new version number will be **1.1.0**.
Finally, if you commit with the following message:
```
Added some extraordinary new stuff!!! [bump major]
```
the new version number will be **2.0.0**.

# Skip CI
You can prevent the CI pipeline from being triggered by adding ***[skip ci]*** to your commit message.
Example:
```
Updated the README file. [skip ci]
```
**Be careful!** If you skip the CI process, any new code will not be validated and no new version will be deployed/published. So, think twice before using it.

# Hosting
CI pipelines for GitHub public repositories are run on GitHub-hosted runners. See the [GitHub documentation](https://docs.github.com/en/free-pro-team@latest/actions/learn-github-actions/introduction-to-github-actions#runners) for more details

# How to setup CI
This "How to" section applies to python package projects only. If you want to setup CI to an application project or another programing language, you will have to modify the CI pipeline definition according to your needs.

## For a GitHub repository
1. Add this [ci.yml](resources/ci.yml) file to the `github/workflow/` directory (create the directory if it doesn't exist) into your local repository.
Note that [wads](https://pypi.org/project/wads/) does it for you by running the following command from the project's root directory (documentation [here](https://i2mint.github.io/wads/module_docs/wads/populate.html)):
```
 populate . --root-url=GITHUB_ROOT_URL
```
Note that you can specify the root directory (in case you're not in the root directory), root url (in case the directory is not already associated to a git repo), and have many other parametrization choices. 

Fear not: `populate` will **not** create or modify the `ci.yml` file (or any other file) if there is one already. 

2. In the `ci.yml` file, replace `#PROJECT_NAME#` with the project name (must be the exact same name as the main module of the project, not needed if you ran the `populate` tool because it did it for you) and modify the pipeline workflow to suit the project's needs. Documentation [here](https://docs.github.com/en/free-pro-team@latest/actions/reference/workflow-syntax-for-github-actions).
3. Add secrets `PYPI_USERNAME` and `PYPI_PASSWORD` with your PYPI credentials to the remote repository. Documentation [here](https://docs.github.com/en/free-pro-team@latest/actions/reference/encrypted-secrets).
4. If you want the project's documentation to be published, configure the project's Github Pages for the project by selecting the `/docs` folder. Documentation [here](https://guides.github.com/features/pages/).
5. Push your code and see the execution of the new `Continuous Integration` workflow. Documentation [here](https://docs.github.com/en/free-pro-team@latest/actions/managing-workflow-runs).
Consider using [wads](https://pypi.org/project/wads/) to automatically validate your code locally, commit and push by running the following command (documentation [here](https://i2mint.github.io/wads/module_docs/wads/pack.html)):
```
pack check-in 'Your commit message.'
```

# Useful resources

[troubleshooting tests](https://github.com/i2mint/tested/wiki/Troubleshooting-Tests)

# Troubleshooting

## Common (non fatal) error during publishing

It has been reported that users get this error:

```
/home/runner/work/_temp/1a136567-cb0c-4c9f-a44f-4cbe6633d4eb.sh: line 2: --non-interactive: command not found
Error: Process completed with exit code 127.
```

when publishing. The package publishes fine, but this error causes the CI "publish" part to show up as red, which is annoying. 

Solution: This will happen when any of the variables (most of the time, the PYPI_PASSWORD contain newlines in it, which breaks the `twine upload ...` command into several pieces. 
This can happen, for example, when copy/pasting from doing a `echo $PYPI_TOKEN | pbcopy` since the echo adds a newline. 
Try copying the pypi token again and ensure there's no newline in it. 

## Github token problems (e.g. tagging)

At the point of writing this, some jobs don't fail when there are (non-essential) errors.
One hidden problem that you might get in when "Tag Repository With New Version Number" does a `Run isee tag-repo $VERSION`. You'll get:

```
remote: Permission to thorwhalen/sung.git denied to github-actions[bot].
fatal: unable to access 'https://github.com/thorwhalen/sung/': The requested URL returned error: 403
Error executing git command: Command 'git --git-dir="/home/runner/work/sung/sung/.git" --work-tree="/home/runner/work/sung/sung" push origin 0.0.16' returned non-zero exit status 128.
Standard output: 
Exit code: 128
```

Top cause and solution:
* Check Repository Permissions: Ensure that the `GITHUB_TOKEN` has the necessary permissions (i.e. read **and write**) to push to the repository.
You can configure this in the repository settings under Actions -> General -> Workflow permissions (`https://github.com/{username_or_org}/{repo}/settings/actions`).

![image](https://github.com/user-attachments/assets/0a35c514-216c-4616-92fa-b8978762594c)

Other possible problesm:
* Verify SSH keys: Did you put a ssh public key, and a corresponding SSH_PRIVATE_KEY in your environment), and are they correct?
Global ssh public keys can be managed [here in user or org level settings](https://github.com/settings/keys). 
Set repository secrets (envoronment variable) here: `https://github.com/{username_or_org}/{repo}/settings/secrets/actions`.
* Review the Token Usage
* Check Branch Protection Rules


## Vesion tag misalignment

Sometimes the twine PYPI publishing may fail with such a message:

```
WARNING  Skipping PKGNAME-0.1.4-py3-none-any.whl because it appears to already exist 
WARNING  Skipping PKGNAME-0.1.4.tar.gz because it appears to already exist
```

This often means that your git tags are misaligned with the `setup.cfg` version. 
You can see your git tags here: `https://github.com/ORG/REPO/tags`.

To repair, do this:

* go to the https://pypi.org/project/ project page and note the PYPI_VERSION number
* got to `setup.cfg` and see what version is there, called it SETUP_VERSION
* make a NEW_VERSION, which is a version number ABOVE the SETUP_VERSION and PYPI_VERSION.
* edit the `setup.cfg` so it shows NEW_VERSION
* `git tag NEW_VERSION`
* `git push origin NEW_VERSION`

Sometimes I need to update the setup version again, and push again.
