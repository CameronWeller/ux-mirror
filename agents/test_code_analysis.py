#!/usr/bin/env python3
"""
Tests for UX-MIRROR Code Analysis Agents
=======================================

Tests the functionality of our lightweight code analysis agents.
"""

import asyncio
import unittest
from code_analysis_agents import (
    CodeLine,
    StyleAnalyzer,
    ComplexityAnalyzer,
    SecurityAnalyzer,
    CodeAnalysisOrchestrator
)

class TestCodeAnalysisAgents(unittest.TestCase):
    """Test cases for code analysis agents"""
    
    def setUp(self):
        """Set up test cases"""
        self.style_analyzer = StyleAnalyzer()
        self.complexity_analyzer = ComplexityAnalyzer()
        self.security_analyzer = SecurityAnalyzer()
        self.orchestrator = CodeAnalysisOrchestrator()
    
    async def test_style_analyzer(self):
        """Test style analysis"""
        # Test long line
        line = CodeLine(
            line_number=1,
            content="def very_long_function_name_with_many_parameters(param1, param2, param3, param4, param5, param6, param7, param8):",
            file_path="test.py"
        )
        result = await self.style_analyzer.analyze_line(line)
        self.assertTrue(any(issue['type'] == 'line_length' for issue in result['issues']))
        
        # Test trailing whitespace
        line = CodeLine(
            line_number=2,
            content="    print('test')    ",
            file_path="test.py"
        )
        result = await self.style_analyzer.analyze_line(line)
        self.assertTrue(any(issue['type'] == 'trailing_whitespace' for issue in result['issues']))
    
    async def test_complexity_analyzer(self):
        """Test complexity analysis"""
        # Test control flow
        line = CodeLine(
            line_number=1,
            content="if condition and another_condition:",
            file_path="test.py"
        )
        result = await self.complexity_analyzer.analyze_line(line)
        self.assertEqual(result['metrics']['control_flow_count'], 1)
        
        # Test nested blocks
        line = CodeLine(
            line_number=2,
            content="    {",
            file_path="test.py"
        )
        result = await self.complexity_analyzer.analyze_line(line)
        self.assertEqual(result['metrics']['nesting_level'], 1)
    
    async def test_security_analyzer(self):
        """Test security analysis"""
        # Test SQL injection
        line = CodeLine(
            line_number=1,
            content="query = f'SELECT * FROM users WHERE id = {user_input}'",
            file_path="test.py"
        )
        result = await self.security_analyzer.analyze_line(line)
        self.assertTrue(any(issue['type'] == 'sql_injection' for issue in result['issues']))
        
        # Test command injection
        line = CodeLine(
            line_number=2,
            content="os.system(f'echo {user_input}')",
            file_path="test.py"
        )
        result = await self.security_analyzer.analyze_line(line)
        self.assertTrue(any(issue['type'] == 'command_injection' for issue in result['issues']))
    
    async def test_orchestrator(self):
        """Test the orchestrator"""
        # Create a test file with various issues
        test_content = """
def very_long_function_name_with_many_parameters(param1, param2, param3, param4, param5, param6, param7, param8):
    if condition and another_condition:    
        query = f'SELECT * FROM users WHERE id = {user_input}'
        os.system(f'echo {user_input}')
        password = 'hardcoded_secret'
"""
        
        # Write test file
        with open('test_analysis.py', 'w') as f:
            f.write(test_content)
        
        # Analyze file
        results = await self.orchestrator.analyze_file('test_analysis.py')
        
        # Verify results
        self.assertIn('line_analysis', results)
        self.assertIn('summary', results)
        self.assertGreater(results['summary']['total_issues'], 0)
        self.assertGreater(results['summary']['severity_counts']['high'], 0)

def run_tests():
    """Run all tests"""
    unittest.main()

if __name__ == '__main__':
    asyncio.run(run_tests()) 