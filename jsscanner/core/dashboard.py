"""
Dashboard Module
Rich-based TUI dashboard for live scan visualization
"""
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from rich.live import Live
from rich.console import Console, Group
from rich.text import Text
from datetime import datetime
from typing import Dict


class ScanDashboard:
    """  Real-time TUI dashboard for scan progress"""
    
    def __init__(self, target: str, console: Console = None, logger=None):
        """
        Initialize dashboard
        
        Args:
            target: Target domain being scanned
            console: Rich console instance
            logger: Logger instance to manage console output
        """
        self.target = target
        self.console = console or Console()
        self.logger = logger
        self.start_time = datetime.now()
        
        # Store original console handler state
        self._console_handler = None
        self._original_level = None
        
        # Update throttling to prevent flicker
        self._last_update = 0
        self._update_interval = 0.25  # Minimum 250ms between updates
        
        # Progress tracking
        self.progress = Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=self.console,
            expand=False
        )
        
        # Progress tasks
        self.discovery_task = None
        self.download_task = None
        self.analysis_task = None
        
        # Statistics
        self.stats = {
            'urls_discovered': 0,
            'files_downloaded': 0,
            'files_processed': 0,
            'secrets_found': 0,
            'endpoints_found': 0,
            'errors': 0,
            'phase': 'Initializing'
        }
        
        self.live = None
    
    def start(self):
        """Start the live dashboard and disable console logging"""
        # Disable console logging to prevent interference with Live display
        if self.logger:
            for handler in self.logger.handlers:
                if hasattr(handler, '__class__') and 'RichHandler' in handler.__class__.__name__:
                    self._console_handler = handler
                    self._original_level = handler.level
                    handler.setLevel(100)  # Effectively disable (higher than CRITICAL)
        
        self.discovery_task = self.progress.add_task("[cyan]Discovery", total=100)
        self.download_task = self.progress.add_task("[yellow]Download", total=100)
        self.analysis_task = self.progress.add_task("[green]Analysis", total=100)
        
        self.live = Live(
            self._generate_layout(),
            console=self.console,
            refresh_per_second=2,  # Reduced from 4 to minimize flicker
            vertical_overflow="visible"
        )
        self.live.start()
    
    def stop(self):
        """Stop the live dashboard and re-enable console logging"""
        if self.live:
            self.live.stop()
        
        # Re-enable console logging
        if self._console_handler and self._original_level is not None:
            self._console_handler.setLevel(self._original_level)
    
    def update_stats(self, **kwargs):
        """Update statistics with throttling to prevent flicker"""
        self.stats.update(kwargs)
        if self.live and self._should_update():
            self.live.update(self._generate_layout())
    
    def _should_update(self) -> bool:
        """Check if enough time has passed since last update"""
        import time
        now = time.time()
        if now - self._last_update >= self._update_interval:
            self._last_update = now
            return True
        return False
    
    def update_progress(self, phase: str, current: int, total: int):
        """Update progress bars with throttling"""
        if total == 0:
            return
        
        percentage = (current / total) * 100
        
        if phase == "discovery":
            self.progress.update(self.discovery_task, completed=percentage)
        elif phase == "download":
            self.progress.update(self.download_task, completed=percentage)
        elif phase == "analysis":
            self.progress.update(self.analysis_task, completed=percentage)
        
        if self.live and self._should_update():
            self.live.update(self._generate_layout())
    
    def _generate_layout(self) -> Panel:
        """Generate the dashboard layout"""
        # Header
        duration = (datetime.now() - self.start_time).total_seconds()
        header = Table.grid(padding=1)
        header.add_column(style="cyan", justify="left")
        header.add_column(style="white", justify="right")
        header.add_row(
            f"🎯 Target: [bold]{self.target}[/bold]",
            f"⏱️  Duration: {duration:.1f}s"
        )
        header.add_row(
            f"📍 Phase: [bold yellow]{self.stats['phase']}[/bold yellow]",
            ""
        )
        
        # Findings Counter
        findings = Table.grid(padding=1, expand=True)
        findings.add_column(style="bold", justify="center")
        findings.add_column(style="bold", justify="center")
        findings.add_column(style="bold", justify="center")
        findings.add_column(style="bold", justify="center")
        
        findings.add_row(
            f"[red]🔐 Secrets: {self.stats['secrets_found']}[/red]",
            f"[blue]🔗 Endpoints: {self.stats['endpoints_found']}[/blue]",
            f"[green]📄 Files: {self.stats['files_processed']}[/green]",
            f"[yellow]⚠️  Errors: {self.stats['errors']}[/yellow]"
        )
        
        # Combine into group
        group = Group(
            header,
            "",
            self.progress,
            "",
            findings
        )
        
        return Panel(
            group,
            title="[bold cyan]🚀 JS-Scanner v4.0 - Commander's Dashboard[/bold cyan]",
            border_style="cyan",
            padding=(1, 2)
        )
