# flake8: noqa: E501
import yaml
from autoevals.llm import LLMClassifier
import json
from autoevals.llm import OpenAILLMClassifier, DEFAULT_MODEL
from braintrust_core.score import Score


class CustomClassifierBase(LLMClassifier):
    """
    Base class to create custom LLM classifiers by overriding the prompt.
    """
    prompt = ""  # Placeholder to be overridden in subclasses

    def __new__(cls):
        """
        Customize the instantiation of the LLMClassifier by loading the prompt from the subclass.
        """
        kwargs = {}
        cls_name = cls.__name__  # Derive class name for identification
        cls._SPEC_FILE_CONTENTS = cls.prompt
        spec = yaml.safe_load(cls._SPEC_FILE_CONTENTS)
        return LLMClassifier(cls_name, spec['prompt'], spec['choice_scores'], **kwargs)


class ChecklistClassifier(CustomClassifierBase):
    """
    Evaluate whether an LLM-generated answer meets all criteria defined in a checklist.

    Inherits from CustomClassifier to utilize YAML-defined prompts and scoring.
    """
    prompt = """
prompt: |-
  You are assessing a submitted answer against a checklist on a given question. Here is the data:
  [BEGIN DATA]
  ************
  [Question]: {{{input}}}
  ************
  [Checklist]: {{{expected}}}
  ************
  [Submission]: {{{output}}}
  ************
  [END DATA]

  Assess the submitted answer against the checklist. Ignore any differences in style, grammar, or punctuation.
  Determine which case applies. Answer by selecting one of the following options:
  (A) The submitted answer passes some of the checklists.
  (B) The submitted answer passes most of the checklists.
  (C) The submitted answer passes all the checklists.
  (D) The submitted answer does not pass any of the checklists.
choice_scores:
  "A": 0.4
  "B": 0.6
  "C": 1
  "D": 0
"""


class ChecklistClassifier2(OpenAILLMClassifier):
    """
    Evaluate each item in a checklist individually with detailed scoring and rationale.

    Uses OpenAI's function calling to get structured feedback on each checklist 
    criterion.
    """

    def __init__(self, model=DEFAULT_MODEL, context="", **kwargs):
        # Define the conversation messages
        messages = [
            {
                "role": "system",
                "content": """You are an expert evaluator assessing answers against specific criteria. 
For each checklist item, carefully evaluate if the submission meets the criterion and provide a detailed rationale.
Return criterion verbatim, exactly as it is in the checklist."""
            },
            {
                "role": "user",
                "content": """Please evaluate this submission against each checklist item.

{{context}}

Question: {{input}}

Checklist:
{{expected}}

Submission: {{output}}

Evaluate each checklist item individually, providing a score and detailed rationale."""
            }
        ]

        # Schema for evaluating each checklist item
        checklist_eval_schema = {
            "type": "object",
            "properties": {
                "evaluations": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "criterion": {
                                "type": "string",
                                "description": "The checklist item being evaluated",
                            },
                            "score": {
                                "type": "number",
                                "minimum": 0,
                                "maximum": 1,
                                "description": "Score between 0 and 1",
                            },
                            "rationale": {
                                "type": "string",
                                "description": "Detailed explanation for the score",
                            },
                        },
                        "required": ["criterion", "score", "rationale"],
                    },
                },
                "overall_score": {
                    "type": "number",
                    "description": "Average score across all criteria",
                },
            },
            "required": ["evaluations", "overall_score"],
        }

        # Define the evaluation function for OpenAI's function calling
        tools = [{
            "type": "function",
            "function": {
                "name": "evaluate_checklist",
                "description": "Evaluate each checklist item and provide detailed scoring",
                "parameters": checklist_eval_schema
            }
        }]

        super().__init__(
            name="ChecklistClassifier2",
            messages=messages,
            model=model,
            classification_tools=tools,
            choice_scores={"evaluate_checklist": 1},  # Required by parent class
            render_args={"context": context},
            **kwargs
        )

    def _process_response(self, resp):
        """
        Process the function call response and calculate the final score.
        """
        if "tool_calls" not in resp:
            raise ValueError("No tool call found in response")

        tool_call = resp["tool_calls"][0]
        if tool_call["function"]["name"] != "evaluate_checklist":
            raise ValueError(f"Unexpected tool call ({tool_call['function']['name']}) found in response")

        # Parse the arguments returned by the function call
        result = json.loads(tool_call["function"]["arguments"])
        evaluations = result["evaluations"]

        def _clean_string(s):
            """Remove all spaces and special characters from a string."""
            return ''.join(c.lower() for c in s.replace("\\n", "").replace("\n", "").replace("\\", "") if c.isalnum())

        if not isinstance(self._original_checklist, str):
            # Calculate overall score based on individual criteria
            total_score = 0
            for eval in evaluations:
                score = eval["score"]
                # Find matching checklist item to check for min_score
                for item in self._original_checklist:
                    if isinstance(item, dict):
                        criterion_text = item["text"]
                        if _clean_string(criterion_text) == _clean_string(eval["criterion"]):
                            min_score = item.get('min_score')
                            if min_score is not None and score >= min_score:
                                score = 1.0
                            break

                total_score += score

            overall_score = total_score / len(evaluations)
        else:
            # If the checklist is a string, use the overall score directly
            overall_score = result["overall_score"]

        return Score(
            name=self.name,
            score=overall_score,
            metadata={
                "evaluations": evaluations,
                "overall_score": overall_score
            }
        )

    def _build_args(self, output, expected, **kwargs):
        """
        Build the arguments for the LLM classifier, including parsing YAML if necessary.
        """
        # Store original checklist for score processing
        self._original_checklist = expected

        # Parse the YAML checklist if it's provided as a string
        if isinstance(expected, str):
            try:
                expected = yaml.safe_load(expected)
            except yaml.YAMLError as e:
                raise ValueError(f"Invalid YAML checklist: {e}")

        # Convert list to YAML string for template rendering
        if isinstance(expected, list):
            simplified_checklist = []
            for item in expected:
                if isinstance(item, dict):
                    criterion_text = item["text"]
                    simplified_checklist.append(criterion_text)
                else:
                    simplified_checklist.append(item)
            expected = yaml.dump(simplified_checklist)

        args = super()._build_args(output=output, expected=expected, **kwargs)
        args["tool_choice"] = {"type": "function", "function": {"name": "evaluate_checklist"}}
        return args
