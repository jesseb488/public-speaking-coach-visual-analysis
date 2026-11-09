import re
from collections import Counter
from pathlib import Path

#beginning configuration

TRANSCRIPT_FILE = "transcript.txt"
OUTPUT_FILE = "speech_report.txt"

TARGET_PHRASES = [
    "basically",
    "literally",
    "honestly",
    "I think", 
    "I mean",
    "you know",
]

FILLER_WORDS = [
    "um",
    "uh",
    "umm",
    "uhh", 
    "erm",
    "like",
    "you know",
    "I mean",
    "basically", 
    "actually",
    "kind of", 
    "sort of",
]

ACCEPTABLE_WORDS = [
    "the",
    "and",
    "a",
    "an",
    "or", 
    "but",
    "is",
    "are",
    "was",
    "were",
    "to",
    "of",
    "in",
    "on",
    "at",
    "for",
    "with",
    "it",
    "this",
    "that",
    "i",
    "you",
    "he",
    "she",
    "they",
    "we", 
    "my",
    "your",
    "as",
    "be",
    "have",
    "has",
    "do",
    "did",
    "so",
    "not",
]

def read_transcript(filename):
    path = Path(filename)

    if not path.is_file():
        raise FileNotFoundError(f"Transcript file not found: {filename}")

    return path.read_text(encoding="utf-8")

def tokenize(text):
    return re.findall(r"\b[\w]+(?:['’][\w]+)*\b", text.lower())


def count_phrases(text, phrases):
    words = tokenize(text)
    results = {}

    for phrase in phrases:
        phrase_words = tokenize(phrase)
        size = len(phrase_words)

        if size == 0:
            continue

        count = 0
        for i in range(len(words) - size + 1):
            if words[i:i + size] == phrase_words:
                count += 1

        results[phrase] = count

    return results


def sequence_length(item):
    return len(item[1])


def analyze_fillers(text):
    filler_counts = count_phrases(text, FILLER_WORDS)
    total_words = len(tokenize(text))

    tokens = tokenize(text)
    filler_sequences = []
    for phrase in FILLER_WORDS:
        sequence = tokenize(phrase)
        filler_sequences.append((phrase, sequence))

    filler_sequences.sort(key=sequence_length, reverse=True)

    matched_counts = Counter()
    filler_token_total = 0
    i = 0

    while i < len(tokens):
        match = None
        for phrase, sequence in filler_sequences:
            if tokens[i:i + len(sequence)] == sequence:
                match = (phrase, sequence)
                break

        if match:
            phrase, sequence = match
            matched_counts[phrase] += 1
            filler_token_total += len(sequence)
            i += len(sequence)
        else:
            i += 1

    if total_words > 0:
        filler_percentage = (filler_token_total / total_words) * 100
    else:
        filler_percentage = 0

    result = {
        "counts": dict(matched_counts.most_common()),
        "total_occurrences": sum(matched_counts.values()),
        "percentage": filler_percentage,
    }
    return result


def most_common_words(text, top_n=10):
    words = tokenize(text)
    filtered_words = []
    for word in words:
        if word not in ACCEPTABLE_WORDS:
            filtered_words.append(word)

    return Counter(filtered_words).most_common(top_n)


def most_commom_phrases(text, phrase_length=2, top_n=10):
    words = tokenize(text)
    phrases = []
    for i in range(len(words) - phrase_length + 1):
        phrase = " ".join(words[i:i + phrase_length])
        phrases.append(phrase)

    counts = Counter(phrases)

    common_phrases = []
    for phrase, count in counts.most_common():
        if count > 1:
            common_phrases.append((phrase, count))

    return common_phrases[:top_n]


def generate_report(text):
    total_words = len(tokenize(text))
    fillers = analyze_fillers(text)
    target_counts = count_phrases(text, TARGET_PHRASES)

    lines = []

    lines.append("Speech Analysis Report")
    lines.append("=" * 45)

    lines.append(f"\nTotal words: {total_words}")

    lines.append("\n Filler Words Analysis:")
    lines.append("=" * 45)

    for word, count in fillers["counts"].items():
        lines.append(f"  {word}: {count}")

    lines.append(f"\n  Total filler occurrences: {fillers['total_occurrences']}")
    lines.append(f"  Filler words percentage: {fillers['percentage']:.2f}%")

    lines.append("\n Target words/phrases Analysis:")
    lines.append("=" * 45)

    for word, count in most_common_words(text):
        lines.append(f"  {word}: {count}")

    lines.append("\n Most common two-word phrases:")
    lines.append("=" * 45)

    for phrase, count in most_commom_phrases(text, 2):
        lines.append(f"  {phrase}: {count}")

    lines.append("\n Most common three-word phrases:")
    lines.append("=" * 45)

    for phrase, count in most_commom_phrases(text, 3):
        lines.append(f"  {phrase}: {count}")

    return "\n".join(lines)


def main():
    transcript = read_transcript(TRANSCRIPT_FILE)
    report = generate_report(transcript)
    print(report)

    Path(OUTPUT_FILE).write_text(report, encoding="utf-8")
    print(f"\nReport saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()