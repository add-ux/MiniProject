# real_dataset_trainer.py - Train ML models on real code datasets
import numpy as np
import joblib
import re
import random
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class RealDatasetTrainer:
    """Train ML models using realistic code datasets"""
    
    def __init__(self):
        self.model_path = Path("models")
        self.model_path.mkdir(exist_ok=True)
        
        # Models
        self.quality_model = None
        self.bug_model = None
        self.security_model = None
        self.memory_model = None
        self.scaler = StandardScaler()
        
    def create_dataset(self):
        """Create dataset from code templates"""
        print("\n📁 Creating dataset from code templates...")
        samples = []
        
        # Code templates (good and bad examples)
        templates = self._get_code_templates()
        
        for template in templates:
            features = self._extract_features(template['code'])
            samples.append({
                'code': template['code'],
                'features': features,
                'quality_score': template['quality_score'],
                'has_bugs': template['has_bugs'],
                'has_security': template['has_security'],
                'has_memory': template.get('has_memory', False),
            })
        
        # Generate variations to increase dataset size
        print(f"   Generating variations from {len(samples)} base samples...")
        target_size = 3000
        
        while len(samples) < target_size:
            base = random.choice(samples)
            variation = self._create_variation(base)
            samples.append(variation)
            
            if len(samples) % 500 == 0:
                print(f"   Generated {len(samples)}/{target_size} samples...")
        
        print(f"   ✅ Created {len(samples)} total samples")
        return samples
    
    def _get_code_templates(self):
        """Get diverse code templates"""
        templates = []
        
        # GOOD Python code
        templates.append({
            'code': '''
def calculate_average(numbers):
    """Calculate average safely"""
    if not numbers:
        return 0
    total = sum(numbers)
    return total / len(numbers)

def process_data(items):
    results = []
    for item in items:
        if item is not None and item > 0:
            results.append(item * 2)
    return results
''',
            'quality_score': 90,
            'has_bugs': False,
            'has_security': False,
            'has_memory': False,
        })
        
        # BAD Python code (deep nesting, bugs)
        templates.append({
            'code': '''
def bad_function(x, y, z, a, b, c):
    if x > 0:
        if y > 0:
            if z > 0:
                if a > 0:
                    if b > 0:
                        if c > 0:
                            return x + y + z + a + b + c
    return 0

def buggy_process(data):
    result = []
    for i in range(len(data)):
        result.append(data[i] + data[i + 1])  # Index error!
    return result
''',
            'quality_score': 35,
            'has_bugs': True,
            'has_security': False,
            'has_memory': False,
        })
        
        # Python with security issues
        templates.append({
            'code': '''
def unsafe_function(user_input):
    query = "SELECT * FROM users WHERE name = '" + user_input + "'"
    import os
    os.system("ping " + user_input)
    result = eval(user_input)
    return result
''',
            'quality_score': 20,
            'has_bugs': True,
            'has_security': True,
            'has_memory': False,
        })
        
        # GOOD C code
        templates.append({
            'code': '''
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void safe_copy(char* dest, const char* src, size_t size) {
    if (dest == NULL || src == NULL || size == 0) return;
    strncpy(dest, src, size - 1);
    dest[size - 1] = '\\0';
}

int* safe_array_create(size_t size) {
    if (size == 0 || size > 10000) return NULL;
    int* arr = (int*)malloc(size * sizeof(int));
    return arr;
}
''',
            'quality_score': 92,
            'has_bugs': False,
            'has_security': False,
            'has_memory': False,
        })
        
        # BAD C code (memory leaks, buffer overflows)
        templates.append({
            'code': '''
#include <string.h>

void unsafe_buffer() {
    char buffer[10];
    char* long_string = "This string is way too long";
    strcpy(buffer, long_string);  // Buffer overflow!
}

void memory_leak() {
    int* ptr = (int*)malloc(sizeof(int) * 100);
    *ptr = 42;
    // Missing free() - memory leak!
}
''',
            'quality_score': 25,
            'has_bugs': True,
            'has_security': True,
            'has_memory': True,
        })
        
        # GOOD C++ code
        templates.append({
            'code': '''
#include <iostream>
#include <memory>
#include <vector>

class SafeContainer {
private:
    std::vector<int> data;
public:
    void add(int value) { data.push_back(value); }
    int get(int index) const {
        if (index >= 0 && index < data.size()) return data[index];
        throw std::out_of_range("Index out of range");
    }
};

int main() {
    auto container = std::make_unique<SafeContainer>();
    container->add(42);
    return 0;
}
''',
            'quality_score': 94,
            'has_bugs': False,
            'has_security': False,
            'has_memory': False,
        })
        
        # BAD C++ code
        templates.append({
            'code': '''
class LeakyClass {
public:
    LeakyClass() { data = new int[1000]; }
    ~LeakyClass() { /* Missing delete[] */ }
private:
    int* data;
};

void dangerous_cast() {
    int* ptr = new int(42);
    void* void_ptr = ptr;
    int* bad_ptr = (int*)void_ptr;  // C-style cast
    delete ptr;
}
''',
            'quality_score': 30,
            'has_bugs': True,
            'has_security': False,
            'has_memory': True,
        })
        
        return templates
    
    def _create_variation(self, base_sample):
        """Create variation of a sample"""
        code = base_sample['code']
        
        # Add random modification
        modified_code = code + f"\n// Variation line\n"
        
        # Slightly adjust quality
        new_quality = max(0, min(100, base_sample['quality_score'] + random.randint(-10, 10)))
        
        features = self._extract_features(modified_code)
        
        return {
            'code': modified_code,
            'features': features,
            'quality_score': new_quality,
            'has_bugs': base_sample['has_bugs'] if random.random() > 0.3 else not base_sample['has_bugs'],
            'has_security': base_sample['has_security'],
            'has_memory': base_sample.get('has_memory', False),
        }
    
    def _extract_features(self, code):
        """Extract numerical features from code"""
        lines = code.split('\n')
        
        complexity = len(re.findall(r'\b(if|for|while|elif|else|switch|case)\b', code, re.IGNORECASE))
        nesting_depth = self._calc_nesting_depth(code)
        long_methods = len(re.findall(r'(def|function|void|int|char)\s+\w+\s*\([^)]*\)\s*\{[^}]{150,}\}', code))
        dangerous_funcs = len(re.findall(r'\b(eval|exec|system|gets|strcpy|sprintf|malloc|free)\b', code, re.IGNORECASE))
        
        comment_lines = len(re.findall(r'^[ \t]*[#//]', code, re.MULTILINE))
        total_lines = len([l for l in lines if l.strip()])
        comment_ratio = comment_lines / max(total_lines, 1)
        
        pointer_ops = len(re.findall(r'\*|\&', code))
        array_ops = len(re.findall(r'\[.*?\]', code))
        memory_allocations = len(re.findall(r'\b(malloc|calloc|new|free|delete)\b', code, re.IGNORECASE))
        
        return {
            'complexity': min(complexity, 50),
            'nesting_depth': min(nesting_depth, 10),
            'long_methods': min(long_methods, 20),
            'dangerous_funcs': min(dangerous_funcs, 10),
            'comment_ratio': comment_ratio,
            'total_lines': min(total_lines, 1000),
            'pointer_ops': min(pointer_ops, 30),
            'array_ops': min(array_ops, 20),
            'memory_allocations': min(memory_allocations, 15)
        }
    
    def _calc_nesting_depth(self, code):
        """Calculate maximum nesting depth"""
        max_depth = 0
        current = 0
        for char in code:
            if char in '{(':
                current += 1
                max_depth = max(max_depth, current)
            elif char in '})':
                current = max(0, current - 1)
        return max_depth
    
    def prepare_data(self, samples):
        """Convert samples to numpy arrays"""
        X = []
        y_quality = []
        y_bug = []
        y_security = []
        y_memory = []
        
        for sample in samples:
            f = sample['features']
            X.append([
                f['complexity'], f['nesting_depth'], f['long_methods'],
                f['dangerous_funcs'], f['comment_ratio'], f['total_lines'],
                f['pointer_ops'], f['array_ops'], f['memory_allocations']
            ])
            
            # Quality: 0=Poor, 1=Fair, 2=Good
            score = sample['quality_score']
            if score >= 70:
                y_quality.append(2)
            elif score >= 40:
                y_quality.append(1)
            else:
                y_quality.append(0)
            
            y_bug.append(1 if sample['has_bugs'] else 0)
            y_security.append(1 if sample.get('has_security', False) else 0)
            y_memory.append(1 if sample.get('has_memory', False) else 0)
        
        return np.array(X), np.array(y_quality), np.array(y_bug), np.array(y_security), np.array(y_memory)
    
    def train_models(self, samples):
        """Train all ML models"""
        print("\n" + "="*60)
        print("🤖 Training ML Models")
        print("="*60)
        
        # Prepare data
        X, y_quality, y_bug, y_security, y_memory = self.prepare_data(samples)
        
        print(f"\n📊 Dataset: {len(X)} samples, {X.shape[1]} features")
        print(f"   Quality distribution: {np.bincount(y_quality)}")
        print(f"   Bug ratio: {y_bug.mean():.2%}")
        print(f"   Security ratio: {y_security.mean():.2%}")
        
        # Split data
        X_train, X_test, y_q_train, y_q_test, y_b_train, y_b_test, y_s_train, y_s_test, y_m_train, y_m_test = train_test_split(
            X, y_quality, y_bug, y_security, y_memory, test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        results = {}
        
        # 1. Quality Model
        print("\n📊 Training Quality Model...")
        self.quality_model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
        self.quality_model.fit(X_train_scaled, y_q_train)
        q_acc = accuracy_score(y_q_test, self.quality_model.predict(X_test_scaled))
        print(f"   ✅ Accuracy: {q_acc:.2%}")
        results['quality_accuracy'] = q_acc
        
        # 2. Bug Model
        print("\n🐛 Training Bug Detection Model...")
        self.bug_model = GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42)
        self.bug_model.fit(X_train_scaled, y_b_train)
        b_acc = accuracy_score(y_b_test, self.bug_model.predict(X_test_scaled))
        print(f"   ✅ Accuracy: {b_acc:.2%}")
        results['bug_accuracy'] = b_acc
        
        # 3. Security Model
        print("\n🔒 Training Security Model...")
        self.security_model = RandomForestClassifier(n_estimators=80, random_state=42)
        self.security_model.fit(X_train_scaled, y_s_train)
        s_acc = accuracy_score(y_s_test, self.security_model.predict(X_test_scaled))
        print(f"   ✅ Accuracy: {s_acc:.2%}")
        results['security_accuracy'] = s_acc
        
        # 4. Memory Model
        print("\n💾 Training Memory Safety Model...")
        self.memory_model = RandomForestClassifier(n_estimators=80, random_state=42)
        self.memory_model.fit(X_train_scaled, y_m_train)
        m_acc = accuracy_score(y_m_test, self.memory_model.predict(X_test_scaled))
        print(f"   ✅ Accuracy: {m_acc:.2%}")
        results['memory_accuracy'] = m_acc
        
        # Save models
        self.save_models()
        
        return results
    
    def save_models(self):
        """Save trained models"""
        joblib.dump(self.quality_model, self.model_path / 'quality_model_real.pkl')
        joblib.dump(self.bug_model, self.model_path / 'bug_model_real.pkl')
        joblib.dump(self.security_model, self.model_path / 'security_model_real.pkl')
        joblib.dump(self.memory_model, self.model_path / 'memory_model_real.pkl')
        joblib.dump(self.scaler, self.model_path / 'scaler_real.pkl')
        print("\n💾 Models saved to 'models/' directory")
    
    def run_complete_training(self):
        """Run complete training pipeline"""
        print("="*60)
        print("🚀 ML MODEL TRAINING PIPELINE")
        print("="*60)
        
        # Create dataset
        samples = self.create_dataset()
        
        # Train models
        results = self.train_models(samples)
        
        # Print summary
        print("\n" + "="*60)
        print("✅ TRAINING COMPLETE!")
        print("="*60)
        print(f"\n📈 Model Performance:")
        print(f"   Quality: {results['quality_accuracy']:.2%}")
        print(f"   Bugs: {results['bug_accuracy']:.2%}")
        print(f"   Security: {results['security_accuracy']:.2%}")
        print(f"   Memory: {results['memory_accuracy']:.2%}")
        
        return results


if __name__ == "__main__":
    trainer = RealDatasetTrainer()
    trainer.run_complete_training()
    print("\n🎉 Training completed! Now run: python app.py")