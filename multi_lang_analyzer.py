# multi_lang_analyzer.py - Complete updated version
import ast
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Try to import ML modules
try:
    from ml_models import CodeMLAnalyzer, CodePatternDetector, CodeSimilarityAnalyzer
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("Warning: ML modules not available.")

class MultiLanguageAnalyzer:
    """Analyzes Python, C, and C++ files for readability and memory safety with ML enhancement"""
    
    def __init__(self, file_path: str, use_ml: bool = True):
        self.file_path = Path(file_path)
        self.language = self._detect_language()
        self.source_code = self.file_path.read_text(encoding='utf-8', errors='ignore')
        self.use_ml = use_ml and ML_AVAILABLE
        
        # Initialize ML components if enabled
        if self.use_ml:
            try:
                self.ml_analyzer = CodeMLAnalyzer()
                self.pattern_detector = CodePatternDetector()
                self.similarity_analyzer = CodeSimilarityAnalyzer()
            except Exception as e:
                print(f"ML initialization warning: {e}")
                self.use_ml = False
        
    def _detect_language(self) -> str:
        """Detect language from file extension"""
        ext = self.file_path.suffix.lower()
        lang_map = {
            '.py': 'python',
            '.c': 'c',
            '.h': 'c',
            '.cpp': 'cpp',
            '.cc': 'cpp',
            '.cxx': 'cpp',
            '.hpp': 'cpp'
        }
        detected = lang_map.get(ext, 'unknown')
        if detected == 'unknown':
            raise ValueError(f"Unsupported file type: {ext}")
        return detected
    
    def analyze(self) -> Dict[str, Any]:
        """Run complete analysis based on language"""
        
        if self.language == 'python':
            results = self._analyze_python()
        elif self.language in ['c', 'cpp']:
            results = self._analyze_c_cpp()
        else:
            results = self._analyze_generic()
        
        results.update({
            "file": str(self.file_path),
            "language": self.language,
            "timestamp": datetime.now().isoformat(),
            "metrics": self._get_basic_metrics()
        })
        
        return results
    
    def analyze_with_ml(self) -> Dict[str, Any]:
        """Run complete analysis with ML enhancement"""
        results = self.analyze()
        
        if self.use_ml and hasattr(self, 'ml_analyzer'):
            try:
                metrics = results.get('metrics', {})
                readability = results.get('readability', {})
                
                complexity_val = readability.get('cyclomatic_complexity', 0)
                if complexity_val == 'N/A' or complexity_val is None:
                    complexity_val = 0
                
                ml_metrics = {
                    'cyclomatic_complexity': complexity_val if isinstance(complexity_val, (int, float)) else 0,
                    'max_nesting_depth': readability.get('max_nesting_depth', 0),
                    'comment_ratio': metrics.get('comment_ratio', 0),
                    'total_lines': metrics.get('total_lines', 0)
                }
                
                ml_quality = self.ml_analyzer.predict_quality_enhanced(
                    self.source_code, language=self.language, metrics=ml_metrics
                )
                ml_bugs = self.ml_analyzer.predict_bugs_enhanced(
                    self.source_code, language=self.language, metrics=ml_metrics
                )
                ml_security = self.ml_analyzer.predict_security_enhanced(
                    self.source_code, language=self.language, metrics=ml_metrics
                )
                ml_memory = self.ml_analyzer.predict_memory_safety(
                    self.source_code, language=self.language, metrics=ml_metrics
                )
                patterns = self.pattern_detector.detect_patterns(
                    self.source_code, language=self.language, metrics=ml_metrics
                )
                
                results['ml_enhancement'] = {
                    'quality_prediction': ml_quality,
                    'bug_prediction': ml_bugs,
                    'security_prediction': ml_security,
                    'memory_safety_prediction': ml_memory,
                    'pattern_detection': patterns,
                    'analyzed_language': self.language,
                    'ml_enabled': True
                }
                
                if results.get('summary'):
                    ml_risk_score = (ml_bugs.get('bug_probability', 0) + 
                                   ml_security.get('security_risk_probability', 0) + 
                                   ml_memory.get('memory_risk_probability', 0)) / 3
                    results['summary']['ml_risk_score'] = round(ml_risk_score * 100, 1)
                    results['summary']['ml_risk_level'] = ml_bugs.get('risk_level', 'UNKNOWN')
                    
                    recommendations = []
                    if ml_memory.get('has_memory_issues', False) and self.language in ['c', 'cpp']:
                        recommendations.append("💾 Memory safety issues detected. Review pointers and allocations.")
                    if ml_bugs.get('bug_probability', 0) > 0.6:
                        recommendations.append("🤖 High bug probability detected. Consider thorough testing.")
                    if ml_security.get('security_risk_probability', 0) > 0.5:
                        recommendations.append("🔒 Security risks identified. Review dangerous functions.")
                    if ml_quality.get('quality_score', 0) < 60:
                        recommendations.append("📊 Code quality needs improvement. Consider refactoring.")
                    if patterns.get('suggestions'):
                        recommendations.extend(patterns['suggestions'][:2])
                    
                    results['summary']['ml_recommendations'] = recommendations
                    
            except Exception as e:
                results['ml_error'] = str(e)
                results['ml_enhancement'] = {'error': str(e), 'ml_enabled': False}
        
        return results
    
    def _get_basic_metrics(self) -> Dict[str, int]:
        """Get basic code metrics"""
        lines = self.source_code.split('\n')
        code_lines = 0
        comment_lines = 0
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            
            is_comment = False
            
            if stripped.startswith('//'):
                is_comment = True
            elif stripped.startswith('/*') or stripped.startswith('*'):
                is_comment = True
            elif stripped.startswith('#') and not stripped.startswith('#include'):
                is_comment = True
            
            if is_comment:
                comment_lines += 1
            else:
                code_lines += 1
        
        return {
            "total_lines": len(lines),
            "code_lines": code_lines,
            "comment_lines": comment_lines,
            "blank_lines": len([l for l in lines if not l.strip()]),
            "comment_ratio": round(comment_lines / max(code_lines, 1), 2)
        }
    
    def _analyze_python(self) -> Dict[str, Any]:
        """Analyze Python file using AST"""
        try:
            tree = ast.parse(self.source_code)
            readability = self._python_readability(tree)
            memory_issues = self._python_memory_safety(tree)
            security_issues = self._python_security(tree)
            
            return {
                "readability": readability,
                "memory_issues": memory_issues,
                "security_issues": security_issues,
                "summary": self._generate_summary(memory_issues, security_issues, readability)
            }
        except SyntaxError as e:
            return {
                "error": f"Python syntax error: {e}",
                "readability": {},
                "memory_issues": [],
                "security_issues": []
            }
    
    def _python_readability(self, tree: ast.AST) -> Dict[str, Any]:
        """Calculate Python readability metrics"""
        class ComplexityVisitor(ast.NodeVisitor):
            def __init__(self):
                self.complexity = 0
                self.max_nesting = 0
                self.current_nesting = 0
                
            def visit_If(self, node):
                self.complexity += 1
                self.current_nesting += 1
                self.max_nesting = max(self.max_nesting, self.current_nesting)
                self.generic_visit(node)
                self.current_nesting -= 1
                
            def visit_For(self, node):
                self.complexity += 1
                self.current_nesting += 1
                self.max_nesting = max(self.max_nesting, self.current_nesting)
                self.generic_visit(node)
                self.current_nesting -= 1
                
            def visit_While(self, node):
                self.complexity += 1
                self.current_nesting += 1
                self.max_nesting = max(self.max_nesting, self.current_nesting)
                self.generic_visit(node)
                self.current_nesting -= 1
                
            def visit_With(self, node):
                self.current_nesting += 1
                self.max_nesting = max(self.max_nesting, self.current_nesting)
                self.generic_visit(node)
                self.current_nesting -= 1
        
        visitor = ComplexityVisitor()
        visitor.visit(tree)
        
        complexity_score = max(0, 100 - (visitor.complexity * 2))
        nesting_score = max(0, 100 - (visitor.max_nesting * 8))
        overall = (complexity_score + nesting_score) / 2
        
        return {
            "cyclomatic_complexity": visitor.complexity,
            "max_nesting_depth": visitor.max_nesting,
            "score": round(overall, 1),
            "grade": self._grade_score(overall)
        }
    
    def _python_memory_safety(self, tree: ast.AST) -> List[Dict]:
        """Detect memory safety issues in Python"""
        issues = []
        
        class MemVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                if isinstance(node.func, ast.Name) and node.func.id == 'open':
                    parent = getattr(node, 'parent', None)
                    if not isinstance(parent, ast.With):
                        issues.append({
                            'type': 'Unmanaged file handle',
                            'line': node.lineno,
                            'severity': 'MEDIUM',
                            'message': 'Use "with open()" for automatic resource management'
                        })
                self.generic_visit(node)
        
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                setattr(child, 'parent', node)
        
        MemVisitor().visit(tree)
        return issues
    
    def _python_security(self, tree: ast.AST) -> List[Dict]:
        """Detect security issues in Python"""
        issues = []
        
        dangerous_funcs = {
            'eval': 'CRITICAL',
            'exec': 'CRITICAL',
            'compile': 'HIGH',
            '__import__': 'HIGH',
            'pickle.load': 'HIGH',
            'pickle.loads': 'HIGH',
            'os.system': 'HIGH',
        }
        
        class SecVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                func_name = None
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    if hasattr(node.func.value, 'id'):
                        func_name = f"{node.func.value.id}.{node.func.attr}"
                
                if func_name and func_name in dangerous_funcs:
                    issues.append({
                        'type': f'Dangerous function: {func_name}',
                        'line': node.lineno,
                        'severity': dangerous_funcs[func_name],
                        'message': f'Use of {func_name} can lead to code injection'
                    })
                self.generic_visit(node)
        
        SecVisitor().visit(tree)
        return issues
    
    def _analyze_c_cpp(self) -> Dict[str, Any]:
        """Analyze C/C++ file using regex"""
        return self._analyze_with_regex()
    
    def _analyze_with_regex(self) -> Dict[str, Any]:
        """Use regex patterns for C/C++ analysis with complete memory detection"""
        memory_issues = []
        security_issues = []
        lines = self.source_code.split('\n')
        full_text = self.source_code
        
        # Track memory allocations for leak detection
        allocations = []
        deallocations = []
        
        for i, line in enumerate(lines, 1):
            # Uninitialized pointers
            if '*' in line and ';' in line and '=' not in line:
                if 'new' not in line and 'malloc' not in line and 'NULL' not in line and 'nullptr' not in line:
                    if not re.search(r'\([^)]*\*[^)]*\)', line):
                        memory_issues.append({
                            'type': 'Uninitialized pointer',
                            'line': i,
                            'severity': 'HIGH',
                            'message': 'Pointer declared without initialization'
                        })
            
            # Memory allocation detection
            if 'new' in line and ('int' in line or 'char' in line or 'double' in line):
                allocations.append({'line': i, 'type': 'new', 'line_content': line})
            if 'malloc(' in line or 'calloc(' in line:
                allocations.append({'line': i, 'type': 'malloc', 'line_content': line})
            
            # Deallocation detection
            if 'delete' in line:
                deallocations.append({'line': i, 'type': 'delete', 'line_content': line})
            if 'free(' in line:
                deallocations.append({'line': i, 'type': 'free', 'line_content': line})
            
            # Use after free detection
            if 'free(' in line or 'delete' in line:
                for offset in range(1, 4):
                    if i + offset <= len(lines):
                        next_line = lines[i + offset - 1]
                        if re.search(r'\*\s*\w+\s*=', next_line) or \
                           re.search(r'\w+\s*->\s*\w+', next_line):
                            ptr_match = re.search(r'(?:free|delete)\s*\(\s*(\w+)\s*\)', line)
                            if ptr_match:
                                ptr_name = ptr_match.group(1)
                                if ptr_name in next_line:
                                    memory_issues.append({
                                        'type': 'Use after free',
                                        'line': i + offset,
                                        'severity': 'HIGH',
                                        'message': f'Pointer used after being freed'
                                    })
                                    break
            
            # Security issues
            if 'gets(' in line:
                security_issues.append({
                    'type': 'Extremely unsafe: gets()',
                    'line': i,
                    'severity': 'CRITICAL',
                    'message': 'Never use gets() - use fgets() instead'
                })
            
            if 'strcpy(' in line:
                security_issues.append({
                    'type': 'Unsafe: strcpy()',
                    'line': i,
                    'severity': 'HIGH',
                    'message': 'Use strncpy() instead'
                })
            
            if 'strcat(' in line:
                security_issues.append({
                    'type': 'Unsafe: strcat()',
                    'line': i,
                    'severity': 'HIGH',
                    'message': 'Use strncat() instead'
                })
            
            if 'sprintf(' in line:
                security_issues.append({
                    'type': 'Unsafe: sprintf()',
                    'line': i,
                    'severity': 'HIGH',
                    'message': 'Use snprintf() instead'
                })
        
        # Memory leak detection
        malloc_count = len([a for a in allocations if a['type'] == 'malloc'])
        free_count = len([d for d in deallocations if d['type'] == 'free'])
        new_count = len([a for a in allocations if a['type'] == 'new'])
        delete_count = len([d for d in deallocations if d['type'] == 'delete'])
        
        if malloc_count > free_count:
            leaked = malloc_count - free_count
            memory_issues.append({
                'type': 'Memory leak (malloc/free mismatch)',
                'line': allocations[0]['line'] if allocations else 0,
                'severity': 'MEDIUM',
                'message': f'{leaked} malloc() call(s) without matching free()'
            })
        
        if new_count > delete_count:
            leaked = new_count - delete_count
            memory_issues.append({
                'type': 'Memory leak (new/delete mismatch)',
                'line': allocations[0]['line'] if allocations else 0,
                'severity': 'MEDIUM',
                'message': f'{leaked} new statement(s) without matching delete'
            })
        
        # Remove duplicates
        unique_memory = []
        seen = set()
        for issue in memory_issues:
            key = (issue['line'], issue['type'])
            if key not in seen:
                seen.add(key)
                unique_memory.append(issue)
        
        unique_security = []
        seen = set()
        for issue in security_issues:
            key = (issue['line'], issue['type'])
            if key not in seen:
                seen.add(key)
                unique_security.append(issue)
        
        readability = self._c_readability_regex()
        
        return {
            "readability": readability,
            "memory_issues": unique_memory,
            "security_issues": unique_security,
            "summary": self._generate_summary(unique_memory, unique_security, readability)
        }
    
    def _c_readability_regex(self) -> Dict[str, Any]:
        """Calculate C/C++ readability metrics"""
        lines = self.source_code.split('\n')
        complexity = 0
        max_nesting = 0
        current_nesting = 0
        
        for line in lines:
            stripped = line.strip()
            
            if stripped.endswith('{'):
                current_nesting += 1
                max_nesting = max(max_nesting, current_nesting)
            
            if stripped == '}' or stripped.startswith('}'):
                current_nesting = max(0, current_nesting - 1)
            
            if re.search(r'\bif\b|\bfor\b|\bwhile\b|\bswitch\b', stripped):
                complexity += 1
            
            complexity += stripped.count('&&') + stripped.count('||')
        
        complexity_score = max(0, 100 - (complexity * 2))
        nesting_score = max(0, 100 - (max_nesting * 8))
        overall = (complexity_score + nesting_score) / 2
        
        return {
            "cyclomatic_complexity": complexity if complexity > 0 else 0,
            "max_nesting_depth": max_nesting,
            "score": round(overall, 1),
            "grade": self._grade_score(overall)
        }
    
    def _analyze_generic(self) -> Dict[str, Any]:
        """Generic analysis for unsupported languages"""
        return {
            "readability": self._generic_readability(),
            "memory_issues": [],
            "security_issues": [],
            "summary": {"status": "UNSUPPORTED"}
        }
    
    def _generic_readability(self) -> Dict[str, Any]:
        """Generic readability metrics"""
        lines = self.source_code.split('\n')
        long_lines = sum(1 for line in lines if len(line) > 80)
        complexity = sum(1 for line in lines if any(kw in line for kw in ['if', 'for', 'while']))
        score = max(0, 100 - (long_lines * 2) - complexity)
        
        return {
            "cyclomatic_complexity": complexity,
            "max_nesting_depth": "Unknown",
            "score": round(min(100, score), 1),
            "grade": self._grade_score(score)
        }
    
    def _grade_score(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 80: return "A - Excellent"
        if score >= 60: return "B - Good"
        if score >= 40: return "C - Fair"
        if score >= 20: return "D - Poor"
        return "F - Very Poor"
    
    def _generate_summary(self, memory_issues: List, security_issues: List, readability: Dict) -> Dict:
        """Generate overall summary"""
        total_issues = len(memory_issues) + len(security_issues)
        critical = sum(1 for i in security_issues if i.get('severity') == 'CRITICAL')
        
        if total_issues == 0 and readability.get('score', 0) >= 70:
            status = "PASS"
        elif total_issues <= 5 and readability.get('score', 0) >= 50:
            status = "CAUTION"
        else:
            status = "FAIL"
        
        return {
            "status": status,
            "total_issues": total_issues,
            "critical_issues": critical,
            "memory_issues_count": len(memory_issues),
            "security_issues_count": len(security_issues)
        }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python multi_lang_analyzer.py <file>")
        sys.exit(1)
    
    try:
        analyzer = MultiLanguageAnalyzer(sys.argv[1], use_ml=True)
        results = analyzer.analyze_with_ml()
        print(json.dumps(results, indent=2))
    except Exception as e:
        print(f"Error: {e}")