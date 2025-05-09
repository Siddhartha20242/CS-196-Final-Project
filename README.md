The Quote Manager Application is a simple desktop program built with Python and tkinter. It lets you save, view, and organize your favorite 
quotes in an easy-to-use window. When you open the app, it reads all your saved quotes and user preferences from JSON files. If the files are missing,
 it creates fresh ones so you can start without any setup worries.

Inside the app, the main window shows one quote at a time with colorful pastel backgrounds that change randomly. You can click 
buttons to see the next, previous, or a random quote. This playful design makes browsing your collection feel fun. In addition, you can copy 
the displayed quote to your clipboard or rate it on a five-star scale. All these actions update the in-memory list of quotes immediately.

Below the main area, you will find tools to filter quotes by category or search by keywords. When you choose a category or enter text to search, 
the list of matching quotes appears on the side. Selecting any quote in that list opens a popup with its full text and author. This feature helps 
you quickly find specific quotes among hundreds.

At the bottom, there is a panel to add, edit, or delete quotes. You type in the quote text, the author’s name, and a category name. Adding or 
editing pushes your changes into the working list. Deleting removes the quote from the app. To save all changes permanently, you click the
“Save All” button. The app then writes the complete list back to quotes.json, ensuring nothing is lost between sessions.

We also added a menu bar with File, View, and Help menus. Under File, you can import or export quotes in CSV format, save changes, or exit 
the program. The View menu lets you check basic statistics like total quotes and toggle between light and dark themes. The Help menu gives an 
About dialog with version information.

Behind the scenes, helper functions handle reading and writing JSON or CSV files safely, with error logging to quote_app.log. If any file 
operations fail, the app logs the error and shows a warning to the user without crashing. Theme preferences and the last chosen category are 
stored in settings.json. This way, the app remembers how you like to work.

What this design did not include is a networked database or multi‑user sync. There is no user login system, so everyone shares the same local 
files. We also did not build animations or advanced visual transitions—only simple color changes. The app does not track quote history over time, 
nor does it automatically feature a "quote of the day." There is no backup or cloud integration out of the box.

In summary, the Quote Manager Application gives you an offline, easy, and colorful way to save and manage your favorite quotes. It covers basic
needs like browsing, searching, and organizing, while keeping the design straightforward and reliable. Further extensions can add cloud sync, 
user accounts, or more polished animations in the future.
