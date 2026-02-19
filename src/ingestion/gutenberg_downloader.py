"""
Downloading books from Project Gutenberg.

How it works:
1. We have a list of book IDs that we want to download.
2. For each book ID, we construct the URL to download the book
3. We download the book as a text file and save it to data/raw/
4. We generate JSON file with metadata of each book

Using :
    python -m src.ingestion.gutenberg_downloader --output data/raw --max-books 5
    python -m src.ingestion.gutenberg_downloader --list-books
    python -m src.ingestion.gutenberg_downloader --genres fantasy_sf
"""

import argparse
import json
import time
import urllib.request
import urllib.error
from dataclasses import dataclass, asdict
from pathlib import Path

# Define global constants
GUTENBERG_URL = "https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt"

CURATED_BOOKS = {
    "hugo_miserables_t1": 17489,
    "hugo_miserables_t2": 17493,
    "hugo_notre_dame": 2610,
    "flaubert_bovary": 14155,
    "flaubert_education": 14156,
    "stendhal_rouge_noir": 798,
    "zola_germinal": 5711,
    "zola_assommoir": 8600,
    "zola_nana": 5765,
    "zola_bete_humaine": 14553,
    "balzac_pere_goriot": 5090,
    "balzac_illusions": 13159,
    "dumas_monte_cristo_t1": 17989,
    "dumas_monte_cristo_t2": 17990,
    "dumas_trois_mousquetaires": 13951,
    "maupassant_bel_ami": 3790,
    "maupassant_contes": 3090,
    "proust_swann": 7178,
    "voltaire_candide": 4650,
    
    "leroux_fantome_opera": 175,
    "leroux_chambre_jaune": 13071,
    "leroux_parfum_dame": 13072,
    "leblanc_arsene_lupin": 6133,
    "leblanc_aiguille": 12389,
    "leblanc_813": 28371,
    
    "verne_20000_lieues": 5097,
    "verne_tour_monde": 800,
    "verne_voyage_centre": 4791,
    "verne_ile_mysterieuse": 9080,
    "verne_5_semaines": 4548,
    "verne_terre_lune": 799,
    "maupassant_horla": 14063,
}

GENRES = {
    "hugo": "litterature_generale",
    "flaubert": "litterature_generale",
    "stendhal": "litterature_generale",
    "zola": "litterature_generale",
    "balzac": "litterature_generale",
    "dumas": "litterature_generale",
    "maupassant_bel": "litterature_generale",
    "maupassant_contes": "litterature_generale",
    "proust": "litterature_generale",
    "voltaire": "litterature_generale",
    "leroux": "thriller_policier",
    "leblanc": "thriller_policier",
    "verne": "fantasy_sf",
    "maupassant_horla": "fantasy_sf",
}

# Data structure
@dataclass
class BookMetadata:
    """
    Stores informations of a downloaded book.
    """
    
    book_id: int
    key: str
    genre: str
    file_path: str
    file_size: int
    download_success: bool
    error: str | None = None
    
# Utils functions
def get_genre(book_key: str) -> str:
    """
    Give book genre based on its key.
    """
    
    for prefix, genre in GENRES.items():
        if book_key.startswith(prefix):
            return genre
    return "litterature_generale"

# Main function
def download_book(book_id: int, output_dir: Path, retries: int = 3) -> str | None:
    """
    Download a book from Project Gutenberg.
    
    Args:
        book_id: The ID of the book to download.
        output_dir: The directory where the downloaded book will be saved.
        retries: The number of times to retry downloading in case of failure.
    
    Returns:
        Saved file path or None if download failed.
    """
    
    url = GUTENBERG_URL.format(book_id=book_id)
    
    output_path = output_dir / f"pg{book_id}.txt"
    
    if output_path.exists() and output_path.stat().st_size > 1000:
        print(f"    [SKIP] pg{book_id}.txt already exists ({output_path.stat().st_size:,} octets)")
        return str(output_path)

    for attempt in range(1, retries + 1):
        try:
            print(f"    [DOWNLOAD] Attempt {attempt}/{retries}...")
            
            req = urllib.request.Request(url, headers={
                "User-Agent": "AITextGen-Corpus-Builder/1.0 (personal project)"
            })
            
            with urllib.request.urlopen(req, timeout=30) as response:
                content = response.read()
            
            if len(content) < 500:
                print(f"    [WARN] File too small ({len(content)} octets)")
                continue
            
            output_path.write_bytes(content)
            print(f"    [OK] {output_path.name} ({len(content)} octets)")
            return str(output_path)
        except urllib.error.HTTPError as e:
            print(f"    [ERR] HTTP error: {e.code} for book ID {book_id}")
            if e.code == 404:
                return None
        
        except (urllib.error.URLError, TimeoutError) as e:
            print(f"    [ERR] Network error: {e}")
            
        if attempt < retries:
            wait = attempt * 2
            print(f"    [WAIT] Retrying in {wait} seconds...")
            time.sleep(wait)
        
    return None

# Download function
def download_curated_corpus(
    output_dir: str = "data/raw",
    max_books: int | None = None,
    genres: list[str] | None = None,
    delay: float = 1.0,
) -> list[BookMetadata]:
    """
    Download the curated corpus of books from Project Gutenberg.
    
    Args:
        output_dir: The directory where the downloaded books will be saved.
        max_books: The maximum number of books to download (None for all).
        genres: List of genres to include (None for all).
        delay: Delay in seconds between downloads to avoid overloading the server.
    
    Returns:
        A list of BookMetadata objects for the downloaded books.
    """
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    books_to_download = list(CURATED_BOOKS.items())
    
    if genres:
        books_to_download = [
            (key, bid) for key, bid in books_to_download
            if get_genre(key) in genres
        ]
    
    if max_books:
        books_to_download = books_to_download[:max_books]
    
    total = len(books_to_download)
    
    print(f"\n{'='*60}")
    print(f"  {total} books to download")
    print(f"  Destination : {output_path.resolve()}")
    
    if genres:
        print(f"  Genres : {', '.join(genres)}")
    print(f"{'='*60}\n")
    
    results: list[BookMetadata] = []
    
    for i, (key, book_id) in enumerate(books_to_download, 1):
        genre = get_genre(key)
        print(f"[{i}/{total}] {key} (id={book_id}, genre={genre})")
        
        file_path = download_book(book_id, output_path)
        
        metadata = BookMetadata(
            book_id=book_id,
            key=key,
            genre=genre,
            file_path=file_path or "",
            file_size=Path(file_path).stat().st_size if file_path else 0,
            download_success=file_path is not None,
            error=None if file_path else "Download failed",
        )
        results.append(metadata)
        
        if i < total and delay > 0:
            time.sleep(delay)
            
    success = sum(1 for r in results if r.download_success)
    total_size = sum(r.file_size for r in results)
    
    print(f"\n{'='*60}")
    print(f"  Results : {success}/{total} downloaded books")
    print(f"  Total size : {total_size / 1024 / 1024:.1f} Mo")
    print(f"{'='*60}\n")
    
    metadata_path = output_path / "metadata.json"
    with metadata_path.open("w", encoding="utf-8") as f:
        json.dump([asdict(r) for r in results], f, ensure_ascii=False, indent=2)
    print(f"Metadata saved to {metadata_path}")
    
    return results

# Entry point
def main():
    """
    Entry point when running the script from command line.
    
    argparse is used to parse command line arguments :
        --output data/raw : output directory for downloaded books
        --max-books 5 : maximum number of books to download
        --genres fantasy_sf : filter books by genre
        --list-books : list available books without downloading
    
    Example :
        python -m src.ingestion.gutenberg_downloader --max-books 5 --genres fantasy_sf
    """
    
    parser = argparse.ArgumentParser(
        description="Download books from Project Gutenberg"
    )
    
    parser.add_argument(
        "--output", type=str, default="data/raw",
        help="Output directory for downloaded books (default: data/raw)"
    )
    
    parser.add_argument(
        "--max-books", type=int, default=None,
        help="Maximum number of books to download"
    )
    
    parser.add_argument(
        "--genres", nargs="+",
        choices=["litterature_generale", "thriller_policier", "fantasy_sf"],
        help="Filter books by genre"
    )
    
    parser.add_argument(
        "--delay", type=float, default=1.0,
        help="Delay in seconds between downloads (default: 1.0)"
    )
    
    parser.add_argument(
        "--list-books", action="store_true",
        help="List available books without downloading"
    )
    
    args = parser.parse_args()
    
    if args.list_books:
        print("\nAvailable books in the curated corpus:\n")
        for key, book_id in CURATED_BOOKS.items():
            genre = get_genre(key)
            print(f"  {key:40s} (id={book_id:6d}, genre={genre})")
        print(f"\nTotal: {len(CURATED_BOOKS)} books")
        return
    
    download_curated_corpus(
        output_dir=args.output,
        max_books=args.max_books,
        genres=args.genres,
        delay=args.delay,
    )
    
if __name__ == "__main__":
    main()