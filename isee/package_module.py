"""Generate Python Package with setup.cfg and setup.py configured to embed dependency wheels and
install them.
"""

import tempfile
from functools import partial
from pathlib import Path
from typing import List, Union
import os
import shutil
from distutils.command.sdist import sdist
from setuptools import setup
from setuptools.command.install import install as _install

from isee import generate_project_wheels


def generate_package(
    module_path: Union[str, Path],
    install_requires: List[str],
    output_path: Union[str, Path],
):
    """

    :param module_path: Path to python folder or .py file to package
    :param install_requires: required package list like in setup.py or requirements.txt
    :param output_path: Folder to output package. Must not already exist.
    :return:
    """
    module_path = Path(module_path)
    assert module_path.exists(), f'module does not exist: "{str(module_path)}"'
    assert not os.path.exists(
        output_path
    ), f'output path already exists: "{output_path}"'

    with tempfile.TemporaryDirectory() as temp_dir:
        print('Created temporary directory:', temp_dir)
        temp_path = Path(temp_dir)

        generate_module_folder(module_path, dst_path=temp_path)

        (temp_path / 'setup.cfg').write_text(
            setup_cfg_template(install_requires, name=module_path.stem)
        )
        (temp_path / 'setup.py').write_text(setup_py)
        (temp_path / 'MANIFEST.in').write_text(manifest_in)

        shutil.copytree(temp_path, output_path)


def generate_module_folder(module_path: Path, dst_path: Path):
    if module_path.is_dir():
        shutil.copytree(module_path, dst_path / module_path.name)
    elif module_path.is_file() and module_path.suffix == '.py':
        module_folder = dst_path / module_path.stem
        module_folder.mkdir()
        shutil.copy(module_path, module_folder / '__init__.py')
    else:
        raise ValueError('module path must be a directory or .py file')


def setup_cfg_template(
    install_requires: List[str], name: str, version: str = '1.0.0'
) -> str:
    setup_cfg = f'''[metadata]
name = {name}
version = {version}
url = https://github.com/otosense/isee
platforms = any
description_file = README.md
root_url = https://github.com/otosense/
license = None
author = isee
author_email = andie.phan@analog.com
description = {name}
long_description = file:README.md
long_description_content_type = text/markdown

[options]
packages = find:
include_package_data = True
zip_safe = False
install_requires = 
    isee
'''
    for r in install_requires:
        if r != 'isee':
            setup_cfg += f'    {r}\n'
    return setup_cfg


class CustomSdistCommand(sdist):
    """Custom sdist command to include wheels in the distribution"""

    description = 'create a source distribution tarball with embedded wheels'

    def _remove_wheels_from_install_requires(self, wheel_package_names):
        project_dir = os.getcwd()
        requirements_filepath = os.path.join(project_dir, 'requirements.txt')
        setup_cfg_filepath = os.path.join(project_dir, 'setup.cfg')
        if os.path.isfile(requirements_filepath):
            self._remove_lines(requirements_filepath, wheel_package_names)
        if os.path.isfile(setup_cfg_filepath):
            self._remove_lines(setup_cfg_filepath, wheel_package_names)

    def _remove_lines(self, filepath, exclude_lines):
        with open(filepath, 'r') as file:
            lines = file.readlines()

        # Find the line to delete and remove it
        new_lines = []
        for line in lines:
            if line.strip() not in exclude_lines:
                new_lines.append(line)
            else:
                print(f'Removing {line.strip()} from {filepath}')

        # Write the new lines back to the file
        with open(filepath, 'w') as file:
            file.writelines(new_lines)

    def _save_original_files(self):
        project_dir = os.getcwd()

        requirements_filepath = os.path.join(project_dir, 'requirements.txt')
        setup_cfg_filepath = os.path.join(project_dir, 'setup.cfg')
        if os.path.isfile(requirements_filepath):
            with open(requirements_filepath, 'r') as f:
                self._requirements_txt = f.read()
        else:
            self._requirements_txt = None
        if os.path.isfile(setup_cfg_filepath):
            with open(setup_cfg_filepath, 'r') as f:
                self._setup_cfg = f.read()
        else:
            self._setup_cfg = None

    def _restore_original_files(self):
        project_dir = os.getcwd()

        if self._requirements_txt:
            print('Restoring requirements.txt')
            requirements_filepath = os.path.join(project_dir, 'requirements.txt')
            if os.path.isfile(requirements_filepath):
                with open(requirements_filepath, 'w') as f:
                    f.write(self._requirements_txt)
        if self._setup_cfg:
            print('Restoring setup.cfg')
            setup_cfg_filepath = os.path.join(project_dir, 'setup.cfg')
            if os.path.isfile(setup_cfg_filepath):
                with open(setup_cfg_filepath, 'w') as f:
                    f.write(self._setup_cfg)

    def _generate_wheels(self):

        if self.dist_dir is None:
            self.dist_dir = 'dist'
        if os.path.exists(self.dist_dir):
            print(f'Deleting {self.dist_dir}')
            shutil.rmtree(self.dist_dir)
        os.mkdir(self.dist_dir)

        # create a temporary directory to store the wheels
        project_dir = os.getcwd()
        wheel_generation_dir = os.path.join(project_dir, 'wheels')
        if os.path.exists(wheel_generation_dir):
            print(f'Deleting {wheel_generation_dir}')

            shutil.rmtree(wheel_generation_dir)
        os.mkdir(wheel_generation_dir)
        print('Generating dependency wheels')
        git_info = generate_project_wheels(
            project_dir, wheel_generation_dir, github_credentails=None
        )
        wheel_package_names = {g['name'] for g in git_info}
        # remove wheels from install_requires to skip pip dependency pre-check
        self._remove_wheels_from_install_requires(wheel_package_names)
        # copy the wheels into the package directory
        wheelhouse_dir = os.path.join(wheel_generation_dir, 'wheelhouse')
        for wheel_file in os.listdir(wheelhouse_dir):
            if wheel_file.endswith('.whl'):
                copy_wheel_file = os.path.join(wheelhouse_dir, wheel_file)
                shutil.copy2(copy_wheel_file, self.dist_dir)
                print(f'Copying to {copy_wheel_file}')

        # cleanup the temporary directory
        shutil.rmtree(wheel_generation_dir)

    def initialize_options(self) -> None:
        super().initialize_options()
        # generating wheels here to modify setup.cfg before it's automatically copied
        self._save_original_files()
        try:
            self._generate_wheels()
        except Exception as e:
            self._restore_original_files()
            raise e

    def run(self):
        super().run()
        self._restore_original_files()


class CustomInstallCommand(_install):
    """Custom pip install command to install embedded wheels"""

    def run(self):
        temp_dir = os.getcwd()

        # Install wheels from the dist directory of the tarball
        if os.path.isdir(dist_dir := os.path.join(temp_dir, 'dist')):
            for wheel in os.listdir(dist_dir):
                if wheel.endswith('.whl'):
                    print(f'Installing {wheel}')
                    self.spawn(
                        [
                            'pip',
                            'install',
                            os.path.join(dist_dir, wheel),
                            f'--find-links={dist_dir}',
                        ]
                    )

        # Run Normal Install
        _install.run(self)


embedded_wheel_setup = partial(
    setup, cmdclass={'install': CustomInstallCommand, 'sdist': CustomSdistCommand}
)
setup_py = (
    'from isee.package_module import embedded_wheel_setup\nembedded_wheel_setup()'
)
manifest_in = 'recursive-include dist *.whl'
