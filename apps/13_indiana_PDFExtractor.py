import argparse
import fitz  # PyMuPDF
import re

def extract_formula(pdf_path, output_txt):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    # Try to extract the section(s) that describe the Three Hour Outline formula
    # This is a heuristic and may need tuning for your PDF
    match = re.search(r'(Three Hour Outline[\s\S]{0,1000}?Act [I1l][\s\S]{0,5000}?)(?:\n[A-Z][^\n]+:|$)', text, re.IGNORECASE)
    formula = match.group(1).strip() if match else text[:2000]
    with open(output_txt, 'w', encoding='utf-8') as f:
        f.write(formula)
    print(f"Extracted formula to {output_txt}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract Three Hour Outline formula from PDF.")
    parser.add_argument('--pdf', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    extract_formula(args.pdf, args.output)
