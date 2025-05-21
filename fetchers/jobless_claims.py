import requests
import pdfplumber
import re
from datetime import datetime

def fetch_jobless_claims(pdf_url: str = "https://www.dol.gov/ui/data.pdf") -> dict:
    resp = requests.get(pdf_url, timeout=10)
    with open("temp_jobless.pdf", "wb") as f:
        f.write(resp.content)

    initial = continuing = None
    with pdfplumber.open("temp_jobless.pdf") as pdf:
        text = "\n".join(page.extract_text() for page in pdf.pages)
        m_init = re.search(r"Initial claims[\s:]+([\d,]+)", text)
        m_cont = re.search(r"Continuing claims[\s:]+([\d,]+)", text)
        if m_init:
            initial = int(m_init.group(1).replace(",", ""))
        if m_cont:
            continuing = int(m_cont.group(1).replace(",", ""))

    return {
        "initial_claims": initial,
        "continuing_claims": continuing,
        "timestamp": datetime.utcnow().isoformat()
    }
