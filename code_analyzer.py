import cProfile
import pstats
import io
import os
import subprocess
import json
import argparse
from typing import Dict, Any, List
import requests
from dotenv import load_dotenv
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import importlib.util
import sys
import tracemalloc
import time

class CodeAnalyzer:
    def __init__(self):
        load_dotenv()
        # Use environment variables with fallback defaults
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "dolphin3")
        self.profiling_timeout = int(os.getenv("PROFILING_TIMEOUT", "30"))  # seconds
        self.history_file = "performance_history.json"
        
    def run_test_with_profiling(self, test_file: str) -> Dict[str, Any]:
        """Run the test file with profiling and collect performance metrics."""
        # Start memory tracing
        tracemalloc.start()
        
        # Import the test module
        spec = importlib.util.spec_from_file_location("test_module", test_file)
        test_module = importlib.util.module_from_spec(spec)
        sys.modules["test_module"] = test_module
        spec.loader.exec_module(test_module)
        
        # Run cProfile on the test functions
        pr = cProfile.Profile()
        pr.enable()
        
        # Find and run test functions
        test_output = []
        start_time = time.time()
        
        for name in dir(test_module):
            if name.startswith('test_'):
                test_func = getattr(test_module, name)
                try:
                    test_func()
                    test_output.append(f"Test {name} passed")
                except Exception as e:
                    test_output.append(f"Test {name} failed: {str(e)}")
        
        end_time = time.time()
        pr.disable()
        
        # Get memory statistics
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Get profiling stats
        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
        ps.print_stats()
        
        return {
            "profile_stats": s.getvalue(),
            "test_file": test_file,
            "test_output": "\n".join(test_output),
            "timestamp": datetime.now().isoformat(),
            "execution_time": end_time - start_time,
            "memory_usage": {
                "current": current / 1024 / 1024,  # Convert to MB
                "peak": peak / 1024 / 1024  # Convert to MB
            }
        }
    
    def analyze_with_llm(self, profile_data: Dict[str, Any], analysis_type: str = "standard") -> str:
        """Send profiling data to LLM for analysis and suggestions."""
        if analysis_type == "comparative":
            prompt = f"""
            Compare the following two test implementations and provide insights:
            
            Test File 1: {profile_data['test_file1']}
            Profiling Data 1:
            {profile_data['profile_stats1']}
            
            Test File 2: {profile_data['test_file2']}
            Profiling Data 2:
            {profile_data['profile_stats2']}
            
            Please provide:
            1. Performance comparison
            2. Key differences in implementation
            3. Recommendations for best approach
            4. Potential hybrid solutions
            """
        elif analysis_type == "pattern":
            prompt = f"""
            Analyze the following test code for patterns and best practices:
            
            Test File: {profile_data['test_file']}
            Test Output: {profile_data['test_output']}
            Profiling Data:
            {profile_data['profile_stats']}
            
            Please identify:
            1. Test patterns used
            2. Potential anti-patterns
            3. Best practice recommendations
            4. Industry standard comparisons
            """
        else:
            # Read the original test file content
            with open(profile_data['test_file'], 'r') as f:
                original_code = f.read()
            
            prompt = f"""
            Analyze this code and provide a concise optimization:
            
            Original Code:
            {original_code}
            
            Profiling Results:
            Time: {profile_data['execution_time']:.2f}s
            Memory: {profile_data['memory_usage']['peak']:.2f}MB
            
            Provide a SHORT response in this exact format:
            
            === Problems ===
            - [List each problem on a new line with hyphen]
            
            === Optimizations ===
            - [List each optimization on a new line with hyphen]
            
            === Optimized Code ===
            [Complete optimized code here]
            """
        
        try:
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": False
                }
            )
            response.raise_for_status()
            return response.json()["response"]
        except Exception as e:
            return f"Error analyzing with LLM: {str(e)}"
    
    def save_to_history(self, profile_data: Dict[str, Any]):
        """Save profiling results to history file."""
        history = []
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as f:
                history = json.load(f)
        
        history.append(profile_data)
        
        with open(self.history_file, 'w') as f:
            json.dump(history, f, indent=2)
    
    def plot_performance_history(self, test_file: str):
        """Generate performance history plot."""
        if not os.path.exists(self.history_file):
            return "No history data available"
        
        with open(self.history_file, 'r') as f:
            history = json.load(f)
        
        # Filter history for the specific test file
        test_history = [h for h in history if h['test_file'] == test_file]
        
        if not test_history:
            return "No history data available for this test file"
        
        # Extract timing data
        timestamps = []
        execution_times = []
        memory_usage = []
        
        for entry in test_history:
            timestamps.append(datetime.fromisoformat(entry['timestamp']))
            execution_times.append(entry['execution_time'])
            memory_usage.append(entry['memory_usage']['peak'])
        
        # Create plot
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        
        # Plot execution time
        ax1.plot(timestamps, execution_times, marker='o', color='blue')
        ax1.set_title(f'Execution Time History: {os.path.basename(test_file)}')
        ax1.set_ylabel('Execution Time (seconds)')
        ax1.tick_params(axis='x', rotation=45)
        
        # Plot memory usage
        ax2.plot(timestamps, memory_usage, marker='o', color='red')
        ax2.set_title('Memory Usage History')
        ax2.set_ylabel('Peak Memory Usage (MB)')
        ax2.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        # Save plot with a safe filename
        safe_filename = os.path.basename(test_file).replace('\\', '_').replace('/', '_')
        plot_file = f"performance_history_{safe_filename}.png"
        plt.savefig(plot_file)
        plt.close()
        
        return f"Performance history plot saved to {plot_file}"
    
    def compare_implementations(self, test_file1: str, test_file2: str) -> Dict[str, Any]:
        """Compare two different implementations of the same test."""
        profile1 = self.run_test_with_profiling(test_file1)
        profile2 = self.run_test_with_profiling(test_file2)
        
        comparative_data = {
            "test_file1": test_file1,
            "test_file2": test_file2,
            "profile_stats1": profile1["profile_stats"],
            "profile_stats2": profile2["profile_stats"]
        }
        
        analysis = self.analyze_with_llm(comparative_data, "comparative")
        
        return {
            "implementation1": profile1,
            "implementation2": profile2,
            "comparative_analysis": analysis
        }
    
    def analyze_test_patterns(self, test_file: str) -> Dict[str, Any]:
        """Analyze test code for patterns and best practices."""
        profile_data = self.run_test_with_profiling(test_file)
        
        # Read the test file content
        with open(test_file, 'r') as f:
            test_code = f.read()
        
        prompt = f"""
        Analyze this test code and provide specific insights:

        Test Code:
        {test_code}

        Profiling Data:
        {profile_data['profile_stats']}

        Provide a structured analysis in this format:

        === Test Structure Analysis ===
        - Test framework used
        - Number of test cases
        - Test case organization
        - Setup/teardown patterns

        === Test Quality Indicators ===
        - Test independence
        - Assertion patterns
        - Test coverage
        - Edge case handling

        === Performance Patterns ===
        - Time complexity patterns
        - Memory usage patterns
        - Resource management
        - Potential bottlenecks

        === Recommendations ===
        - Specific improvements
        - Best practice suggestions
        - Optimization opportunities
        - Test coverage gaps
        """
        
        try:
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": False
                }
            )
            response.raise_for_status()
            return {
                "profile_data": profile_data,
                "pattern_analysis": response.json()["response"]
            }
        except Exception as e:
            return {
                "profile_data": profile_data,
                "pattern_analysis": f"Error analyzing test patterns: {str(e)}"
            }
    
    def analyze_test_code(self, test_file: str, save_history: bool = True) -> Dict[str, Any]:
        """Main method to analyze test code and get optimization suggestions."""
        if not os.path.exists(test_file):
            raise FileNotFoundError(f"Test file {test_file} not found")
            
        # Run profiling
        profile_data = self.run_test_with_profiling(test_file)
        
        if save_history:
            self.save_to_history(profile_data)
        
        # Get LLM analysis
        analysis = self.analyze_with_llm(profile_data)
        
        # Format profiling results for better readability
        formatted_profile = self._format_profiling_results(profile_data)
        
        return {
            "profile_data": profile_data,
            "formatted_profile": formatted_profile,
            "optimization_suggestions": analysis
        }
    
    def _format_profiling_results(self, profile_data: Dict[str, Any]) -> str:
        """Format profiling results in a concise way."""
        formatted = []
        
        # Basic metrics in 2-3 lines
        formatted.append("=== Quick Profiling Summary ===")
        formatted.append(f"Execution Time: {profile_data['execution_time']:.2f}s | Memory: {profile_data['memory_usage']['peak']:.2f}MB peak")
        
        # Test results in one line
        test_status = "PASSED" if "failed" not in profile_data['test_output'].lower() else "FAILED"
        formatted.append(f"Test Status: {test_status}")
        
        return "\n".join(formatted)

def main():
    parser = argparse.ArgumentParser(description='Advanced Code Analyzer CLI Tool')
    
    # Required arguments
    parser.add_argument('test_file', 
                       help='Path to the test file to analyze')
    
    # Optional arguments
    parser.add_argument('--output', '-o',
                       help='Output file to save results (optional)',
                       default=None)
    parser.add_argument('--verbose', '-v',
                       help='Enable verbose output',
                       action='store_true')
    parser.add_argument('--timeout', '-t',
                       help='Profiling timeout in seconds',
                       type=int,
                       default=30)
    parser.add_argument('--compare', '-c',
                       help='Compare with another implementation',
                       default=None)
    parser.add_argument('--history', '-H',
                       help='Generate performance history plot',
                       action='store_true')
    parser.add_argument('--patterns', '-p',
                       help='Analyze test patterns',
                       action='store_true')
    
    args = parser.parse_args()
    
    # Create analyzer instance
    analyzer = CodeAnalyzer()
    
    try:
        # Run analysis
        if args.verbose:
            print(f"Analyzing test file: {args.test_file}")
            print("Running profiling...")
        
        if args.compare:
            results = analyzer.compare_implementations(args.test_file, args.compare)
        elif args.patterns:
            results = analyzer.analyze_test_patterns(args.test_file)
        else:
            results = analyzer.analyze_test_code(args.test_file)
        
        if args.history:
            plot_result = analyzer.plot_performance_history(args.test_file)
            print(f"\n{plot_result}")
        
        # Print or save results
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"Results saved to {args.output}")
        else:
            if args.compare:
                print("\n=== Comparative Analysis ===")
                print(results["comparative_analysis"])
            elif args.patterns:
                print("\n=== Pattern Analysis ===")
                print(results["pattern_analysis"])
            else:
                print("\n=== Quick Analysis ===")
                print(results["formatted_profile"])
                print("\n=== Optimization Results ===")
                print(results["optimization_suggestions"])
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 