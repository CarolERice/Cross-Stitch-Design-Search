Cross-Stitch Design Search Utility

> **Update:** Want a standalone desktop window with automatic backend startup? [Check out the Electron + JavaScript version here](https://github.com/CarolERice/Cross-Stitch-Design-Search-with-Electron-wrapper-and-js).


A utility to read all the Cross-Stitch Designs I have created and search through them in a variety of ways. It pairs directory scanning with a CSV tracking sheet so I can quickly check design status and model stitcher assignments from my desktop or phone.

Features

• Model Stitcher Visibility: Shows who, if anybody, currently has an unreleased design for model stitching.
• Design Name Search: Searches by part or all of a design name, creation date (YYMMDD), or completion status (Finished vs. WIP).
• Stitcher Assignment Filter: Filters for designs with or without a model stitcher assigned, or lists all unfinished designs a specific stitcher currently has.
• Partial Stitcher Search: Searches by partial stitcher name, returning all matching stitchers alongside the designs they are currently stitching.
• Priority Sorting: Sorts designs by oldest first to highlight older unfinished pieces.

How It Works

• Design Directories: Scans two main design directories—including any nested subdirectories of designs—to gather project names, creation dates, and completion status.
• Stitcher Data: Reads live model stitcher assignments directly from a local CSV file (current wips.csv) with typo-tolerant matching.
	Stitcher names are twitch/Discord names not real names
• Web Interface: Uses Django for the web interface, paired with custom HTML5 and CSS that adapts fluidly across desktop monitors and mobile browsers.

Running Locally

1. Activate the virtual environment from the project root (~/code/myproject):
source ~/.venv/bin/activate

2. Start the Django development server (allowing access from both this computer and devices on the local Wi-Fi network):bash
python manage.py runserver 0.0.0.0:8000

3. Open in a browser:
	• On this computer: Go to 'http://127.0.0.1:8000'
	• On an iPhone or other local device: Go to 'http://<computer-local-ip>:8000/' (find the IP with hostname -I).
4. Updating stitcher assignments: Export or overwrite search_app/current wips.csv at any time—changes appear on the next search without restarting the server.

Background

I have about 15 years of experience in COBOL, plus HTML5 and CSS for the web pages those systems displayed. This is the same kind of structured file-processing work translated into Python—the new part is learning the Python/Django stack, not learning how to program.

