# Code Analyzer

A dynamic analysis tool for Python test code that provides real-time performance insights and optimization suggestions. The tool helps developers identify performance bottlenecks, memory issues, and optimization opportunities in their test code.

## Features

- **Performance Profiling**: Measures execution time, memory usage, and CPU utilization
- **Code Pattern Analysis**: Identifies testing patterns and best practices
- **Optimization Suggestions**: Provides AI-powered code improvement recommendations
- **Comparative Analysis**: Compares different implementations of the same functionality
- **Visualization**: Generates performance graphs and trends
- **Memory Analysis**: Tracks memory usage patterns and potential leaks

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Step 1: Install Required Packages
You can install the required packages in two ways:

#### Option 1: Using requirements.txt
```bash
pip install -r requirements.txt
```

#### Option 2: Manual Installation
```bash
pip install matplotlib pandas requests python-dotenv
```

### Step 2: Set Up Environment Variables
Create a `.env` file in your project directory with the following content:
```bash
OLLAMA_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=dolphin3
PROFILING_TIMEOUT=30
```

### Step 3: Verify Installation
Run the analyzer on a sample test file:
```bash
python code_analyzer.py your_test_file.py
```

## Usage

### Basic Analysis
```bash
python code_analyzer.py your_test_file.py
```

### Advanced Options
```bash
# Pattern analysis
python code_analyzer.py your_test_file.py -p

# Performance visualization
python code_analyzer.py your_test_file.py -v

# Comparative analysis
python code_analyzer.py version1.py -c version2.py

# Set timeout (seconds)
python code_analyzer.py your_test_file.py -t 60

# Save results to file
python code_analyzer.py your_test_file.py -o results.json
```

## What It Analyzes

### Performance Metrics
- Execution time
- Memory usage
- CPU utilization
- I/O operations
- Network calls
- Resource leaks

### Code Patterns
- Test structure
- Assertion patterns
- Error handling
- Resource management
- Documentation quality

### Best Practices
- Test independence
- Proper cleanup
- Resource management
- Error handling
- Documentation

## Support

For help:
1. Check the output files
2. Review error messages
3. Try different analysis types
4. Consult the examples "# dynamiccodeanalysis" 
