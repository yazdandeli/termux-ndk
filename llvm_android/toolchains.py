#
# Copyright (C) 2020 The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""APIs for accessing toolchains."""

from pathlib import Path
from typing import Optional

from builder_registry import BuilderRegistry
import paths
import version

class Toolchain:
    """Base toolchain."""

    path: Path

    @property
    def cc(self) -> Path:  # pylint: disable=invalid-name
        """Returns the path to c compiler."""
        raise NotImplementedError()

    @property
    def cxx(self) -> Path:
        """Returns the path to c++ compiler."""
        raise NotImplementedError()

    @property
    def lib_dir(self) -> Path:
        """Returns the path to lib dir."""
        raise NotImplementedError()

    def get_resource_dir(self, arch: str = '') -> Path:
        """Returns resource dir path for an arch."""
        raise NotImplementedError()


class _HostToolchain(Toolchain):
    """Base toolchain that compiles host binary."""

    def __init__(self, path: Path, build_path: Optional[Path] = None) -> None:
        self.path = path
        self.build_path = build_path

    @property
    def cc(self) -> Path:  # pylint: disable=invalid-name
        return self.path / 'bin' / 'clang'

    @property
    def cxx(self) -> Path:
        """Returns the path to c++ compiler."""
        return self.path / 'bin' / 'clang++'

    @property
    def lib_dir(self) -> Path:
        """Returns the path to lib dir."""
        return self.path / 'lib64'

    @property
    def _version_file(self) -> Path:
        return self.path / 'include' / 'clang' / 'Basic'/ 'Version.inc'

    @property
    def _version(self) -> version.Version:
        return version.Version(self._version_file)

    def get_resource_dir(self, arch: str = '') -> Path:
        """Returns the path to resource dir."""
        return (self.lib_dir / 'clang' / self._version.long_version() /
                'lib' / 'linux' / arch)


def build_toolchain_for_path(path: Path, build_path: Optional[Path] = None) -> Toolchain:
    """Returns a toolchain object for a given path."""
    return _HostToolchain(path, build_path)


def get_prebuilt_toolchain() -> Toolchain:
    """Returns the prebuilt toolchain."""
    return build_toolchain_for_path(paths.CLANG_PREBUILT_DIR)


def _get_toolchain_from_builder(builder) -> Toolchain:
    return build_toolchain_for_path(builder.install_dir, builder.output_dir)


def get_toolchain_by_name(name: str) -> Toolchain:
    """Tet a toolchain by name."""
    if name == 'prebuilt':
        return get_prebuilt_toolchain()
    return _get_toolchain_from_builder(BuilderRegistry.get(name))


def get_runtime_toolchain() -> Toolchain:
    """Gets the toolchain used to build runtime."""
    builder = BuilderRegistry.get('stage2')
    if not builder or builder.build_instrumented or builder.debug_build:
        builder = BuilderRegistry.get('stage1')
    return _get_toolchain_from_builder(builder)
