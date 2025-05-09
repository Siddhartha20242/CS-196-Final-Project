Quote Manager Overview
The Quote Manager app is a lightweight desktop tool built with Python and Tkinter that makes saving and browsing your favorite quotations a breeze. When you launch it, the program checks for two JSON files—one to store all your quotes and another to remember your theme preference and last-used category. If those files aren’t there yet, the app quietly creates them so you can dive right in.

At the top of the window, you’ll see one quote at a time set against a randomly chosen pastel background. Navigate through your collection with Previous, Next, or Random buttons, copy the current quote to your clipboard in one click, or rate it on a scale of one to five stars. Every action updates the in-memory list instantly so you never lose your place.

Along the left side, filters let you narrow down which quotes you see. Pick a category from the dropdown or type in a keyword to search quote text or author names—matching entries populate the list immediately. Click on any quote in that list to view its full text and author in a simple popup, making it easy to find exactly what you’re looking for.

Down below, an input panel lets you add brand-new quotes or tweak existing ones. Enter the quote text, the author’s name, and a category, then hit Add or Save. If a quote needs to go away, just select it and click Delete. When you’re happy with your edits, the Save All button writes everything back to quotes.json, keeping your collection safe between sessions.

The menu bar at the top groups file and view commands neatly:

File → Import or export CSV, save your work, or exit.

View → Toggle between light and dark themes or peek at basic stats (total quotes, categories, authors, and how many you’ve rated).

Help → Opens an About dialog with version info.

Under the hood, helper functions handle all JSON and CSV reading/writing, complete with error logging to quote_app.log. If something goes wrong with file I/O, the app logs the issue and shows you a warning instead of crashing. Your display preferences and last-picked category live in settings.json, so the app always remembers how you like to work.

This version doesn’t include cloud sync, user accounts, or a networked database—it’s strictly local. There are no fancy animations beyond the background color shifts, no “quote of the day” scheduler, and no automated backups. It’s a straightforward, reliable way to keep your favorite lines at your fingertips.

Getting Started
Install Python

Make sure you have Python 3.8+ installed.
pip install pyperclip
pyperclip is used for the “copy to clipboard” feature.

All other modules (tkinter, json, csv, logging, random, os) are part of the Python standard library.


First launch

The app creates quotes.json and settings.json in the same folder if they don’t already exist.

You’re ready to start adding, browsing, and rating quotes!

