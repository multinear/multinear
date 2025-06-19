#!/usr/bin/env python3
"""
Comprehensive test suite for the NumericEvaluator implementation.
Tests all extraction methods, comparison algorithms, and edge cases.
"""

import pytest

from multinear.engine.numeric import (
    NumberExtractor, 
    ComparisonEngine, 
    NumericEvaluator,
    generate_debug_info
)


class TestNumberExtraction:
    """Test number extraction from various text formats."""
    
    def setup_method(self):
        self.extractor = NumberExtractor(use_llm=False)  # Disable LLM for unit tests
    
    def test_regex_extraction_formats(self):
        """Test various number formats extraction."""
        test_cases = [
            ("The result is 42.5", 42.5, "basic decimal"),
            ("Success rate: 85.3%", 0.853, "percentage"),
            ("Temperature: $123.45", 123.45, "currency"),
            ("Fraction: 3/4 of total", 0.75, "fraction"),
            ("Scientific: 1.23e-4", 0.000123, "scientific notation"),
            ("With commas: 1,234.567", 1234.567, "comma separator"),
            ("Negative: -42.5", -42.5, "negative number"),
            ("Euro price: €99.99", 99.99, "euro currency"),
            ("Multiple currencies: £50.00", 50.0, "pound currency"),
        ]
        
        for text, expected, description in test_cases:
            value, metadata = self.extractor.extract_regex(text)
            assert value is not None, f"Failed to extract from: {description}"
            assert abs(value - expected) < 0.001, f"Wrong value for {description}: got {value}, expected {expected}"
            assert metadata["extraction_method"] == "regex"
    
    def test_extraction_failures(self):
        """Test cases where extraction should fail."""
        test_cases = [
            "No numbers here",
            "",
            "Only text: abc def",
        ]
        
        for text in test_cases:
            value, metadata = self.extractor.extract_regex(text)
            assert value is None, f"Should not extract from: {text}"
            assert "error" in metadata
    
    def test_division_by_zero_handling(self):
        """Test that division by zero is handled gracefully."""
        # Test that fractions with zero denominator are ignored but other numbers are found
        text = "Calculate 5/0 and also 3/4"
        value, metadata = self.extractor.extract_regex(text)
        # Should extract 0.75 (3/4) and ignore 5/0
        assert value == 0.75, f"Should extract 3/4 = 0.75, got {value}"
    
    def test_multiple_numbers_handling(self):
        """Test handling of multiple numbers in text."""
        text = "The accuracy was 85.3% and the loss was 0.42"
        value, metadata = self.extractor.extract_regex(text)
        
        assert value is not None
        assert "warnings" in metadata
        assert "Multiple numbers found" in metadata["warnings"][0]
    
    def test_jsonpath_extraction(self):
        """Test JSONPath extraction from structured data."""
        test_data = {
            "result": {
                "accuracy": 0.85,
                "loss": 0.15
            },
            "metrics": [1.2, 3.4, 5.6]
        }
        
        # Test simple path
        value, metadata = self.extractor.extract_jsonpath(test_data, "$.result.accuracy")
        assert value == 0.85
        assert metadata["extraction_method"] == "jsonpath"
        
        # Test array access
        value, metadata = self.extractor.extract_jsonpath(test_data, "$.metrics[0]")
        assert value == 1.2
        
        # Test non-existent path
        value, metadata = self.extractor.extract_jsonpath(test_data, "$.nonexistent")
        assert value is None
        assert "error" in metadata
    
    def test_preprocessing(self):
        """Test number format preprocessing."""
        # Test percentage to decimal
        text = "The accuracy is 85.3% which is good"
        processed = self.extractor.preprocess_number(text, "percentage_to_decimal")
        assert "0.853" in processed
        
        # Test fraction to decimal
        text = "The result is 3/4 of the total"
        processed = self.extractor.preprocess_number(text, "fraction_to_decimal")
        assert "0.75" in processed
        
        # Test currency removal
        text = "The price is $99.99"
        processed = self.extractor.preprocess_number(text, "remove_currency")
        assert "$" not in processed


class TestComparisonMethods:
    """Test different comparison algorithms."""
    
    def setup_method(self):
        self.engine = ComparisonEngine()
    
    def test_direct_difference_scaling(self):
        """Test direct difference with expected-value-based scaling."""
        # Normal case
        score, metadata = self.engine.direct_difference(42, 40)
        expected_score = 1 - abs(42 - 40) / abs(40)  # 1 - 2/40 = 0.95
        assert abs(score - expected_score) < 0.001
        assert metadata["comparison_method"] == "direct_diff"
        
        # Perfect match
        score, metadata = self.engine.direct_difference(42, 42)
        assert score == 1.0
        
        # Zero expected value
        score, metadata = self.engine.direct_difference(0, 0)
        assert score == 1.0
        assert metadata["zero_expected_handling"] == True
        
        # Zero expected, non-zero actual
        score, metadata = self.engine.direct_difference(5, 0)
        assert score == 0.0  # max(0, 1 - 5) = 0
    
    def test_mse_comparison(self):
        """Test MSE scaling with various expected values."""
        # Test MSE calculation
        score, metadata = self.engine.mse_comparison(42, 40)
        mse = (42 - 40) ** 2  # 4
        scaling_factor = max(abs(40), 1.0)  # 40
        normalized_mse = mse / (scaling_factor ** 2)  # 4/1600 = 0.0025
        expected_score = max(0, 1 - normalized_mse)  # 0.9975
        
        assert abs(score - expected_score) < 0.001
        assert metadata["comparison_method"] == "mse"
        
        # Perfect match
        score, metadata = self.engine.mse_comparison(42, 42)
        assert score == 1.0
    
    def test_rmse_comparison(self):
        """Test RMSE scaling."""
        score, metadata = self.engine.rmse_comparison(42, 40)
        rmse = abs(42 - 40)  # 2
        scaling_factor = max(abs(40), 1.0)  # 40
        normalized_rmse = rmse / scaling_factor  # 2/40 = 0.05
        expected_score = max(0, 1 - normalized_rmse)  # 0.95
        
        assert abs(score - expected_score) < 0.001
        assert metadata["comparison_method"] == "rmse"
    
    def test_tolerance_comparison(self):
        """Test tolerance-based binary evaluation."""
        # Within absolute tolerance
        score, metadata = self.engine.tolerance_comparison(42, 40, absolute_tolerance=5.0)
        assert score == 1.0
        assert metadata["passed_absolute"] == True
        
        # Outside absolute tolerance
        score, metadata = self.engine.tolerance_comparison(50, 40, absolute_tolerance=5.0)
        assert score == 0.0
        assert metadata["passed_absolute"] == False
        
        # Within relative tolerance
        score, metadata = self.engine.tolerance_comparison(42, 40, relative_tolerance=0.1)
        assert score == 1.0  # 2/40 = 0.05 < 0.1
        assert metadata["passed_relative"] == True
        
        # Outside relative tolerance
        score, metadata = self.engine.tolerance_comparison(50, 40, relative_tolerance=0.1)
        assert score == 0.0  # 10/40 = 0.25 > 0.1
        assert metadata["passed_relative"] == False
    
    def test_range_comparison(self):
        """Test range validation."""
        # Within range
        score, metadata = self.engine.range_comparison(75, min_value=70, max_value=80)
        assert score == 1.0
        assert metadata["within_range"] == True
        
        # Below minimum
        score, metadata = self.engine.range_comparison(65, min_value=70, max_value=80)
        assert score == 0.0
        assert metadata["below_minimum"] == True
        
        # Above maximum
        score, metadata = self.engine.range_comparison(85, min_value=70, max_value=80)
        assert score == 0.0
        assert metadata["above_maximum"] == True
    
    def test_edge_cases(self):
        """Test edge cases like NaN and infinity."""
        # NaN values
        score, metadata = self.engine.direct_difference(float('nan'), 40)
        assert score == 0.0
        assert "NaN" in metadata["error"]
        
        # Infinite values
        score, metadata = self.engine.direct_difference(float('inf'), 40)
        assert score == 0.0
        assert "Infinite" in metadata["error"]


class TestIntegration:
    """Test the complete evaluation pipeline."""
    
    def setup_method(self):
        self.evaluator = NumericEvaluator(use_llm=False)
    
    def test_full_evaluation_pipeline(self):
        """Test complete evaluation from config to final score."""
        # Basic direct difference evaluation
        output = "The model achieved an accuracy of 87.3% on the test set."
        spec = {
            "expected": 0.873,
            "method": "direct_diff",
            "extraction_hint": "accuracy percentage",
            "preprocessing": "percentage_to_decimal"
        }
        
        result = self.evaluator(output, spec)
        assert result["score"] == 1.0  # Perfect match after preprocessing
        assert result["metadata"]["extracted_value"] == 0.873
        
        # Tolerance-based evaluation
        output = "The temperature reading is 23.5°C"
        spec = {
            "expected": 25.0,
            "method": "tolerance",
            "absolute_tolerance": 2.0,
            "extraction_hint": "temperature reading"
        }
        
        result = self.evaluator(output, spec)
        assert result["score"] == 1.0  # Within tolerance
    
    def test_error_handling(self):
        """Test graceful failure modes."""
        # Missing required fields
        result = self.evaluator("test", {"method": "direct_diff"})
        assert result["score"] == 0.0
        assert "Missing required field: expected" in result["metadata"]["error"]
        
        # Invalid method
        result = self.evaluator("test", {"expected": 42, "method": "invalid"})
        assert result["score"] == 0.0
        assert "Invalid method" in result["metadata"]["error"]
        
        # No extractable number
        result = self.evaluator("No numbers here", {"expected": 42, "method": "direct_diff"})
        assert result["score"] == 0.0
        assert "Failed to extract numeric value" in result["metadata"]["error"]
    
    def test_jsonpath_integration(self):
        """Test JSONPath extraction in full pipeline."""
        output = {"results": {"accuracy": 0.85, "f1_score": 0.92}}
        spec = {
            "expected": 0.85,
            "method": "direct_diff",
            "path": "$.results.accuracy"
        }
        
        result = self.evaluator(output, spec)
        assert result["score"] == 1.0
        assert result["metadata"]["extraction_details"]["extraction_method"] == "jsonpath"
    
    def test_extraction_priority(self):
        """Test that extraction method priority works correctly."""
        # Test 1: Path specified - should always use JSONPath
        output = {"value": 42}
        spec = {
            "expected": 42,
            "method": "direct_diff",
            "path": "$.value",
            "extraction_hint": "specific value"  # Should be ignored when path is present
        }
        result = self.evaluator(output, spec)
        assert result["metadata"]["extraction_details"]["extraction_method"] == "jsonpath"
        
        # Test 2: Specific extraction hint - should use LLM (when enabled)
        evaluator_with_llm = NumericEvaluator(use_llm=True)
        spec = {
            "expected": 85,
            "method": "direct_diff", 
            "extraction_hint": "the temperature reading"
        }
        # Note: This would use LLM if OpenAI API was available, fallback to regex otherwise
        
        # Test 3: Default hint should use regex first
        spec = {
            "expected": 42,
            "method": "direct_diff"
            # No extraction_hint or path - should use regex
        }
        output = "The answer is 42"
        result = self.evaluator(output, spec)
        assert result["metadata"]["extraction_details"]["extraction_method"] == "regex"


class TestRealisticModelOutputs:
    """Test with realistic LLM outputs containing numbers."""
    
    def setup_method(self):
        self.evaluator = NumericEvaluator(use_llm=False)
    
    def test_complex_text_outputs(self):
        """Test extraction from complex, realistic model outputs."""
        test_cases = [
            {
                "output": "After analyzing the data thoroughly, I calculated the accuracy to be 87.3%. This represents a significant improvement over the baseline model which achieved 82.1%.",
                "config": {
                    "expected": 0.873, 
                    "method": "direct_diff", 
                    "extraction_hint": "accuracy percentage",
                    "preprocessing": "percentage_to_decimal"
                },
                "expected_score": 1.0
            },
            {
                "output": "The final answer is approximately 42, though it could range from 40 to 45 depending on the specific parameters used.",
                "config": {
                    "expected": 43, 
                    "method": "tolerance", 
                    "absolute_tolerance": 2
                },
                "expected_score": 1.0
            },
            {
                "output": "Based on my calculations, the total cost including tax comes to $127.89. This breaks down as $115.00 for the item plus $12.89 in taxes.",
                "config": {
                    "expected": 127.50, 
                    "method": "tolerance", 
                    "absolute_tolerance": 1.0,
                    "extraction_hint": "total cost"
                },
                "expected_score": 1.0
            },
            {
                "output": "The temperature sensor reads 23.8°C, which is within the normal operating range of 20-25°C.",
                "config": {
                    "expected": 24.0, 
                    "method": "rmse",
                    "extraction_hint": "temperature reading"
                },
                "expected_score": 0.99  # Very close
            }
        ]
        
        for i, case in enumerate(test_cases):
            result = self.evaluator(case["output"], case["config"])
            assert result["score"] >= case["expected_score"] - 0.01, f"Test case {i} failed: got {result['score']}, expected >= {case['expected_score']}"


class TestPerformance:
    """Test performance characteristics."""
    
    def setup_method(self):
        self.evaluator = NumericEvaluator(use_llm=False)
    
    def test_extraction_speed(self):
        """Test that regex extraction is fast."""
        import time
        
        text = "The accuracy is 85.3% and the F1 score is 0.92"
        spec = {"expected": 0.853, "method": "direct_diff", "preprocessing": "percentage_to_decimal"}
        
        start_time = time.time()
        for _ in range(100):
            self.evaluator(text, spec)
        end_time = time.time()
        
        # Should complete 100 evaluations in well under 1 second
        assert (end_time - start_time) < 1.0
    
    def test_memory_usage(self):
        """Test memory usage with many evaluations."""
        import gc
        
        initial_objects = len(gc.get_objects())
        
        # Run many evaluations
        for i in range(1000):
            text = f"The result is {i}.5"
            spec = {"expected": i + 0.5, "method": "direct_diff"}
            self.evaluator(text, spec)
        
        gc.collect()
        final_objects = len(gc.get_objects())
        
        # Should not create too many persistent objects
        assert final_objects - initial_objects < 100


class TestDebugOutput:
    """Test debug information generation."""
    
    def test_debug_info_generation(self):
        """Test that debug info is comprehensive and readable."""
        evaluator = NumericEvaluator(use_llm=False)
        output = "The accuracy is 87.3%"
        spec = {
            "expected": 0.873,
            "method": "direct_diff",
            "extraction_hint": "accuracy percentage", 
            "preprocessing": "percentage_to_decimal"
        }
        
        result = evaluator(output, spec)
        debug_info = generate_debug_info(result)
        
        assert "Numeric Evaluation Debug Info" in debug_info
        assert "Final score: 1.000" in debug_info
        assert "Extracted value: 0.873" in debug_info
        assert "Expected value: 0.873" in debug_info


def test_all_components_integration():
    """Test that all components work together correctly."""
    evaluator = NumericEvaluator(use_llm=False)
    
    # Test a comprehensive evaluation scenario
    output = {
        "model_performance": {
            "accuracy": 0.923,
            "f1_score": 0.876,
            "precision": 0.901
        },
        "runtime_metrics": {
            "inference_time_ms": 245.7,
            "memory_usage_mb": 1024
        }
    }
    
    # Test multiple extractions from the same structured output
    test_cases = [
        {
            "spec": {
                "expected": 0.923,
                "method": "direct_diff",
                "path": "$.model_performance.accuracy"
            },
            "expected_score": 1.0
        },
        {
            "spec": {
                "expected": 250,
                "method": "tolerance",
                "absolute_tolerance": 10,
                "path": "$.runtime_metrics.inference_time_ms"
            },
            "expected_score": 1.0
        },
        {
            "spec": {
                "expected": 1000,
                "method": "tolerance",
                "relative_tolerance": 0.05,
                "path": "$.runtime_metrics.memory_usage_mb"
            },
            "expected_score": 1.0
        }
    ]
    
    for i, case in enumerate(test_cases):
        result = evaluator(output, case["spec"])
        assert result["score"] == case["expected_score"], f"Test case {i} failed: got {result['score']}, expected {case['expected_score']}"
        assert "extraction_details" in result["metadata"]
        assert result["metadata"]["extraction_details"]["extraction_method"] == "jsonpath"


@pytest.mark.parametrize("text,expected,description", [
    ("The result is 42.5", 42.5, "basic decimal"),
    ("Success rate: 85.3%", 0.853, "percentage"),
    ("Temperature: $123.45", 123.45, "currency"),
    ("Fraction: 3/4 of total", 0.75, "fraction"),
])
def test_parametrized_extraction(text, expected, description):
    """Parametrized test for various extraction formats."""
    extractor = NumberExtractor(use_llm=False)
    value, metadata = extractor.extract_regex(text)
    assert value is not None, f"Failed to extract from: {description}"
    assert abs(value - expected) < 0.001, f"Wrong value for {description}: got {value}, expected {expected}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])