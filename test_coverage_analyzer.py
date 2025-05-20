#!/usr/bin/env python3
"""
Test Coverage Analyzer for GödelOS

This script analyzes the test coverage of GödelOS components, focusing on
the metacognition and inference engine modules. It creates a mapping between
source components and their test files, and identifies gaps in test coverage.
"""

import os
import re
import json
import inspect
import importlib
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, field, asdict

@dataclass
class ComponentInfo:
    """Information about a component and its test coverage."""
    module_path: str
    file_path: str
    class_names: List[str] = field(default_factory=list)
    function_names: List[str] = field(default_factory=list)
    test_files: List[str] = field(default_factory=list)
    has_unit_tests: bool = False
    has_integration_tests: bool = False
    tested_classes: List[str] = field(default_factory=list)
    tested_functions: List[str] = field(default_factory=list)
    untested_classes: List[str] = field(default_factory=list)
    untested_functions: List[str] = field(default_factory=list)
    test_coverage_percentage: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

class TestCoverageAnalyzer:
    """Analyzes test coverage for GödelOS components."""
    
    def __init__(self, project_root: str):
        """
        Initialize the analyzer.
        
        Args:
            project_root: Path to the GödelOS project root directory
        """
        self.project_root = project_root
        self.source_files: Dict[str, ComponentInfo] = {}
        self.test_files: Dict[str, List[str]] = {}
        self.component_test_mapping: Dict[str, ComponentInfo] = {}
        
    def find_source_files(self, module_paths: List[str]) -> None:
        """
        Find all source files in the specified modules.
        
        Args:
            module_paths: List of module paths to analyze (e.g., ['godelOS/metacognition', 'godelOS/inference_engine'])
        """
        for module_path in module_paths:
            full_path = os.path.join(self.project_root, module_path)
            if not os.path.exists(full_path):
                print(f"Warning: Module path {full_path} does not exist")
                continue
                
            for file_name in os.listdir(full_path):
                if file_name.endswith('.py') and not file_name.startswith('__'):
                    file_path = os.path.join(module_path, file_name)
                    module_name = f"{module_path.replace('/', '.')}.{file_name[:-3]}"
                    self.source_files[module_name] = ComponentInfo(
                        module_path=module_name,
                        file_path=file_path
                    )
        
        print(f"Found {len(self.source_files)} source files")
    
    def find_test_files(self, test_paths: List[str]) -> None:
        """
        Find all test files for the specified modules.
        
        Args:
            test_paths: List of test paths to analyze (e.g., ['tests/metacognition', 'tests'])
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
        
        print(f"Found {sum(len(tests) for tests in self.test_files.values())} test files for {len(self.test_files)} components")
    
    def _extract_component_name(self, test_file_name: str) -> str:
        """
        Extract the component name from a test file name.
        
        Args:
            test_file_name: Name of the test file (e.g., 'test_meta_knowledge.py')
            
        Returns:
            The component name (e.g., 'meta_knowledge')
        """
        # Remove 'test_' prefix and '.py' suffix
        if test_file_name.startswith('test_') and test_file_name.endswith('.py'):
            return test_file_name[5:-3]
        return test_file_name
    
    def analyze_source_files(self) -> None:
        """Analyze source files to extract classes and functions."""
        for module_name, component_info in self.source_files.items():
            try:
                # Try to import the module to inspect its contents
                module = importlib.import_module(module_name)
                
                # Extract classes and functions
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and obj.__module__ == module_name:
                        component_info.class_names.append(name)
                    elif inspect.isfunction(obj) and obj.__module__ == module_name:
                        component_info.function_names.append(name)
                
                print(f"Analyzed {module_name}: {len(component_info.class_names)} classes, {len(component_info.function_names)} functions")
            except (ImportError, ModuleNotFoundError) as e:
                print(f"Warning: Could not import {module_name}: {e}")
                
                # Fall back to regex-based analysis
                self._analyze_source_file_with_regex(component_info.file_path, component_info)
    
    def _analyze_source_file_with_regex(self, file_path: str, component_info: ComponentInfo) -> None:
        """
        Analyze a source file using regex to extract classes and functions.
        
        Args:
            file_path: Path to the source file
            component_info: ComponentInfo object to update
        """
        full_path = os.path.join(self.project_root, file_path)
        if not os.path.exists(full_path):
            print(f"Warning: Source file {full_path} does not exist")
            return
            
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Extract class definitions
                class_pattern = r'class\s+(\w+)'
                component_info.class_names = re.findall(class_pattern, content)
                
                # Extract function definitions
                function_pattern = r'def\s+(\w+)'
                component_info.function_names = re.findall(function_pattern, content)
                
                print(f"Analyzed {file_path} with regex: {len(component_info.class_names)} classes, {len(component_info.function_names)} functions")
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
    
    def create_component_test_mapping(self) -> None:
        """Create a mapping between components and their test files."""
        for module_name, component_info in self.source_files.items():
            # Extract the base name of the module (e.g., 'meta_knowledge' from 'godelOS.metacognition.meta_knowledge')
            parts = module_name.split('.')
            base_name = parts[-1]
            
            # Find test files for this component
            if base_name in self.test_files:
                component_info.test_files = self.test_files[base_name]
                component_info.has_unit_tests = any('test_' + base_name + '.py' in test_file for test_file in component_info.test_files)
                component_info.has_integration_tests = any('test_integration.py' in test_file for test_file in component_info.test_files)
                
                # Update the mapping
                self.component_test_mapping[module_name] = component_info
            else:
                # No test files found for this component
                component_info.has_unit_tests = False
                component_info.has_integration_tests = False
                self.component_test_mapping[module_name] = component_info
    
    def analyze_test_coverage(self) -> None:
        """Analyze test coverage for each component."""
        for module_name, component_info in self.component_test_mapping.items():
            if not component_info.test_files:
                # No test files, so all classes and functions are untested
                component_info.untested_classes = component_info.class_names.copy()
                component_info.untested_functions = component_info.function_names.copy()
                component_info.test_coverage_percentage = 0.0
                continue
                
            # Analyze each test file to determine which classes and functions are tested
            tested_classes = set()
            tested_functions = set()
            
            for test_file in component_info.test_files:
                full_path = os.path.join(self.project_root, test_file)
                if not os.path.exists(full_path):
                    continue
                    
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        # Check for references to each class
                        for class_name in component_info.class_names:
                            if class_name in content:
                                tested_classes.add(class_name)
                        
                        # Check for references to each function
                        for function_name in component_info.function_names:
                            if function_name in content:
                                tested_functions.add(function_name)
                except Exception as e:
                    print(f"Error analyzing test file {test_file}: {e}")
            
            # Update component info
            component_info.tested_classes = list(tested_classes)
            component_info.tested_functions = list(tested_functions)
            component_info.untested_classes = [c for c in component_info.class_names if c not in tested_classes]
            component_info.untested_functions = [f for f in component_info.function_names if f not in tested_functions]
            
            # Calculate test coverage percentage
            total_items = len(component_info.class_names) + len(component_info.function_names)
            tested_items = len(tested_classes) + len(tested_functions)
            component_info.test_coverage_percentage = (tested_items / total_items * 100) if total_items > 0 else 0.0
    
    def generate_report(self, output_file: str) -> None:
        """
        Generate a JSON report of the test coverage analysis.
        
        Args:
            output_file: Path to the output JSON file
        """
        report = {
            "summary": {
                "total_components": len(self.component_test_mapping),
                "components_with_tests": sum(1 for info in self.component_test_mapping.values() if info.test_files),
                "components_without_tests": sum(1 for info in self.component_test_mapping.values() if not info.test_files),
                "average_test_coverage": sum(info.test_coverage_percentage for info in self.component_test_mapping.values()) / len(self.component_test_mapping) if self.component_test_mapping else 0.0
            },
            "components": {name: info.to_dict() for name, info in self.component_test_mapping.items()}
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"Report generated: {output_file}")
    
    def print_summary(self) -> None:
        """Print a summary of the test coverage analysis."""
        print("\n=== Test Coverage Analysis Summary ===")
        print(f"Total components analyzed: {len(self.component_test_mapping)}")
        
        components_with_tests = [info for info in self.component_test_mapping.values() if info.test_files]
        components_without_tests = [info for info in self.component_test_mapping.values() if not info.test_files]
        
        print(f"Components with tests: {len(components_with_tests)} ({len(components_with_tests) / len(self.component_test_mapping) * 100:.1f}%)")
        print(f"Components without tests: {len(components_without_tests)} ({len(components_without_tests) / len(self.component_test_mapping) * 100:.1f}%)")
        
        if components_with_tests:
            avg_coverage = sum(info.test_coverage_percentage for info in components_with_tests) / len(components_with_tests)
            print(f"Average test coverage for components with tests: {avg_coverage:.1f}%")
        
        print("\n=== Components Without Tests ===")
        for info in sorted(components_without_tests, key=lambda x: x.module_path):
            print(f"- {info.module_path}")
        
        print("\n=== Components With Lowest Test Coverage ===")
        for info in sorted(components_with_tests, key=lambda x: x.test_coverage_percentage)[:5]:
            print(f"- {info.module_path}: {info.test_coverage_percentage:.1f}%")
            
        print("\n=== Components With Highest Test Coverage ===")
        for info in sorted(components_with_tests, key=lambda x: -x.test_coverage_percentage)[:5]:
            print(f"- {info.module_path}: {info.test_coverage_percentage:.1f}%")

def main():
    """Main entry point for the script."""
    # Set the project root to the current directory
    project_root = os.getcwd()
    
    # Create the analyzer
    analyzer = TestCoverageAnalyzer(project_root)
    
    # Find source files in the metacognition and inference engine modules
    analyzer.find_source_files(['godelOS/metacognition', 'godelOS/inference_engine'])
    
    # Find test files
    analyzer.find_test_files(['tests/metacognition', 'tests'])
    
    # Analyze source files
    analyzer.analyze_source_files()
    
    # Create component-test mapping
    analyzer.create_component_test_mapping()
    
    # Analyze test coverage
    analyzer.analyze_test_coverage()
    
    # Print summary
    analyzer.print_summary()
    
    # Generate report
    analyzer.generate_report('test_coverage_report.json')

if __name__ == '__main__':
    main()