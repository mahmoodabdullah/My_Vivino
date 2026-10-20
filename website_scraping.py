import argparse
import csv
import sys
import time
import requests

# This is the API endpoint that Vivino uses to get wine information.
API_URL = "https://www.vivino.com/api/explore/explore"

# These headers describe the type of request we are sending to the website.
HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/100.0 Safari/537.36"),
    "Accept": "application/json",
}

# Each number represents a different type of wine on Vivino.
WINE_TYPES = {
    1: "Red",
    2: "White",
    3: "Sparkling",
    4: "Rose",
    7: "Dessert",
    24: "Fortified"
}

# These are the columns I want to save in my final CSV file.
CSV_FIELDS = [
    "vintage_id", "wine_id", "winery", "wine_name", "vintage_year", "wine_type",
    "region", "country", "rating_avg", "rating_count", "price", "currency",
    "vivino_url",
]

# I added a short delay between requests to avoid sending them too quickly.
DELAY_SECONDS = 2.0


def dig(obj, *keys):
    """Get a value from a nested dictionary without causing an error if a key is missing."""

    # Some wine details are stored inside other dictionaries.
    # This loop follows the keys one by one until it finds the value.
    for key in keys:
        if not isinstance(obj, dict):
            return None
        obj = obj.get(key)

    return obj


def parse_match(match, wine_type_id):
    # Each result contains information about a particular wine and its vintage.
    # I separate the information here so it is easier to work with.
    vintage = match.get("vintage") or {}
    wine = vintage.get("wine") or {}
    price = match.get("price") or {}

    # I need the wine ID to identify the wine and create its Vivino link.
    wine_id = wine.get("id")

    # Return the information I want to keep for each wine.
    # Using a dictionary makes it easier to save everything into a CSV later.
    return {
        "vintage_id": vintage.get("id"),
        "wine_id": wine_id,
        "winery": dig(wine, "winery", "name"),
        "wine_name": wine.get("name"),
        "vintage_year": vintage.get("year"),

        # Use the wine type name instead of only keeping its ID.
        "wine_type": WINE_TYPES.get(wine.get("type_id", wine_type_id)),

        "region": dig(wine, "region", "name"),
        "country": dig(wine, "region", "country", "name"),

        # These values help me compare wines based on their ratings.
        "rating_avg": dig(vintage, "statistics", "ratings_average"),
        "rating_count": dig(vintage, "statistics", "ratings_count"),

        # Save the price and currency separately.
        "price": price.get("amount"),
        "currency": dig(price, "currency", "code"),

        # Create a direct link to the wine if its ID is available.
        "vivino_url": ("https://www.vivino.com/w/{}".format(wine_id) if wine_id else ""),
    }


def fetch_page(session, wine_type_id, page, country="US", retries=3):
    # These are the filters sent with each request.
    # They control the country, currency, price range, wine type and page.
    params = {
        "country_code": country,
        "currency_code": "USD",
        "min_rating": 1,
        "order_by": "ratings_count",
        "order": "desc",
        "page": page,
        "price_range_min": 0,
        "price_range_max": 500,
        "wine_type_ids[]": wine_type_id,
    }

    # Try the request a few times in case there is a temporary connection problem.
    for attempt in range(retries):
        try:
            resp = session.get(API_URL, params=params, timeout=30)
        except requests.RequestException:
            # Wait a little longer after each failed connection attempt.
            time.sleep(3 * (attempt + 1))
            continue

        # Stop if Vivino refuses the request or limits access.
        # Retrying immediately could make the problem worse.
        if resp.status_code in (403, 429):
            sys.exit(
                "Blocked / rate limited (HTTP {}). Stop and try later.".format(
                    resp.status_code
                )
            )

        # If the request worked, convert the JSON response into Python data.
        if resp.status_code == 200:
            return resp.json()

        # Wait before trying again if the server returns another error.
        time.sleep(3 * (attempt + 1))

    # Return None if all attempts fail.
    return None


def main():
    # These arguments let me change the settings when running the script.
    # For example, I can choose how many pages to collect and the output filename.
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", type=int, default=5,
                    help="pages per wine type (25 wines/page)")
    ap.add_argument("--out", default="vivino_wines.csv")
    ap.add_argument("--country", default="US")
    args = ap.parse_args()

    # A session allows me to reuse the same connection settings for each request.
    session = requests.Session()
    session.headers.update(HEADERS)

    # 'seen' keeps track of vintage IDs so I don't save the same vintage twice.
    # 'rows' stores all the wine information collected from the requests.
    seen, rows = set(), []

    # Go through each wine type, such as red, white and sparkling.
    for type_id, type_name in sorted(WINE_TYPES.items()):

        # Collect the requested number of pages for the current wine type.
        for page in range(1, args.pages + 1):
            data = fetch_page(session, type_id, page, args.country)

            # Find the list of wines inside the API response.
            matches = dig(data, "explore_vintage", "matches") if data else None

            # If no results are returned, move on to the next wine type.
            if not matches:
                print("{} page {}: no data, moving on".format(type_name, page))
                break

            new = 0

            # Go through each wine returned on the current page.
            for m in matches:
                row = parse_match(m, type_id)
                key = row["vintage_id"]

                # Skip wines that have no vintage ID or have already been collected.
                if key is None or key in seen:
                    continue

                # Save the ID and add the wine details to my results.
                seen.add(key)
                rows.append(row)
                new += 1

            # Print progress so I can see how many new wines were collected.
            print("{} page {}: +{} wines (total {})".format(
                type_name, page, new, len(rows)
            ))

            # Wait before requesting the next page.
            time.sleep(DELAY_SECONDS)

    # If nothing was collected, stop instead of creating an empty CSV file.
    if not rows:
        sys.exit(
            "No rows collected - the endpoint may have changed. "
            "Open DevTools > Network on vivino.com/explore and compare the request."
        )

    # Create the CSV file and write the column names followed by all the wine data.
    # UTF-8 encoding helps keep text and special characters readable.
    with open(args.out, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    # Print a final message showing where the data was saved.
    print("Saved {} rows to {}".format(len(rows), args.out))


# Run main() only when this file is executed directly.
# This also lets me import its functions into another Python file if needed.
if __name__ == "__main__":
    main()
