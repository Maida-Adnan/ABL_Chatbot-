#we have loader +chunking function here 


import re
from pathlib import Path
from pypdf import PdfReader

# Tier 1: matches "Product: ..." or "Process: ..." at the start of a line
# (allows leading whitespace, since some headers in this doc are indented)
HEADER_PATTERN = re.compile(r"^\s*(Product|Process):\s*(.+)$", re.MULTILINE)

# Tier 2: matches numbered sub-headers like "1. Positive Pay" inside a big section
# Revised pattern allows Mixed Case / Sentence Case right after the number.
SUBHEADER_PATTERN = re.compile(r"^\s*\d+\.\s+([A-Za-z][^\n]{3,80})$", re.MULTILINE)

# If a section (or sub-section) has more words than this, we split it further
OVERSIZED_THRESHOLD = 900

# Tier 3 fallback: word-count chunk size and overlap
MAX_WORDS = 400
OVERLAP_WORDS = 50


def extract_text_from_pdf(pdf_path: str) -> str:
    """Reads a PDF file and returns all its text as one string."""
    reader = PdfReader(pdf_path)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() + "\n"
    return full_text


_AI_BLOB_PATTERN = re.compile(
    r'Topic:.*?(?=\nProduct:|\nProcess:|\Z)',
    re.DOTALL,
)


def clean_text(text: str) -> str:
    """
    Removes AI-generated chatbot blobs from extracted PDF text.
    These are sections starting with 'Topic:' that were accidentally
    included in the source document — they are not real bank content.
    """
    return _AI_BLOB_PATTERN.sub("", text)


def split_by_pattern(text: str, pattern: re.Pattern, title_group: int) -> list[dict]:
    """
    Generic splitter: finds all matches of `pattern` in `text` and splits
    the text into pieces, one per match, using each match's title.
    Returns [{title, text}], or a single piece with title=None if no matches found.
    """
    matches = list(pattern.finditer(text))

    if not matches:
        return [{"title": None, "text": text.strip()}]

    pieces = []
    for i, match in enumerate(matches):
        title = match.group(title_group).strip()
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        piece_text = text[start:end].strip()
        pieces.append({"title": title, "text": piece_text})

    return pieces


def word_count_split(text: str) -> list[str]:
    """Tier 3 fallback: splits text into overlapping word-count chunks."""
    words = text.split()
    if len(words) <= MAX_WORDS:
        return [text]

    chunks = []
    start = 0
    while start < len(words):
        end = start + MAX_WORDS
        chunks.append(" ".join(words[start:end]))
        start += MAX_WORDS - OVERLAP_WORDS
    return chunks


def split_section_further(section_text: str) -> list[str]:
    """
    Takes one oversized section's text and tries Tier 2 (numbered sub-headers)
    first. If that doesn't help enough, falls back to Tier 3 (word count).
    Returns a flat list of text pieces.
    """
    sub_pieces = split_by_pattern(section_text, SUBHEADER_PATTERN, title_group=1)

    MIN_PIECE_WORDS = 60
    merged_pieces = []
    for piece in sub_pieces:
        word_count = len(piece["text"].split())
        if word_count < MIN_PIECE_WORDS and merged_pieces:
            merged_pieces[-1]["text"] += "\n" + piece["text"]
        else:
            merged_pieces.append(dict(piece))
    sub_pieces = merged_pieces

    final_pieces = []
    for piece in sub_pieces:
        word_count = len(piece["text"].split())
        if word_count > OVERSIZED_THRESHOLD:
            # still too big even after sub-header split -> Tier 3 fallback
            final_pieces.extend(word_count_split(piece["text"]))
        else:
            final_pieces.append(piece["text"])

    return final_pieces


MIN_CHUNK_WORDS = 30


def load_documents(raw_folder: str = "data/raw") -> list[dict]:
    """
    Loads all PDFs in the given folder and splits each into clean chunks
    using the 3-tier strategy: Product/Process headers -> numbered
    sub-headers (for oversized sections) -> word-count fallback.

    A final pass merges any chunk below MIN_CHUNK_WORDS into the preceding
    chunk, absorbing page-break fragments and stray navigational lines.

    Returns a list of {source, title, text} dicts.
    """
    all_chunks = []

    for pdf_file in Path(raw_folder).glob("*.pdf"):
        full_text = clean_text(extract_text_from_pdf(str(pdf_file)))
        sections = split_by_pattern(full_text, HEADER_PATTERN, title_group=2)

        for section in sections:
            word_count = len(section["text"].split())

            if word_count <= OVERSIZED_THRESHOLD:
                all_chunks.append({
                    "source": pdf_file.name,
                    "title": section["title"],
                    "text": section["text"]
                })
            else:
                sub_texts = split_section_further(section["text"])
                for sub_text in sub_texts:
                    all_chunks.append({
                        "source": pdf_file.name,
                        "title": section["title"],
                        "text": sub_text
                    })

    merged: list[dict] = []
    for chunk in all_chunks:
        if merged and len(chunk["text"].split()) < MIN_CHUNK_WORDS:
            merged[-1]["text"] += "\n" + chunk["text"]
        else:
            merged.append(chunk)

    return merged