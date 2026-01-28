import time
import pandas as pd

from src.common.paths import RAW_DIR, PROCESSED_DIR
from src.task1_scrape.sources import BOOK_URLS
from src.task1_scrape.packt_scraper import parse_packt_product


def main() -> None:
    rows = []
    for i, url in enumerate(BOOK_URLS, start=1):
        print(f"\n=== {i}/{len(BOOK_URLS)} ===")
        try:
            row = parse_packt_product(url)
            print("[PARSED]", row)
            rows.append(row)
        except Exception as e:
            print("[SKIP] error:", repr(e))
        time.sleep(1)

    df = pd.DataFrame(rows).dropna(subset=["title"]).drop_duplicates(subset=["title"]).reset_index(drop=True)

    # Save raw and processed (for now they’re the same, but later we can clean further in processed)
    raw_path = RAW_DIR / "books_packt.csv"
    processed_path = PROCESSED_DIR / "books.csv"

    df.to_csv(raw_path, index=False)
    df.to_csv(processed_path, index=False)

    print("\n[DF] shape:", df.shape)
    print("Saved RAW:", raw_path)
    print("Saved PROCESSED:", processed_path)


if __name__ == "__main__":
    main()
