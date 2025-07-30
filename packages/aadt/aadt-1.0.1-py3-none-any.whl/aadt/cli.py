#!/usr/bin/env python

# Anki Add-on Builder
#
# Copyright (C)  2016-2021 Aristotelis P. <https://glutanimate.com/>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version, with the additions
# listed at the end of the license file that accompanied this program.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# NOTE: This program is subject to certain additional terms pursuant to
# Section 7 of the GNU Affero General Public License.  You should have
# received a copy of these additional terms immediately following the
# terms and conditions of the GNU Affero General Public License that
# accompanied this program.
#
# If not, please request a copy through one of the means of contact
# listed here: <https://glutanimate.com/contact/>.
#
# Any modifications to this file must keep this entire header intact.

import argparse
import logging
import sys
from collections.abc import Callable
from typing import Any

from . import COPYRIGHT_MSG, DIST_TYPES, PATH_PROJECT_ROOT
from .builder import AddonBuilder, VersionError, clean_repo
from .config import PATH_CONFIG, Config
from .git import VersionManager
from .init import ProjectInitializationError, ProjectInitializer
from .manifest import ManifestUtils
from .ui import UIBuilder


class CLIError(Exception):
    """Exception raised for CLI-specific errors"""

    pass


# Checks
##############################################################################


def validate_cwd() -> bool:
    """Checks if CWD is a valid project root."""
    return (PATH_PROJECT_ROOT / "src").exists() and PATH_CONFIG.exists()


# Helpers
##############################################################################


def _get_dist_list(dist_arg: str) -> list[str]:
    """Get list of distributions to build based on argument"""
    return [dist_arg] if dist_arg != "all" else DIST_TYPES


def _execute_multi_dist_task(
    task_name: str,
    dists: list[str],
    task_func: Callable[..., Any],
    version: str | None = None,
    **kwargs: Any,
) -> None:
    """Execute a task across multiple distribution types"""
    try:
        builder = AddonBuilder(version=version)
    except VersionError as e:
        raise CLIError(f"Failed to initialize builder: {e}") from e

    total = len(dists)
    for cnt, dist in enumerate(dists, 1):
        logging.info("\n=== %s task %s/%s ===", task_name.title(), cnt, total)
        task_func(builder, dist, **kwargs)


# Entry points
##############################################################################


def build(args: argparse.Namespace) -> None:
    """Build and package add-on for distribution"""
    _execute_multi_dist_task(
        task_name="build",
        dists=_get_dist_list(args.dist),
        task_func=lambda builder, dist, **kwargs: builder.build(
            disttype=dist, **kwargs
        ),
        version=args.version,
    )


def ui(args: argparse.Namespace) -> None:
    """Compile add-on user interface files"""
    builder = UIBuilder(dist=PATH_PROJECT_ROOT, config=Config())

    logging.info("\n=== Building Qt6 UI ===\n")
    should_create_shim = builder.build()

    if should_create_shim:
        logging.info("\n=== Writing Qt compatibility shim ===")
        builder.create_qt_shim()

    logging.info("Done.")


def manifest(args: argparse.Namespace) -> None:
    """Generate manifest file from add-on properties"""
    try:
        dists = DIST_TYPES if args.dist == "all" else [args.dist]

        config = Config()
        addon_config = config.as_dataclass()
        exclude_patterns = addon_config.build_config.archive_exclude_patterns

        version_manager = VersionManager(PATH_PROJECT_ROOT, exclude_patterns)
        version = version_manager.parse_version(vstring=args.version)
        target_dir = PATH_PROJECT_ROOT / "src" / addon_config.module_name

        for dist_type in dists:
            logging.info(f"Generating manifest for {dist_type} distribution")
            ManifestUtils.generate_and_write_manifest(
                addon_properties=config,
                version=version,
                dist_type=dist_type,  # type: ignore
                target_dir=target_dir,
            )
    except Exception as e:
        raise CLIError(f"Failed to generate manifest: {e}") from e


def create_dist(args: argparse.Namespace) -> None:
    """Prepare source tree distribution for building"""
    try:
        builder = AddonBuilder(version=args.version)
        builder.create_dist()
    except VersionError as e:
        raise CLIError(f"Failed to create distribution: {e}") from e


def build_dist(args: argparse.Namespace) -> None:
    """Build add-on files from prepared source tree"""
    _execute_multi_dist_task(
        task_name="build_dist",
        dists=_get_dist_list(args.dist),
        task_func=lambda builder, dist, **kwargs: builder.build_dist(
            disttype=dist, **kwargs
        ),
        version=args.version,
    )


def package_dist(args: argparse.Namespace) -> None:
    """Package pre-built distribution into distributable package"""
    _execute_multi_dist_task(
        task_name="package_dist",
        dists=_get_dist_list(args.dist),
        task_func=lambda builder, dist: builder.package_dist(disttype=dist),
        version=args.version,
    )


def clean(args: argparse.Namespace) -> None:
    """Clean leftover build files"""
    clean_repo()


def init(args: argparse.Namespace) -> None:
    """Initialize a new add-on project"""
    from pathlib import Path

    target_dir = Path(args.directory).resolve() if args.directory else Path.cwd()

    initializer = ProjectInitializer(target_dir)
    try:
        initializer.init_project(interactive=not args.yes)
    except ProjectInitializationError as e:
        raise CLIError(f"Failed to initialize project: {e}") from e


# Argument parsing
##############################################################################


def construct_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.set_defaults(func=lambda x: parser.print_usage())
    subparsers = parser.add_subparsers()

    # Logging options (mutually exclusive)
    log_group = parser.add_mutually_exclusive_group()
    log_group.add_argument(
        "-v",
        "--verbose",
        help="Enable verbose output (debug level)",
        action="store_true",
    )
    log_group.add_argument(
        "-q",
        "--quiet",
        help="Quiet mode (errors only)",
        action="store_true",
    )

    dist_parent = argparse.ArgumentParser(add_help=False)
    dist_parent.add_argument(
        "-d",
        "--dist",
        help="Distribution channel to build for",
        type=str,
        default="local",
        choices=["local", "ankiweb", "all"],
    )

    build_parent = argparse.ArgumentParser(add_help=False)
    build_parent.add_argument(
        "version",
        nargs="?",
        help="Version to (pre-)build as a git reference "
        "(e.g. 'v1.2.0' or 'd338f6405'). "
        "Special keywords: 'dev' - working directory, "
        "'current' – latest commit, 'release' – latest tag. "
        "Leave empty to build latest tag.",
    )

    build_group = subparsers.add_parser(
        "build",
        parents=[build_parent, dist_parent],
        help="Build and package add-on for distribution",
    )
    build_group.set_defaults(func=build)

    ui_group = subparsers.add_parser(
        "ui", parents=[], help="Compile add-on user interface files"
    )
    ui_group.set_defaults(func=ui)

    manifest_group = subparsers.add_parser(
        "manifest",
        parents=[build_parent, dist_parent],
        help="Generate manifest file from add-on properties",
    )
    manifest_group.set_defaults(func=manifest)

    init_group = subparsers.add_parser("init", help="Initialize a new add-on project")
    init_group.add_argument(
        "directory",
        nargs="?",
        help="Target directory for the new project (default: current directory)",
    )
    init_group.add_argument(
        "-y",
        "--yes",
        help="Use default values without prompting",
        action="store_true",
    )
    init_group.set_defaults(func=init)

    clean_group = subparsers.add_parser("clean", help="Clean leftover build files")
    clean_group.set_defaults(func=clean)

    create_dist_group = subparsers.add_parser(
        "create_dist",
        parents=[build_parent, dist_parent],
        help="Prepare source tree distribution for building under build/dist. "
        "This is intended to be used in build scripts and should be run before "
        "`build_dist` and `package_dist`.",
    )
    create_dist_group.set_defaults(func=create_dist)

    build_dist_group = subparsers.add_parser(
        "build_dist",
        parents=[build_parent, dist_parent],
        help="Build add-on files from prepared source tree under build/dist. "
        "This step performs all source code post-processing handled by "
        "aab itself (e.g. building the Qt UI and writing the add-on manifest). "
        "As with `create_dist` and `package_dist`, this command is meant to be "
        "used in build scripts where it can provide an avenue for performing "
        "additional processing ahead of packaging the add-on.",
    )
    build_dist_group.set_defaults(func=build_dist)

    package_dist_group = subparsers.add_parser(
        "package_dist",
        parents=[build_parent, dist_parent],
        help="Package pre-built distribution of add-on files under build/dist into a "
        "distributable .ankiaddon package. This is inteded to be used in build "
        "scripts and called after both `create_dist` and `build_dist` have been "
        "run.",
    )
    package_dist_group.set_defaults(func=package_dist)

    return parser


# Main
##############################################################################


def main() -> None:
    parser = construct_parser()
    args = parser.parse_args()

    # Configure logging level
    if args.verbose:
        log_level = logging.DEBUG
    elif args.quiet:
        log_level = logging.ERROR
    else:
        log_level = logging.INFO

    logging.basicConfig(
        level=log_level,
        format="%(message)s",
    )

    # Show copyright message unless in quiet mode
    if not args.quiet:
        logging.info(COPYRIGHT_MSG)

    try:
        # Skip validation for init command as it creates the project structure
        if hasattr(args, "func") and args.func != init:
            if not validate_cwd():
                raise CLIError(
                    "Could not find 'src' or 'addon.json'. "
                    "Please run this from the project root."
                )

        args.func(args)

    except CLIError as e:
        logging.error("Error: %s", e)
        sys.exit(1)
    except KeyboardInterrupt:
        logging.info("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        logging.error("Unexpected error: %s", e)
        logging.debug("Full traceback:", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
