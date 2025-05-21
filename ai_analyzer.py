import os
import openai

openai.api_key = os.getenv('OPENAI_API_KEY')

def build_prompt(name, data):
    if name == "CPI":
        actual = data.get("cpi_mom")
        core = data.get("core_cpi_mom")
        prev_cpi = data.get("prev_CPI")
        prev_core = data.get("prev_CoreCPI")
        return (
            f"The Consumer Price Index (CPI) month-over-month came in at {actual}%. "
            f"Core CPI (ex food and energy) was {core}%. "
            f"The previous month's CPI was {prev_cpi}% and Core CPI was {prev_core}%. "
            "Compare these results versus expectations and provide implications."
        )
    # Default generic prompt
    return f"Here is the data for {name}: {data}. Provide a brief analysis comparing actual versus forecast versus previous and discuss implications."

def analyze_release(context):
    name = context["name"]
    data = context["data"]
    prompt = build_prompt(name, data)
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a financial analyst. Provide concise insights."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=200,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()
