"""
core/llm.py

Shared Gemini integration using the new google-genai SDK.
All model apps use these two functions — never import google.genai directly in apps.

Two functions:
    - generate_code()        → produces the Python script for the sandbox
    - generate_explanation() → produces a student-friendly explanation of results
"""

import logging
from google import genai
from django.conf import settings

logger = logging.getLogger(__name__)

# ─── Model type → sandbox instruction context ──────────────────────────────────
_SYSTEM_CONTEXT = {
    'REGRESSION': (
        "You are an AI assistant for a middle-school education platform teaching "
        "Linear Regression. Generate ONLY raw Python code (no markdown, no ```). "
        "The script must:\n"
        "- Read data from /app/data/input.csv using pandas\n"
        "- Train a LinearRegression model using scikit-learn\n"
        "- Save the trained model to /app/data/model.pkl using joblib\n"
        "- Save a matplotlib plot to /app/data/output.jpg\n"
        "- Print key metrics (R² score, predictions) to stdout\n"
        "Use clear variable names suitable for a 12-14 year old reading the code. "
        "Do not use plt.show(). Save the figure with plt.savefig('/app/data/output.jpg', bbox_inches='tight', dpi=100)."
    ),
    'CLASSIFICATION': (
        "You are an AI assistant for a middle-school education platform teaching "
        "Classification. Generate ONLY raw Python code (no markdown, no ```). "
        "The script must:\n"
        "- Read data from /app/data/input.csv using pandas\n"
        "- The last column is always the target label\n"
        "- Train a classifier (prefer DecisionTreeClassifier or GaussianNB from scikit-learn)\n"
        "- Save a confusion matrix plot to /app/data/output.jpg using matplotlib\n"
        "- Print accuracy, a classification report to stdout\n"
        "Use clear variable names suitable for a 12-14 year old. "
        "Do not use plt.show(). Save with plt.savefig('/app/data/output.jpg', bbox_inches='tight', dpi=100)."
    ),
    'NEURAL_NETWORK': (
        "You are an AI assistant for a middle-school education platform teaching "
        "Neural Networks. Generate ONLY raw Python code (no markdown, no ```). "
        "The script must:\n"
        "- Use sklearn.datasets.load_digits() as the data source (DO NOT read any CSV file)\n"
        "- Train an MLPClassifier from sklearn.neural_network\n"
        "- Apply the variant transformation described below to the data BEFORE training\n"
        "- Save a training loss curve plot to /app/data/output.jpg using matplotlib\n"
        "- Print accuracy and a short classification report to stdout\n"
        "Use clear variable names suitable for a 12-14 year old. "
        "Do not use plt.show(). Save with plt.savefig('/app/data/output.jpg', bbox_inches='tight', dpi=100)."
    ),
}

_EXPLANATION_SYSTEM = (
    "You are a friendly AI tutor explaining machine learning results to a middle-school "
    "student aged 12-14 who is learning about AI for the first time. "
    "Use simple language, relatable analogies, and avoid technical jargon. "
    "Be encouraging, curious, and concise (3-5 sentences max). "
    "Focus on what the result MEANS in the context of the scenario, not the code."
)


def _get_client() -> genai.Client:
    """Return a configured Gemini client instance."""
    return genai.Client(api_key=settings.GEMINI_API_KEY)


def generate_code(
    model_type: str,
    scenario_title: str,
    variant_label: str,
    student_prompt: str = '',
    data_columns: str = '',
) -> str:
    """
    Generate a Python script for the sandbox.

    Args:
        model_type:      'REGRESSION' | 'CLASSIFICATION' | 'NEURAL_NETWORK'
        scenario_title:  e.g. 'The Smart Greenhouse'
        variant_label:   e.g. 'Messy Sensors (broken data)'
        student_prompt:  Optional custom instruction from the student.
        data_columns:    Comma-separated list of columns in the CSV.

    Returns:
        Raw Python source code as a string.
    """
    system_ctx = _SYSTEM_CONTEXT.get(model_type, _SYSTEM_CONTEXT['REGRESSION'])

    user_message = (
        f"Scenario: {scenario_title}\n"
        f"Data variant: {variant_label}\n"
    )
    if data_columns:
        user_message += f"Available columns in input.csv: {data_columns}\n"
    if student_prompt:
        user_message += f"Student's additional instruction: {student_prompt}\n"

    full_prompt = f"{system_ctx}\n\n{user_message}"

    try:
        client = _get_client()
        response = client.models.generate_content(
            model='gemini-3.0-flash',
            contents=full_prompt,
        )
        code = response.text.strip()

        # Strip markdown fences if the model adds them anyway
        if code.startswith('```python'):
            code = code[9:]
        if code.startswith('```'):
            code = code[3:]
        if code.endswith('```'):
            code = code[:-3]

        return code.strip()
    except Exception as e:
        logger.exception(f'[llm] generate_code failed: {e}')
        raise


def generate_explanation(
    model_type: str,
    scenario_title: str,
    variant_label: str,
    stdout: str,
) -> str:
    """
    Generate a student-friendly explanation of the experiment output.

    Args:
        model_type:     'REGRESSION' | 'CLASSIFICATION' | 'NEURAL_NETWORK'
        scenario_title: e.g. 'The Smart Greenhouse'
        variant_label:  e.g. 'Messy Sensors'
        stdout:         The raw console output from the sandbox run.

    Returns:
        A short, friendly explanation string.
    """
    user_message = (
        f"Scenario: {scenario_title}\n"
        f"Data variant: {variant_label}\n"
        f"Model type: {model_type}\n"
        f"Console output from the experiment:\n{stdout[:1000]}\n\n"
        "Explain what these results mean to a 12-14 year old student."
    )

    full_prompt = f"{_EXPLANATION_SYSTEM}\n\n{user_message}"

    try:
        client = _get_client()
        response = client.models.generate_content(
            model='gemini-3.0-flash',
            contents=full_prompt,
        )
        return response.text.strip()
    except Exception as e:
        logger.exception(f'[llm] generate_explanation failed: {e}')
        return "The experiment ran successfully! Ask your teacher to help interpret the results."
