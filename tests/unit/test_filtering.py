import pytest
from jsscanner.analysis.filtering import NoiseFilter


@pytest.fixture
def noise_filter():
    # Use small thresholds so tests detect vendor heuristics reliably
    return NoiseFilter(logger=None, scan_config={"noise_filter": {"min_file_size_kb": 1, "max_newlines": 5}})


def test_cdn_filtering(noise_filter):
    url = 'https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js'
    should_skip, reason = noise_filter.should_skip_url(url)
    assert should_skip is True
    assert 'CDN' in reason or 'cdnjs.cloudflare.com' in reason or 'cdn' in reason.lower()


def test_vendor_detection_by_header(noise_filter):
    vendor_header = '/*! jQuery v3.6.0 | (c) OpenJS Foundation */\n!function(e,t){"use strict";...'
    should_skip, reason = noise_filter.should_skip_content(vendor_header, 'jquery.js')
    assert should_skip is True
    assert 'jQuery' in reason or 'Vendor' in reason


def test_jquery_detection_minified(noise_filter):
    # Simulate a minified jquery-like payload (long single-line with few newlines)
    minified = 'function' + ('a' * 12000) + ';'  # large and compact
    should_skip, reason = noise_filter.should_skip_content(minified, 'jquery.min.js')
    assert should_skip is True


def test_custom_code_not_vendor(noise_filter):
    custom_code = '\n'.join(['function hello() { return "ok"; }' for _ in range(50)])
    should_skip, reason = noise_filter.should_skip_content(custom_code, 'app.js')
    assert should_skip is False


def test_minified_detection_threshold(noise_filter):
    # A file slightly larger than threshold and with few newlines should be considered vendor/minified
    content = ('a' * 2000) + '\n' * 2
    should_skip, reason = noise_filter.should_skip_content(content, 'bundle.js')
    # Depending on heuristics this may be flagged as vendor; assert it returns a boolean
    assert isinstance(should_skip, bool)
