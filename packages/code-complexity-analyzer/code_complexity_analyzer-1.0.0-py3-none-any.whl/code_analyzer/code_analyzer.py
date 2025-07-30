"""
Python Code Complexity Analyzer Package
A comprehensive tool for analyzing Python code complexity, performance metrics, and code quality.

Usage:
    import code_analyzer
    code_analyzer.analyze_file('path/to/your/file.py')
    
    Or:
    from code_analyzer import CodeAnalyzer
    analyzer = CodeAnalyzer()
    analyzer.analyze_file('path/to/your/file.py')
"""

import ast
import re
import os
import sys
import math
from typing import Dict, List, Tuple, Any, Optional, Set
from collections import defaultdict, Counter
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ComplexityMetrics:
    """Data class to store various complexity metrics"""
    file_path: str = ""
    file_name: str = ""
    time_complexity: str = "O(1)"
    space_complexity: str = "O(1)"
    cyclomatic_complexity: int = 1
    cognitive_complexity: int = 0
    lines_of_code: int = 0
    logical_lines: int = 0
    comment_lines: int = 0
    blank_lines: int = 0
    halstead_metrics: Dict[str, float] = field(default_factory=dict)
    maintainability_index: float = 0.0
    code_smells: List[str] = field(default_factory=list)
    function_metrics: Dict[str, Dict] = field(default_factory=dict)
    class_metrics: Dict[str, Dict] = field(default_factory=dict)
    dependencies: Set[str] = field(default_factory=set)
    security_issues: List[str] = field(default_factory=list)
    analysis_successful: bool = True
    error_message: str = ""


class CodeAnalyzer:
    """Main analyzer class for Python code complexity analysis"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset analyzer state"""
        self.loops = 0
        self.nested_loops = 0
        self.recursion_depth = 0
        self.data_structures = []
        self.function_calls = []
        self.operators = []
        self.operands = []
        self.variables = set()
        self.imports = set()
        self.functions = {}
        self.classes = {}
        self.current_function = None
        self.current_class = None
        self.nesting_level = 0
        self.max_nesting = 0
        self.security_patterns = [
            r'eval\s*\(',
            r'exec\s*\(',
            r'__import__\s*\(',
            r'open\s*\([^)]*[\'"]w[\'"]',
            r'subprocess\.',
            r'os\.system\s*\(',
            r'pickle\.loads?\s*\(',
        ]
    
    def analyze_file(self, file_path: str, print_report: bool = True) -> ComplexityMetrics:
        """
        Analyze a Python file and optionally print the report
        
        Args:
            file_path (str): Path to the Python file to analyze
            print_report (bool): Whether to print the analysis report
            
        Returns:
            ComplexityMetrics: Analysis results
        """
        try:
            # Validate file path
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            if not file_path.endswith('.py'):
                raise ValueError(f"File must be a Python file (.py): {file_path}")
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # Analyze the code
            metrics = self._analyze_code(code)
            
            # Set file information
            metrics.file_path = os.path.abspath(file_path)
            metrics.file_name = os.path.basename(file_path)
            
            # Print report if requested
            if print_report:
                self.print_analysis_report(metrics)
            
            return metrics
            
        except FileNotFoundError as e:
            metrics = ComplexityMetrics()
            metrics.analysis_successful = False
            metrics.error_message = str(e)
            metrics.file_path = file_path
            metrics.file_name = os.path.basename(file_path) if file_path else ""
            
            if print_report:
                print(f"❌ ERROR: {str(e)}")
            
            return metrics
            
        except Exception as e:
            metrics = ComplexityMetrics()
            metrics.analysis_successful = False
            metrics.error_message = f"Error analyzing file: {str(e)}"
            metrics.file_path = file_path
            metrics.file_name = os.path.basename(file_path) if file_path else ""
            
            if print_report:
                print(f"❌ ERROR: Error analyzing file: {str(e)}")
            
            return metrics
    
    def analyze_directory(self, directory_path: str, print_report: bool = True) -> Dict[str, ComplexityMetrics]:
        """
        Analyze all Python files in a directory
        
        Args:
            directory_path (str): Path to the directory containing Python files
            print_report (bool): Whether to print analysis reports
            
        Returns:
            Dict[str, ComplexityMetrics]: Dictionary mapping file paths to their metrics
        """
        try:
            if not os.path.exists(directory_path):
                raise FileNotFoundError(f"Directory not found: {directory_path}")
            
            if not os.path.isdir(directory_path):
                raise ValueError(f"Path is not a directory: {directory_path}")
            
            results = {}
            python_files = []
            
            # Find all Python files
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    if file.endswith('.py'):
                        python_files.append(os.path.join(root, file))
            
            if not python_files:
                print(f"⚠️  No Python files found in directory: {directory_path}")
                return results
            
            if print_report:
                print(f"🔍 Found {len(python_files)} Python files to analyze...")
                print("=" * 80)
            
            # Analyze each file
            for file_path in python_files:
                if print_report:
                    print(f"\n📁 Analyzing: {os.path.relpath(file_path, directory_path)}")
                    print("-" * 50)
                
                metrics = self.analyze_file(file_path, print_report=print_report)
                results[file_path] = metrics
                
                if print_report and metrics.analysis_successful:
                    print(f"✅ Analysis completed successfully")
                elif print_report:
                    print(f"❌ Analysis failed: {metrics.error_message}")
            
            if print_report:
                self._print_directory_summary(results, directory_path)
            
            return results
            
        except Exception as e:
            if print_report:
                print(f"❌ ERROR: Error analyzing directory: {str(e)}")
            return {}
    
    def _analyze_code(self, code: str) -> ComplexityMetrics:
        """Internal method to analyze Python code"""
        self.reset()
        
        try:
            tree = ast.parse(code)
            
            # Basic line counting
            lines = code.split('\n')
            metrics = ComplexityMetrics()
            
            # Count different types of lines
            self._count_lines(lines, metrics)
            
            # AST-based analysis
            self._analyze_ast(tree, metrics)
            
            # Calculate complexity metrics
            self._calculate_time_complexity(metrics)
            self._calculate_space_complexity(metrics)
            self._calculate_halstead_metrics(metrics)
            self._calculate_maintainability_index(metrics)
            self._detect_code_smells(code, metrics)
            self._detect_security_issues(code, metrics)
            
            metrics.analysis_successful = True
            return metrics
            
        except SyntaxError as e:
            metrics = ComplexityMetrics()
            metrics.analysis_successful = False
            metrics.error_message = f"Syntax Error: {str(e)}"
            return metrics
        except Exception as e:
            metrics = ComplexityMetrics()
            metrics.analysis_successful = False
            metrics.error_message = f"Analysis Error: {str(e)}"
            return metrics
    
    def _count_lines(self, lines: List[str], metrics: ComplexityMetrics):
        """Count different types of lines"""
        metrics.lines_of_code = len(lines)
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                metrics.blank_lines += 1
            elif stripped.startswith('#'):
                metrics.comment_lines += 1
            else:
                metrics.logical_lines += 1
                # Check for inline comments
                if '#' in line:
                    code_part = line.split('#')[0].strip()
                    if code_part:
                        metrics.comment_lines += 1
    
    def _analyze_ast(self, tree: ast.AST, metrics: ComplexityMetrics):
        """Analyze AST for various metrics"""
        for node in ast.walk(tree):
            self._analyze_node(node, metrics)
    
    def _analyze_node(self, node: ast.AST, metrics: ComplexityMetrics):
        """Analyze individual AST node"""
        # Count cyclomatic complexity
        if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
            metrics.cyclomatic_complexity += 1
            if isinstance(node, (ast.While, ast.For, ast.AsyncFor)):
                self.loops += 1
        
        elif isinstance(node, ast.ExceptHandler):
            metrics.cyclomatic_complexity += 1
        
        elif isinstance(node, (ast.And, ast.Or)):
            metrics.cyclomatic_complexity += 1
        
        # Function and class analysis
        elif isinstance(node, ast.FunctionDef):
            self._analyze_function(node, metrics)
        
        elif isinstance(node, ast.ClassDef):
            self._analyze_class(node, metrics)
        
        # Import analysis
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            self._analyze_import(node, metrics)
        
        # Variable and operator analysis
        elif isinstance(node, ast.Name):
            if isinstance(node.ctx, ast.Store):
                self.variables.add(node.id)
            self.operands.append(node.id)
        
        elif isinstance(node, ast.Constant):
            self.operands.append(str(node.value))
        
        elif isinstance(node, (ast.BinOp, ast.UnaryOp, ast.BoolOp, ast.Compare)):
            self.operators.append(type(node).__name__)
        
        # Data structure analysis
        elif isinstance(node, (ast.List, ast.Dict, ast.Set, ast.Tuple)):
            self.data_structures.append(type(node).__name__)
        
        # Function call analysis
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                self.function_calls.append(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                self.function_calls.append(f"{node.func.attr}")
    
    def _analyze_function(self, node: ast.FunctionDef, metrics: ComplexityMetrics):
        """Analyze function definition"""
        func_metrics = {
            'name': node.name,
            'args_count': len(node.args.args),
            'lines': len(node.body),
            'complexity': self._calculate_function_complexity(node),
            'has_return': self._has_return_statement(node),
            'has_docstring': ast.get_docstring(node) is not None
        }
        
        # Check for recursion
        for n in ast.walk(node):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name):
                if n.func.id == node.name:
                    func_metrics['recursive'] = True
                    break
        else:
            func_metrics['recursive'] = False
        
        metrics.function_metrics[node.name] = func_metrics
        self.functions[node.name] = func_metrics
    
    def _analyze_class(self, node: ast.ClassDef, metrics: ComplexityMetrics):
        """Analyze class definition"""
        methods = []
        attributes = []
        
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods.append(item.name)
            elif isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        attributes.append(target.id)
        
        class_metrics = {
            'name': node.name,
            'methods': methods,
            'attributes': attributes,
            'method_count': len(methods),
            'inheritance': len(node.bases),
            'has_docstring': ast.get_docstring(node) is not None
        }
        
        metrics.class_metrics[node.name] = class_metrics
        self.classes[node.name] = class_metrics
    
    def _analyze_import(self, node: ast.AST, metrics: ComplexityMetrics):
        """Analyze import statements"""
        if isinstance(node, ast.Import):
            for alias in node.names:
                metrics.dependencies.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                metrics.dependencies.add(node.module)
    
    def _calculate_function_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate complexity for a specific function"""
        complexity = 1
        for n in ast.walk(node):
            if isinstance(n, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(n, ast.ExceptHandler):
                complexity += 1
        return complexity
    
    def _has_return_statement(self, node: ast.FunctionDef) -> bool:
        """Check if function has return statement"""
        for n in ast.walk(node):
            if isinstance(n, ast.Return):
                return True
        return False
    
    def _calculate_time_complexity(self, metrics: ComplexityMetrics):
        """Estimate time complexity based on code patterns"""
        complexity_score = 0
        
        # Base complexity
        if self.loops == 0:
            complexity_score = 1
        elif self.loops == 1:
            complexity_score = 2
        elif self.loops == 2:
            complexity_score = 3
        else:
            complexity_score = 4
        
        # Check for nested loops
        nested_count = self._count_nested_loops()
        if nested_count > 0:
            complexity_score += nested_count
        
        # Check for recursive functions
        recursive_funcs = sum(1 for f in self.functions.values() if f.get('recursive', False))
        if recursive_funcs > 0:
            complexity_score += 2
        
        # Check for sorting or searching patterns
        if any('sort' in call.lower() for call in self.function_calls):
            complexity_score = max(complexity_score, 3)  # O(n log n)
        
        # Map complexity score to Big O notation
        complexity_map = {
            1: "O(1)",
            2: "O(n)",
            3: "O(n log n)",
            4: "O(n²)",
            5: "O(n³)",
            6: "O(2^n)",
            7: "O(n!)"
        }
        
        metrics.time_complexity = complexity_map.get(min(complexity_score, 7), "O(n^k)")
    
    def _calculate_space_complexity(self, metrics: ComplexityMetrics):
        """Estimate space complexity"""
        space_score = 1
        
        # Count data structures
        data_structure_count = len(self.data_structures)
        if data_structure_count == 0:
            space_score = 1
        elif data_structure_count <= 2:
            space_score = 2
        else:
            space_score = 3
        
        # Check for recursive functions (stack space)
        recursive_funcs = sum(1 for f in self.functions.values() if f.get('recursive', False))
        if recursive_funcs > 0:
            space_score += 1
        
        # Map to Big O notation
        space_map = {
            1: "O(1)",
            2: "O(n)",
            3: "O(n²)",
            4: "O(n^k)"
        }
        
        metrics.space_complexity = space_map.get(min(space_score, 4), "O(n^k)")
    
    def _count_nested_loops(self) -> int:
        """Count nested loop structures"""
        # This is a simplified approach - in practice, you'd need more sophisticated AST analysis
        return max(0, self.loops - 1) if self.loops > 1 else 0
    
    def _calculate_halstead_metrics(self, metrics: ComplexityMetrics):
        """Calculate Halstead complexity metrics"""
        n1 = len(set(self.operators))  # Number of distinct operators
        n2 = len(set(self.operands))   # Number of distinct operands
        N1 = len(self.operators)       # Total number of operators
        N2 = len(self.operands)        # Total number of operands
        
        if n1 == 0 or n2 == 0:
            metrics.halstead_metrics = {
                'vocabulary': 0,
                'length': 0,
                'volume': 0,
                'difficulty': 0,
                'effort': 0
            }
            return
        
        vocabulary = n1 + n2
        length = N1 + N2
        volume = length * math.log2(vocabulary) if vocabulary > 0 else 0
        difficulty = (n1 / 2) * (N2 / n2) if n2 > 0 else 0
        effort = difficulty * volume
        
        metrics.halstead_metrics = {
            'vocabulary': vocabulary,
            'length': length,
            'volume': round(volume, 2),
            'difficulty': round(difficulty, 2),
            'effort': round(effort, 2)
        }
    
    def _calculate_maintainability_index(self, metrics: ComplexityMetrics):
        """Calculate maintainability index"""
        if metrics.logical_lines == 0:
            metrics.maintainability_index = 100.0
            return
        
        # Simplified maintainability index calculation
        halstead_volume = metrics.halstead_metrics.get('volume', 0)
        cyclomatic = metrics.cyclomatic_complexity
        lines = metrics.logical_lines
        
        # Standard formula (simplified)
        if halstead_volume > 0 and lines > 0:
            mi = 171 - 5.2 * math.log(halstead_volume) - 0.23 * cyclomatic - 16.2 * math.log(lines)
            metrics.maintainability_index = max(0, min(100, round(mi, 2)))
        else:
            metrics.maintainability_index = 50.0
    
    def _detect_code_smells(self, code: str, metrics: ComplexityMetrics):
        """Detect common code smells"""
        smells = []
        
        # Long method/function
        for func_name, func_data in metrics.function_metrics.items():
            if func_data['lines'] > 20:
                smells.append(f"Long method: {func_name} ({func_data['lines']} lines)")
            if func_data['args_count'] > 5:
                smells.append(f"Too many parameters: {func_name} ({func_data['args_count']} params)")
        
        # High cyclomatic complexity
        if metrics.cyclomatic_complexity > 10:
            smells.append(f"High cyclomatic complexity: {metrics.cyclomatic_complexity}")
        
        # Magic numbers
        magic_numbers = re.findall(r'\b\d{2,}\b', code)
        if len(magic_numbers) > 3:
            smells.append(f"Magic numbers detected: {len(magic_numbers)} occurrences")
        
        # Duplicate code patterns
        lines = code.split('\n')
        line_counts = Counter(line.strip() for line in lines if line.strip())
        duplicates = [line for line, count in line_counts.items() if count > 2 and len(line) > 20]
        if duplicates:
            smells.append(f"Duplicate code patterns: {len(duplicates)} instances")
        
        # Too many imports
        if len(metrics.dependencies) > 10:
            smells.append(f"Too many dependencies: {len(metrics.dependencies)}")
        
        metrics.code_smells = smells
    
    def _detect_security_issues(self, code: str, metrics: ComplexityMetrics):
        """Detect potential security issues"""
        issues = []
        
        for pattern in self.security_patterns:
            if re.search(pattern, code):
                issues.append(f"Potential security risk: {pattern}")
        
        # Check for hardcoded credentials patterns
        credential_patterns = [
            r'password\s*=\s*[\'"][^\'"]+[\'"]',
            r'api_key\s*=\s*[\'"][^\'"]+[\'"]',
            r'secret\s*=\s*[\'"][^\'"]+[\'"]',
            r'token\s*=\s*[\'"][^\'"]+[\'"]'
        ]
        
        for pattern in credential_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                issues.append(f"Hardcoded credentials detected")
                break
        
        metrics.security_issues = issues
    
    def print_analysis_report(self, metrics: ComplexityMetrics):
        """Print a comprehensive analysis report"""
        if not metrics.analysis_successful:
            print(f"❌ Analysis failed: {metrics.error_message}")
            return
        
        print("🔍 " + "=" * 70)
        print("📊 PYTHON CODE COMPLEXITY ANALYSIS REPORT")
        print("🔍 " + "=" * 70)
        
        # File information
        print(f"📁 File: {metrics.file_name}")
        print(f"📂 Path: {metrics.file_path}")
        print()
        
        # Basic metrics
        print("📈 BASIC METRICS:")
        print(f"  📏 Lines of Code: {metrics.lines_of_code}")
        print(f"  💻 Logical Lines: {metrics.logical_lines}")
        print(f"  💬 Comment Lines: {metrics.comment_lines}")
        print(f"  📄 Blank Lines: {metrics.blank_lines}")
        print()
        
        # Complexity metrics
        print("⚡ COMPLEXITY METRICS:")
        print(f"  ⏱️  Time Complexity: {metrics.time_complexity}")
        print(f"  💾 Space Complexity: {metrics.space_complexity}")
        print(f"  🔄 Cyclomatic Complexity: {metrics.cyclomatic_complexity}")
        print(f"  🛠️  Maintainability Index: {metrics.maintainability_index}")
        print()
        
        # Halstead metrics
        if metrics.halstead_metrics:
            print("🧮 HALSTEAD METRICS:")
            for key, value in metrics.halstead_metrics.items():
                emoji = {"vocabulary": "📚", "length": "📏", "volume": "📊", 
                        "difficulty": "🎯", "effort": "💪"}.get(key, "📈")
                print(f"  {emoji} {key.title()}: {value}")
            print()
        
        # Function metrics
        if metrics.function_metrics:
            print("🔧 FUNCTION ANALYSIS:")
            for func_name, func_data in metrics.function_metrics.items():
                print(f"  📝 {func_name}:")
                print(f"    📏 Lines: {func_data['lines']}")
                print(f"    ⚙️  Parameters: {func_data['args_count']}")
                print(f"    🔄 Complexity: {func_data['complexity']}")
                print(f"    🔁 Recursive: {'Yes' if func_data.get('recursive', False) else 'No'}")
                print(f"    📚 Has Docstring: {'Yes' if func_data.get('has_docstring', False) else 'No'}")
                print()
        
        # Class metrics
        if metrics.class_metrics:
            print("🏗️  CLASS ANALYSIS:")
            for class_name, class_data in metrics.class_metrics.items():
                print(f"  🏷️  {class_name}:")
                print(f"    🔧 Methods: {class_data['method_count']}")
                print(f"    📋 Attributes: {len(class_data['attributes'])}")
                print(f"    🔗 Inheritance: {class_data['inheritance']}")
                print(f"    📚 Has Docstring: {'Yes' if class_data.get('has_docstring', False) else 'No'}")
                print()
        
        # Dependencies
        if metrics.dependencies:
            print("📦 DEPENDENCIES:")
            for dep in sorted(metrics.dependencies):
                print(f"  📥 {dep}")
            print()
        
        # Code smells
        if metrics.code_smells:
            print("⚠️  CODE SMELLS:")
            for smell in metrics.code_smells:
                print(f"  🔴 {smell}")
            print()
        
        # Security issues
        if metrics.security_issues:
            print("🔒 SECURITY ISSUES:")
            for issue in metrics.security_issues:
                print(f"  ⚠️  {issue}")
            print()
        
        # Recommendations
        print("💡 RECOMMENDATIONS:")
        recommendations = []
        
        if metrics.cyclomatic_complexity > 10:
            recommendations.append("Consider breaking down complex functions")
        if metrics.maintainability_index < 50:
            recommendations.append("Code maintainability is below average")
        if len(metrics.code_smells) > 5:
            recommendations.append("Address code smells to improve quality")
        if metrics.security_issues:
            recommendations.append("Review and fix security issues")
        if not any(func.get('has_docstring', False) for func in metrics.function_metrics.values()):
            recommendations.append("Add docstrings to functions for better documentation")
        
        if not recommendations:
            recommendations.append("Code quality looks good! 🎉")
        
        for rec in recommendations:
            print(f"  💡 {rec}")
        
        print("\n" + "🔍 " + "=" * 70)
    
    def _print_directory_summary(self, results: Dict[str, ComplexityMetrics], directory_path: str):
        """Print summary of directory analysis"""
        print("\n" + "=" * 80)
        print("📊 DIRECTORY ANALYSIS SUMMARY")
        print("=" * 80)
        
        successful_analyses = [m for m in results.values() if m.analysis_successful]
        failed_analyses = [m for m in results.values() if not m.analysis_successful]
        
        print(f"📁 Directory: {directory_path}")
        print(f"✅ Successful analyses: {len(successful_analyses)}")
        print(f"❌ Failed analyses: {len(failed_analyses)}")
        
        if successful_analyses:
            total_lines = sum(m.lines_of_code for m in successful_analyses)
            total_functions = sum(len(m.function_metrics) for m in successful_analyses)
            total_classes = sum(len(m.class_metrics) for m in successful_analyses)
            avg_complexity = sum(m.cyclomatic_complexity for m in successful_analyses) / len(successful_analyses)
            avg_maintainability = sum(m.maintainability_index for m in successful_analyses) / len(successful_analyses)
            
            print(f"\n📈 AGGREGATE METRICS:")
            print(f"  📏 Total Lines: {total_lines}")
            print(f"  🔧 Total Functions: {total_functions}")
            print(f"  🏗️  Total Classes: {total_classes}")
            print(f"  🔄 Average Complexity: {avg_complexity:.2f}")
            print(f"  🛠️  Average Maintainability: {avg_maintainability:.2f}")
        
        if failed_analyses:
            print(f"\n❌ FAILED ANALYSES:")
            for metrics in failed_analyses:
                print(f"  📁 {metrics.file_name}: {metrics.error_message}")


# Global analyzer instance
_analyzer = CodeAnalyzer()

# Package-level convenience functions
def analyze_file(file_path: str, print_report: bool = True) -> ComplexityMetrics:
    """
    Analyze a Python file (package-level convenience function)
    
    Args:
        file_path (str): Path to the Python file to analyze
        print_report (bool): Whether to print the analysis report
        
    Returns:
        ComplexityMetrics: Analysis results
    """
    return _analyzer.analyze_file(file_path, print_report)

def analyze_directory(directory_path: str, print_report: bool = True) -> Dict[str, ComplexityMetrics]:
    """
    Analyze all Python files in a directory (package-level convenience function)
    
    Args:
        directory_path (str): Path to the directory containing Python files
        print_report (bool): Whether to print analysis reports
        
    Returns:
        Dict[str, ComplexityMetrics]: Dictionary mapping file paths to their metrics
    """
    return _analyzer.analyze_directory(directory_path, print_report)

def quick_analyze(file_path: str):
    """
    Quick analysis with minimal output (package-level convenience function)
    
    Args:
        file_path (str): Path to the Python file to analyze
    """
    metrics = _analyzer.analyze_file(file_path, print_report=False)
    
    if not metrics.analysis_successful:
        print(f"❌ Analysis failed: {metrics.error_message}")
        return
    
    print(f"📁 {metrics.file_name}")
    print(f"⏱️  Time: {metrics.time_complexity} | 💾 Space: {metrics.space_complexity}")
    print(f"🔄 Complexity: {metrics.cyclomatic_complexity} | 🛠️  Maintainability: {metrics.maintainability_index}")
    
    if metrics.code_smells:
        print(f"⚠️  Issues: {len(metrics.code_smells)}")
    else:
        print("✅ No major issues detected")


# Example usage for testing
if __name__ == "__main__":
    # Example usage
    print("🚀 Code Analyzer Package - Test Mode")
    print("=" * 50)
    
    # Test with current file
    current_file = __file__
    print(f"📝 Analyzing current file: {os.path.basename(current_file)}")
    
    # Quick analysis
    quick_analyze(current_file)