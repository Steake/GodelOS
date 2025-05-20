#!/usr/bin/env python3
"""
Method-Level Test Coverage Analyzer for GödelOS

This script analyzes the method-level test coverage of GödelOS components,
focusing on the metacognition and inference engine modules. It identifies
which methods within each class are tested and which are not.
"""

import os
import re
import ast
import json
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, field, asdict

@dataclass
class MethodInfo:
    """Information about a method and its test coverage."""
    name: str
    class_name: str
    is_tested: bool = False
    is_private: bool = False
    is_dunder: bool = False
    line_count: int = 0
    complexity: int = 0  # A simple approximation of cyclomatic complexity

@dataclass
class ClassInfo:
    """Information about a class and its method coverage."""
    name: str
    methods: List[MethodInfo] = field(default_factory=list)
    tested_method_count: int = 0
    total_method_count: int = 0
    test_coverage_percentage: float = 0.0

@dataclass
class ComponentMethodCoverage:
    """Method-level coverage information for a component."""
    module_path: str
    file_path: str
    classes: List[ClassInfo] = field(default_factory=list)
    test_files: List[str] = field(default_factory=list)
    test_coverage_percentage: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "module_path": self.module_path,
            "file_path": self.file_path,
            "classes": [asdict(cls) for cls in self.classes],
            "test_files": self.test_files,
            "test_coverage_percentage": self.test_coverage_percentage
        }

class MethodVisitor(ast.NodeVisitor):
    """AST visitor to extract methods from a class."""
    
    def __init__(self):
        self.methods = []
        self.current_class = None
    
    def visit_ClassDef(self, node):
        """Visit a class definition."""
        old_class = self.current_class
        self.current_class = node.name
        
        # Visit all child nodes
        for child in node.body:
            self.visit(child)
        
        self.current_class = old_class
    
    def visit_FunctionDef(self, node):
        """Visit a function definition."""
        if self.current_class:
            # This is a method within a class
            is_private = node.name.startswith('_') and not node.name.startswith('__')
            is_dunder = node.name.startswith('__') and node.name.endswith('__')
            
            # Count lines in the method
            line_count = node.end_lineno - node.lineno + 1 if hasattr(node, 'end_lineno') else 1
            
            # Simple approximation of cyclomatic complexity
            complexity = 1
            for child in ast.walk(node):
                if isinstance(child, (ast.If, ast.For, ast.While, ast.Try, ast.ExceptHandler)):
                    complexity += 1
                elif isinstance(child, ast.BoolOp) and isinstance(child.op, (ast.And, ast.Or)):
                    complexity += len(child.values) - 1
            
            self.methods.append(MethodInfo(
                name=node.name,
                class_name=self.current_class,
                is_private=is_private,
                is_dunder=is_dunder,
                line_count=line_count,
                complexity=complexity
            ))

class MethodCoverageAnalyzer:
    """Analyzes method-level test coverage for GödelOS components."""
    
    def __init__(self, project_root: str):
        """
        Initialize the analyzer.
        
        Args:
            project_root: Path to the GödelOS project root directory
        """
        self.project_root = project_root
        self.component_coverage: Dict[str, ComponentMethodCoverage] = {}
        self.test_files: Dict[str, List[str]] = {}
    
    def find_source_files(self, module_paths: List[str]) -> List[str]:
        """
        Find all source files in the specified modules.
        
        Args:
            module_paths: List of module paths to analyze
            
        Returns:
            List of source file paths
        """
        source_files = []
        
        for module_path in module_paths:
            full_path = os.path.join(self.project_root, module_path)
            if not os.path.exists(full_path):
                print(f"Warning: Module path {full_path} does not exist")
                continue
                
            for file_name in os.listdir(full_path):
                if file_name.endswith('.py') and not file_name.startswith('__'):
                    file_path = os.path.join(module_path, file_name)
                    source_files.append(file_path)
        
        return source_files
    
    def find_test_files(self, test_paths: List[str]) -> None:
        """
        Find all test files for the specified modules.
        
        Args:
            test_paths: List of test paths to analyze
        """
        for test_path in test_paths:
            full_path = os.path.join(self.project_root, test_path)
            if not os.path.exists(full_path):
                print(f"Warning: Test path {full_path} does not exist")
                continue
                
            for root, _, files in os.walk(full_path):
                for file_name in files:
                    if file_name.startswith('test_') and file_name.endswith('.py'):
                        rel_path = os.path.relpath(os.path.join(root, file_name), self.project_root)
                        component_name = self._extract_component_name(file_name)
                        if component_name not in self.test_files:
                            self.test_files[component_name] = []
                        self.test_files[component_name].append(rel_path)
    
    def _extract_component_name(self, test_file_name: str) -> str:
        """
        Extract the component name from a test file name.
        
        Args:
            test_file_name: Name of the test file
            
        Returns:
            The component name
        """
        if test_file_name.startswith('test_') and test_file_name.endswith('.py'):
            return test_file_name[5:-3]
        return test_file_name
    
    def analyze_source_file(self, file_path: str) -> Optional[ComponentMethodCoverage]:
        """
        Analyze a source file to extract classes and methods.
        
        Args:
            file_path: Path to the source file
            
        Returns:
            ComponentMethodCoverage object if successful, None otherwise
        """
        full_path = os.path.join(self.project_root, file_path)
        if not os.path.exists(full_path):
            print(f"Warning: Source file {full_path} does not exist")
            return None
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            # Parse the source code into an AST
            tree = ast.parse(source_code)
            
            # Extract module name
            module_name = file_path.replace('/', '.').replace('\\', '.').replace('.py', '')
            
            # Create a component coverage object
            component = ComponentMethodCoverage(
                module_path=module_name,
                file_path=file_path
            )
            
            # Extract classes and methods
            visitor = MethodVisitor()
            visitor.visit(tree)
            
            # Group methods by class
            methods_by_class = {}
            for method in visitor.methods:
                if method.class_name not in methods_by_class:
                    methods_by_class[method.class_name] = []
                methods_by_class[method.class_name].append(method)
            
            # Create class info objects
            for class_name, methods in methods_by_class.items():
                class_info = ClassInfo(name=class_name, methods=methods)
                class_info.total_method_count = len(methods)
                component.classes.append(class_info)
            
            return component
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return None
    
    def analyze_test_coverage(self, component: ComponentMethodCoverage) -> None:
        """
        Analyze test coverage for a component.
        
        Args:
            component: ComponentMethodCoverage object to analyze
        """
        # Extract the base name of the module
        parts = component.module_path.split('.')
        base_name = parts[-1]
        
        # Find test files for this component
        if base_name in self.test_files:
            component.test_files = self.test_files[base_name]
        else:
            # No test files found
            return
        
        # Analyze each test file
        for test_file in component.test_files:
            full_path = os.path.join(self.project_root, test_file)
            if not os.path.exists(full_path):
                continue
            
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    test_content = f.read()
                
                # Check for references to each class and method
                for class_info in component.classes:
                    class_pattern = r'\b' + re.escape(class_info.name) + r'\b'
                    if re.search(class_pattern, test_content):
                        # Class is referenced in the test
                        for method in class_info.methods:
                            method_pattern = r'\b' + re.escape(method.name) + r'\b'
                            if re.search(method_pattern, test_content):
                                method.is_tested = True
            except Exception as e:
                print(f"Error analyzing test file {test_file}: {e}")
        
        # Update test coverage statistics
        for class_info in component.classes:
            tested_methods = [m for m in class_info.methods if m.is_tested]
            class_info.tested_method_count = len(tested_methods)
            
            if class_info.total_method_count > 0:
                class_info.test_coverage_percentage = class_info.tested_method_count / class_info.total_method_count * 100
        
        # Calculate overall test coverage percentage
        total_methods = sum(len(cls.methods) for cls in component.classes)
        tested_methods = sum(len([m for m in cls.methods if m.is_tested]) for cls in component.classes)
        
        if total_methods > 0:
            component.test_coverage_percentage = tested_methods / total_methods * 100
    
    def analyze_components(self, module_paths: List[str], test_paths: List[str]) -> None:
        """
        Analyze components in the specified modules.
        
        Args:
            module_paths: List of module paths to analyze
            test_paths: List of test paths to analyze
        """
        # Find test files
        self.find_test_files(test_paths)
        
        # Find and analyze source files
        source_files = self.find_source_files(module_paths)
        
        for file_path in source_files:
            component = self.analyze_source_file(file_path)
            if component:
                self.analyze_test_coverage(component)
                self.component_coverage[component.module_path] = component
    
    def generate_report(self, output_file: str) -> None:
        """
        Generate a JSON report of the method-level test coverage analysis.
        
        Args:
            output_file: Path to the output JSON file
        """
        # Calculate summary statistics
        total_classes = sum(len(component.classes) for component in self.component_coverage.values())
        total_methods = sum(sum(len(cls.methods) for cls in component.classes) for component in self.component_coverage.values())
        tested_methods = sum(sum(len([m for m in cls.methods if m.is_tested]) for cls in component.classes) for component in self.component_coverage.values())
        
        average_coverage = 0.0
        if total_methods > 0:
            average_coverage = tested_methods / total_methods * 100
        
        # Create the report
        report = {
            "summary": {
                "total_components": len(self.component_coverage),
                "total_classes": total_classes,
                "total_methods": total_methods,
                "tested_methods": tested_methods,
                "untested_methods": total_methods - tested_methods,
                "average_method_coverage": average_coverage
            },
            "components": {name: component.to_dict() for name, component in self.component_coverage.items()}
        }
        
        # Write the report to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"Method-level coverage report generated: {output_file}")
    
    def print_summary(self) -> None:
        """Print a summary of the method-level test coverage analysis."""
        print("\n=== Method-Level Test Coverage Analysis Summary ===")
        
        # Calculate summary statistics
        total_classes = sum(len(component.classes) for component in self.component_coverage.values())
        total_methods = sum(sum(len(cls.methods) for cls in component.classes) for component in self.component_coverage.values())
        tested_methods = sum(sum(len([m for m in cls.methods if m.is_tested]) for cls in component.classes) for component in self.component_coverage.values())
        
        print(f"Total components analyzed: {len(self.component_coverage)}")
        print(f"Total classes: {total_classes}")
        print(f"Total methods: {total_methods}")
        print(f"Tested methods: {tested_methods} ({tested_methods / total_methods * 100:.1f}% if total_methods > 0 else 0.0)")
        print(f"Untested methods: {total_methods - tested_methods} ({(total_methods - tested_methods) / total_methods * 100:.1f}% if total_methods > 0 else 0.0)")
        
        # Print components with lowest method coverage
        print("\n=== Components With Lowest Method Coverage ===")
        sorted_components = sorted(
            self.component_coverage.values(),
            key=lambda x: x.test_coverage_percentage
        )
        
        for component in sorted_components[:5]:
            print(f"- {component.module_path}: {component.test_coverage_percentage:.1f}%")
        
        # Print classes with no test coverage
        print("\n=== Classes With No Test Coverage ===")
        untested_classes = []
        
        for component in self.component_coverage.values():
            for cls in component.classes:
                if cls.tested_method_count == 0 and cls.total_method_count > 0:
                    untested_classes.append((component.module_path, cls.name))
        
        for module_path, class_name in sorted(untested_classes):
            print(f"- {module_path}.{class_name}")
        
        # Print complex methods with no test coverage
        print("\n=== Complex Methods With No Test Coverage ===")
        complex_untested_methods = []
        
        for component in self.component_coverage.values():
            for cls in component.classes:
                for method in cls.methods:
                    if not method.is_tested and method.complexity > 5 and not method.is_private and not method.is_dunder:
                        complex_untested_methods.append((component.module_path, cls.name, method.name, method.complexity))
        
        for module_path, class_name, method_name, complexity in sorted(complex_untested_methods, key=lambda x: -x[3]):
            print(f"- {module_path}.{class_name}.{method_name} (complexity: {complexity})")

def main():
    """Main entry point for the script."""
    # Set the project root to the current directory
    project_root = os.getcwd()
    
    # Create the analyzer
    analyzer = MethodCoverageAnalyzer(project_root)
    
    # Analyze metacognition and inference engine components
    analyzer.analyze_components(
        module_paths=['godelOS/metacognition', 'godelOS/inference_engine'],
        test_paths=['tests/metacognition', 'tests']
    )
    
    # Print summary
    analyzer.print_summary()
    
    # Generate report
    analyzer.generate_report('method_coverage_report.json')

if __name__ == '__main__':
    main()