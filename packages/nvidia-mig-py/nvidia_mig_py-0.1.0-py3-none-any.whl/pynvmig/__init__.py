from .mig_allocator import MIGInstanceAllocator
from .mig_manager import MIGConfigManager
# from .mig_monitor import dcgm_monitor_mig_resource, dcgm_monitor_gpu_resource

_MAJOR = 0  # Major version number
_MINOR = 1  # Minor version number
_PATCH = 0  # Patch version number

__version__ = f"{_MAJOR}.{_MINOR}.{_PATCH}"

__all__ = [
    "__version__",
    "MIGInstanceAllocator",
    "MIGConfigManager",
    # "dcgm_monitor_mig_resource",
    # "dcgm_monitor_gpu_resource"
]
