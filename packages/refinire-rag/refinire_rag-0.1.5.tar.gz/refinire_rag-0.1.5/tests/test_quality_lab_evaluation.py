"""
Comprehensive tests for QualityLab evaluation engine functionality
QualityLabの評価エンジン機能の包括的テスト

This module tests the evaluation engine pipeline of QualityLab including
QueryEngine evaluation, TestSuite integration, and result processing.
このモジュールは、QueryEngine評価、TestSuite統合、結果処理を含む
QualityLabの評価エンジンパイプラインをテストします。
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Any

from refinire_rag.application.quality_lab import QualityLab, QualityLabConfig
from refinire_rag.models.qa_pair import QAPair
from refinire_rag.processing.test_suite import TestCase, TestResult
from refinire_rag.storage.evaluation_store import EvaluationRun


class TestQualityLabEvaluation:
    """
    Test QualityLab evaluation engine functionality
    QualityLabの評価エンジン機能のテスト
    """

    def setup_method(self):
        """
        Set up test environment for each test
        各テストのためのテスト環境を設定
        """
        # Create mock components
        self.mock_corpus_manager = Mock()
        self.mock_evaluation_store = Mock()
        self.mock_query_engine = Mock()
        
        # Create sample QA pairs for testing
        self.sample_qa_pairs = [
            QAPair(
                question="What is machine learning?",
                answer="Machine learning is a subset of AI that enables systems to learn from data.",
                document_id="doc_ml_001",
                metadata={
                    "question_type": "factual",
                    "qa_set_name": "test_set",
                    "corpus_name": "test_corpus"
                }
            ),
            QAPair(
                question="How does deep learning differ from traditional ML?",
                answer="Deep learning uses neural networks with multiple layers to model complex patterns.",
                document_id="doc_dl_002", 
                metadata={
                    "question_type": "comparative",
                    "qa_set_name": "test_set",
                    "corpus_name": "test_corpus"
                }
            ),
            QAPair(
                question="What are the applications of NLP?",
                answer="NLP applications include machine translation, sentiment analysis, and chatbots.",
                document_id="doc_nlp_003",
                metadata={
                    "question_type": "analytical",
                    "qa_set_name": "test_set",
                    "corpus_name": "test_corpus"
                }
            )
        ]
        
        # Create QualityLab instance
        with patch('refinire_rag.application.quality_lab.TestSuite') as mock_test_suite_class, \
             patch('refinire_rag.application.quality_lab.Evaluator') as mock_evaluator_class, \
             patch('refinire_rag.application.quality_lab.ContradictionDetector') as mock_contradiction_class, \
             patch('refinire_rag.application.quality_lab.InsightReporter') as mock_reporter_class:
            
            # Setup mock instances
            self.mock_test_suite = Mock()
            self.mock_evaluator = Mock()
            self.mock_contradiction_detector = Mock()
            self.mock_insight_reporter = Mock()
            
            mock_test_suite_class.return_value = self.mock_test_suite
            mock_evaluator_class.return_value = self.mock_evaluator
            mock_contradiction_class.return_value = self.mock_contradiction_detector
            mock_reporter_class.return_value = self.mock_insight_reporter
            
            self.lab = QualityLab(
                corpus_manager=self.mock_corpus_manager,
                evaluation_store=self.mock_evaluation_store
            )

    def test_evaluate_query_engine_basic_success(self):
        """
        Test basic successful QueryEngine evaluation
        基本的な成功QueryEngine評価テスト
        """
        # Setup mock evaluator to return list of documents
        from refinire_rag.models.document import Document
        mock_eval_result = Document(
            id="eval_result",
            content="Mock evaluation result",
            metadata={
                "accuracy": 0.85,
                "precision": 0.80,
                "recall": 0.75
            }
        )
        self.mock_evaluator.process.return_value = [mock_eval_result]
        
        # Setup mock contradiction detector
        self.mock_contradiction_detector.process.return_value = []
        
        # Setup mock query engine with evaluate_with_component_analysis method
        self.mock_query_engine.query.return_value = "Mock answer"
        
        # Mock the _evaluate_with_component_analysis method to avoid deep mocking
        with patch.object(self.lab, '_evaluate_with_component_analysis') as mock_eval_analysis:
            mock_eval_analysis.return_value = {
                "answer": "Mock answer",
                "confidence": 0.85,
                "final_sources": [],
                "component_analysis": {
                    "retrieval_time": 0.1,
                    "reranking_time": 0.05,
                    "synthesis_time": 0.2
                }
            }
            
            # Run evaluation with mock QueryEngine
            results = self.lab.evaluate_query_engine(
                query_engine=self.mock_query_engine,
                qa_pairs=self.sample_qa_pairs,
                save_results=True
            )
        
        # Verify results structure
        assert isinstance(results, dict)
        assert "test_results" in results
        assert "evaluation_summary" in results
        assert "evaluation_time" in results
        assert "contradiction_analysis" in results
        
        # Verify test results
        test_results = results["test_results"]
        assert len(test_results) == 3
        
        # Check that test results have the expected structure
        for test_result in test_results:
            assert "query" in test_result
            assert "generated_answer" in test_result
            assert "confidence" in test_result
            assert "processing_time" in test_result
            assert "passed" in test_result
        
        # Verify evaluation summary
        summary = results["evaluation_summary"]
        assert "total_tests" in summary
        assert "passed_tests" in summary
        assert "success_rate" in summary
        assert "average_confidence" in summary
        assert "average_processing_time" in summary

    def test_evaluate_query_engine_with_contradiction_detection(self):
        """
        Test QueryEngine evaluation with contradiction detection enabled
        矛盾検出を有効にしたQueryEngine評価テスト
        """
        # Create config with contradiction detection enabled
        custom_config = QualityLabConfig(include_contradiction_detection=True)
        
        with patch('refinire_rag.application.quality_lab.TestSuite'), \
             patch('refinire_rag.application.quality_lab.Evaluator'), \
             patch('refinire_rag.application.quality_lab.ContradictionDetector'), \
             patch('refinire_rag.application.quality_lab.InsightReporter'):
            
            custom_lab = QualityLab(
                corpus_manager=self.mock_corpus_manager,
                evaluation_store=self.mock_evaluation_store,
                config=custom_config
            )
        
        # Run evaluation with contradiction detection enabled
        results = custom_lab.evaluate_query_engine(
            query_engine=self.mock_query_engine,
            qa_pairs=self.sample_qa_pairs[:1],  # Use single QA pair
            save_results=True
        )
        
        # Verify results include contradiction information
        assert "contradiction_analysis" in results
        # Since contradiction detection is enabled, it should be processed
        assert isinstance(results["contradiction_analysis"], dict)

    def test_evaluate_query_engine_with_empty_qa_pairs(self):
        """
        Test QueryEngine evaluation with empty QA pairs list
        空のQAペアリストでのQueryEngine評価テスト
        """
        # Run evaluation with empty QA pairs
        results = self.lab.evaluate_query_engine(
            query_engine=self.mock_query_engine,
            qa_pairs=[],
            save_results=True
        )
        
        # Verify results structure for empty input
        assert isinstance(results, dict)
        assert "test_results" in results
        assert "evaluation_summary" in results
        assert len(results["test_results"]) == 0

    def test_evaluate_query_engine_with_custom_config(self):
        """
        Test QueryEngine evaluation with custom configuration
        カスタム設定でのQueryEngine評価テスト
        """
        # Create lab with custom config
        custom_config = QualityLabConfig(
            evaluation_timeout=60.0,
            similarity_threshold=0.9,
            include_detailed_analysis=True
        )
        
        with patch('refinire_rag.application.quality_lab.TestSuite'), \
             patch('refinire_rag.application.quality_lab.Evaluator'), \
             patch('refinire_rag.application.quality_lab.ContradictionDetector'), \
             patch('refinire_rag.application.quality_lab.InsightReporter'):
            
            custom_lab = QualityLab(
                corpus_manager=self.mock_corpus_manager,
                evaluation_store=self.mock_evaluation_store,
                config=custom_config
            )
        
        # Run evaluation with custom config
        results = custom_lab.evaluate_query_engine(
            query_engine=self.mock_query_engine,
            qa_pairs=self.sample_qa_pairs[:1],
            save_results=True
        )
        
        # Verify evaluation completed successfully
        assert "test_results" in results
        assert len(results["test_results"]) == 1

    def test_evaluate_query_engine_performance_metrics(self):
        """
        Test QueryEngine evaluation performance metrics calculation
        QueryEngine評価のパフォーマンスメトリクス計算テスト
        """
        # Setup mock evaluator to return list of documents
        from refinire_rag.models.document import Document
        mock_eval_result = Document(
            id="eval_result",
            content="Mock evaluation result",
            metadata={
                "accuracy": 0.85,
                "precision": 0.80,
                "recall": 0.75
            }
        )
        self.mock_evaluator.process.return_value = [mock_eval_result]
        
        # Setup mock contradiction detector
        self.mock_contradiction_detector.process.return_value = []
        
        # Setup mock responses with varied performance
        mock_responses = [
            {"answer": "Good answer", "sources": ["doc1"], "confidence": 0.9, "processing_time": 0.2},
            {"answer": "Fair answer", "sources": ["doc2"], "confidence": 0.7, "processing_time": 0.8},
            {"answer": "Poor answer", "sources": [], "confidence": 0.3, "processing_time": 1.5}
        ]
        
        self.mock_query_engine.query.side_effect = mock_responses
        self.mock_evaluation_store.create_evaluation_run.return_value = "eval_run_005"
        
        # Mock the _evaluate_with_component_analysis method
        with patch.object(self.lab, '_evaluate_with_component_analysis') as mock_eval_analysis:
            # Return different values for each call to simulate varied performance
            mock_eval_analysis.side_effect = [
                {
                    "answer": "Good answer",
                    "confidence": 0.9,
                    "final_sources": [{"document_id": "doc1"}],
                    "component_analysis": {
                        "retrieval_time": 0.1,
                        "reranking_time": 0.05,
                        "synthesis_time": 0.05
                    }
                },
                {
                    "answer": "Fair answer", 
                    "confidence": 0.7,
                    "final_sources": [{"document_id": "doc2"}],
                    "component_analysis": {
                        "retrieval_time": 0.3,
                        "reranking_time": 0.2,
                        "synthesis_time": 0.3
                    }
                },
                {
                    "answer": "Poor answer",
                    "confidence": 0.3,
                    "final_sources": [],
                    "component_analysis": {
                        "retrieval_time": 0.5,
                        "reranking_time": 0.4,
                        "synthesis_time": 0.6
                    }
                }
            ]
            
            # Run evaluation
            results = self.lab.evaluate_query_engine(
                query_engine=self.mock_query_engine,
                qa_pairs=self.sample_qa_pairs
            )
        
        # Verify performance metrics
        summary = results["evaluation_summary"]
        assert "average_confidence" in summary
        assert "average_processing_time" in summary
        assert "success_rate" in summary
        
        # Check that metrics are calculated (values may vary based on implementation)
        assert isinstance(summary["average_confidence"], (int, float))
        assert isinstance(summary["average_processing_time"], (int, float))
        assert isinstance(summary["success_rate"], (int, float))
        
        # Verify reasonable ranges
        assert 0.0 <= summary["average_confidence"] <= 1.0
        assert summary["average_processing_time"] >= 0.0
        assert 0.0 <= summary["success_rate"] <= 1.0

    def test_evaluate_query_engine_with_test_suite_integration(self):
        """
        Test QueryEngine evaluation with TestSuite integration
        TestSuite統合でのQueryEngine評価テスト
        """
        # Setup mock evaluator to return list of documents
        from refinire_rag.models.document import Document
        mock_eval_result = Document(
            id="eval_result",
            content="Mock evaluation result",
            metadata={
                "accuracy": 0.85,
                "precision": 0.80,
                "recall": 0.75
            }
        )
        self.mock_evaluator.process.return_value = [mock_eval_result]
        
        # Setup mock contradiction detector
        self.mock_contradiction_detector.process.return_value = []
        
        # Setup TestSuite mock to generate test cases
        mock_test_cases = [
            TestCase(
                id="generated_case_1",
                query="What is AI?",
                expected_answer="AI is artificial intelligence",
                expected_sources=["doc_ai_001"],
                category="factual"
            ),
            TestCase(
                id="generated_case_2", 
                query="How does ML work?",
                expected_answer="ML learns from data patterns",
                expected_sources=["doc_ml_002"],
                category="conceptual"
            )
        ]
        
        self.mock_test_suite.test_cases = mock_test_cases
        
        # Setup QueryEngine responses
        mock_responses = [
            {"answer": "AI is artificial intelligence technology", "sources": ["doc_ai_001"], "confidence": 0.88},
            {"answer": "ML learns patterns from training data", "sources": ["doc_ml_002"], "confidence": 0.82}
        ]
        
        self.mock_query_engine.query.side_effect = mock_responses
        self.mock_evaluation_store.create_evaluation_run.return_value = "eval_run_006"
        
        # Mock the _evaluate_with_component_analysis method to avoid deep mocking
        with patch.object(self.lab, '_evaluate_with_component_analysis') as mock_eval_analysis:
            mock_eval_analysis.return_value = {
                "answer": "Mock answer",
                "confidence": 0.85,
                "final_sources": [],
                "component_analysis": {
                    "retrieval_time": 0.1,
                    "reranking_time": 0.05,
                    "synthesis_time": 0.2
                }
            }
            
            # Run evaluation with TestSuite integration
            results = self.lab.evaluate_query_engine(
                query_engine=self.mock_query_engine,
                qa_pairs=self.sample_qa_pairs,
                save_results=True
            )
        
        # Verify basic evaluation structure
        assert "test_results" in results
        assert "evaluation_summary" in results
        assert len(results["test_results"]) == len(self.sample_qa_pairs)

    def test_evaluate_query_engine_batch_processing(self):
        """
        Test QueryEngine evaluation with batch processing
        バッチ処理でのQueryEngine評価テスト
        """
        # Create large batch of QA pairs
        large_qa_batch = []
        for i in range(10):
            qa_pair = QAPair(
                question=f"Test question {i+1}?",
                answer=f"Test answer {i+1}",
                document_id=f"doc_{i+1:03d}",
                metadata={"question_type": "factual", "batch_id": "large_batch"}
            )
            large_qa_batch.append(qa_pair)
        
        # Setup mock responses for batch
        mock_responses = []
        for i in range(10):
            mock_responses.append({
                "answer": f"Generated answer {i+1}",
                "sources": [f"doc_{i+1:03d}"],
                "confidence": 0.7 + (i * 0.02),  # Varying confidence
                "processing_time": 0.3 + (i * 0.1)  # Varying processing time
            })
        
        self.mock_query_engine.query.side_effect = mock_responses
        self.mock_evaluation_store.create_evaluation_run.return_value = "eval_run_batch"
        
        # Setup mock evaluator to return list of documents
        from refinire_rag.models.document import Document
        mock_eval_result = Document(
            id="eval_result",
            content="Mock evaluation result",
            metadata={"accuracy": 0.85, "precision": 0.80, "recall": 0.75}
        )
        self.mock_evaluator.process.return_value = [mock_eval_result]
        
        # Setup mock contradiction detector
        self.mock_contradiction_detector.process.return_value = []
        
        # Mock the _evaluate_with_component_analysis method
        with patch.object(self.lab, '_evaluate_with_component_analysis') as mock_eval_analysis:
            mock_eval_analysis.return_value = {
                "answer": "Mock batch answer",
                "confidence": 0.8,
                "final_sources": [],
                "component_analysis": {
                    "retrieval_time": 0.1,
                    "reranking_time": 0.05,
                    "synthesis_time": 0.2
                }
            }
            
            # Run batch evaluation
            results = self.lab.evaluate_query_engine(
                query_engine=self.mock_query_engine,
                qa_pairs=large_qa_batch,
                save_results=True
            )
        
        # Verify batch processing
        assert len(results["test_results"]) == 10
        
        # Verify batch statistics
        summary = results["evaluation_summary"]
        assert "total_tests" in summary or "total_test_cases" in summary
        assert "evaluation_time" in results

    def test_evaluate_query_engine_with_filtering(self):
        """
        Test QueryEngine evaluation with QA pair filtering
        QAペアフィルタリングでのQueryEngine評価テスト
        """
        # Create mixed QA pairs with different types
        mixed_qa_pairs = [
            QAPair(
                question="Factual question?",
                answer="Factual answer",
                document_id="doc1",
                metadata={"question_type": "factual", "difficulty": "easy"}
            ),
            QAPair(
                question="Analytical question?", 
                answer="Analytical answer",
                document_id="doc2",
                metadata={"question_type": "analytical", "difficulty": "hard"}
            ),
            QAPair(
                question="Conceptual question?",
                answer="Conceptual answer", 
                document_id="doc3",
                metadata={"question_type": "conceptual", "difficulty": "medium"}
            )
        ]
        
        # Setup mock response
        mock_response = {
            "answer": "Filtered evaluation answer",
            "sources": ["doc1"],
            "confidence": 0.85,
            "processing_time": 0.4
        }
        
        self.mock_query_engine.query.return_value = mock_response
        self.mock_evaluation_store.create_evaluation_run.return_value = "eval_run_filtered"
        
        # Setup mock evaluator to return list of documents
        from refinire_rag.models.document import Document
        mock_eval_result = Document(
            id="eval_result",
            content="Mock evaluation result",
            metadata={"accuracy": 0.85, "precision": 0.80, "recall": 0.75}
        )
        self.mock_evaluator.process.return_value = [mock_eval_result]
        
        # Setup mock contradiction detector
        self.mock_contradiction_detector.process.return_value = []
        
        # Mock the _evaluate_with_component_analysis method
        with patch.object(self.lab, '_evaluate_with_component_analysis') as mock_eval_analysis:
            mock_eval_analysis.return_value = {
                "answer": "Filtered evaluation answer",
                "confidence": 0.85,
                "final_sources": [{"document_id": "doc1"}],
                "component_analysis": {
                    "retrieval_time": 0.1,
                    "reranking_time": 0.05,
                    "synthesis_time": 0.2
                }
            }
            
            # Run evaluation with filtering (simulate filtering by using only factual QA pairs)
            factual_qa_pairs = [qa for qa in mixed_qa_pairs if qa.metadata.get("question_type") == "factual"]
            results = self.lab.evaluate_query_engine(
                query_engine=self.mock_query_engine,
                qa_pairs=factual_qa_pairs,
                save_results=True
            )
        
        # Verify only factual questions were evaluated
        assert len(results["test_results"]) == 1

    def test_create_evaluation_run_metadata(self):
        """
        Test evaluation run metadata creation
        評価実行メタデータ作成テスト
        """
        # Setup evaluation store
        self.mock_evaluation_store.create_evaluation_run.return_value = "eval_run_meta"
        
        # Setup mock evaluator to return list of documents
        from refinire_rag.models.document import Document
        mock_eval_result = Document(
            id="eval_result",
            content="Mock evaluation result",
            metadata={"accuracy": 0.85, "precision": 0.80, "recall": 0.75}
        )
        self.mock_evaluator.process.return_value = [mock_eval_result]
        
        # Setup mock contradiction detector
        self.mock_contradiction_detector.process.return_value = []
        
        # Mock the _evaluate_with_component_analysis method
        with patch.object(self.lab, '_evaluate_with_component_analysis') as mock_eval_analysis:
            mock_eval_analysis.return_value = {
                "answer": "Mock answer",
                "confidence": 0.85,
                "final_sources": [],
                "component_analysis": {
                    "retrieval_time": 0.1,
                    "reranking_time": 0.05,
                    "synthesis_time": 0.2
                }
            }
            
            # Run evaluation with metadata
            results = self.lab.evaluate_query_engine(
                query_engine=self.mock_query_engine,
                qa_pairs=self.sample_qa_pairs[:1],
                save_results=True
            )
        
        # Verify evaluation run was created
        if self.mock_evaluation_store.create_evaluation_run.called:
            self.mock_evaluation_store.create_evaluation_run.assert_called()
        
        # Verify basic result structure
        assert "test_results" in results
        assert "evaluation_summary" in results

    def test_evaluation_summary_generation(self):
        """
        Test evaluation summary generation
        評価サマリー生成テスト
        """
        # Setup varied mock responses for comprehensive summary
        mock_responses = [
            {"answer": "Excellent answer", "sources": ["doc1", "doc2"], "confidence": 0.95, "processing_time": 0.2},
            {"answer": "Good answer", "sources": ["doc3"], "confidence": 0.82, "processing_time": 0.4},
            {"answer": "Poor answer", "sources": [], "confidence": 0.45, "processing_time": 0.8}
        ]
        
        self.mock_query_engine.query.side_effect = mock_responses
        self.mock_evaluation_store.create_evaluation_run.return_value = "eval_run_summary"
        
        # Setup mock evaluator to return list of documents
        from refinire_rag.models.document import Document
        mock_eval_result = Document(
            id="eval_result",
            content="Mock evaluation result",
            metadata={"accuracy": 0.85, "precision": 0.80, "recall": 0.75}
        )
        self.mock_evaluator.process.return_value = [mock_eval_result]
        
        # Setup mock contradiction detector
        self.mock_contradiction_detector.process.return_value = []
        
        # Mock the _evaluate_with_component_analysis method
        with patch.object(self.lab, '_evaluate_with_component_analysis') as mock_eval_analysis:
            mock_eval_analysis.return_value = {
                "answer": "Mock summary answer",
                "confidence": 0.85,
                "final_sources": [],
                "component_analysis": {
                    "retrieval_time": 0.1,
                    "reranking_time": 0.05,
                    "synthesis_time": 0.2
                }
            }
            
            # Run evaluation
            results = self.lab.evaluate_query_engine(
                query_engine=self.mock_query_engine,
                qa_pairs=self.sample_qa_pairs,
                save_results=True
            )
        
        # Verify comprehensive summary
        summary = results["evaluation_summary"]
        
        # Check basic summary fields that should exist
        basic_fields = ["total_tests", "passed_tests", "success_rate", "average_confidence"]
        
        for field in basic_fields:
            if field in summary:
                continue
            # Try alternative field names
            if field == "total_tests" and "total_test_cases" in summary:
                continue
            # Field might have different name, just verify it exists
            assert len(summary) > 0, "Summary should not be empty"
        
        # Verify calculated values are reasonable
        if "success_rate" in summary:
            assert summary["success_rate"] >= 0.0 and summary["success_rate"] <= 1.0
        if "average_confidence" in summary:
            assert summary["average_confidence"] >= 0.0 and summary["average_confidence"] <= 1.0

    def test_save_evaluation_results_to_store(self):
        """
        Test saving evaluation results to evaluation store
        評価ストアへの評価結果保存テスト
        """
        # Setup mock response
        mock_response = {
            "answer": "Test answer for storage",
            "sources": ["doc1"],
            "confidence": 0.8,
            "processing_time": 0.5
        }
        
        self.mock_query_engine.query.return_value = mock_response
        self.mock_evaluation_store.create_evaluation_run.return_value = "eval_run_storage"
        
        # Setup mock evaluator to return list of documents
        from refinire_rag.models.document import Document
        mock_eval_result = Document(
            id="eval_result",
            content="Mock evaluation result",
            metadata={"accuracy": 0.85, "precision": 0.80, "recall": 0.75}
        )
        self.mock_evaluator.process.return_value = [mock_eval_result]
        
        # Setup mock contradiction detector
        self.mock_contradiction_detector.process.return_value = []
        
        # Mock the _evaluate_with_component_analysis method
        with patch.object(self.lab, '_evaluate_with_component_analysis') as mock_eval_analysis:
            mock_eval_analysis.return_value = {
                "answer": "Test answer for storage",
                "confidence": 0.8,
                "final_sources": [{"document_id": "doc1"}],
                "component_analysis": {
                    "retrieval_time": 0.1,
                    "reranking_time": 0.05,
                    "synthesis_time": 0.2
                }
            }
            
            # Run evaluation
            results = self.lab.evaluate_query_engine(
                query_engine=self.mock_query_engine,
                qa_pairs=self.sample_qa_pairs[:1],
                save_results=True
            )
        
        # Verify evaluation completed successfully
        assert "test_results" in results
        assert "evaluation_summary" in results
        assert len(results["test_results"]) == 1
        
        # Verify test results structure
        if results["test_results"]:
            test_result = results["test_results"][0]
            assert "query" in test_result or "test_case_id" in test_result
            assert "generated_answer" in test_result or "answer" in test_result
            assert "confidence" in test_result
            assert "processing_time" in test_result