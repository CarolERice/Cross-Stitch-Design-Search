from pathlib import Path
import sys
import csv
import difflib
import os
from django.conf import settings
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
  sys.path.insert(0, str(BASE_DIR))

from project import web_search

# read and map the current wips.csv file to get a lookup of who has each design of those that are currently in progress. This is used to display the "Who has it" field in the search results.
# open the fire read only if it exists, otherwise return an empty lookup
# for each non blank row, map the design name (lowercase, stripped of whitespace) to the "Who Has" value (stripped of whitespace)
# To get the clean row, we will strip whitespace from the keys and values, and convert the keys to lowercase. We will also ignore any rows that have a blank design name or a blank "Who Has" value.
# ignore any rows that have a blank design name or a blank "Who Has" value.
# ignore unused columns, and only use the "Design" and "Who Has" columns. The CSV file may have other columns that we don't care about, so we will ignore them.
# assign the result to a dictionary where the key is the design name and the value is the "Who Has" value. The design name will be converted to lowercase and stripped of whitespace, and the "Who Has" value will be stripped of whitespace.
# Finally return the lookup dictionary containing the mapping of design names to "Who Has" values. If the file does not exist, return an empty dictionary.

def get_stitcher_lookup():
    """Reads 'current wips.csv' and maps 'Design' -> 'Who Has'."""
    lookup: dict[str, str] = {}
    # Get the path to the CSV file in the search_app directory
    file_path = os.path.join(settings.BASE_DIR, 'search_app', 'current wips.csv')

    if os.path.exists(file_path):
        with open(file_path, mode='r', encoding='utf-8-sig', newline='') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                clean_row = {k.strip().lower(): (v or '').strip() for k, v in row.items() if k}
                design_name = " ".join(clean_row.get('design', '').lower().split())
                who_has = clean_row.get('who has', '')
                
                if design_name and who_has:
                    lookup[design_name] = who_has
    return lookup

# First make sure the project name is a string, otherwise return an empty string. Then clean the project name by converting it to lowercase and stripping whitespace. Check for an exact match in the lookup dictionary first. If found, return the corresponding "Who Has" value. If not found, use difflib.get_close_matches to find a close match with a cutoff of 0.90. If a close match is found, return the corresponding "Who Has" value. If no matches are found, return an empty string.
# convert the project name to lowercase and strip whitespace before checking for matches in the lookup dictionary. This ensures that the search is case-insensitive and ignores leading/trailing whitespace. The function will return the "Who Has" value for the exact match or close match, or an empty string if no match is found.
# if the project name is in the lookup dictionary, return the corresponding "Who Has" value. If not, use difflib.get_close_matches to find a close match with a cutoff of 0.90. If a close match is found, return the corresponding "Who Has" value. If no matches are found, return an empty string.
# if no exact match is found, use difflib.get_close_matches to find a close match with a cutoff of 0.90. If a close match is found, return the corresponding "Who Has" value. If no matches are found, return an empty string.
# if no matches are found, return an empty string. This ensures that the function always returns a string, either the "Who Has" value or an empty string if no match is found.

def find_stitcher(project_name: str | bool | None, lookup: dict[str, str]) -> str:
    """Checks for an exact match first, then falls back to a 90%+ close match."""
    if not isinstance(project_name, str):
        return ""

    clean_name = " ".join(project_name.lower().split())

    if clean_name in lookup:
        return lookup[clean_name]

    matches: list[str] = difflib.get_close_matches(clean_name, lookup.keys(), n=1, cutoff=0.90)
    if matches:
        return lookup[matches[0]]

    return ""

# Django view to handle search requests. It retrieves query parameters from the request, performs a search using the web_search function, and filters results based on additional criteria such as finished status, date, priority, and assigned stitcher. The results are then rendered in the 'search_app/index.html' template along with any error messages.
# Get query parameters from the request, including 'q' for the search query, 'finished' for finished status, 'date' for filtering by date, 'priority' for sorting preference, 'assigned' for filtering by assignment status, and 'stitcher' for filtering by stitcher name. If both date and priority are specified, an error message is generated. The search results are filtered based on the provided criteria, and the final results are passed to the template for rendering.
# validate the query parameters and handle any errors. Some combinations of parameters may not be valid, such as specifying both a date and a priority. In such cases, an error message is generated and displayed to the user. The search results are filtered based on the provided criteria, including finished status, date, priority, assignment status, and stitcher name. The final results are passed to the template for rendering along with any error messages.
# If both date and priority are specified, an error message is generated. The search results are filtered based on the provided criteria, including finished status, date, priority, assignment status, and stitcher name. The final results are passed to the template for rendering along with any error messages.
# stitcher status of all is no compatible with the stitcher name filter, so if stitcher is specified, assigned must be either yes or no. If assigned is all and stitcher is specified, the results will be filtered by stitcher name only. The final results are passed to the template for rendering along with any error messages.
# if all parms are valid, the search results are filtered based on the provided criteria, including finished status, date, priority, assignment status, and stitcher name. The final results are passed to the template for rendering along with any error messages.

def search_view(request: HttpRequest) -> HttpResponse:
  query = request.GET.get('q', '').strip()
  finished = request.GET.get('finished', 'both')
  date = request.GET.get('date', '').strip()
  priority = request.GET.get('priority', 'no')
  assigned = request.GET.get('assigned', 'all')
  stitcher = request.GET.get('stitcher', '').strip()
  error = ''

  if date and priority == 'yes':
    error = (
        'Cannot filter by a specific date (YYMMDD) and sort by oldest priority'
        ' at the same time.'
    )
    results = []
  elif stitcher != "" and assigned == "all":
    error = (
        'Cannot filter by stitcher name when assigned status is set to "all".'
        ' Please select "Has Stitcher" for assigned status when filtering by stitcher name.'
    )
    results = []    
  else:
    results = web_search(
        query=query,
        search_finished=finished,
        search_date=date,
        search_priority=priority,
    )

  if results:
    stitcher_lookup: dict[str, str] = get_stitcher_lookup()
    for item in results:
      item['who_has'] = find_stitcher(
          str(item.get('name', '')), stitcher_lookup
      )

    if assigned == 'yes':
      results = [item for item in results if item.get('who_has')]
    elif assigned == 'no':
      results = [item for item in results if not item.get('who_has')]

    if stitcher:
      stitcher_lower = stitcher.lower()
      results = [
          item
          for item in results
          if item.get('who_has') and stitcher_lower in item['who_has'].lower()
      ]

  return render(
      request,
      'search_app/index.html',
      {
          'query': query,
          'finished': finished,
          'date': date,
          'priority': priority,
          'assigned': assigned,
          'stitcher': stitcher,
          'results': results,
          'error': error,
      },
  )
