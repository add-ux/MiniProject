# ml_models.py - Machine Learning Models for Code Analysis
import numpy as np
import joblib
import re
from pathlib import Path
from typing import Dict, List, Any
import warnings
warnings.filterwarnings('ignore')

class CodeMLAnalyzer:
    """Machine Learning models for code quality analysis"""
    
    def __init__(self, model_path: str = "models/"):
        self.model_path = Path(model_path)
        self.model_path.mkdir(exist_ok=True)
        
        # Try to load real dataset trained models first
        self.quality_predictor = None
        self.bug_predictor = None
        self.security_predictor = None
        self.memory_predictor = None
        self.scaler = None
        self.using_real_data = False
        
        self._load_real_models()
        
        # Fallback to synthetic models if real not available
        if self.quality_predictor is None:
            self._load_synthetic_models()
        
        if self.quality_predictor is None:
            self._create_default_models()
    
    def save_models(self):
        """Save trained models to disk"""
        if self.quality_predictor is not None:
            quality_path = self.model_path / 'quality_predictor.pkl'
            bug_path = self.model_path / 'bug_predictor.pkl'
            security_path = self.model_path / 'security_predictor.pkl'
            memory_path = self.model_path / 'memory_predictor.pkl'
            scaler_path = self.model_path / 'scaler.pkl'
            
            joblib.dump(self.quality_predictor, quality_path)
            joblib.dump(self.bug_predictor, bug_path)
            
            if self.security_predictor is not None:
                joblib.dump(self.security_predictor, security_path)
            
            if self.memory_predictor is not None:
                joblib.dump(self.memory_predictor, memory_path)
            
            if self.scaler is not None:
                joblib.dump(self.scaler, scaler_path)
            
            print(f"✅ Models saved to {self.model_path}")
            return True
        else:
            print("❌ No models to save.")
            return False
    
    def _load_real_models(self):
        """Load models trained on real datasets"""
        quality_path = self.model_path / 'quality_model_real.pkl'
        bug_path = self.model_path / 'bug_model_real.pkl'
        security_path = self.model_path / 'security_model_real.pkl'
        memory_path = self.model_path / 'memory_model_real.pkl'
        scaler_path = self.model_path / 'scaler_real.pkl'
        
        if quality_path.exists() and bug_path.exists():
            self.quality_predictor = joblib.load(quality_path)
            self.bug_predictor = joblib.load(bug_path)
            self.security_predictor = joblib.load(security_path) if security_path.exists() else None
            self.memory_predictor = joblib.load(memory_path) if memory_path.exists() else None
            self.scaler = joblib.load(scaler_path) if scaler_path.exists() else None
            self.using_real_data = True
            print("✅ Loaded models trained on REAL datasets")
            return True
        return False
    
    def _load_synthetic_models(self):
        """Fallback to synthetic models"""
        quality_path = self.model_path / 'quality_predictor.pkl'
        bug_path = self.model_path / 'bug_predictor.pkl'
        
        if quality_path.exists():
            self.quality_predictor = joblib.load(quality_path)
            self.bug_predictor = joblib.load(bug_path)
            security_path = self.model_path / 'security_predictor.pkl'
            if security_path.exists():
                self.security_predictor = joblib.load(security_path)
            print("⚠️ Using synthetic models (run train_real_models.py for better accuracy)")
            return True
        return False
    
    def _create_default_models(self):
        """Create default models if none exist"""
        print("📊 Creating default models...")
        
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.preprocessing import StandardScaler
        
        # Generate dummy training data
        X_dummy = np.random.rand(200, 9)
        
        # Quality: 3 classes (0, 1, 2)
        y_quality_dummy = np.random.randint(0, 3, 200)
        
        # Bugs: 2 classes (0, 1)
        y_bug_dummy = np.random.randint(0, 2, 200)
        
        # Security: 2 classes (0, 1)
        y_security_dummy = np.random.randint(0, 2, 200)
        if np.sum(y_security_dummy) == 0:
            y_security_dummy[0] = 1
        if np.sum(y_security_dummy) == len(y_security_dummy):
            y_security_dummy[0] = 0
        
        # Memory: 2 classes (0, 1)
        y_memory_dummy = np.random.randint(0, 2, 200)
        
        # Train quality model
        self.quality_predictor = RandomForestClassifier(n_estimators=10, random_state=42)
        self.quality_predictor.fit(X_dummy, y_quality_dummy)
        
        # Train bug model
        self.bug_predictor = RandomForestClassifier(n_estimators=10, random_state=42)
        self.bug_predictor.fit(X_dummy, y_bug_dummy)
        
        # Train security model
        self.security_predictor = RandomForestClassifier(n_estimators=10, random_state=42)
        self.security_predictor.fit(X_dummy, y_security_dummy)
        
        # Train memory model
        self.memory_predictor = RandomForestClassifier(n_estimators=10, random_state=42)
        self.memory_predictor.fit(X_dummy, y_memory_dummy)
        
        # Train scaler
        self.scaler = StandardScaler()
        self.scaler.fit(X_dummy)
        
        print("✅ Default models created")
    
    def extract_code_features(self, code: str, language: str = None, metrics: Dict = None) -> np.ndarray:
        """Extract features from code for ML prediction"""
        lines = code.split('\n')
        code_lines = [l for l in lines if l.strip() and not l.strip().startswith(('#', '//', '/*'))]
        
        features = np.array([[
            min(len(re.findall(r'\b(if|for|while|elif|else|switch|case)\b', code)), 50),
            min(self._calculate_nesting_depth(code), 10),
            min(len(re.findall(r'(def|function|void|int|char)\s+\w+\s*\([^)]*\)\s*\{[^}]{150,}\}', code)), 20),
            min(len(re.findall(r'\b(eval|exec|system|gets|strcpy|sprintf|scanf)\b', code)), 10),
            len(re.findall(r'^[ \t]*[#//]', code, re.MULTILINE)) / max(len(lines), 1),
            min(len(lines), 1000),
            min(len(re.findall(r'\*|\&', code)), 30),
            min(len(re.findall(r'\[.*?\]', code)), 20),
            min(len(re.findall(r'\b(malloc|calloc|new|free|delete)\b', code)), 15)
        ]])
        
        # Scale if scaler exists
        if self.scaler is not None:
            features = self.scaler.transform(features)
        
        return features
    
    def _calculate_nesting_depth(self, code: str) -> int:
        max_depth = 0
        current_depth = 0
        for char in code:
            if char in '{(':
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif char in '})':
                current_depth = max(0, current_depth - 1)
        return max_depth
    
    def predict_quality_enhanced(self, code: str, language: str = None, metrics: Dict = None) -> Dict:
        """Enhanced quality prediction using ML"""
        if self.quality_predictor is None:
            return {'error': 'Model not trained'}
        
        features = self.extract_code_features(code, language, metrics)
        prediction = self.quality_predictor.predict(features)[0]
        
        try:
            proba = self.quality_predictor.predict_proba(features)[0]
            confidence = float(max(proba))
        except Exception:
            confidence = 0.7
        
        quality_map = {0: 'Poor', 1: 'Fair', 2: 'Good'}
        quality_score_map = {0: 35, 1: 65, 2: 85}
        
        return {
            'quality_level': quality_map.get(prediction, 'Unknown'),
            'quality_score': quality_score_map.get(prediction, 50),
            'confidence': confidence,
            'ml_enhanced': True,
            'trained_on': 'real_dataset' if self.using_real_data else 'synthetic',
            'language': language or 'unknown'
        }
    
    def predict_bugs_enhanced(self, code: str, language: str = None, metrics: Dict = None) -> Dict:
        """Enhanced bug prediction using ML"""
        if self.bug_predictor is None:
            return {'error': 'Model not trained'}
        
        features = self.extract_code_features(code, language, metrics)
        prediction = self.bug_predictor.predict(features)[0]
        
        try:
            proba = self.bug_predictor.predict_proba(features)[0]
            if len(proba) >= 2:
                bug_probability = float(proba[1])
            else:
                bug_probability = float(prediction)
        except Exception:
            bug_probability = 0.5
        
        return {
            'has_bugs': bool(prediction),
            'bug_probability': bug_probability,
            'risk_level': 'HIGH' if bug_probability > 0.7 else 'MEDIUM' if bug_probability > 0.3 else 'LOW',
            'ml_enhanced': True,
            'trained_on': 'real_dataset' if self.using_real_data else 'synthetic',
            'language': language or 'unknown'
        }
    
    def predict_security_enhanced(self, code: str, language: str = None, metrics: Dict = None) -> Dict:
        """Enhanced security risk prediction"""
        if self.security_predictor is None:
            # Fallback to simple detection
            dangerous = len(re.findall(r'\b(eval|exec|system|gets|strcpy|sprintf)\b', code)) > 0
            return {
                'has_security_risks': dangerous,
                'security_risk_probability': 0.8 if dangerous else 0.1,
                'ml_enhanced': False,
                'language': language or 'unknown'
            }
        
        features = self.extract_code_features(code, language, metrics)
        prediction = self.security_predictor.predict(features)[0]
        
        try:
            proba = self.security_predictor.predict_proba(features)[0]
            if len(proba) >= 2:
                risk_probability = float(proba[1])
            else:
                risk_probability = float(prediction) if prediction else 0.0
        except Exception:
            risk_probability = 0.5
        
        return {
            'has_security_risks': bool(prediction),
            'security_risk_probability': risk_probability,
            'ml_enhanced': True,
            'trained_on': 'real_dataset' if self.using_real_data else 'synthetic',
            'language': language or 'unknown'
        }
    
    def predict_memory_safety(self, code: str, language: str = None, metrics: Dict = None) -> Dict:
        """Predict memory safety issues (critical for C/C++)"""
        if self.memory_predictor is not None:
            features = self.extract_code_features(code, language, metrics)
            prediction = self.memory_predictor.predict(features)[0]
            
            try:
                proba = self.memory_predictor.predict_proba(features)[0]
                if len(proba) >= 2:
                    memory_probability = float(proba[1])
                else:
                    memory_probability = float(prediction) if prediction else 0.0
            except Exception:
                memory_probability = 0.5
        else:
            # Simple detection for memory issues
            has_malloc = 'malloc' in code or 'new' in code
            has_free = 'free' in code or 'delete' in code
            prediction = has_malloc and not has_free
            memory_probability = 0.7 if (has_malloc and not has_free) else 0.2
        
        return {
            'has_memory_issues': bool(prediction),
            'memory_risk_probability': memory_probability,
            'risk_level': 'HIGH' if memory_probability > 0.7 else 'MEDIUM' if memory_probability > 0.3 else 'LOW',
            'ml_enhanced': self.memory_predictor is not None,
            'language': language or 'unknown'
        }


class CodePatternDetector:
    """Detects code patterns and anti-patterns"""
    
    def detect_patterns(self, code: str, language: str = None, metrics: Dict = None) -> Dict:
        """Detect common patterns and anti-patterns in code"""
        suggestions = []
        patterns_found = []
        
        lines = code.split('\n')
        
        # Long function detection
        if len(lines) > 100:
            patterns_found.append({
                'pattern': 'Long Function',
                'severity': 'MEDIUM',
                'description': f'Function has {len(lines)} lines. Consider refactoring.'
            })
            suggestions.append("📏 Break long functions into smaller, focused functions")
        
        # Deep nesting detection
        max_nesting = self._calculate_max_nesting(code)
        if max_nesting > 4:
            patterns_found.append({
                'pattern': 'Deep Nesting',
                'severity': 'MEDIUM',
                'description': f'Maximum nesting depth of {max_nesting} makes code hard to read'
            })
            suggestions.append("🔀 Reduce nesting depth by using early returns or guard clauses")
        
        # Magic numbers detection
        magic_numbers = re.findall(r'(?<![a-zA-Z_])[0-9]+(?![a-zA-Z_])', code)
        magic_numbers = [n for n in magic_numbers if n not in ['0', '1', '-1', '2']]
        if len(magic_numbers) > 5:
            patterns_found.append({
                'pattern': 'Magic Numbers',
                'severity': 'LOW',
                'description': f'Found {len(magic_numbers)} magic numbers'
            })
            suggestions.append("🔢 Replace magic numbers with named constants")
        
        # Language-specific patterns
        if language == 'python':
            # Check for missing type hints
            def_count = len(re.findall(r'\bdef\s+\w+\s*\([^)]*\):', code))
            hint_count = len(re.findall(r':\s*(int|str|float|bool|list|dict|tuple|Optional|List|Dict)', code))
            if def_count > 0 and hint_count < def_count:
                patterns_found.append({
                    'pattern': 'Missing Type Hints',
                    'severity': 'LOW',
                    'description': f'Only {hint_count}/{def_count} functions have type hints'
                })
                suggestions.append("📝 Add type hints to improve code clarity and IDE support")
        
        elif language in ['c', 'cpp']:
            # Check for C-style casts in C++
            if language == 'cpp' and re.search(r'\([a-z*&]+\)', code):
                patterns_found.append({
                    'pattern': 'C-Style Casts',
                    'severity': 'LOW',
                    'description': 'Use static_cast, dynamic_cast, or reinterpret_cast instead'
                })
                suggestions.append("🔧 Replace C-style casts with C++ casts for better type safety")
        
        return {
            'patterns_found': patterns_found,
            'suggestions': suggestions,
            'total_patterns': len(patterns_found)
        }
    
    def _calculate_max_nesting(self, code: str) -> int:
        """Calculate maximum nesting depth"""
        max_depth = 0
        current_depth = 0
        
        for char in code:
            if char == '{' or char == '(':
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif char == '}' or char == ')':
                current_depth = max(0, current_depth - 1)
        
        return max_depth


class CodeSimilarityAnalyzer:
    """Analyzes code similarity for plagiarism detection"""
    
    def __init__(self):
        self._normalization_cache = {}
    
    def calculate_similarity(self, code1: str, code2: str, language: str = None) -> float:
        """Calculate similarity between two code snippets"""
        from difflib import SequenceMatcher
        similarity = SequenceMatcher(None, code1[:1000], code2[:1000]).ratio()
        return round(similarity * 100, 2)
    
    def find_similar_blocks(self, code: str, min_block_size: int = 3) -> List[Dict]:
        """Find similar blocks within the same code"""
        return []  # Simplified for now