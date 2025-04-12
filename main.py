import csv
import argparse
from pathlib import Path
import epitran



LANG_MAP = {
    "english": "eng-Latn",
    "french": "fra-Latn",
    "german": "deu-Latn",
    "spanish": "spa-Latn",
    "italian": "ita-Latn",
    "portuguese": "por-Latn"
}


def load_input(file_path=None, text=None):
    words = []
    if file_path:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        with path.open("r", encoding="utf-8-sig", errors="replace") as f:
            for line in f:
                line = line.strip()
                if line:
                    if ',' in line:
                        words.extend([w.strip() for w in line.split(',') if w.strip()])
                    else:
                        words.append(line)
    elif text:
        words.extend([w.strip() for w in text.split(',') if w.strip()])
    else:
        raise ValueError("No input provided.")
    return words

def clean_words(words):
    seen = set()
    cleaned = []
    for word in words:
        if word and word not in seen:
            cleaned.append(word)
            seen.add(word)
    return cleaned

def fetch_ipa_from_wiktionary(word, lang_code):
    import requests
    from bs4 import BeautifulSoup
    import re

    lang_domain = {
        "french": "fr",
        "portuguese": "pt"
    }.get(lang_code.lower(), "en")

    url = f"https://{lang_domain}.wiktionary.org/w/api.php"
    params = {
        "action": "parse",
        "page": word,
        "prop": "text",
        "format": "json"
    }

    try:
        res = requests.get(url, params=params, timeout=5)
        res.raise_for_status()
        html = res.json().get("parse", {}).get("text", {}).get("*", "")
        soup = BeautifulSoup(html, "html.parser")

        ipa_spans = soup.find_all("span", class_="API")
        for span in ipa_spans:
            ipa = span.get_text().strip()
            if ipa.startswith("/") or ipa.startswith("["):
                return ipa


        # Look for <span class="API">/ipa/</span>
        """ spans = soup.find_all("span", class_="API")
        ipa_list = [span.get_text().strip() for span in spans]

        # Only return those that look like phonetics
        ipa = next((i for i in ipa_list if i.startswith("/") or i.startswith("[")), None)
        return ipa """
    except Exception as e:
        print(f"[Wiktionary fetch error: {word}] {e}")
        return None
    
    
def get_ipa(word, lang, epi):
    if lang.lower() in ["french", "portuguese"]:
        ipa = fetch_ipa_from_wiktionary(word, lang)
        if ipa:
            return ipa

    try:
        return epi.transliterate(word)
    except Exception:
        return "/error/"

""" def get_ipa(word, epi):
    try:
        return epi.transliterate(word)
    except Exception:
        return "/error/" """

def export_results(results, output_format, output_path):
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        if output_format == "csv":
            writer = csv.writer(f)
            writer.writerow(["Word", "IPA"])
            for word, ipa in results:
                writer.writerow([word, ipa])
        elif output_format == "txt":
            for word, ipa in results:
                f.write(f"{word}: {ipa}\n")
        else:
            raise ValueError("Unsupported output format.")

def main():
    parser = argparse.ArgumentParser(description="Multilingual IPA Transcription Tool")
    parser.add_argument("--file", help="Path to input .txt or .csv file in utf-8 encoding")
    parser.add_argument("--text", help="Direct comma-separated word input, input between \"\",")
    parser.add_argument("--lang", required=True, help="Language for IPA (e.g., english, french, german)")
    parser.add_argument("--csv", action="store_true", help="Output in CSV format")
    parser.add_argument("--txt", action="store_true", help="Output in TXT format")
    parser.add_argument("--out", default="output", help="Output file name without extension")

    args = parser.parse_args()

    lang_code = LANG_MAP.get(args.lang.lower())
    if not lang_code:
        print(f"Unsupported language: {args.lang}")
        print("Supported languages are:", ", ".join(LANG_MAP.keys()))
        return

    try:
        epi = epitran.Epitran(lang_code, preproc=True, ligatures=True)
        words = load_input(args.file, args.text)
        words = clean_words(words)
        results = [(word, get_ipa(word, args.lang, epi)) for word in words]


        output_format = "csv" if args.csv else "txt"
        output_path = f"{args.out}.{output_format}"

        export_results(results, output_format, output_path)
        print(f"Processed {len(results)} words. Output saved to {output_path}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
