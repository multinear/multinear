import json
import yaml
from autoevals.llm import OpenAILLMClassifier, DEFAULT_MODEL
from braintrust_core.score import Score


class WeightedScoreEvaluator(OpenAILLMClassifier):
    """
    Evaluate a submission against multiple weighted criteria using an LLM.

    Uses OpenAI's function calling to get structured feedback on each criterion,
    calculates a weighted score based on predefined weights, and returns a score
    object compatible with other evaluators.
    """

    def __init__(self, model=DEFAULT_MODEL, context="", **kwargs):
        # Define the conversation messages
        messages = [
            {
                "role": "system",
                "content": """You are an expert evaluator assessing submissions against several weighted criteria.
For each criterion, carefully evaluate if the submission meets it based on the provided context and input/output.
Provide a score between 0 (fails to meet) and 1 (fully meets) for each criterion.
Include a detailed rationale for each score.
Return the original criterion ID and text verbatim.
"""
            },
            {
                "role": "user",
                "content": """Please evaluate the submission against each weighted criterion listed below.

**Context:**
{{context}}

**Input:**
{{input}}

**Submission:**
{{output}}

**Weighted Criteria:**
{{expected}}

Evaluate each criterion individually, providing its ID, a score (0-1), and a detailed rationale.
"""
            }
        ]

        # Schema for evaluating each weighted criterion
        weighted_score_eval_schema = {
            "type": "object",
            "properties": {
                "evaluations": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {
                                "type": "string",
                                "description": "The unique identifier for the criterion being evaluated.",
                            },
                            "criterion": {
                                "type": "string",
                                "description": "The criterion text being evaluated (verbatim).",
                            },
                            "score": {
                                "type": "number",
                                "minimum": 0,
                                "maximum": 1,
                                "description": "Score between 0 and 1 for this criterion.",
                            },
                            "rationale": {
                                "type": "string",
                                "description": "Detailed explanation for the score.",
                            },
                        },
                        "required": ["id", "criterion", "score", "rationale"],
                    },
                },
            },
            "required": ["evaluations"],
        }

        # Define the evaluation function for OpenAI's function calling
        tools = [{
            "type": "function",
            "function": {
                "name": "evaluate_weighted_criteria",
                "description": "Evaluate each weighted criterion and provide detailed scoring and rationale.",
                "parameters": weighted_score_eval_schema
            }
        }]

        super().__init__(
            name="WeightedScoreEvaluator",
            messages=messages,
            model=model,
            classification_tools=tools,
            choice_scores={"evaluate_weighted_criteria": 1},  # Dummy value required by parent
            render_args={"context": context},
            **kwargs
        )
        self._original_weighted_scores = [] # Initialize to ensure attribute exists

    def _build_args(self, output, expected, **kwargs):
        """
        Build the arguments for the LLM classifier.
        'expected' is the list of dicts: [{'id': ..., 'eval': ..., 'weight': ...}]
        """
        if not isinstance(expected, list):
             raise ValueError("Weighted score 'expected' argument must be a list of criteria definitions.")

        # Store original weighted scores list for score processing
        self._original_weighted_scores = expected

        # Format the criteria list into a string for the prompt template
        formatted_expected_string = ""
        for item in expected:
             formatted_expected_string += f"- ID: {item.get('id', 'N/A')}\\n  Eval: {item.get('eval', 'No evaluation text provided.')}\\n"

        # Use the formatted string as 'expected' for rendering
        args = super()._build_args(output=output, expected=formatted_expected_string.strip(), **kwargs)

        # Force the specific tool call
        args["tool_choice"] = {"type": "function", "function": {"name": "evaluate_weighted_criteria"}}
        return args

    def _process_response(self, resp):
        """
        Process the function call response, calculate the weighted score,
        and format metadata.
        """
        if "tool_calls" not in resp:
            raise ValueError("No tool call found in LLM response for WeightedScoreEvaluator")

        tool_call = resp["tool_calls"][0]
        if tool_call["function"]["name"] != "evaluate_weighted_criteria":
            raise ValueError(f"Unexpected tool call ({tool_call['function']['name']}) found in response")

        # Parse the arguments returned by the function call
        try:
            result = json.loads(tool_call["function"]["arguments"])
            llm_evaluations = result["evaluations"]
        except (json.JSONDecodeError, KeyError) as e:
             raise ValueError(f"Failed to parse LLM function arguments: {e}. Raw args: {tool_call['function']['arguments']}")

        # Create a lookup map from the original scores for quick access by ID
        original_map = {item['id']: item for item in self._original_weighted_scores}

        total_weighted_score = 0.0
        processed_evaluations = []
        total_weight_sum = sum(item.get('weight', 0) for item in self._original_weighted_scores) # For normalization if weights don't sum to 1

        if not llm_evaluations:
             print("Warning: LLM returned empty evaluations list.")
             # Handle empty list case, perhaps return score 0 or raise error depending on desired behaviour
             return Score(name=self.name, score=0.0, metadata={"evaluations": [], "overall_score": 0.0, "evaluator_type": "weighted_score", "warning": "LLM returned no evaluations"})

        for llm_eval in llm_evaluations:
            eval_id = llm_eval.get('id')
            if not eval_id:
                print(f"Warning: LLM evaluation missing 'id'. Skipping: {llm_eval}")
                continue # Skip evaluation if ID is missing

            original_item = original_map.get(eval_id)
            if not original_item:
                print(f"Warning: LLM returned evaluation for unknown ID '{eval_id}'. Skipping.")
                continue # Skip if the ID doesn't match any original criteria

            weight = original_item.get('weight', 0) # Default weight to 0 if missing
            llm_score = llm_eval.get('score', 0) # Default score to 0 if missing

            # Ensure score is within bounds
            llm_score = max(0.0, min(1.0, llm_score))

            total_weighted_score += llm_score * weight

            # Append detailed info for metadata, matching ChecklistClassifier2 format where possible
            processed_evaluations.append({
                "id": eval_id,
                "criterion": llm_eval.get('criterion', original_item.get('eval')), # Use LLM criterion, fallback to original eval text
                "score": llm_score,
                "rationale": llm_eval.get('rationale', 'No rationale provided.'),
                "weight": weight,
            })

        # Calculate final score (normalize in case weights don't sum to 1, though they should)
        final_score = total_weighted_score / total_weight_sum if total_weight_sum > 0 else 0.0
        final_score = max(0.0, min(1.0, final_score)) # Ensure final score is 0-1

        return Score(
            name=self.name,
            score=final_score,
            metadata={
                "evaluations": processed_evaluations,
                "overall_score": final_score,
                "evaluator_type": "weighted_score" # Add type for later distinction
            }
        ) 