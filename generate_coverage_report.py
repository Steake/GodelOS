#!/usr/bin/env python3
"""
Test Coverage Report Generator for GödelOS

This script generates an HTML report from the JSON test coverage data
produced by the test_coverage_analyzer.py script.
"""

import os
import json
import datetime
from typing import Dict, List, Any, Optional

def generate_html_report(json_file: str, output_file: str) -> None:
    """
    Generate an HTML report from the JSON test coverage data.
    
    Args:
        json_file: Path to the JSON file containing test coverage data
        output_file: Path to the output HTML file
    """
    # Load the JSON data
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract summary data
    summary = data['summary']
    components = data['components']
    
    # Sort components by test coverage percentage
    sorted_components = sorted(
        [(name, info) for name, info in components.items()],
        key=lambda x: x[1]['test_coverage_percentage'],
        reverse=True
    )
    
    # Generate HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GödelOS Test Coverage Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1, h2, h3, h4 {{
            color: #2c3e50;
        }}
        .summary {{
            background-color: #f8f9fa;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 20px;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}
        .summary-item {{
            background-color: #fff;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 15px;
            text-align: center;
        }}
        .summary-item h3 {{
            margin-top: 0;
        }}
        .summary-item .value {{
            font-size: 24px;
            font-weight: bold;
            color: #3498db;
        }}
        .coverage-bar {{
            height: 20px;
            background-color: #ecf0f1;
            border-radius: 10px;
            margin-top: 5px;
            overflow: hidden;
        }}
        .coverage-fill {{
            height: 100%;
            background-color: #2ecc71;
        }}
        .low-coverage {{
            background-color: #e74c3c;
        }}
        .medium-coverage {{
            background-color: #f39c12;
        }}
        .high-coverage {{
            background-color: #2ecc71;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }}
        th, td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #f8f9fa;
            font-weight: bold;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .component-details {{
            margin-top: 30px;
        }}
        .component-card {{
            background-color: #fff;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 20px;
        }}
        .component-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        .component-title {{
            margin: 0;
        }}
        .coverage-badge {{
            padding: 5px 10px;
            border-radius: 15px;
            color: white;
            font-weight: bold;
        }}
        .details-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }}
        .detail-section {{
            background-color: #f8f9fa;
            border-radius: 5px;
            padding: 15px;
        }}
        .detail-section h4 {{
            margin-top: 0;
        }}
        .detail-list {{
            list-style-type: none;
            padding-left: 0;
            margin: 0;
        }}
        .detail-list li {{
            padding: 5px 0;
            border-bottom: 1px solid #eee;
        }}
        .detail-list li:last-child {{
            border-bottom: none;
        }}
        .timestamp {{
            text-align: center;
            font-size: 12px;
            color: #7f8c8d;
            margin-top: 30px;
        }}
    </style>
</head>
<body>
    <h1>GödelOS Test Coverage Report</h1>
    
    <div class="summary">
        <h2>Summary</h2>
        <div class="summary-grid">
            <div class="summary-item">
                <h3>Total Components</h3>
                <div class="value">{summary['total_components']}</div>
            </div>
            <div class="summary-item">
                <h3>Components with Tests</h3>
                <div class="value">{summary['components_with_tests']} ({summary['components_with_tests'] / summary['total_components'] * 100:.1f}%)</div>
            </div>
            <div class="summary-item">
                <h3>Components without Tests</h3>
                <div class="value">{summary['components_without_tests']} ({summary['components_without_tests'] / summary['total_components'] * 100:.1f}%)</div>
            </div>
            <div class="summary-item">
                <h3>Average Test Coverage</h3>
                <div class="value">{summary['average_test_coverage']:.1f}%</div>
                <div class="coverage-bar">
                    <div class="coverage-fill {'low-coverage' if summary['average_test_coverage'] < 50 else 'medium-coverage' if summary['average_test_coverage'] < 80 else 'high-coverage'}" style="width: {summary['average_test_coverage']}%;"></div>
                </div>
            </div>
        </div>
    </div>
    
    <h2>Component Coverage Overview</h2>
    <table>
        <thead>
            <tr>
                <th>Component</th>
                <th>Test Coverage</th>
                <th>Has Unit Tests</th>
                <th>Has Integration Tests</th>
                <th>Classes Tested</th>
                <th>Functions Tested</th>
            </tr>
        </thead>
        <tbody>
"""
    
    # Add component rows
    for name, info in sorted_components:
        coverage = info['test_coverage_percentage']
        coverage_class = 'low-coverage' if coverage < 50 else 'medium-coverage' if coverage < 80 else 'high-coverage'
        
        html += f"""
            <tr>
                <td>{name}</td>
                <td>
                    {coverage:.1f}%
                    <div class="coverage-bar">
                        <div class="coverage-fill {coverage_class}" style="width: {coverage}%;"></div>
                    </div>
                </td>
                <td>{'Yes' if info['has_unit_tests'] else 'No'}</td>
                <td>{'Yes' if info['has_integration_tests'] else 'No'}</td>
                <td>{len(info['tested_classes'])}/{len(info['class_names'])}</td>
                <td>{len(info['tested_functions'])}/{len(info['function_names'])}</td>
            </tr>
"""
    
    html += """
        </tbody>
    </table>
    
    <h2>Detailed Component Analysis</h2>
    <div class="component-details">
"""
    
    # Add detailed component cards
    for name, info in sorted_components:
        coverage = info['test_coverage_percentage']
        coverage_class = 'low-coverage' if coverage < 50 else 'medium-coverage' if coverage < 80 else 'high-coverage'
        
        html += f"""
        <div class="component-card">
            <div class="component-header">
                <h3 class="component-title">{name}</h3>
                <span class="coverage-badge {coverage_class}">{coverage:.1f}% Coverage</span>
            </div>
            
            <p><strong>File:</strong> {info['file_path']}</p>
            <p><strong>Test Files:</strong> {', '.join(info['test_files']) if info['test_files'] else 'None'}</p>
            
            <div class="details-grid">
                <div class="detail-section">
                    <h4>Classes ({len(info['tested_classes'])}/{len(info['class_names'])} tested)</h4>
                    <ul class="detail-list">
"""
        
        # Add classes
        if info['class_names']:
            for class_name in info['class_names']:
                is_tested = class_name in info['tested_classes']
                html += f"""
                        <li>{class_name} {'✅' if is_tested else '❌'}</li>
"""
        else:
            html += """
                        <li><em>No classes defined</em></li>
"""
        
        html += """
                    </ul>
                </div>
                
                <div class="detail-section">
                    <h4>Functions ({len(info['tested_functions'])}/{len(info['function_names'])} tested)</h4>
                    <ul class="detail-list">
"""
        
        # Add functions
        if info['function_names']:
            for function_name in info['function_names']:
                is_tested = function_name in info['tested_functions']
                html += f"""
                        <li>{function_name} {'✅' if is_tested else '❌'}</li>
"""
        else:
            html += """
                        <li><em>No functions defined</em></li>
"""
        
        html += """
                    </ul>
                </div>
            </div>
        </div>
"""
    
    # Add timestamp and close HTML
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    html += f"""
    </div>
    
    <div class="timestamp">
        Report generated on {timestamp}
    </div>
</body>
</html>
"""
    
    # Write the HTML to the output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"HTML report generated: {output_file}")

def main():
    """Main entry point for the script."""
    json_file = 'test_coverage_report.json'
    output_file = 'test_coverage_report.html'
    
    if not os.path.exists(json_file):
        print(f"Error: JSON file {json_file} not found.")
        print("Please run test_coverage_analyzer.py first to generate the JSON data.")
        return
    
    generate_html_report(json_file, output_file)

if __name__ == '__main__':
    main()