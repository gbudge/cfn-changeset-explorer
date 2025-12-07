#!/usr/bin/env python3

import logging
from rich.console import Console
from rich.logging import RichHandler

# Initialize rich console for pretty printing
console = Console()

# Configure logging with RichHandler
logging.basicConfig(
    level="INFO",
    format="%(message)s",
    handlers=[RichHandler(console=console, show_time=False, show_level=False, show_path=False)]
)
log = logging.getLogger("rich")
