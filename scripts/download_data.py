from pathlib import Path

import gdown

# Google Drive file IDs from the assignment brief
FILE_IDS = {
    "historical": "1IAfLZwu6rJzyWKgBToqwSmmVYU6VbjVs",
    "fear_greed": "1PgQC0tO8XN-wqkNyghWc_-mnrYv_nhSf",
}

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

# You may need to adjust these output filenames after you inspect the downloads
TARGETS = {
    "historical": RAW_DIR / "hyperliquid_trades.csv",  # or .parquet / .zip
    "fear_greed": RAW_DIR / "fear_greed.csv",
}


def download_by_id(file_id: str, output_path: Path) -> None:
    url = f"https://drive.google.com/uc?id={file_id}"
    print(f"Downloading {file_id} -> {output_path}")
    gdown.download(url, str(output_path), quiet=False)


def main() -> None:
    for key, file_id in FILE_IDS.items():
        out = TARGETS.get(key)
        if out is None:
            continue
        download_by_id(file_id, out)
    print("Done. Inspect data/raw and update filenames if downloaded formats differ.")


if __name__ == "__main__":
    main()
