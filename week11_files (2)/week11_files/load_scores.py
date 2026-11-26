import csv

MIN_SCORE = 0
MAX_SCORE = 100


def load_scores(path):
    """Return valid rows and records for skipped rows."""
    kept = []
    skipped = []

    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        for line_no, row in enumerate(reader, start=1):
            if line_no == 1:  # Header
                continue
            if not row:  # Blank line
                continue

            original = ",".join(row)

            if len(row) != 2:
                skipped.append((line_no, original, "열 개수가 2가 아님"))
                continue

            name = row[0].strip()
            raw_score = row[1].strip()

            if not name:
                skipped.append((line_no, original, "이름이 비어 있음"))
                continue
            if not raw_score:
                skipped.append((line_no, original, "점수가 비어 있음"))
                continue

            try:
                score = int(raw_score)
            except ValueError:
                skipped.append((line_no, original, "점수가 정수가 아님"))
                continue

            if not MIN_SCORE <= score <= MAX_SCORE:
                skipped.append((line_no, original, "점수가 0~100 밖"))
                continue

            kept.append((name, score))

    return kept, skipped


if __name__ == "__main__":
    import sys

    path = sys.argv[1] if len(sys.argv) > 1 else "scores.csv"
    kept, skipped = load_scores(path)
    print(f"읽은 줄 : {len(kept)}개")
    for name, score in kept:
        print(f"  {name} {score}")
    print(f"건너뛴 줄 : {len(skipped)}개")
    for line_no, original, reason in skipped:
        print(f"  {line_no}행  {original}   ← {reason}")
