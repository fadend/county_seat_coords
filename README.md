# Utility to get the coordinates of county seats via Wikipedia

This is pretty fragile, but it worked for my purposes. Maybe it'll work for you too.

## Usage

```
$ python -m venv seatenv
$ cd seatenv
$ bin/pip3 install git+https://github.com/fadend/county_seat_coords
$ bin/python -m county_seat_coords.fetch_county_seat_coords \
  --county_list_wiki_url=https://en.wikipedia.org/wiki/List_of_counties_in_California \
  --output_csv=county_seats.csv
```

## Acknowledgments

Thank you to
[Leonard Richardson](https://en.wikipedia.org/wiki/Beautiful_Soup_(HTML_parser))
for [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/),
to [Kenneth Reitz](https://kennethreitz.org/) for [requests](https://requests.readthedocs.io/en/latest/),
and to all the wonderful people contributing to Wikipedia.

Code was formatted using [black](https://github.com/psf/black).
Thank you also to [Łukasz Langa](https://lukasz.langa.pl/) for that.
