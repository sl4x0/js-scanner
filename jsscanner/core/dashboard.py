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
    """Real-time TUI dashboard for scan progress"""
    
    def __init__(self, target: str, console: Console = None):
        """
        Initialize dashboard
        
        Args:
            target: Target domain being scanned
            console: Rich console instance
        """
        self.target = target
        self.console = console or Console()
        self.start_time = datetime.now()
        
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
        """Start the live dashboard"""
        self.discovery_task = self.progress.add_task("[cyan]Discovery", total=100)
        self.download_task = self.progress.add_task("[yellow]Download", total=100)
        self.analysis_task = self.progress.add_task("[green]Analysis", total=100)
        
        self.live = Live(
            self._generate_layout(),
            console=self.console,
            refresh_per_second=4,
            vertical_overflow="visible"
        )
        self.live.start()
    
    def stop(self):
        """Stop the live dashboard"""
        if self.live:
            self.live.stop()
    
    def update_stats(self, **kwargs):
        """Update statistics"""
        self.stats.update(kwargs)
        if self.live:
            self.live.update(self._generate_layout())
    
    def update_progress(self, phase: str, current: int, total: int):
        """Update progress bars"""
        if total == 0:
            return
        
        percentage = (current / total) * 100
        
        if phase == "discovery":
            self.progress.update(self.discovery_task, completed=percentage)
        elif phase == "download":
            self.progress.update(self.download_task, completed=percentage)
        elif phase == "analysis":
            self.progress.update(self.analysis_task, completed=percentage)
        
        if self.live:
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
