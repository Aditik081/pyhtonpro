print("STARTING FLASK APP")

from flask import Flask, request, jsonify
from flask_cors import CORS

import os, io, re, unicodedata, tempfile

import fitz  # PyMuPDF
import pdfplumber

import spacy
from PIL import Image
import pytesseract
from google import genai
import os

from google import genai

client = genai.Client(api_key="YOUR_NEW_API_KEY")




# =========================
# TESSERACT PATH (LOCAL)
# =========================
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Users\aditi kumari\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
)

# =========================
# INIT
# =========================
app = Flask(__name__)
CORS(app)

nlp = spacy.load("en_core_web_sm")
if "sentencizer" not in nlp.pipe_names:
    nlp.add_pipe("sentencizer")


# =========================
# OCR HELPERS
# =========================
def preprocess_for_ocr(img):
    img = img.convert("L")
    img = img.point(lambda x: 0 if x < 180 else 255, "1")
    return img


def extract_pdf_native_text(pdf_path):
    text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text.append(t)
    return "\n\n".join(text)


def ocr_pdf_with_tesseract(pdf_path, dpi=300):
    chunks = []
    with fitz.open(pdf_path) as doc:
        mat = fitz.Matrix(dpi / 72, dpi / 72)
        for page in doc:
            pix = page.get_pixmap(matrix=mat)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            img = preprocess_for_ocr(img)
            txt = pytesseract.image_to_string(img, config="--psm 6")
            chunks.append(txt)
    return "\n\n".join(chunks)


def ocr_image(path):
    img = Image.open(path)
    img = preprocess_for_ocr(img)
    return pytesseract.image_to_string(img, config="--psm 6")


# =========================
# TEXT CLEANING
# =========================
def normalize_text(s):
    s = unicodedata.normalize("NFKC", s)
    s = s.replace("\u00ad", "")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def clean_medical_text(s):
    s = s.lower()
    s = re.sub(r"[^\w\s\-\+\.\,\:\;\(\)/%°]", " ", s)
    s = re.sub(r"[ \t]{2,}", " ", s)
    return s.strip()


# =========================
# TEST EXTRACTION
# =========================
VALID_TESTS = [
    "haemoglobin", "hemoglobin", "haematocrit", "pcv",
    "rbcs count", "rbc", "mcv", "mch", "mchc", "rdw-cv",
    "platelet count", "total leucocytic count",
    "neutrophils", "lymphocytes", "monocytes", "eosinophils"
]


def extract_all_tests(clean_text):
    results = []
    doc = nlp(clean_text)

    for test in VALID_TESTS:
        patterns = [
            rf"{test}[^0-9]*([\d\.]+)\s*([a-zA-Z/%]+)\s*([\d\.]+\s*-\s*[\d\.]+)",
            rf"{test}[^0-9]*([\d\.]+)\s*([a-zA-Z/%]+)\s*/\s*([\d\.]+\s*-\s*[\d\.]+)",
        ]

        for sent in doc.sents:
            for p in patterns:
                m = re.search(p, sent.text, re.IGNORECASE)
                if m:
                    results.append({
                        "test_name": test,
                        "value": m.group(1),
                        "unit": m.group(2),
                        "reference_range": m.group(3)
                    })
                    break
            else:
                continue
            break

    return results


# =========================
# DISEASE PREDICTION
# =========================
def predict_disease(test_results):
    findings = []
    diseases = []

    test_map = {}
    for t in test_results:
        try:
            test_map[t["test_name"]] = float(t["value"])
        except:
            pass

    hb = test_map.get("haemoglobin") or test_map.get("hemoglobin")
    if hb and hb < 13:
        diseases.append("Possible Anemia")
        findings.append(f"Low Hemoglobin ({hb} g/dL)")

    wbc = test_map.get("total leucocytic count")
    if wbc:
        if wbc > 11000:
            diseases.append("Possible Infection")
            findings.append(f"High WBC Count ({wbc})")
        elif wbc < 4000:
            diseases.append("Possible Leukopenia")
            findings.append(f"Low WBC Count ({wbc})")

    platelets = test_map.get("platelet count")
    if platelets:
        if platelets < 150000:
            diseases.append("Possible Thrombocytopenia")
            findings.append(f"Low Platelet Count ({platelets})")
        elif platelets > 450000:
            diseases.append("Possible Thrombocytosis")
            findings.append(f"High Platelet Count ({platelets})")

    eos = test_map.get("eosinophils")
    if eos and eos > 6:
        diseases.append("Possible Allergy or Parasitic Infection")
        findings.append(f"High Eosinophils ({eos}%)")

    if not diseases:
        diseases.append("No major abnormality detected")

    return {
        "possible_conditions": diseases,
        "observations": findings
    }


# =========================
# API ROUTES
# =========================
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/extract", methods=["POST"])
def extract():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    f = request.files["file"]

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        f.save(tmp.name)
        path = tmp.name

    ext = f.filename.lower().split(".")[-1]

    if ext == "pdf":
        native = extract_pdf_native_text(path)
        text = native if len(re.findall(r"\d", native)) > 10 else ocr_pdf_with_tesseract(path)
    else:
        text = ocr_image(path)

    clean = clean_medical_text(normalize_text(text))
    results = extract_all_tests(clean)
    prediction = predict_disease(results)

    os.remove(path)

    return jsonify({
        "file": f.filename,
        "tests": results,
        "analysis": prediction
    })
# ask api
@app.route('/ask', methods=['POST'])
def ask():
    data = request.json or {}
    question = data.get('question', '')
    analysis = data.get('analysis', {})

    observations = ', '.join(analysis.get('observations', [])) or 'No observations'
    conditions = ', '.join(analysis.get('possible_conditions', [])) or 'No major abnormality detected'

    user_prompt = f"""
You are an expert doctor/pathologist.

Observations:
{observations}

Possible Conditions:
{conditions}

Patient asks: "{question}"

Answer professionally. Give medical advice, precautions, and answer in 2 or 3 line and just answer the question add nothing more .
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_prompt
        )

        return jsonify({"answer": response.text})

    except Exception as e:
        print(e)
        return jsonify({"answer": str(e)})

# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
