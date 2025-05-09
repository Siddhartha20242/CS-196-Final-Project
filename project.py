import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import json
import csv
import random
import os
import logging

# Configuration and constants
DATA_FILE = 'quotes.json'
SETTINGS_FILE = 'settings.json'
PASTEL_COLORS = ['#FFB3BA', '#FFDFBA', '#BAFFC9', '#BAE1FF']
DARK_THEME = {'bg': '#2E2E2E', 'fg': '#FFFFFF', 'btn_bg': '#3C3C3C', 'btn_fg': '#FFFFFF'}
LIGHT_THEME = {'bg': '#FFFFFF', 'fg': '#000000', 'btn_bg': '#E0E0E0', 'btn_fg': '#000000'}

logging.basicConfig(filename='quote_app.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def load_json_file(path, default):
    """Load JSON from path or return default if failed."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.warning(f"Could not load {path}: {e}")
        return default


def save_json_file(path, data):
    """Save data as JSON to path. Returns True on success."""
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        logging.error(f"Error saving {path}: {e}")
        return False


def export_to_csv(path, quotes):
    """Export list of quotes to CSV at path. Returns True on success."""
    try:
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Quote', 'Author', 'Category', 'Rating'])
            for q in quotes:
                writer.writerow([q['quote'], q['author'], q['category'], q.get('rating', '')])
        return True
    except Exception as e:
        logging.error(f"CSV export failed: {e}")
        return False


def import_from_csv(path):
    """Import quotes from CSV at path. Returns list of quote dicts."""
    imported = []
    try:
        with open(path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                imported.append({
                    'quote': row.get('Quote', '').strip(),
                    'author': row.get('Author', '').strip(),
                    'category': row.get('Category', '').strip(),
                    'rating': int(row.get('Rating') or 0)
                })
        return imported
    except Exception as e:
        logging.error(f"CSV import failed: {e}")
        return imported


class QuoteApp(tk.Tk):
    """Main application window for managing quotes."""

    def __init__(self):
        """Initialize the application, load data, and build the UI."""
        super().__init__()
        self.title("Quote Manager")
        self.geometry("800x600")
        self.resizable(True, True)

        self.quotes = load_json_file(DATA_FILE, [])
        self.settings = load_json_file(SETTINGS_FILE, {'theme': 'light', 'last_category': ''})
        self.categories = sorted({q['category'] for q in self.quotes})
        self.authors = sorted({q['author'] for q in self.quotes})
        self.filtered = list(self.quotes)
        self.edit_mode = False

        self._configure_style()
        self._create_menu()
        self._build_widgets()
        self.apply_theme()
        self.show_random_quote()

    def _configure_style(self):
        """Configure ttk styles for consistency."""
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('TButton', font=('Helvetica', 11), padding=5)
        style.configure('TLabel', font=('Helvetica', 11))

    def _create_menu(self):
        """Build the application menu bar."""
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label='Import CSV', command=self.import_csv)
        file_menu.add_command(label='Export CSV', command=self.export_csv)
        file_menu.add_separator()
        file_menu.add_command(label='Save', command=self.save_all)
        file_menu.add_command(label='Exit', command=self.quit)
        menubar.add_cascade(label='File', menu=file_menu)

        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label='Stats', command=self.show_stats)
        view_menu.add_command(label='Toggle Theme', command=self.toggle_theme)
        menubar.add_cascade(label='View', menu=view_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label='About', command=self.show_about)
        menubar.add_cascade(label='Help', menu=help_menu)

        self.config(menu=menubar)

    def _build_widgets(self):
        """Build and arrange all main UI components."""
        self._build_top_frame()
        self._build_middle_frame()
        self._build_bottom_frame()

    def _build_top_frame(self):
        """Create top area with quote display and navigation buttons."""
        self.top_frame = ttk.Frame(self)
        self.top_frame.pack(fill='x', padx=10, pady=10)

        self.quote_label = tk.Label(
            self.top_frame,
            text='', wraplength=760,
            justify='center', font=('Arial', 14, 'italic'),
            bd=2, relief='solid', padx=10, pady=10
        )
        self.quote_label.pack(fill='x')

        btn_frame = ttk.Frame(self.top_frame)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text='⏮ Previous', command=self.show_prev_quote).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text='🔀 Random',  command=self.show_random_quote).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text='⏭ Next',    command=self.show_next_quote).grid(row=0, column=2, padx=5)
        ttk.Button(btn_frame, text='⭐ Rate',    command=self.rate_current).grid(row=0, column=3, padx=5)
        ttk.Button(btn_frame, text='📋 Copy',    command=self.copy_to_clipboard).grid(row=0, column=4, padx=5)

    def _build_middle_frame(self):
        """Create middle area with filters and list of quotes."""
        middle = ttk.Frame(self)
        middle.pack(fill='both', expand=True, padx=10, pady=10)

        filter_pane = ttk.LabelFrame(middle, text='Filters', width=200)
        filter_pane.pack(side='left', fill='y', padx=5)
        ttk.Label(filter_pane, text='Category:').pack(anchor='w', padx=5, pady=2)
        self.category_var = tk.StringVar(value=self.settings.get('last_category',''))
        self.category_combo = ttk.Combobox(
            filter_pane, textvariable=self.category_var,
            values=self.categories, state='readonly'
        )
        self.category_combo.pack(fill='x', padx=5)
        ttk.Button(filter_pane, text='Apply', command=self.filter_quotes).pack(pady=5)

        ttk.Label(filter_pane, text='Search:').pack(anchor='w', padx=5, pady=2)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(filter_pane, textvariable=self.search_var)
        search_entry.pack(fill='x', padx=5)
        ttk.Button(filter_pane, text='Search', command=self.search_quotes).pack(pady=5)

        list_pane = ttk.Frame(middle)
        list_pane.pack(side='right', fill='both', expand=True)
        self.listbox = tk.Listbox(list_pane, font=('Arial', 11))
        self.listbox.pack(fill='both', expand=True)
        self.listbox.bind('<<ListboxSelect>>', self.on_select)

    def _build_bottom_frame(self):
        """Create bottom area for adding/editing quotes."""
        bottom = ttk.LabelFrame(self, text='Manage Quote')
        bottom.pack(fill='x', padx=10, pady=10)

        ttk.Label(bottom, text='Quote:').grid(row=0, column=0, sticky='e')
        self.new_quote_var = tk.StringVar()
        ttk.Entry(bottom, textvariable=self.new_quote_var, width=80).grid(row=0, column=1, columnspan=3, pady=2)

        ttk.Label(bottom, text='Author:').grid(row=1, column=0, sticky='e')
        self.new_author_var = tk.StringVar()
        ttk.Entry(bottom, textvariable=self.new_author_var).grid(row=1, column=1, pady=2)

        ttk.Label(bottom, text='Category:').grid(row=1, column=2, sticky='e')
        self.new_category_var = tk.StringVar()
        ttk.Entry(bottom, textvariable=self.new_category_var).grid(row=1, column=3, pady=2)

        self.add_button = ttk.Button(bottom, text='➕ Add', command=self.add_or_save)
        self.add_button.grid(row=2, column=0, pady=5)
        ttk.Button(bottom, text='✏️ Edit', command=self.prepare_edit).grid(row=2, column=1)
        ttk.Button(bottom, text='🗑️ Delete', command=self.delete_quote).grid(row=2, column=2)
        ttk.Button(bottom, text='💾 Save All', command=self.save_all).grid(row=2, column=3)

    def apply_theme(self):
        """Apply light or dark theme based on settings."""
        theme = self.settings.get('theme','light')
        colors = LIGHT_THEME if theme=='light' else DARK_THEME
        self.configure(bg=colors['bg'])
        for widget in self.winfo_children():
            try:
                widget.configure(bg=colors['bg'], fg=colors['fg'])
            except:
                pass

    def toggle_theme(self):
        """Switch between light and dark themes and save setting."""
        current = self.settings.get('theme','light')
        self.settings['theme'] = 'dark' if current=='light' else 'light'
        save_json_file(SETTINGS_FILE, self.settings)
        self.apply_theme()

    def show_random_quote(self):
        """Display a random quote from the list."""
        if not self.quotes:
            self.quote_label.config(text="No quotes available!")
            return
        idx = random.randrange(len(self.quotes))
        self.display_quote(idx)

    def show_next_quote(self):
        """Display the next quote in sequence."""
        self._current = (self._current + 1) % len(self.quotes)
        self.display_quote(self._current)

    def show_prev_quote(self):
        """Display the previous quote in sequence."""
        self._current = (self._current - 1) % len(self.quotes)
        self.display_quote(self._current)

    def display_quote(self, index):
        """Update the quote label to show the quote at index."""
        self._current = index
        q = self.quotes[index]
        bg = random.choice(PASTEL_COLORS)
        self.quote_label.config(text=f'“{q["quote"]}”\n\n— {q["author"]}', bg=bg)

    def add_or_save(self):
        """Add a new quote or save edits depending on edit_mode."""
        text = 'Save' if self.edit_mode else 'Add'
        if self.edit_mode:
            self._save_edit()
        else:
            self._add_quote()
        self.add_button.config(text='➕ Add')
        self.edit_mode = False

    def _add_quote(self):
        """Validate inputs and append a new quote."""
        quote = self.new_quote_var.get().strip()
        author = self.new_author_var.get().strip()
        category = self.new_category_var.get().strip()
        if not (quote and author and category):
            messagebox.showwarning("Error", "All fields are required.")
            return
        new_q = {'quote': quote, 'author': author, 'category': category, 'rating': 0}
        self.quotes.append(new_q)
        self._refresh_categories()
        self.filtered.append(new_q)
        self.listbox.insert(tk.END, f"“{quote}” — {author}")
        self._clear_inputs()
        logging.info(f"Added quote: {quote}")

    def prepare_edit(self):
        """Populate inputs for editing the selected quote."""
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("Edit", "Select a quote first.")
            return
        idx = sel[0]
        q = self.filtered[idx]
        self.new_quote_var.set(q['quote'])
        self.new_author_var.set(q['author'])
        self.new_category_var.set(q['category'])
        self._edit_index = self.quotes.index(q)
        self.add_button.config(text='💾 Save')
        self.edit_mode = True

    def _save_edit(self):
        """Apply edits to the previously selected quote."""
        idx = self._edit_index
        self.quotes[idx]['quote'] = self.new_quote_var.get().strip()
        self.quotes[idx]['author'] = self.new_author_var.get().strip()
        self.quotes[idx]['category'] = self.new_category_var.get().strip()
        self.refresh_list()
        self._clear_inputs()
        logging.info(f"Edited quote at index {idx}")

    def delete_quote(self):
        """Remove the selected quote from data and list."""
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("Delete", "Select a quote to delete.")
            return
        idx = sel[0]
        q = self.filtered.pop(idx)
        self.quotes.remove(q)
        self.listbox.delete(idx)
        logging.info(f"Deleted quote: {q}")

    def filter_quotes(self):
        """Filter quotes by selected category."""
        cat = self.category_var.get().strip()
        self.settings['last_category'] = cat
        save_json_file(SETTINGS_FILE, self.settings)
        self.filtered = [q for q in self.quotes if q['category'] == cat] if cat else list(self.quotes)
        self.refresh_list()

    def search_quotes(self):
        """Filter quotes by search term in quote text or author."""
        term = self.search_var.get().strip().lower()
        self.filtered = [q for q in self.quotes if term in q['quote'].lower() or term in q['author'].lower()]
        self.refresh_list()

    def refresh_list(self):
        """Refresh the listbox display from filtered quotes."""
        self.listbox.delete(0, tk.END)
        for q in self.filtered:
            self.listbox.insert(tk.END, f"“{q['quote']}” — {q['author']}")

    def on_select(self, event):
        """Handle listbox selection (placeholder)."""
        pass

    def rate_current(self):
        """Prompt user to rate the current quote."""
        rating = simpledialog.askinteger("Rate Quote", "Rate 1-5 stars:", minvalue=1, maxvalue=5)
        if rating:
            self.quotes[self._current]['rating'] = rating
            logging.info(f"Rated quote {self._current} as {rating}")
            messagebox.showinfo("Thanks!", f"Quote rated {rating} stars.")

    def copy_to_clipboard(self):
        """Copy current quote text to clipboard."""
        text = self.quote_label.cget('text')
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("Copied", "Quote copied to clipboard.")

    def export_csv(self):
        """Ask for path and export quotes as CSV."""
        path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV Files', '*.csv')])
        if path and export_to_csv(path, self.quotes):
            messagebox.showinfo("Exported", "Quotes exported successfully.")

    def import_csv(self):
        """Ask for CSV path and import quotes into the list."""
        path = filedialog.askopenfilename(filetypes=[('CSV Files', '*.csv')])
        if path:
            imported = import_from_csv(path)
            self.quotes.extend(imported)
            self._refresh_categories()
            logging.info(f"Imported {len(imported)} quotes from CSV")
            messagebox.showinfo("Imported", f"{len(imported)} quotes imported.")
            self.filter_quotes()

    def _refresh_categories(self):
        """Update category/autocomplete lists after data change."""
        self.categories = sorted({q['category'] for q in self.quotes})
        self.authors = sorted({q['author'] for q in self.quotes})
        self.category_combo['values'] = self.categories

    def save_all(self):
        """Save all quotes to JSON file."""
        if save_json_file(DATA_FILE, self.quotes):
            messagebox.showinfo("Saved", "All changes saved.")

    def show_about(self):
        """Display about dialog."""
        messagebox.showinfo("About", "Quote Manager v1.0\nBy Your Name")

    def show_stats(self):
        """Display basic statistics of quote collection."""
        total = len(self.quotes)
        cats = len(self.categories)
        authors = len(self.authors)
        rated = sum(1 for q in self.quotes if q.get('rating', 0) > 0)
        stats = f"Total Quotes: {total}\nCategories: {cats}\nAuthors: {authors}\nRated: {rated}"
        messagebox.showinfo("Stats", stats)


if __name__ == '__main__':
    if not os.path.exists(DATA_FILE):
        save_json_file(DATA_FILE, [])
    if not os.path.exists(SETTINGS_FILE):
        save_json_file(SETTINGS_FILE, {'theme': 'light', 'last_category': ''})
    app = QuoteApp()
    app.mainloop()
