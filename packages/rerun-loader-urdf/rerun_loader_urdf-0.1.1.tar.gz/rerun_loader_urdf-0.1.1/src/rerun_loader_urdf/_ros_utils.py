import os
from pathlib import Path
from typing import Optional


def resolve_ros_path(path_str: str) -> str:
    """Resolve a ROS path to an absolute path."""
    if path_str.startswith("package://"):
        path = Path(path_str)
        package_name = path.parts[1]
        relative_path = Path(*path.parts[2:])

        package_path = (
            resolve_ros1_package(package_name)
            or resolve_ros2_package(package_name)
            or resolve_robot_description_package(package_name, relative_path)
        )

        if package_path is None:
            raise ValueError(
                f"Could not resolve {path}."
                f"Replace with relative / absolute path, source the correct ROS environment, or install {package_name}."
            )

        return str(package_path / relative_path)
    elif path_str.startswith("file://"):
        return path_str[len("file://") :]
    else:
        return path_str


def resolve_ros2_package(package_name: str) -> Optional[str]:
    try:
        import ament_index_python

        try:
            return ament_index_python.get_package_share_directory(package_name)
        except ament_index_python.packages.PackageNotFoundError:
            return None
    except ImportError:
        return None


def resolve_ros1_package(package_name: str) -> Optional[str]:
    try:
        import rospkg

        try:
            return rospkg.RosPack().get_path(package_name)
        except rospkg.ResourceNotFound:
            return None
    except ImportError:
        return None


def resolve_robot_description_package(package_name: str, relative_path: str) -> Optional[str]:
    cache_dir = os.path.expanduser(os.environ.get("ROBOT_DESCRIPTIONS_CACHE", "~/.cache/robot_descriptions"))
    # check that cache_dir exists
    cache_dir = Path(os.path.abspath(os.path.expanduser(cache_dir)))
    abs_path = find_first_absolute_path(cache_dir, relative_path)
    if abs_path:
        return abs_path.replace(str(relative_path), "")
    else:
        return None


def find_first_absolute_path(root_dir, suffix_path):
    root = Path(root_dir)
    pattern = f"*/{suffix_path}"  # e.g., */logs/output.txt

    for path in root.rglob(pattern):
        return str(path.resolve())
