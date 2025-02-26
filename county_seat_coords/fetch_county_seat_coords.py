"""Fetch county seat coordinates from Wikipedia."""

import argparse
import csv
import html
import re
from typing import Mapping
import urllib

import bs4
import requests


def float_from_soup_class(
    soup: bs4.BeautifulSoup, class_name: str, url: str = ""
) -> float:
    """Parses a float from the text of element for the given CSS class.

    Args:
        soup: Parsed document to examine.
        class_name: CSS class to look for.
        url: For debugging messages, URL of the document.
    Returns: the parsed float.
    """
    elem = soup.find(class_=class_name)
    if not elem:
        raise RuntimeError(f"Didn't find {class_name} in {url}")
    return float(elem.text)


def fetch_coordinates_from_geohack(url: str) -> Mapping[str, str]:
    """Fetches the decimal lat-lng from the given GeoHack page.

    Args:
        url: URL of the GeoHack page.
    Returns: dict with keys "lat", "lng".
    """
    geohack_html = requests.get(url).text
    geohack_soup = bs4.BeautifulSoup(geohack_html, "html.parser")
    lat = float_from_soup_class(geohack_soup, "p-latitude", url=url)
    lng = float_from_soup_class(geohack_soup, "p-longitude", url=url)
    return {"lat": str(lat), "lng": str(lng)}


def fetch_county_seat_coordinates(url: str) -> Mapping[str, str]:
    """Fetches the coordinates for the given county seat.

    Args:
        url: URL of the county seat.
    Returns: dict with keys "lat" and "lng" with the coordinates.
    """
    seat_html = requests.get(url).text
    geohack_url_match = re.search(r"https://geohack\.[^\"]+", seat_html)
    if not geohack_url_match:
        raise RuntimeError(f"Didn't find geohack URL for {url}")
    return fetch_coordinates_from_geohack(html.unescape(geohack_url_match[0]))


def fetch_coordinates_for_county_seats(url: str) -> list[Mapping[str, str]]:
    """Fetches the coordinates for each county seat.

    Args:
        url: URL of a Wikipedia page listing the counties for a state.
    Returns: a list of dicts with the following keys: "county", "county_seat",
      "lat", "lng".
    """
    counties_html = requests.get(url).text
    counties_soup = bs4.BeautifulSoup(counties_html, "html.parser")
    counties_table = counties_soup.find("table", class_="wikitable")
    if not counties_table:
        raise RuntimeError(f"Didn't find .wikitable in {url}")
    result = []
    for tr in counties_table.find_all("tr")[1:]:
        county = tr.th.text.strip()
        cells = tr.find_all("td")
        county_seat = cells[1].text.strip()
        county_seat_url = cells[1].a["href"]
        if not county_seat_url.startswith("http"):
            county_seat_url = urllib.parse.urljoin(url, county_seat_url)
        row_result = fetch_county_seat_coordinates(county_seat_url)
        row_result["county"] = county
        row_result["county_seat"] = county_seat
        result.append(row_result)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="county_seats_coords",
        description="Fetch county seat coordinates from Wikipedia",
    )
    parser.add_argument(
        "--county_list_wiki_url",
        required=True,
        help="URL of the county list Wikipedia page.",
    )
    parser.add_argument(
        "--output_csv", required=True, help="Path at which to store the CSV output"
    )
    args = parser.parse_args()
    rows = fetch_coordinates_for_county_seats(args.county_list_wiki_url)
    with open(args.output_csv, "w") as f:
        writer = csv.DictWriter(f, fieldnames=["county", "county_seat", "lat", "lng"])
        writer.writeheader()
        writer.writerows(rows)
