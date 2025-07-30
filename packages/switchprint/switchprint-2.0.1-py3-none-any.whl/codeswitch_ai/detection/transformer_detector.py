#!/usr/bin/env python3
"""Transformer-based language detection using mBERT and XLM-R."""

import torch
import numpy as np
from typing import List, Dict, Optional, Tuple, Union
from functools import lru_cache
import warnings

from transformers import (
    AutoTokenizer, AutoModel, AutoModelForSequenceClassification,
    XLMRobertaTokenizer, XLMRobertaModel, XLMRobertaForSequenceClassification,
    BertTokenizer, BertModel, BertForSequenceClassification
)

from .language_detector import LanguageDetector, DetectionResult

warnings.filterwarnings("ignore", category=UserWarning, module="transformers")


class TransformerDetector(LanguageDetector):
    """Advanced language detector using transformer models (mBERT, XLM-R)."""
    
    def __init__(self, 
                 model_name: str = "bert-base-multilingual-cased",
                 max_length: int = 512,
                 batch_size: int = 16,
                 device: Optional[str] = None,
                 cache_size: int = 1000):
        """Initialize transformer-based detector.
        
        Args:
            model_name: Name of the transformer model to use
            max_length: Maximum sequence length
            batch_size: Batch size for processing
            device: Device to run on ('cpu', 'cuda', or None for auto)
            cache_size: Size of LRU cache for embeddings
        """
        super().__init__()
        self.model_name = model_name
        self.max_length = max_length
        self.batch_size = batch_size
        self.cache_size = cache_size
        self.detector_type = "transformer"  # Add detector type attribute
        
        # Set device
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)
        
        # Initialize model and tokenizer
        self.tokenizer = None
        self.model = None
        self._load_model()
        
        # Language mappings for different models
        self.language_mappings = {
            'bert-base-multilingual-cased': self._get_mbert_language_mapping(),
            'xlm-roberta-base': self._get_xlmr_language_mapping(),
            'xlm-roberta-large': self._get_xlmr_language_mapping(),
        }
        
        # Confidence thresholds
        self.confidence_thresholds = {
            'high': 0.8,
            'medium': 0.6,
            'low': 0.4
        }
    
    def _load_model(self):
        """Load the transformer model and tokenizer."""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModel.from_pretrained(self.model_name)
            self.model.to(self.device)
            self.model.eval()
            
            print(f"Loaded {self.model_name} on {self.device}")
            
        except Exception as e:
            raise RuntimeError(f"Failed to load transformer model {self.model_name}: {e}")
    
    def _get_mbert_language_mapping(self) -> Dict[str, str]:
        """Get language mapping for mBERT."""
        return {
            'en': 'english', 'es': 'spanish', 'fr': 'french', 'de': 'german',
            'it': 'italian', 'pt': 'portuguese', 'ru': 'russian', 'zh': 'chinese',
            'ja': 'japanese', 'ko': 'korean', 'ar': 'arabic', 'hi': 'hindi',
            'ur': 'urdu', 'fa': 'persian', 'tr': 'turkish', 'nl': 'dutch',
            'pl': 'polish', 'sv': 'swedish', 'da': 'danish', 'no': 'norwegian',
            'fi': 'finnish', 'el': 'greek', 'he': 'hebrew', 'th': 'thai',
            'vi': 'vietnamese', 'id': 'indonesian', 'ms': 'malay', 'tl': 'tagalog',
            'ta': 'tamil', 'te': 'telugu', 'bn': 'bengali', 'gu': 'gujarati',
            'kn': 'kannada', 'ml': 'malayalam', 'mr': 'marathi', 'pa': 'punjabi'
        }
    
    def _get_xlmr_language_mapping(self) -> Dict[str, str]:
        """Get language mapping for XLM-R."""
        # XLM-R supports 100 languages
        return self._get_mbert_language_mapping()  # Simplified for now
    
    @lru_cache(maxsize=1000)
    def _get_embeddings_cached(self, text: str) -> torch.Tensor:
        """Get cached embeddings for text."""
        if not text.strip():
            return torch.zeros(self.model.config.hidden_size, device=self.device)
        
        try:
            # Tokenize text
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                max_length=self.max_length,
                truncation=True,
                padding=True
            )
            
            # Move to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Get embeddings
            with torch.no_grad():
                outputs = self.model(**inputs)
                # Use [CLS] token embedding (first token)
                embeddings = outputs.last_hidden_state[:, 0, :]
                
            return embeddings.squeeze().cpu()
            
        except Exception as e:
            print(f"Error getting embeddings: {e}")
            return torch.zeros(self.model.config.hidden_size)
    
    def _detect_language_by_script(self, text: str) -> Optional[str]:
        """Detect language based on script/character patterns."""
        # Unicode script detection
        script_patterns = {
            'zh': r'[\u4e00-\u9fff]',  # Chinese
            'ja': r'[\u3040-\u309f\u30a0-\u30ff]',  # Japanese
            'ko': r'[\uac00-\ud7af]',  # Korean
            'ar': r'[\u0600-\u06ff]',  # Arabic
            'hi': r'[\u0900-\u097f]',  # Hindi/Devanagari
            'ru': r'[\u0400-\u04ff]',  # Cyrillic
            'el': r'[\u0370-\u03ff]',  # Greek
            'he': r'[\u0590-\u05ff]',  # Hebrew
            'th': r'[\u0e00-\u0e7f]',  # Thai
        }
        
        import re
        for lang, pattern in script_patterns.items():
            if re.search(pattern, text):
                return lang
        
        return None
    
    def _calculate_language_confidence(self, 
                                     text: str, 
                                     embeddings: torch.Tensor,
                                     user_languages: Optional[List[str]] = None) -> Dict[str, float]:
        """Calculate confidence scores for different languages."""
        confidences = {}
        
        # Script-based detection gets high confidence
        script_lang = self._detect_language_by_script(text)
        if script_lang:
            confidences[script_lang] = 0.9
        
        # For Latin script text, use heuristics
        if not script_lang:
            # Simple heuristics based on common words and patterns
            text_lower = text.lower()
            
            # English indicators
            if any(word in text_lower for word in ['the', 'and', 'is', 'to', 'a', 'in', 'that', 'it']):
                confidences['en'] = 0.7
            
            # Spanish indicators  
            if any(word in text_lower for word in ['el', 'la', 'de', 'que', 'y', 'en', 'un', 'es']):
                confidences['es'] = 0.7
            
            # French indicators
            if any(word in text_lower for word in ['le', 'de', 'et', 'à', 'un', 'il', 'être', 'et']):
                confidences['fr'] = 0.7
            
            # German indicators
            if any(word in text_lower for word in ['der', 'die', 'und', 'in', 'den', 'von', 'zu', 'das']):
                confidences['de'] = 0.7
        
        # Apply user language boost
        if user_languages:
            user_lang_codes = [self._normalize_language_code(lang) for lang in user_languages]
            for lang in user_lang_codes:
                if lang in confidences:
                    confidences[lang] = min(1.0, confidences[lang] * 1.2)
                else:
                    confidences[lang] = 0.5  # Default confidence for user languages
        
        # Normalize confidence scores
        if confidences:
            max_confidence = max(confidences.values())
            if max_confidence > 0:
                confidences = {k: v/max_confidence for k, v in confidences.items()}
        
        return confidences
    
    def detect_language(self, text: str, user_languages: Optional[List[str]] = None) -> DetectionResult:
        """Detect language using transformer model."""
        if not text.strip():
            return DetectionResult(
                detected_languages=[],
                confidence=0.0,
                probabilities={},
                method=f'transformer-{self.model_name}'
            )
        
        # Get embeddings
        embeddings = self._get_embeddings_cached(text)
        
        # Calculate language confidences
        confidences = self._calculate_language_confidence(text, embeddings, user_languages)
        
        if not confidences:
            return DetectionResult(
                detected_languages=[],
                confidence=0.0,
                probabilities={},
                method=f'transformer-{self.model_name}'
            )
        
        # Get primary language
        primary_language = max(confidences.keys(), key=lambda k: confidences[k])
        primary_confidence = confidences[primary_language]
        
        return DetectionResult(
            detected_languages=[primary_language],
            confidence=float(primary_confidence),
            probabilities=confidences,
            method=f'transformer-{self.model_name}'
        )
    
    def detect_code_switching_points(self, text: str, window_size: int = 5) -> List[Tuple[int, str, str, float]]:
        """Detect code-switching points using sliding window approach."""
        words = text.split()
        if len(words) < 2:
            return []
        
        switch_points = []
        
        for i in range(len(words) - window_size + 1):
            window = ' '.join(words[i:i + window_size])
            result = self.detect_language(window)
            
            if result.detected_languages:
                lang = result.detected_languages[0]
                confidence = result.confidence
                
                # Check if this is a switch point
                if i > 0:
                    prev_window = ' '.join(words[max(0, i-window_size):i])
                    prev_result = self.detect_language(prev_window)
                    
                    if (prev_result.detected_languages and 
                        prev_result.detected_languages[0] != lang and
                        confidence > self.confidence_thresholds['medium']):
                        
                        switch_points.append((i, prev_result.detected_languages[0], lang, confidence))
        
        return switch_points
    
    def get_contextual_embeddings(self, text: str, layer: int = -1) -> torch.Tensor:
        """Get contextual embeddings from specific layer."""
        if not text.strip():
            return torch.zeros(self.model.config.hidden_size, device=self.device)
        
        try:
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                max_length=self.max_length,
                truncation=True,
                padding=True
            )
            
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.model(**inputs, output_hidden_states=True)
                # Get embeddings from specified layer
                layer_embeddings = outputs.hidden_states[layer]
                # Average over sequence length
                embeddings = layer_embeddings.mean(dim=1)
                
            return embeddings.squeeze().cpu()
            
        except Exception as e:
            print(f"Error getting contextual embeddings: {e}")
            return torch.zeros(self.model.config.hidden_size)
    
    def _normalize_language_code(self, language: str) -> str:
        """Normalize language code to ISO 639-1 format."""
        language = language.lower().strip()
        
        normalization_map = {
            'english': 'en', 'spanish': 'es', 'french': 'fr', 'german': 'de',
            'italian': 'it', 'portuguese': 'pt', 'russian': 'ru', 'chinese': 'zh',
            'japanese': 'ja', 'korean': 'ko', 'arabic': 'ar', 'hindi': 'hi',
            'urdu': 'ur', 'persian': 'fa', 'farsi': 'fa', 'turkish': 'tr',
            'dutch': 'nl', 'polish': 'pl', 'swedish': 'sv', 'danish': 'da',
            'norwegian': 'no', 'finnish': 'fi', 'greek': 'el', 'hebrew': 'he',
            'thai': 'th', 'vietnamese': 'vi', 'indonesian': 'id', 'malay': 'ms',
            'tagalog': 'tl', 'filipino': 'tl', 'tamil': 'ta', 'telugu': 'te',
            'bengali': 'bn', 'gujarati': 'gu', 'kannada': 'kn', 'malayalam': 'ml',
            'marathi': 'mr', 'punjabi': 'pa'
        }
        
        return normalization_map.get(language, language)
    
    def get_model_info(self) -> Dict:
        """Get information about the loaded model."""
        return {
            'model_name': self.model_name,
            'device': str(self.device),
            'max_length': self.max_length,
            'model_type': 'transformer',
            'num_parameters': sum(p.numel() for p in self.model.parameters()),
            'supports_contextual_embeddings': True,
            'supports_code_switching_detection': True
        }