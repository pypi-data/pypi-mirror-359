# ====================
# 3. __init__.py
# ====================

"""
Code Complexity Analyzer

A comprehensive Python package for analyzing code complexity, performance metrics, and quality.

Usage:
    import code_analyzer
    
    # Analyze a single file
    code_analyzer.analyze_file('path/to/your/file.py')
    
    # Quick analysis
    code_analyzer.quick_analyze('path/to/your/file.py')
    
    # Analyze entire directory
    code_analyzer.analyze_directory('path/to/your/project/')
    
    # Use the analyzer class directly
    from code_analyzer import CodeAnalyzer
    analyzer = CodeAnalyzer()
    metrics = analyzer.analyze_file('your_file.py')
"""

from .code_analyzer import (
    CodeAnalyzer,
    ComplexityMetrics,
    analyze_file,
    analyze_directory,
    quick_analyze
)

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"
__description__ = "A comprehensive Python code complexity analyzer"

__all__ = [
    'CodeAnalyzer',
    'ComplexityMetrics',
    'analyze_file',
    'analyze_directory',
    'quick_analyze'
]