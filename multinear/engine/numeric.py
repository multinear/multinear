import re
import json
import math
from typing import Any, Dict, List, Optional, Tuple, Union
from jsonpath_ng import parse
from autoevals.llm import OpenAILLMClassifier, DEFAULT_MODEL
from braintrust_core.score import Score


# Regex patterns for number extraction (order matters - most specific first)
NUMERIC_PATTERNS = [
    r'-?\d+\.?\d*e[+-]?\d+',       # Scientific notation: 1.23e-4
    r'-?\d+\.?\d*%',               # Percentages: 85.5%
    r'\$-?\d+\.?\d*',              # Currency: $123.45
    r'-?\d+/\d+',                  # Fractions: 3/4
    r'-?\d{1,3}(?:,\d{3})*\.?\d*',  # With commas: 1,234.56
    r'-?\d+\.?\d*',                # Basic: 123.45
]

# Compile patterns for performance
COMPILED_PATTERNS = [re.compile(pattern) for pattern in NUMERIC_PATTERNS]


class NumberExtractor:
    """Handles extraction of numeric values from text using multiple strategies."""
    
    def __init__(self, use_llm: bool = True, model: str = DEFAULT_MODEL):
        self.use_llm = use_llm
        self.model = model
    
    def extract_regex(self, text: str, extraction_hint: Optional[str] = None, preprocessing: Optional[str] = None) -> Tuple[Optional[float], Dict[str, Any]]:
        """Extract number using regex patterns."""
        if not text or not isinstance(text, str):
            return None, {"error": "Empty or invalid input text"}
        
        # Apply preprocessing if specified
        original_text = text
        if preprocessing:
            text = self.preprocess_number(text, preprocessing)
        
        all_matches = []
        
        # Try each pattern in order of specificity
        for i, pattern in enumerate(COMPILED_PATTERNS):
            matches = pattern.findall(text)
            for match in matches:
                try:
                    # Find position of match in text
                    position = text.find(match)
                    parsed_value = self._parse_number(match)
                    # Only add valid parsed values (parsed_value can be None or 0, but not for invalid division)
                    if parsed_value is not None:
                        all_matches.append({
                            "value": parsed_value,
                            "raw_match": match,
                            "pattern_index": i,
                            "pattern": NUMERIC_PATTERNS[i],
                            "position": position
                        })
                except (ValueError, ZeroDivisionError):
                    continue
        
        if not all_matches:
            return None, {"error": "No numeric values found", "text": text[:100], "original_text": original_text[:100]}
        
        # Return the first match (most specific pattern)
        best_match = all_matches[0]
        metadata = {
            "extraction_method": "regex",
            "pattern_matched": best_match["pattern"],
            "match_position": best_match["position"],
            "raw_match": best_match["raw_match"],
            "confidence": "high",
            "total_matches_found": len(all_matches),
            "preprocessing_applied": preprocessing
        }
        
        if len(all_matches) > 1:
            metadata["warnings"] = ["Multiple numbers found, used first match"]
        
        return best_match["value"], metadata
    
    def extract_llm(self, text: str, extraction_hint: str = "the numeric value") -> Tuple[Optional[float], Dict[str, Any]]:
        """Extract number using LLM assistance."""
        if not self.use_llm:
            return None, {"error": "LLM extraction disabled"}
        
        prompt = f"""Extract the numeric value that represents {extraction_hint} from the following text.

Text: {text}

Requirements:
- Return only the numeric value
- If multiple numbers exist, return the one that best matches: {extraction_hint}
- If no relevant number exists, return "NOT_FOUND"
- Convert percentages to decimals (e.g., 85% → 0.85)
- Handle fractions as decimals (e.g., 3/4 → 0.75)

Extracted value:"""
        
        try:
            # Create a simple LLM classifier for extraction
            from openai import OpenAI
            client = OpenAI()
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50,
                temperature=0
            )
            
            result = response.choices[0].message.content.strip()
            
            if result == "NOT_FOUND" or not result:
                return None, {"error": "LLM could not find numeric value", "llm_response": result}
            
            # Try to parse the LLM response
            try:
                value = float(result)
                return value, {
                    "extraction_method": "llm",
                    "llm_response": result,
                    "confidence": "medium"
                }
            except ValueError:
                return None, {"error": "LLM returned non-numeric value", "llm_response": result}
                
        except Exception as e:
            return None, {"error": f"LLM extraction failed: {str(e)}"}
    
    def extract_jsonpath(self, data: Any, path: str) -> Tuple[Optional[float], Dict[str, Any]]:
        """Extract number using JSONPath from structured data."""
        try:
            # Parse data if it's a string
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except json.JSONDecodeError:
                    return None, {"error": "Invalid JSON data"}
            
            jsonpath_expr = parse(path)
            matches = jsonpath_expr.find(data)
            
            if not matches:
                return None, {"error": f"JSONPath {path} not found", "data_type": type(data).__name__}
            
            value = matches[0].value
            
            # Convert to float if possible
            if isinstance(value, (int, float)):
                return float(value), {
                    "extraction_method": "jsonpath",
                    "path": path,
                    "confidence": "high"
                }
            elif isinstance(value, str):
                # Try to parse string as number
                parsed, metadata = self.extract_regex(value)
                if parsed is not None:
                    metadata["extraction_method"] = "jsonpath+regex"
                    metadata["path"] = path
                    return parsed, metadata
            
            return None, {"error": f"JSONPath value is not numeric: {type(value).__name__}"}
            
        except Exception as e:
            return None, {"error": f"JSONPath extraction failed: {str(e)}"}
    
    def _parse_number(self, match: str) -> Optional[float]:
        """Parse a matched string into a float with comprehensive format support."""
        if not match:
            return None
        
        # Clean up the match
        match = match.strip()
        
        # Handle percentages
        if match.endswith('%'):
            try:
                return float(match[:-1]) / 100.0
            except ValueError:
                return None
        
        # Handle currency symbols (multiple currencies)
        currency_symbols = ['$', '€', '£', '¥', '₹', '₽']
        for symbol in currency_symbols:
            if match.startswith(symbol):
                try:
                    return float(match[1:].replace(',', ''))
                except ValueError:
                    return None
        
        # Handle fractions
        if '/' in match and not '.' in match and not 'e' in match.lower():
            parts = match.split('/')
            if len(parts) == 2:
                try:
                    numerator = float(parts[0].strip())
                    denominator = float(parts[1].strip())
                    if denominator == 0:
                        return None
                    return numerator / denominator
                except (ValueError, ZeroDivisionError):
                    return None
        
        # Handle numbers with commas (thousands separators)
        if ',' in match:
            # Validate comma placement (every 3 digits from right)
            parts = match.split('.')
            integer_part = parts[0]
            if integer_part.count(',') > 0:
                # Remove commas and validate
                clean_integer = integer_part.replace(',', '')
                if clean_integer.isdigit() or (clean_integer.startswith('-') and clean_integer[1:].isdigit()):
                    match = clean_integer + ('.' + parts[1] if len(parts) > 1 else '')
                else:
                    return None
        
        # Handle scientific notation and regular numbers
        try:
            return float(match)
        except ValueError:
            return None
    
    def preprocess_number(self, text: str, preprocessing: str) -> str:
        """Apply preprocessing transformations to text before extraction."""
        if preprocessing == "percentage_to_decimal":
            # Convert percentage mentions to decimal format
            import re
            # Find percentages and convert them
            percentage_pattern = r'(\d+\.?\d*)%'
            def convert_percentage(match):
                value = float(match.group(1))
                return str(value / 100.0)
            return re.sub(percentage_pattern, convert_percentage, text)
        
        elif preprocessing == "fraction_to_decimal":
            # Convert fractions to decimal format
            import re
            fraction_pattern = r'(\d+)/(\d+)'
            def convert_fraction(match):
                numerator = float(match.group(1))
                denominator = float(match.group(2))
                if denominator == 0:
                    return match.group(0)  # Return original if division by zero
                return str(numerator / denominator)
            return re.sub(fraction_pattern, convert_fraction, text)
        
        elif preprocessing == "remove_currency":
            # Remove currency symbols
            import re
            currency_pattern = r'[\$€£¥₹₽]'
            return re.sub(currency_pattern, '', text)
        
        elif preprocessing == "normalize_separators":
            # Normalize thousand separators
            import re
            # Replace European-style separators (space/period as thousand, comma as decimal)
            # This is a simplified approach - in practice, you'd need more context
            return text.replace(' ', '').replace('.', '', text.count('.') - 1 if text.count('.') > 1 else 0)
        
        return text


class ComparisonEngine:
    """Handles different comparison methods for numeric evaluation."""
    
    @staticmethod
    def direct_difference(actual: float, expected: float) -> Tuple[float, Dict[str, Any]]:
        """Scale absolute difference by expected value magnitude."""
        if math.isnan(actual) or math.isnan(expected):
            return 0.0, {"error": "NaN values in comparison"}
        
        if math.isinf(actual) or math.isinf(expected):
            return 0.0, {"error": "Infinite values in comparison"}
        
        if expected == 0:
            score = 1.0 if actual == 0 else max(0, 1 - abs(actual))
            return score, {
                "comparison_method": "direct_diff",
                "scaling_factor": 1.0,
                "raw_difference": abs(actual - expected),
                "zero_expected_handling": True
            }
        
        error_ratio = abs(actual - expected) / abs(expected)
        score = max(0, 1 - error_ratio)
        
        return score, {
            "comparison_method": "direct_diff",
            "scaling_factor": abs(expected),
            "raw_difference": abs(actual - expected),
            "error_ratio": error_ratio
        }
    
    @staticmethod
    def mse_comparison(actual: float, expected: float) -> Tuple[float, Dict[str, Any]]:
        """Mean Squared Error scaled by expected value."""
        if math.isnan(actual) or math.isnan(expected):
            return 0.0, {"error": "NaN values in comparison"}
        
        if math.isinf(actual) or math.isinf(expected):
            return 0.0, {"error": "Infinite values in comparison"}
        
        mse = (actual - expected) ** 2
        scaling_factor = max(abs(expected), 1.0)
        normalized_mse = mse / (scaling_factor ** 2)
        score = max(0, 1 - normalized_mse)
        
        return score, {
            "comparison_method": "mse",
            "mse": mse,
            "scaling_factor": scaling_factor,
            "normalized_mse": normalized_mse
        }
    
    @staticmethod
    def rmse_comparison(actual: float, expected: float) -> Tuple[float, Dict[str, Any]]:
        """Root Mean Squared Error scaled by expected value."""
        if math.isnan(actual) or math.isnan(expected):
            return 0.0, {"error": "NaN values in comparison"}
        
        if math.isinf(actual) or math.isinf(expected):
            return 0.0, {"error": "Infinite values in comparison"}
        
        rmse = abs(actual - expected)
        scaling_factor = max(abs(expected), 1.0)
        normalized_rmse = rmse / scaling_factor
        score = max(0, 1 - normalized_rmse)
        
        return score, {
            "comparison_method": "rmse",
            "rmse": rmse,
            "scaling_factor": scaling_factor,
            "normalized_rmse": normalized_rmse
        }
    
    @staticmethod
    def tolerance_comparison(actual: float, expected: float, 
                           absolute_tolerance: Optional[float] = None,
                           relative_tolerance: Optional[float] = None) -> Tuple[float, Dict[str, Any]]:
        """Binary pass/fail within tolerance thresholds."""
        if math.isnan(actual) or math.isnan(expected):
            return 0.0, {"error": "NaN values in comparison"}
        
        if math.isinf(actual) or math.isinf(expected):
            return 0.0, {"error": "Infinite values in comparison"}
        
        metadata = {
            "comparison_method": "tolerance",
            "absolute_tolerance": absolute_tolerance,
            "relative_tolerance": relative_tolerance,
            "absolute_difference": abs(actual - expected)
        }
        
        # Check absolute tolerance
        if absolute_tolerance is not None:
            if abs(actual - expected) <= absolute_tolerance:
                metadata["passed_absolute"] = True
                return 1.0, metadata
            else:
                metadata["passed_absolute"] = False
        
        # Check relative tolerance
        if relative_tolerance is not None and expected != 0:
            relative_error = abs(actual - expected) / abs(expected)
            metadata["relative_error"] = relative_error
            if relative_error <= relative_tolerance:
                metadata["passed_relative"] = True
                return 1.0, metadata
            else:
                metadata["passed_relative"] = False
        
        return 0.0, metadata
    
    @staticmethod
    def range_comparison(actual: float, min_value: Optional[float] = None, 
                        max_value: Optional[float] = None) -> Tuple[float, Dict[str, Any]]:
        """Validate that the actual value falls within the specified range."""
        if math.isnan(actual):
            return 0.0, {"error": "NaN value in range comparison"}
        
        if math.isinf(actual):
            return 0.0, {"error": "Infinite value in range comparison"}
        
        metadata = {
            "comparison_method": "range",
            "min_value": min_value,
            "max_value": max_value,
            "actual_value": actual
        }
        
        if min_value is not None and actual < min_value:
            metadata["below_minimum"] = True
            return 0.0, metadata
        
        if max_value is not None and actual > max_value:
            metadata["above_maximum"] = True
            return 0.0, metadata
        
        metadata["within_range"] = True
        return 1.0, metadata


class NumericEvaluator:
    """Main evaluator for numeric comparisons with multiple extraction and comparison methods."""
    
    def __init__(self, use_llm: bool = True, model: str = DEFAULT_MODEL):
        self.extractor = NumberExtractor(use_llm=use_llm, model=model)
        self.comparison_engine = ComparisonEngine()
    
    def __call__(self, output: Any, spec: Dict[str, Any], input: Any = None) -> Dict[str, Any]:
        """Evaluate numeric output against specification."""
        # Validate configuration
        validation_result = self._validate_config(spec)
        if not validation_result[0]:
            return {
                'score': 0.0,
                'metadata': {'error': validation_result[1]}
            }
        
        expected = spec['expected']
        method = spec['method']
        extraction_hint = spec.get('extraction_hint', 'the numeric value')
        
        # Extract the numeric value
        extracted_value, extraction_metadata = self._extract_value(output, spec, extraction_hint)
        
        if extracted_value is None:
            return {
                'score': 0.0,
                'metadata': {
                    'error': 'Failed to extract numeric value',
                    'extraction_details': extraction_metadata,
                    'expected_value': expected,
                    'method': method
                }
            }
        
        # Perform comparison
        score, comparison_metadata = self._compare_values(extracted_value, expected, spec)
        
        # Combine metadata
        final_metadata = {
            'extracted_value': extracted_value,
            'expected_value': expected,
            'extraction_details': extraction_metadata,
            'comparison_details': comparison_metadata
        }
        
        # Add any warnings or errors
        if 'warnings' in extraction_metadata:
            final_metadata['warnings'] = extraction_metadata['warnings']
        
        if 'error' in comparison_metadata:
            final_metadata['error'] = comparison_metadata['error']
        
        return {
            'score': score,
            'metadata': final_metadata
        }
    
    def _extract_value(self, output: Any, spec: Dict[str, Any], extraction_hint: str) -> Tuple[Optional[float], Dict[str, Any]]:
        """Extract numeric value using the appropriate method."""
        # Always use JSONPath if path is specified
        if 'path' in spec:
            value, metadata = self.extractor.extract_jsonpath(output, spec['path'])
            # Return regardless of success - path was explicitly specified
            return value, metadata
        
        # Convert output to string for text-based extraction
        if not isinstance(output, str):
            try:
                text = str(output)
            except:
                return None, {"error": "Could not convert output to string"}
        else:
            text = output
        
        # Get preprocessing option
        preprocessing = spec.get('preprocessing')
        
        # Always use LLM extraction if extraction_hint is provided and LLM is enabled
        if extraction_hint and extraction_hint != "the numeric value" and self.extractor.use_llm:
            # Apply preprocessing before LLM extraction
            processed_text = text
            if preprocessing:
                processed_text = self.extractor.preprocess_number(text, preprocessing)
            
            value, llm_metadata = self.extractor.extract_llm(processed_text, extraction_hint)
            if value is not None:
                return value, llm_metadata
            
            # If LLM fails with specific hint, try regex as fallback
            value, regex_metadata = self.extractor.extract_regex(text, extraction_hint, preprocessing)
            if value is not None:
                # Mark that we fell back to regex
                regex_metadata['llm_extraction_failed'] = llm_metadata.get('error', 'LLM extraction failed')
                return value, regex_metadata
            
            # Both failed, return LLM error as primary
            return None, llm_metadata
        
        # Use regex extraction as default (no specific hint or LLM disabled)
        value, metadata = self.extractor.extract_regex(text, extraction_hint, preprocessing)
        if value is not None:
            return value, metadata
        
        # Fallback to LLM extraction if enabled (even without specific hint)
        if self.extractor.use_llm:
            # Apply preprocessing before LLM extraction too
            processed_text = text
            if preprocessing:
                processed_text = self.extractor.preprocess_number(text, preprocessing)
            
            value, llm_metadata = self.extractor.extract_llm(processed_text, extraction_hint or "the numeric value")
            if value is not None:
                return value, llm_metadata
            
            # Combine error messages from both attempts
            metadata['llm_fallback_error'] = llm_metadata.get('error', 'Unknown LLM error')
        
        return None, metadata
    
    def _compare_values(self, actual: float, expected: float, spec: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """Compare actual and expected values using the specified method."""
        method = spec['method']
        
        if method == 'direct_diff':
            return self.comparison_engine.direct_difference(actual, expected)
        elif method == 'mse':
            return self.comparison_engine.mse_comparison(actual, expected)
        elif method == 'rmse':
            return self.comparison_engine.rmse_comparison(actual, expected)
        elif method == 'tolerance':
            return self.comparison_engine.tolerance_comparison(
                actual, expected,
                spec.get('absolute_tolerance'),
                spec.get('relative_tolerance')
            )
        elif method == 'range':
            return self.comparison_engine.range_comparison(
                actual, spec.get('min_value'), spec.get('max_value')
            )
        else:
            return 0.0, {'error': f'Unknown comparison method: {method}'}
    
    def _validate_config(self, spec: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate numeric evaluation configuration."""
        required_fields = ['expected', 'method']
        for field in required_fields:
            if field not in spec:
                return False, f"Missing required field: {field}"
        
        if not isinstance(spec['expected'], (int, float)):
            return False, "Expected value must be numeric"
        
        valid_methods = ['direct_diff', 'mse', 'rmse', 'tolerance', 'range']
        if spec['method'] not in valid_methods:
            return False, f"Invalid method. Must be one of: {valid_methods}"
        
        # Method-specific validation
        if spec['method'] == 'tolerance':
            if 'absolute_tolerance' not in spec and 'relative_tolerance' not in spec:
                return False, "Tolerance method requires either absolute_tolerance or relative_tolerance"
        
        if spec['method'] == 'range':
            if 'min_value' not in spec and 'max_value' not in spec:
                return False, "Range method requires either min_value or max_value"
        
        return True, "Valid configuration"


def generate_debug_info(result: Dict[str, Any]) -> str:
    """Generate human-readable debug information."""
    metadata = result.get('metadata', {})
    extraction_details = metadata.get('extraction_details', {})
    comparison_details = metadata.get('comparison_details', {})
    
    return f"""
Numeric Evaluation Debug Info:
==============================
Final score: {result.get('score', 'N/A'):.3f}
Extracted value: {metadata.get('extracted_value', 'N/A')}
Expected value: {metadata.get('expected_value', 'N/A')}

Extraction details:
- Method used: {extraction_details.get('extraction_method', 'N/A')}
- Pattern matched: {extraction_details.get('pattern_matched', 'N/A')}
- Confidence: {extraction_details.get('confidence', 'N/A')}

Comparison details:
- Method: {comparison_details.get('comparison_method', 'N/A')}
- Raw difference: {comparison_details.get('raw_difference', 'N/A')}
- Scaling factor: {comparison_details.get('scaling_factor', 'N/A')}

Errors: {metadata.get('error', 'None')}
Warnings: {metadata.get('warnings', 'None')}
"""