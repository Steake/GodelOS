#!/bin/bash
# Test Coverage Analysis Runner for GödelOS
# This script runs all the test coverage analysis scripts in sequence.

echo "=== GödelOS Test Coverage Analysis ==="
echo "Starting analysis at $(date)"
echo

echo "Step 1: Running basic component test coverage analysis..."
python3 test_coverage_analyzer.py
echo "Basic component analysis complete."
echo

echo "Step 2: Running method-level test coverage analysis..."
python3 method_coverage_analyzer.py
echo "Method-level analysis complete."
echo

echo "Step 3: Generating HTML coverage report..."
python3 generate_coverage_report.py
echo "HTML report generation complete."
echo

echo "=== Analysis Complete ==="
echo "The following reports have been generated:"
echo "- test_coverage_report.json: Basic component test coverage data"
echo "- test_coverage_report.html: Interactive HTML report of component test coverage"
echo "- method_coverage_report.json: Detailed method-level test coverage data"
echo
echo "To view the HTML report, open test_coverage_report.html in your web browser."
echo "Analysis completed at $(date)"