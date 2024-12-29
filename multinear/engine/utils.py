from openai import OpenAI
from typing import List


BASE_REPHRASE_PROMPT = """Rephrase the following text in a different way
while fully preserving its meaning. Preserve the language and style."""

VARIATIONS_EXTENSION = """
IMPORTANT: Your rephrasing must be different from all previous variations listed below.

Previous variations:
{previous_variations}"""

FINAL_INPUT_TEMPLATE = """

Provide a unique rephrasing of this text:
{input}"""


def rephrase_input(input: str, previous_variations: List[str] = None) -> str:
    """
    Rephrase the input using OpenAI's API to generate variations
    for repeated tasks.

    Args:
        input: The original input to be rephrased
        previous_variations: List of previously generated variations for this input

    Returns:
        Rephrased version of the input
    """
    prompt = BASE_REPHRASE_PROMPT

    if previous_variations:
        variations_text = "\n".join(
            f"{i+1}. {var}" for i, var in enumerate(previous_variations)
        )
        prompt += VARIATIONS_EXTENSION.format(previous_variations=variations_text)

    prompt += FINAL_INPUT_TEMPLATE.format(input=input)

    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": input}
        ],
        temperature=0.7,
    )

    return response.choices[0].message.content.strip()
