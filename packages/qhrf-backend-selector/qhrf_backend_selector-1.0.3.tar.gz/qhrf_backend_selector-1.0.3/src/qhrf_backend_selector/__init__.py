from .selector import (
    list_and_select_backend,
    get_backend_details,
    check_authentication,
    setup_authentication,
    BackendInfo,
)
from .utils import (
    format_backend_status,
    get_backend_performance,
    recommend_backend,
)

__version__ = "1.0.3"
__author__ = "Zach White"
__email__ = "Xses.Science@gmail.com"

__all__ = [
    "list_and_select_backend",
    "get_backend_details", 
    "check_authentication",
    "setup_authentication",
    "BackendInfo",
    "format_backend_status",
    "get_backend_performance",
    "recommend_backend",
]