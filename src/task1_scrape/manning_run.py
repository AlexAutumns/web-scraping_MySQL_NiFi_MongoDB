import time
import pandas as pd

from src.common.paths import RAW_DIR, PROCESSED_DIR
from src.task1_scrape.sources import CATALOG_URLS
from src.task1_scrape.manning_scraper import scrape_catalog



def main() -> None:
    all_rows = []
    for i, url in enumerate(CATALOG_URLS, start=1):
        print(f"\n=== CATALOG {i}/{len(CATALOG_URLS)} ===")
        try:
            all_rows.extend(scrape_catalog(url))
        except Exception as e:
            print("[SKIP] error:", repr(e))
        time.sleep(1)

    df = pd.DataFrame(all_rows)

    if df.empty:
        print("\n[ERROR] No rows scraped. Try adding more Manning catalog URLs.")
        return

    df = (
        df.dropna(subset=["title", "authors", "year", "price"])
          .drop_duplicates(subset=["title"])
          .reset_index(drop=True)
    )

    # Ensure at least 15 rows
    df_15 = df.head(15).copy()

    raw_path = RAW_DIR / "books_manning_raw.csv"
    processed_path = PROCESSED_DIR / "books.csv"

    df_15.to_csv(raw_path, index=False)
    df_15.to_csv(processed_path, index=False)

    print("\n[DF] shape:", df_15.shape)
    print("[DF] columns:", df_15.columns.tolist())
    print("Saved RAW:", raw_path)
    print("Saved PROCESSED:", processed_path)


if __name__ == "__main__":
    main()
