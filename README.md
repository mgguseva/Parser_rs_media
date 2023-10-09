# Parser_rs_media

**Project Description**: A tool for scraping articles from various Republika Srpska news portals.

**Directory Structure**:
- `main_parser.py`: Main script to execute all the parsers.
- `atv_parser.py`: Script for scraping articles from [`www.atvbl.rs`](`www.atvbl.rs`).
- `frontal_parser.py`: Script for scraping articles from [`www.frontal.rs`](`www.frontal.rs`).
- `rtvbn_parser.py`: Script for scraping articles from [`rtvbn.com`](`rtvbn.com`).
- `nezavisne_scraper.py`: Script for scraping articles from [`nezavisne.com`](`nezavisne.com`)
- `patriotesrpske_scraper.py`: Script for scraping articles from [`patriotesrpske.com`](`patriotesrpske.com`).
- `rtrs_scraper.py`: Script for scraping articles from [`lat.rtrs.tv`](lat.rtrs.tv)

## Usage

1. Ensure all dependencies are installed.
2. Navigate to the project directory.
3. Run the main parser using the following command:
- python main_parser.py
4. Once executed, the script will start scraping articles from the listed websites.
5. The scraped data will be saved in the `Parser_rs_media/data` directory as CSV files.
