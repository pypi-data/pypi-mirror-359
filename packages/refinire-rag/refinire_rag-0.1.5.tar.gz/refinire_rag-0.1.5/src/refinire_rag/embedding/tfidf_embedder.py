"""
TF-IDF Embeddings implementation

Provides embedding functionality using TF-IDF (Term Frequency-Inverse Document Frequency)
vectorization for lightweight, interpretable text representations.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Set
import time
import numpy as np
import pickle
import os
from pathlib import Path

from .base import Embedder, EmbeddingConfig, EmbeddingResult
from ..exceptions import EmbeddingError


@dataclass
class TFIDFEmbeddingConfig(EmbeddingConfig):
    """Configuration for TF-IDF embeddings
    TF-IDF埋め込みの設定"""
    
    # Model name (for consistency with base class)
    model_name: str = "tfidf"
    
    # Vocabulary settings
    max_features: int = 10000  # Maximum number of features (vocabulary size)
    min_df: int = 2  # Minimum document frequency
    max_df: float = 0.95  # Maximum document frequency (as ratio)
    ngram_range: tuple = (1, 2)  # N-gram range (unigrams and bigrams)
    
    # Text preprocessing
    lowercase: bool = True
    remove_stopwords: bool = True
    custom_stopwords: Optional[Set[str]] = None
    
    # TF-IDF parameters
    use_idf: bool = True  # Use inverse document frequency weighting
    smooth_idf: bool = True  # Add 1 to document frequencies
    sublinear_tf: bool = True  # Use log-scaled term frequencies
    
    # Normalization
    normalize_vectors: bool = True  # L2 normalization
    normalize_embeddings: bool = True  # Alternative name for compatibility
    
    # Model persistence
    model_path: Optional[str] = None  # Path to save/load trained model
    auto_save_model: bool = True  # Automatically save trained model
    
    # Performance settings
    embedding_dimension: int = 10000  # Will be set to actual vocabulary size
    batch_size: int = 1000  # For batch processing
    
    # Language settings
    language: str = "english"  # Language for stopwords
    
    def __post_init__(self):
        """Post-initialization processing"""
        # Call parent's post_init if it exists
        if hasattr(super(), '__post_init__'):
            super().__post_init__()


class TFIDFEmbedder(Embedder):
    """TF-IDF embeddings implementation
    TF-IDF埋め込みの実装"""
    
    def __init__(self, **kwargs):
        """Initialize TF-IDF embedder
        
        Args:
            **kwargs: Configuration parameters, environment variables used as fallback
                     設定パラメータ、環境変数をフォールバックとして使用
        """
        # Create config with environment variable support
        config = kwargs.get('config')
        if config is None:
            config = self._create_config_from_env(**kwargs)
        elif not isinstance(config, TFIDFEmbeddingConfig):
            # If dict config provided, merge with env vars
            env_config = self._create_config_from_env()
            config_dict = config if isinstance(config, dict) else {}
            merged_config = {**env_config.to_dict(), **config_dict, **kwargs}
            config = TFIDFEmbeddingConfig(**merged_config)
        
        self.config = config
        super().__init__(self.config)
        
        # TF-IDF components
        self._vectorizer = None
        self._is_fitted = False
        self._vocabulary = None
        self._idf_values = None
        
        # Document corpus for training
        self._training_corpus: List[str] = []
        
        # Initialize sklearn components
        self._init_vectorizer()
        
        # Load pre-trained model if specified
        if self.config.model_path and os.path.exists(self.config.model_path):
            self.load_model(self.config.model_path)
    
    @property
    def vectorizer(self):
        """Public access to vectorizer for compatibility with tests
        テスト互換性のためのベクタライザーへのパブリックアクセス"""
        return self._vectorizer
    
    def _init_vectorizer(self):
        """Initialize the TF-IDF vectorizer"""
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            import nltk
            
            # Download stopwords if needed
            if self.config.remove_stopwords:
                try:
                    nltk.data.find('corpora/stopwords')
                except LookupError:
                    nltk.download('stopwords', quiet=True)
            
            # Prepare stopwords
            stop_words = None
            if self.config.remove_stopwords:
                if self.config.custom_stopwords:
                    stop_words = list(self.config.custom_stopwords)
                else:
                    try:
                        from nltk.corpus import stopwords
                        stop_words = list(stopwords.words(self.config.language))
                    except LookupError:
                        # If NLTK stopwords not available, use built-in sklearn stopwords
                        stop_words = "english"
            
            # Initialize vectorizer
            self._vectorizer = TfidfVectorizer(
                max_features=self.config.max_features,
                min_df=self.config.min_df,
                max_df=self.config.max_df,
                ngram_range=self.config.ngram_range,
                lowercase=self.config.lowercase,
                stop_words=stop_words,
                use_idf=self.config.use_idf,
                smooth_idf=self.config.smooth_idf,
                sublinear_tf=self.config.sublinear_tf,
                norm='l2' if self.config.normalize_vectors else None
            )
            
        except ImportError as e:
            missing_lib = "scikit-learn" if "sklearn" in str(e) else "nltk"
            raise EmbeddingError(
                f"{missing_lib} library not found. Install with: pip install {missing_lib}"
            )
    
    def fit(self, texts: List[str]):
        """Fit the TF-IDF model on a corpus of texts
        
        Args:
            texts: List of text documents to train on
        """
        if not texts:
            raise EmbeddingError("Cannot fit TF-IDF model on empty corpus")
        
        start_time = time.time()
        
        try:
            # Preprocess texts
            processed_texts = [self._preprocess_text(text) for text in texts]
            processed_texts = [text for text in processed_texts if text.strip()]
            
            if not processed_texts:
                raise EmbeddingError("All texts became empty after preprocessing")
            
            # Fit the vectorizer
            self._vectorizer.fit(processed_texts)
            self._is_fitted = True
            
            # Store training information
            self._training_corpus = processed_texts
            self._vocabulary = self._vectorizer.vocabulary_
            self._idf_values = self._vectorizer.idf_ if self.config.use_idf else None
            
            # Update embedding dimension
            self.config.embedding_dimension = len(self._vocabulary)
            
            # Save model if requested
            if self.config.auto_save_model and self.config.model_path:
                self.save_model(self.config.model_path)
            
            fit_time = time.time() - start_time
            print(f"TF-IDF model fitted on {len(processed_texts)} documents in {fit_time:.2f}s")
            print(f"Vocabulary size: {len(self._vocabulary)}")
            
        except ValueError as ve:
            raise ValueError(f"Cannot fit TF-IDF model on empty corpus: {ve}")
        except Exception as e:
            raise EmbeddingError(f"Failed to fit TF-IDF model: {e}")
    
    def embed_text(self, text: str) -> np.ndarray:
        """Embed a single text string using TF-IDF"""
        if not self._is_fitted:
            raise EmbeddingError(
                "TF-IDF model not fitted. Call fit() with training corpus first."
            )
        
        start_time = time.time()
        
        # Check cache first
        cache_key = self._get_cache_key(text)
        cached_vector = self._get_from_cache(cache_key)
        if cached_vector is not None:
            return cached_vector
        
        try:
            # Preprocess text
            processed_text = self._preprocess_text(text)
            
            if not processed_text.strip():
                # Return zero vector for empty text
                vector = np.zeros(self.config.embedding_dimension)
            else:
                # Transform using fitted vectorizer
                tfidf_matrix = self._vectorizer.transform([processed_text])
                vector = tfidf_matrix.toarray()[0]
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Update statistics
            self._update_stats(processing_time, success=True)
            
            # Cache result
            self._store_in_cache(cache_key, vector)
            
            return vector
            
        except Exception as e:
            processing_time = time.time() - start_time
            self._update_stats(processing_time, success=False)
            
            error_msg = f"TF-IDF embedding failed: {e}"
            
            if self.config.fail_on_error:
                raise EmbeddingError(error_msg)
            
            # Return zero vector on error
            return np.zeros(self.config.embedding_dimension)
    
    def embed_texts(self, texts: List[str]) -> List[np.ndarray]:
        """Embed multiple texts efficiently"""
        if not self._is_fitted:
            raise EmbeddingError(
                "TF-IDF model not fitted. Call fit() with training corpus first."
            )
        
        start_time = time.time()
        vectors = []
        
        # Check cache for all texts
        uncached_texts = []
        uncached_indices = []
        
        for i, text in enumerate(texts):
            cache_key = self._get_cache_key(text)
            cached_vector = self._get_from_cache(cache_key)
            
            if cached_vector is not None:
                vectors.append((i, cached_vector))
            else:
                uncached_texts.append(text)
                uncached_indices.append(i)
        
        # Process uncached texts
        if uncached_texts:
            try:
                # Preprocess all texts
                processed_texts = [self._preprocess_text(text) for text in uncached_texts]
                
                # Transform batch
                tfidf_matrix = self._vectorizer.transform(processed_texts)
                batch_vectors = tfidf_matrix.toarray()
                
                # Process results
                batch_processing_time = time.time() - start_time
                individual_time = batch_processing_time / len(uncached_texts)
                
                for i, (text, vector) in enumerate(zip(uncached_texts, batch_vectors)):
                    # Cache result
                    cache_key = self._get_cache_key(text)
                    self._store_in_cache(cache_key, vector)
                    
                    vectors.append((uncached_indices[i], vector))
                    
                    # Update stats
                    self._update_stats(individual_time, success=True)
                
            except Exception as e:
                # Handle batch failure
                batch_processing_time = time.time() - start_time
                individual_time = batch_processing_time / len(uncached_texts)
                error_msg = f"TF-IDF batch embedding failed: {e}"
                
                for i, text in enumerate(uncached_texts):
                    self._update_stats(individual_time, success=False)
                    
                    if self.config.fail_on_error:
                        raise EmbeddingError(error_msg)
                    
                    # Add zero vector on error
                    error_vector = np.zeros(self.config.embedding_dimension)
                    vectors.append((uncached_indices[i], error_vector))
        
        # Sort vectors by original index
        vectors.sort(key=lambda x: x[0])
        return [vector for _, vector in vectors]
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text before embedding"""
        if not text:
            return ""
        
        # Basic cleaning
        processed = text.strip()
        
        # Additional preprocessing can be added here
        # For now, rely on TfidfVectorizer's built-in preprocessing
        
        return processed
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by this embedder"""
        if self._is_fitted:
            return self.config.embedding_dimension
        else:
            # Return configured max_features as estimate
            return self.config.max_features
    
    def get_vocabulary(self) -> Optional[Dict[str, int]]:
        """Get the fitted vocabulary"""
        return self._vocabulary if self._is_fitted else None
    
    def get_feature_names(self) -> Optional[List[str]]:
        """Get feature names (terms) from the vocabulary"""
        if not self._is_fitted:
            return None
        
        try:
            return self._vectorizer.get_feature_names_out().tolist()
        except AttributeError:
            # Older scikit-learn versions
            return self._vectorizer.get_feature_names()
    
    def get_top_features_for_text(self, text: str, top_k: int = 10) -> List[tuple]:
        """Get top contributing features for a text
        
        Args:
            text: Input text
            top_k: Number of top features to return
            
        Returns:
            List of (feature_name, tfidf_score) tuples
        """
        if not self._is_fitted:
            raise EmbeddingError("Model not fitted")
        
        result = self.embed_text(text)
        if not result.success:
            return []
        
        # Get feature names
        feature_names = self.get_feature_names()
        if not feature_names:
            return []
        
        # Get top features by TF-IDF score
        vector = result.vector
        top_indices = np.argsort(vector)[-top_k:][::-1]
        
        top_features = [
            (feature_names[idx], vector[idx])
            for idx in top_indices
            if vector[idx] > 0
        ]
        
        return top_features
    
    def save_model(self, model_path: str):
        """Save the fitted TF-IDF model to disk"""
        if not self._is_fitted:
            raise EmbeddingError("Cannot save unfitted model")
        
        try:
            model_dir = Path(model_path).parent
            model_dir.mkdir(parents=True, exist_ok=True)
            
            model_data = {
                "vectorizer": self._vectorizer,
                "config": self.config,
                "vocabulary": self._vocabulary,
                "idf_values": self._idf_values,
                "training_corpus_size": len(self._training_corpus)
            }
            
            with open(model_path, 'wb') as f:
                pickle.dump(model_data, f)
            
            print(f"TF-IDF model saved to {model_path}")
            
        except Exception as e:
            raise EmbeddingError(f"Failed to save model: {e}")
    
    def load_model(self, model_path: str):
        """Load a fitted TF-IDF model from disk"""
        try:
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            self._vectorizer = model_data["vectorizer"]
            self.config = model_data["config"]
            self._vocabulary = model_data["vocabulary"]
            self._idf_values = model_data["idf_values"]
            self._is_fitted = True
            
            print(f"TF-IDF model loaded from {model_path}")
            print(f"Vocabulary size: {len(self._vocabulary)}")
            print(f"Trained on {model_data.get('training_corpus_size', 'unknown')} documents")
            
        except Exception as e:
            raise EmbeddingError(f"Failed to load model: {e}")
    
    def is_fitted(self) -> bool:
        """Check if the model is fitted"""
        return self._is_fitted
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the fitted model"""
        info = {
            "is_fitted": self._is_fitted,
            "model_name": self.config.model_name,
            "embedding_dimension": self.get_embedding_dimension(),
            "config": self.config.to_dict()
        }
        
        if self._is_fitted:
            info.update({
                "vocabulary_size": len(self._vocabulary),
                "max_features": self.config.max_features,
                "ngram_range": self.config.ngram_range,
                "min_df": self.config.min_df,
                "max_df": self.config.max_df,
                "use_idf": self.config.use_idf,
                "training_corpus_size": len(self._training_corpus)
            })
        
        return info
    
    def compute_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Compute cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score between 0 and 1
        """
        # Normalize vectors if not already normalized
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        # Compute cosine similarity
        similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)
        return float(similarity)
    
    def _create_config_from_env(self, **kwargs) -> TFIDFEmbeddingConfig:
        """Create configuration from environment variables and kwargs
        
        環境変数とkwargsから設定を作成
        """
        import os
        
        # Priority: kwargs > config dict > env vars > defaults
        def get_value(key, default, env_var):
            return kwargs.get(key, os.getenv(env_var, default))
        
        # Map configuration parameters to environment variables
        model_name = get_value('model_name', 'tfidf', 'REFINIRE_RAG_TFIDF_MODEL_NAME')
        
        # Vocabulary settings
        max_features = int(get_value('max_features', '10000', 'REFINIRE_RAG_TFIDF_MAX_FEATURES'))
        min_df = int(get_value('min_df', '2', 'REFINIRE_RAG_TFIDF_MIN_DF'))
        max_df = float(get_value('max_df', '0.95', 'REFINIRE_RAG_TFIDF_MAX_DF'))
        
        # N-gram range (parse tuple from string)
        ngram_range_str = get_value('ngram_range', '1,2', 'REFINIRE_RAG_TFIDF_NGRAM_RANGE')
        if isinstance(ngram_range_str, str):
            ngram_parts = ngram_range_str.split(',')
            ngram_range = (int(ngram_parts[0]), int(ngram_parts[1])) if len(ngram_parts) == 2 else (1, 2)
        else:
            ngram_range = ngram_range_str or (1, 2)
        
        # Boolean parameters
        lowercase = get_value('lowercase', 'true', 'REFINIRE_RAG_TFIDF_LOWERCASE').lower() == 'true'
        remove_stopwords = get_value('remove_stopwords', 'true', 'REFINIRE_RAG_TFIDF_REMOVE_STOPWORDS').lower() == 'true'
        use_idf = get_value('use_idf', 'true', 'REFINIRE_RAG_TFIDF_USE_IDF').lower() == 'true'
        smooth_idf = get_value('smooth_idf', 'true', 'REFINIRE_RAG_TFIDF_SMOOTH_IDF').lower() == 'true'
        sublinear_tf = get_value('sublinear_tf', 'true', 'REFINIRE_RAG_TFIDF_SUBLINEAR_TF').lower() == 'true'
        normalize_vectors = get_value('normalize_vectors', 'true', 'REFINIRE_RAG_TFIDF_NORMALIZE_VECTORS').lower() == 'true'
        auto_save_model = get_value('auto_save_model', 'true', 'REFINIRE_RAG_TFIDF_AUTO_SAVE_MODEL').lower() == 'true'
        enable_caching = get_value('enable_caching', 'true', 'REFINIRE_RAG_TFIDF_ENABLE_CACHING').lower() == 'true'
        fail_on_error = get_value('fail_on_error', 'true', 'REFINIRE_RAG_TFIDF_FAIL_ON_ERROR').lower() == 'true'
        
        # Numeric parameters
        embedding_dimension = int(get_value('embedding_dimension', '10000', 'REFINIRE_RAG_TFIDF_EMBEDDING_DIMENSION'))
        batch_size = int(get_value('batch_size', '1000', 'REFINIRE_RAG_TFIDF_BATCH_SIZE'))
        max_tokens = int(get_value('max_tokens', '8192', 'REFINIRE_RAG_TFIDF_MAX_TOKENS'))
        cache_ttl_seconds = int(get_value('cache_ttl_seconds', '3600', 'REFINIRE_RAG_TFIDF_CACHE_TTL'))
        max_retries = int(get_value('max_retries', '3', 'REFINIRE_RAG_TFIDF_MAX_RETRIES'))
        retry_delay_seconds = float(get_value('retry_delay_seconds', '1.0', 'REFINIRE_RAG_TFIDF_RETRY_DELAY'))
        
        # String parameters
        language = get_value('language', 'english', 'REFINIRE_RAG_TFIDF_LANGUAGE')
        model_path = get_value('model_path', None, 'REFINIRE_RAG_TFIDF_MODEL_PATH')
        
        # Custom stopwords (parse from comma-separated string)
        custom_stopwords_str = get_value('custom_stopwords', None, 'REFINIRE_RAG_TFIDF_CUSTOM_STOPWORDS')
        custom_stopwords = None
        if custom_stopwords_str:
            custom_stopwords = set(word.strip() for word in custom_stopwords_str.split(','))
        
        return TFIDFEmbeddingConfig(
            model_name=model_name,
            max_features=max_features,
            min_df=min_df,
            max_df=max_df,
            ngram_range=ngram_range,
            lowercase=lowercase,
            remove_stopwords=remove_stopwords,
            custom_stopwords=custom_stopwords,
            use_idf=use_idf,
            smooth_idf=smooth_idf,
            sublinear_tf=sublinear_tf,
            normalize_vectors=normalize_vectors,
            normalize_embeddings=normalize_vectors,  # Alias for compatibility
            model_path=model_path,
            auto_save_model=auto_save_model,
            embedding_dimension=embedding_dimension,
            batch_size=batch_size,
            language=language,
            enable_caching=enable_caching,
            cache_ttl_seconds=cache_ttl_seconds,
            max_tokens=max_tokens,
            max_retries=max_retries,
            retry_delay_seconds=retry_delay_seconds,
            fail_on_error=fail_on_error
        )
    
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration as dictionary
        
        Returns:
            Dict[str, Any]: Current configuration parameters
        """
        return {
            'model_name': self.config.model_name,
            'max_features': self.config.max_features,
            'min_df': self.config.min_df,
            'max_df': self.config.max_df,
            'ngram_range': self.config.ngram_range,
            'lowercase': self.config.lowercase,
            'remove_stopwords': self.config.remove_stopwords,
            'custom_stopwords': list(self.config.custom_stopwords) if self.config.custom_stopwords else None,
            'use_idf': self.config.use_idf,
            'smooth_idf': self.config.smooth_idf,
            'sublinear_tf': self.config.sublinear_tf,
            'normalize_vectors': self.config.normalize_vectors,
            'normalize_embeddings': self.config.normalize_embeddings,
            'model_path': self.config.model_path,
            'auto_save_model': self.config.auto_save_model,
            'embedding_dimension': self.config.embedding_dimension,
            'batch_size': self.config.batch_size,
            'language': self.config.language,
            'enable_caching': self.config.enable_caching,
            'cache_ttl_seconds': self.config.cache_ttl_seconds,
            'max_tokens': self.config.max_tokens,
            'max_retries': self.config.max_retries,
            'retry_delay_seconds': self.config.retry_delay_seconds,
            'fail_on_error': self.config.fail_on_error,
            'is_fitted': self._is_fitted,
            'vocabulary_size': len(self._vocabulary) if self._is_fitted else 0
        }
    
    def embed_batch(self, texts: List[str]) -> List[np.ndarray]:
        """Alias for embed_texts for compatibility
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        return self.embed_texts(texts)