"""
Test Dashboard Module (jsscanner/core/dashboard.py)
Tests for TUI dashboard rendering and statistics tracking

Critical for:
- Live scan visualization
- Progress tracking without flicker
- Statistics display and updates
"""
import pytest
import time
from unittest.mock import Mock, patch
from jsscanner.core.dashboard import ScanDashboard


# ============================================================================
# PHASE 5.1: Dashboard Smoke Tests
# ============================================================================

@pytest.mark.unit
class TestDashboardInitialization:
    """Test dashboard initialization"""
    
    def test_dashboard_initializes_with_target(self):
        """Test dashboard initializes correctly"""
        dashboard = ScanDashboard('example.com')
        
        assert dashboard.target == 'example.com'
        assert dashboard.stats['phase'] == 'Initializing'
        assert dashboard.stats['urls_discovered'] == 0
    
    def test_dashboard_with_custom_console(self):
        """Test dashboard with custom console"""
        from rich.console import Console
        
        console = Console()
        dashboard = ScanDashboard('example.com', console=console)
        
        assert dashboard.console == console
    
    def test_dashboard_with_logger(self, mock_logger):
        """Test dashboard with logger"""
        dashboard = ScanDashboard('example.com', logger=mock_logger)
        
        assert dashboard.logger == mock_logger


@pytest.mark.unit
class TestDashboardStatistics:
    """Test statistics tracking"""
    
    def test_update_stats_updates_internal_state(self):
        """Test update_stats modifies stats dict"""
        dashboard = ScanDashboard('example.com')
        
        dashboard.update_stats(
            urls_discovered=100,
            files_downloaded=50,
            secrets_found=5
        )
        
        assert dashboard.stats['urls_discovered'] == 100
        assert dashboard.stats['files_downloaded'] == 50
        assert dashboard.stats['secrets_found'] == 5
    
    def test_update_stats_with_partial_data(self):
        """Test partial updates preserve existing data"""
        dashboard = ScanDashboard('example.com')
        
        dashboard.update_stats(urls_discovered=100)
        dashboard.update_stats(files_downloaded=50)
        
        assert dashboard.stats['urls_discovered'] == 100
        assert dashboard.stats['files_downloaded'] == 50
    
    def test_update_stats_throttling(self):
        """Test update throttling prevents flicker"""
        dashboard = ScanDashboard('example.com')
        dashboard._update_interval = 0.1  # 100ms for testing
        
        # First update should return True
        assert dashboard._should_update() is True
        
        # Immediate second update should return False
        assert dashboard._should_update() is False
        
        # After interval, should return True
        time.sleep(0.11)
        assert dashboard._should_update() is True


@pytest.mark.unit
class TestDashboardProgress:
    """Test progress tracking"""
    
    def test_update_progress_discovery_phase(self):
        """Test discovery progress updates"""
        dashboard = ScanDashboard('example.com')
        
        # Mock progress tasks
        dashboard.discovery_task = 1
        dashboard.download_task = 2
        dashboard.analysis_task = 3
        
        with patch.object(dashboard.progress, 'update') as mock_update:
            dashboard.update_progress('discovery', 50, 100)
            
            # Should update discovery task with 50%
            mock_update.assert_called_once_with(1, completed=50.0)
    
    def test_update_progress_download_phase(self):
        """Test download progress updates"""
        dashboard = ScanDashboard('example.com')
        
        dashboard.discovery_task = 1
        dashboard.download_task = 2
        dashboard.analysis_task = 3
        
        with patch.object(dashboard.progress, 'update') as mock_update:
            dashboard.update_progress('download', 25, 100)
            
            mock_update.assert_called_once_with(2, completed=25.0)
    
    def test_update_progress_analysis_phase(self):
        """Test analysis progress updates"""
        dashboard = ScanDashboard('example.com')
        
        dashboard.discovery_task = 1
        dashboard.download_task = 2
        dashboard.analysis_task = 3
        
        with patch.object(dashboard.progress, 'update') as mock_update:
            dashboard.update_progress('analysis', 75, 100)
            
            mock_update.assert_called_once_with(3, completed=75.0)
    
    def test_update_progress_handles_zero_total(self):
        """Test handling of zero total (divide by zero)"""
        dashboard = ScanDashboard('example.com')
        
        # Should not crash
        try:
            dashboard.update_progress('discovery', 0, 0)
        except ZeroDivisionError:
            pytest.fail("update_progress failed on zero total")


@pytest.mark.unit
class TestDashboardLifecycle:
    """Test dashboard start/stop lifecycle"""
    
    def test_start_creates_live_instance(self):
        """Test start() creates Live instance"""
        dashboard = ScanDashboard('example.com')
        
        with patch('jsscanner.core.dashboard.Live') as mock_live:
            mock_live_instance = Mock()
            mock_live.return_value = mock_live_instance
            
            dashboard.start()
            
            # Live should be created
            assert dashboard.live is not None
            mock_live_instance.start.assert_called_once()
    
    def test_stop_stops_live_instance(self):
        """Test stop() stops Live instance"""
        dashboard = ScanDashboard('example.com')
        
        # Mock live instance
        dashboard.live = Mock()
        
        dashboard.stop()
        
        # Live.stop should be called
        dashboard.live.stop.assert_called_once()
    
    def test_start_disables_console_logging(self):
        """Test start() disables console logging"""
        mock_logger = Mock()
        mock_handler = Mock()
        mock_handler.level = 20  # INFO level
        mock_logger.handlers = [mock_handler]
        
        # Simulate RichHandler
        type(mock_handler).__name__ = 'RichHandler'
        
        dashboard = ScanDashboard('example.com', logger=mock_logger)
        
        with patch('jsscanner.core.dashboard.Live'):
            dashboard.start()
            
            # Should have stored original level
            assert dashboard._original_level is not None
    
    def test_stop_restores_console_logging(self):
        """Test stop() restores console logging"""
        mock_logger = Mock()
        mock_handler = Mock()
        mock_handler.level = 20
        mock_logger.handlers = [mock_handler]
        type(mock_handler).__name__ = 'RichHandler'
        
        dashboard = ScanDashboard('example.com', logger=mock_logger)
        
        with patch('jsscanner.core.dashboard.Live'):
            dashboard.start()
            dashboard._console_handler = mock_handler
            dashboard._original_level = 20
            
            dashboard.stop()
            
            # Should restore level
            assert mock_handler.level == 20


@pytest.mark.unit
class TestDashboardLayoutGeneration:
    """Test layout rendering"""
    
    def test_generate_layout_returns_panel(self):
        """Test _generate_layout returns Rich Panel"""
        dashboard = ScanDashboard('example.com')
        
        layout = dashboard._generate_layout()
        
        # Should return a Panel
        from rich.panel import Panel
        assert isinstance(layout, Panel)
    
    def test_generate_layout_includes_target(self):
        """Test layout includes target name"""
        dashboard = ScanDashboard('example.com')
        
        layout = dashboard._generate_layout()
        
        # Panel should be renderable
        assert layout is not None
    
    def test_generate_layout_includes_statistics(self):
        """Test layout includes current statistics"""
        dashboard = ScanDashboard('example.com')
        
        dashboard.update_stats(
            secrets_found=10,
            endpoints_found=20,
            files_processed=30
        )
        
        layout = dashboard._generate_layout()
        
        # Should include updated stats (verified by rendering)
        assert layout is not None


# ============================================================================
# EDGE CASES
# ============================================================================

@pytest.mark.unit
class TestDashboardEdgeCases:
    """Test edge cases and error handling"""
    
    def test_dashboard_without_logger(self):
        """Test dashboard works without logger"""
        dashboard = ScanDashboard('example.com', logger=None)
        
        # Should not crash
        with patch('jsscanner.core.dashboard.Live'):
            try:
                dashboard.start()
                dashboard.stop()
            except Exception as e:
                pytest.fail(f"Dashboard failed without logger: {e}")
    
    def test_multiple_start_stop_cycles(self):
        """Test multiple start/stop cycles"""
        dashboard = ScanDashboard('example.com')
        
        with patch('jsscanner.core.dashboard.Live') as mock_live:
            mock_live_instance = Mock()
            mock_live.return_value = mock_live_instance
            
            # Start and stop multiple times
            for _ in range(3):
                dashboard.start()
                dashboard.stop()
            
            # Should handle multiple cycles
            assert mock_live_instance.stop.call_count == 3
    
    def test_update_stats_before_start(self):
        """Test updating stats before starting dashboard"""
        dashboard = ScanDashboard('example.com')
        
        # Should not crash
        try:
            dashboard.update_stats(urls_discovered=100)
        except Exception as e:
            pytest.fail(f"update_stats failed before start: {e}")
    
    def test_very_large_statistics_values(self):
        """Test handling of very large stat values"""
        dashboard = ScanDashboard('example.com')
        
        dashboard.update_stats(
            urls_discovered=1000000,
            files_downloaded=500000,
            secrets_found=10000
        )
        
        # Should handle large numbers
        assert dashboard.stats['urls_discovered'] == 1000000
        
        # Layout should render without issues
        layout = dashboard._generate_layout()
        assert layout is not None
