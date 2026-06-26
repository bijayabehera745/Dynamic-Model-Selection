"""
core/llm.py

Shared Gemini integration using the new google-genai SDK.
All model apps use these two functions — never import google.genai directly in apps.

Two functions:
    - generate_code()        → produces the Python script for the sandbox
    - generate_explanation() → produces a student-friendly explanation of results
"""

import logging
import openai
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
    "You MUST return a JSON object with exactly these 5 string keys: "
    "\"chefs_choice\", \"healthy_snacks\", \"guessing_game\", \"tricky_test\", and \"fix_it_mode\". "
    "Each key should contain a short (2-3 sentences max) engaging explanation for the following concepts:\n"
    "- chefs_choice: Why did we pick this specific robot brain? (Model selection)\n"
    "- healthy_snacks: What did we just feed our AI? (Data quality)\n"
    "- guessing_game: Is our AI a Genius, a Guesser, or just Confused? (Model Evaluation/Confidence based on stdout)\n"
    "- tricky_test: Can you trick the AI with a curveball? (Mention they can make their own tricky data in the Data Lab!)\n"
    "- fix_it_mode: How can we make this AI even smarter next time?\n"
    "Respond ONLY with valid JSON. Do not include markdown code blocks."
)


def _get_client() -> openai.OpenAI:
    """Return a configured OpenAI client instance pointing to OpenRouter."""
    return openai.OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=settings.OPENROUTER_API_KEY,
    )


def generate_code(
    model_type: str,
    scenario_title: str,
    variant_label: str,
    student_prompt: str = '',
    data_columns: str = '',
) -> str:
    """
    Generate a Python script for the sandbox.
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

    try:
        client = _get_client()
        response = client.chat.completions.create(
            model='openai/gpt-4o-mini',
            messages=[
                {"role": "system", "content": system_ctx},
                {"role": "user", "content": user_message}
            ]
        )
        code = response.choices[0].message.content.strip()

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
    Generate a student-friendly explanation of the experiment output as JSON.
    """
    user_message = (
        f"Scenario: {scenario_title}\n"
        f"Data variant: {variant_label}\n"
        f"Model type: {model_type}\n"
        f"Console output from the experiment:\n{stdout[:1000]}\n\n"
        "Explain what these results mean, strictly returning JSON."
    )

    try:
        client = _get_client()
        response = client.chat.completions.create(
            model='openai/gpt-4o-mini',
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": _EXPLANATION_SYSTEM},
                {"role": "user", "content": user_message}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.exception(f'[llm] generate_explanation failed: {e}')
        return '{"chefs_choice": "Error generating explanation", "healthy_snacks": "", "guessing_game": "", "tricky_test": "", "fix_it_mode": ""}'


def extract_csv_from_unstructured_data(scenario_title: str, file_type: str, base64_content: str) -> str:
    """
    Uses the Vision/Language LLM to extract a structured CSV from an uploaded Image/Doc/PDF.
    """
    system_prompt = (
        f"You are an AI data extractor. You need to extract structured tabular data from the provided image/document "
        f"for a machine learning scenario titled '{scenario_title}'. "
        f"Return ONLY valid CSV text. Do not use markdown blocks like ```csv. "
        f"Include headers on the first row. Guess the most appropriate features based on the scenario."
    )
    
    try:
        client = _get_client()
        # Create message content depending on whether it's an image
        if file_type.startswith('image/'):
            content = [
                {"type": "text", "text": "Extract tabular data from this image and return it as CSV."},
                {"type": "image_url", "image_url": {"url": f"data:{file_type};base64,{base64_content}"}}
            ]
        else:
            # If it's a PDF/Doc that was converted to base64, we might not be able to read it with vision API directly 
            # if it's just raw bytes. For now, assume it's text or image-based text.
            content = "Please extract the CSV data."
            
        response = client.chat.completions.create(
            model='openai/gpt-4o-mini',
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content}
            ]
        )
        csv_text = response.choices[0].message.content.strip()
        if csv_text.startswith('```csv'):
            csv_text = csv_text[6:]
        if csv_text.startswith('```'):
            csv_text = csv_text[3:]
        if csv_text.endswith('```'):
            csv_text = csv_text[:-3]
        return csv_text.strip()
    except Exception as e:
        logger.exception(f'[llm] extract_csv failed: {e}')
        raise ValueError("Failed to extract data from the uploaded file.")
