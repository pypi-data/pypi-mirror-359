#!/usr/bin/env python3
"""
Ultra-lightweight classifier for the 129KB ONNX model.

This classifier is specifically designed to work with the ultra-lightweight
architecture that uses minimal memory and fast inference.
"""
import json
import logging
import numpy as np
from pathlib import Path
from typing import Tuple, Optional
import re

logger = logging.getLogger(__name__)

class UltraLightweightClassifier:
    """Classifier for the 129KB ultra-lightweight ONNX model."""
    
    def __init__(self, model_dir: Path):
        """Initialize the ultra-lightweight classifier.
        
        Args:
            model_dir: Directory containing the ultra-lightweight models
        """
        self.model_dir = model_dir
        self.onnx_session = None
        self.tokenizer_vocab = None
        self.patterns = None
        self.enabled = False
        
        self._load_components()
    
    def _load_components(self):
        """Load the ultra-lightweight model components."""
        try:
            # Load ONNX model
            model_path = self.model_dir / 'codebert_small_quantized.onnx'
            if model_path.exists():
                import onnxruntime as ort
                self.onnx_session = ort.InferenceSession(str(model_path))
                logger.info(f"Loaded ultra-lightweight ONNX model: {model_path.stat().st_size / 1024:.1f} KB")
            
            # Load tokenizer
            tokenizer_path = self.model_dir / 'code_tokenizer.json'
            if tokenizer_path.exists():
                with open(tokenizer_path, 'r') as f:
                    tokenizer_data = json.load(f)
                    self.tokenizer_vocab = tokenizer_data.get('vocab', {})
                    self.max_length = tokenizer_data.get('max_length', 64)
                logger.info(f"Loaded minimal tokenizer: {len(self.tokenizer_vocab)} tokens")
            
            # Load security patterns
            patterns_path = self.model_dir / 'critical_patterns.json'
            if patterns_path.exists():
                with open(patterns_path, 'r') as f:
                    self.patterns = json.load(f)
                logger.info(f"Loaded security patterns: {len(self.patterns.get('critical', []))} critical")
            
            # Enable if all components loaded
            self.enabled = (self.onnx_session is not None and 
                          self.tokenizer_vocab is not None and 
                          self.patterns is not None)
            
            if self.enabled:
                logger.info("✅ Ultra-lightweight classifier ready")
            else:
                logger.warning("⚠️ Some components missing - using fallback")
                
        except Exception as e:
            logger.error(f"Failed to load ultra-lightweight components: {e}")
            self.enabled = False
    
    def _tokenize(self, text: str) -> np.ndarray:
        """Tokenize text using the minimal tokenizer.
        
        Args:
            text: Input text to tokenize
            
        Returns:
            Array of token IDs padded to max_length
        """
        if not self.tokenizer_vocab:
            return np.zeros(self.max_length, dtype=np.int64)
        
        # Simple tokenization - split on whitespace and punctuation
        tokens = re.findall(r'\w+|[^\w\s]', text.lower())
        
        # Convert to token IDs
        token_ids = []
        for token in tokens:
            if token in self.tokenizer_vocab:
                token_ids.append(self.tokenizer_vocab[token])
            else:
                token_ids.append(self.tokenizer_vocab.get('[UNK]', 1))
        
        # Pad or truncate to max_length
        if len(token_ids) > self.max_length:
            token_ids = token_ids[:self.max_length]
        else:
            pad_id = self.tokenizer_vocab.get('[PAD]', 0)
            token_ids.extend([pad_id] * (self.max_length - len(token_ids)))
        
        return np.array(token_ids, dtype=np.int64).reshape(1, -1)
    
    def _classify_with_patterns(self, content: str) -> Tuple[str, float]:
        """Classify using security patterns (fallback)."""
        if not self.patterns:
            return 'trivial', 0.5
        
        content_lower = content.lower()
        
        # Check critical patterns
        for pattern_info in self.patterns.get('critical', []):
            pattern = pattern_info.get('pattern', '')
            if re.search(pattern, content_lower):
                return 'critical', 0.9
        
        # Check important patterns
        for pattern_info in self.patterns.get('important', []):
            pattern = pattern_info.get('pattern', '')
            if re.search(pattern, content_lower):
                return 'important', 0.8
        
        return 'trivial', 0.5
    
    def classify(self, file_path: str, content: str) -> Tuple[str, float]:
        """Classify code content using ultra-lightweight model.
        
        Args:
            file_path: Path to the file being classified
            content: Code content to classify
            
        Returns:
            Tuple of (classification, confidence)
        """
        if not self.enabled or not self.onnx_session:
            # Fall back to pattern matching
            return self._classify_with_patterns(content)
        
        try:
            # Tokenize input
            input_ids = self._tokenize(content)
            
            # Run ONNX inference
            outputs = self.onnx_session.run(['output'], {'input_ids': input_ids})
            logits = outputs[0][0]  # Shape: [3] for [trivial, important, critical]
            
            # Apply softmax to get probabilities
            exp_logits = np.exp(logits - np.max(logits))  # Numerical stability
            probs = exp_logits / np.sum(exp_logits)
            
            # Get prediction
            pred_idx = np.argmax(probs)
            confidence = float(probs[pred_idx])
            
            classifications = ['trivial', 'important', 'critical']
            classification = classifications[pred_idx]
            
            # If ONNX model confidence is low, fall back to patterns
            if confidence < 0.6:
                pattern_result = self._classify_with_patterns(content)
                # Use pattern result if it's more specific
                if pattern_result[0] != 'trivial' and pattern_result[1] > confidence:
                    return pattern_result
            
            return classification, confidence
            
        except Exception as e:
            logger.debug(f"ONNX inference failed for {file_path}: {e}")
            # Fall back to pattern matching
            return self._classify_with_patterns(content)
    
    def get_stats(self) -> dict:
        """Get classifier statistics."""
        return {
            'type': 'ultra_lightweight',
            'enabled': self.enabled,
            'model_size_kb': (self.model_dir / 'codebert_small_quantized.onnx').stat().st_size / 1024 if (self.model_dir / 'codebert_small_quantized.onnx').exists() else 0,
            'tokenizer_vocab_size': len(self.tokenizer_vocab) if self.tokenizer_vocab else 0,
            'max_sequence_length': getattr(self, 'max_length', 64)
        }