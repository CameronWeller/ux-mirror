#!/usr/bin/env python3
"""
UX-MIRROR Code Analysis Agents
=============================

Lightweight agents specialized in efficient line-by-line code analysis.
These agents use minimal API calls and focus on local analysis where possible.

Author: UX-MIRROR System
Version: 1.0.0
"""

import asyncio
import logging
import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class CodeLine:
    """Represents a single line of code with its context"""
    line_number: int
    content: str
    file_path: str
    context_before: List[str] = None
    context_after: List[str] = None

class BaseCodeAnalyzer:
    """Base class for all code analysis agents"""
    
    def __init__(self, name: str):
        self.name = name
        self.analysis_cache: Dict[str, Any] = {}
    
    async def analyze_line(self, line: CodeLine) -> Dict[str, Any]:
        """Analyze a single line of code"""
        raise NotImplementedError
    
    def _get_context(self, line: CodeLine, context_lines: int = 3) -> None:
        """Get context lines before and after the target line"""
        if line.context_before is None:
            line.context_before = []
        if line.context_after is None:
            line.context_after = []

class StyleAnalyzer(BaseCodeAnalyzer):
    """Analyzes code style and formatting"""
    
    def __init__(self):
        super().__init__("style_analyzer")
        self.style_patterns = {
            'line_length': re.compile(r'^.{81,}$'),  # Lines over 80 chars
            'trailing_whitespace': re.compile(r'\s+$'),
            'indentation': re.compile(r'^(\t|\s{2,})'),  # Mixed indentation
            'blank_lines': re.compile(r'^\s*$')
        }
    
    async def analyze_line(self, line: CodeLine) -> Dict[str, Any]:
        """Analyze code style for a single line"""
        issues = []
        
        # Check line length
        if self.style_patterns['line_length'].match(line.content):
            issues.append({
                'type': 'line_length',
                'message': 'Line exceeds 80 characters',
                'severity': 'warning'
            })
        
        # Check trailing whitespace
        if self.style_patterns['trailing_whitespace'].search(line.content):
            issues.append({
                'type': 'trailing_whitespace',
                'message': 'Line has trailing whitespace',
                'severity': 'info'
            })
        
        return {
            'line_number': line.line_number,
            'issues': issues,
            'analyzer': self.name
        }

class ComplexityAnalyzer(BaseCodeAnalyzer):
    """Analyzes code complexity metrics"""
    
    def __init__(self):
        super().__init__("complexity_analyzer")
        self.complexity_patterns = {
            'nested_blocks': re.compile(r'^\s*{\s*$'),
            'control_flow': re.compile(r'\b(if|else|for|while|switch)\b'),
            'nested_loops': re.compile(r'\b(for|while)\b.*\b(for|while)\b')
        }
    
    async def analyze_line(self, line: CodeLine) -> Dict[str, Any]:
        """Analyze complexity for a single line"""
        metrics = {
            'nesting_level': 0,
            'control_flow_count': 0,
            'complexity_score': 0
        }
        
        # Count control flow statements
        if self.complexity_patterns['control_flow'].search(line.content):
            metrics['control_flow_count'] += 1
        
        # Check for nested blocks
        if self.complexity_patterns['nested_blocks'].match(line.content):
            metrics['nesting_level'] += 1
        
        # Calculate complexity score
        metrics['complexity_score'] = (
            metrics['control_flow_count'] * 2 +
            metrics['nesting_level'] * 3
        )
        
        return {
            'line_number': line.line_number,
            'metrics': metrics,
            'analyzer': self.name
        }

class SecurityAnalyzer(BaseCodeAnalyzer):
    """Analyzes code for security issues"""
    
    def __init__(self):
        super().__init__("security_analyzer")
        self.security_patterns = {
            'sql_injection': re.compile(r'SELECT.*FROM.*WHERE.*=.*\'.*\''),
            'command_injection': re.compile(r'exec\(|system\(|subprocess\.call\('),
            'hardcoded_secrets': re.compile(r'(password|secret|key|token)\s*=\s*[\'"][^\'"]+[\'"]')
        }
    
    async def analyze_line(self, line: CodeLine) -> Dict[str, Any]:
        """Analyze security for a single line"""
        issues = []
        
        for pattern_name, pattern in self.security_patterns.items():
            if pattern.search(line.content):
                issues.append({
                    'type': pattern_name,
                    'message': f'Potential {pattern_name} vulnerability',
                    'severity': 'high'
                })
        
        return {
            'line_number': line.line_number,
            'issues': issues,
            'analyzer': self.name
        }

class CodeAnalysisOrchestrator:
    """Coordinates multiple code analysis agents"""
    
    def __init__(self):
        self.analyzers = [
            StyleAnalyzer(),
            ComplexityAnalyzer(),
            SecurityAnalyzer()
        ]
        self.results_cache: Dict[str, Dict[str, Any]] = {}
    
    async def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze an entire file using all analyzers"""
        if file_path in self.results_cache:
            return self.results_cache[file_path]
        
        results = {
            'file_path': file_path,
            'line_analysis': [],
            'summary': {
                'total_issues': 0,
                'severity_counts': {
                    'high': 0,
                    'medium': 0,
                    'low': 0,
                    'info': 0
                }
            }
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for i, line_content in enumerate(lines, 1):
                line = CodeLine(
                    line_number=i,
                    content=line_content.rstrip(),
                    file_path=file_path
                )
                
                # Get context for the line
                line.context_before = lines[max(0, i-4):i-1]
                line.context_after = lines[i:i+3]
                
                # Run all analyzers on the line
                line_results = []
                for analyzer in self.analyzers:
                    analysis = await analyzer.analyze_line(line)
                    line_results.append(analysis)
                
                results['line_analysis'].append({
                    'line_number': i,
                    'content': line_content.rstrip(),
                    'analysis': line_results
                })
            
            # Generate summary
            for line_result in results['line_analysis']:
                for analysis in line_result['analysis']:
                    if 'issues' in analysis:
                        for issue in analysis['issues']:
                            results['summary']['total_issues'] += 1
                            results['summary']['severity_counts'][issue['severity']] += 1
            
            # Cache results
            self.results_cache[file_path] = results
            return results
            
        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {e}")
            return {
                'file_path': file_path,
                'error': str(e)
            }

async def main():
    """Main entry point for testing"""
    orchestrator = CodeAnalysisOrchestrator()
    
    # Example usage
    test_file = "agents/simple_orchestrator.py"
    results = await orchestrator.analyze_file(test_file)
    
    # Print summary
    print(f"\nAnalysis Summary for {test_file}:")
    print(f"Total Issues: {results['summary']['total_issues']}")
    print("\nSeverity Breakdown:")
    for severity, count in results['summary']['severity_counts'].items():
        print(f"  {severity}: {count}")

if __name__ == "__main__":
    asyncio.run(main()) 