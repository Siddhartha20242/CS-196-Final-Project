import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import csv
import random
import os
import datetime
import logging

# ==================== Configuration and Constants ====================
DATA_FILE = 'quotes.json'
SETTINGS_FILE = 'settings.json'
PASTEL_COLORS = ['#FFB3BA','#FFDFBA','#BAFFC9','#BAE1FF']
DARK_THEME = {'bg': '#2E2E2E', 'fg': '#FFFFFF', 'btn_bg': '#3C3C3C', 'btn_fg': '#FFFFFF'}
LIGHT_THEME = {'bg': '#FFFFFF', 'fg': '#000000', 'btn_bg': '#E0E0E0', 'btn_fg': '#000000'}


logging.basicConfig(filename='quote_app.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')



def load_json_file(path, default):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.warning(f"Could not load {path}: {e}")
        return default


def save_json_file(path, data):
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        logging.error(f"Error saving {path}: {e}")
        return False


def export_to_csv(path, quotes):
    try:
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Quote','Author','Category','Rating'])
            for q in quotes:
                writer.writerow([q['quote'], q['author'], q['category'], q.get('rating', '')])
        return True
    except Exception as e:
        logging.error(f"CSV export failed: {e}")
        return False


def import_from_csv(path):
    imported = []
    try:
        with open(path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                imported.append({
                    'quote': row.get('Quote','').strip(),
                    'author': row.get('Author','').strip(),
                    'category': row.get('Category','').strip(),
                    'rating': int(row.get('Rating') or 0)
                })
        return imported
    except Exception as e:
        logging.error(f"CSV import failed: {e}")
        return imported



class QuoteApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("✨ Advanced Quote Manager ✨")
        self.geometry("800x600")
        self.resizable(True, True)

        # Load data and settings
        self.quotes = load_json_file(DATA_FILE, [])
        self.settings = load_json_file(SETTINGS_FILE, {'theme': 'light', 'last_category': ''})
        self.categories = sorted({q['category'] for q in self.quotes})
        self.authors = sorted({q['author'] for q in self.quotes})

        # Build UI
        self.configure_ui()
        self.create_menu()
        self.create_widgets()
        self.apply_theme()
        self.show_random_quote()

  
    def configure_ui(self):
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('TButton', font=('Helvetica', 11), padding=5)
        style.configure('TLabel', font=('Helvetica', 11))

   
    def create_menu(self):
        menubar = tk.Menu(self)
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label='Import CSV', command=self.import_csv)
        file_menu.add_command(label='Export CSV', command=self.export_csv)
        file_menu.add_separator()
        file_menu.add_command(label='Save', command=self.save_all)
        file_menu.add_command(label='Exit', command=self.quit)
        menubar.add_cascade(label='File', menu=file_menu)
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label='Stats', command=self.show_stats)
        view_menu.add_command(label='Toggle Theme', command=self.toggle_theme)
        menubar.add_cascade(label='View', menu=view_menu)
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label='About', command=self.show_about)
        menubar.add_cascade(label='Help', menu=help_menu)

        self.config(menu=menubar)


    def create_widgets(self):
     
        self.top_frame = ttk.Frame(self)
        self.top_frame.pack(fill='x', padx=10, pady=10)

        self.quote_label = tk.Label(self.top_frame, text='', wraplength=760,
                                    justify='center', font=('Comic Sans MS', 16, 'italic'),
                                    bd=2, relief='solid', padx=10, pady=10)
        self.quote_label.pack(fill='x')

        btn_frame = ttk.Frame(self.top_frame)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text='⏮ Previous', command=self.show_prev_quote).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text='🔀 Random', command=self.show_random_quote).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text='⏭ Next', command=self.show_next_quote).grid(row=0, column=2, padx=5)
        ttk.Button(btn_frame, text='⭐ Rate', command=self.rate_current).grid(row=0, column=3, padx=5)
        ttk.Button(btn_frame, text='📋 Copy', command=self.copy_to_clipboard).grid(row=0, column=4, padx=5)

   
        middle = ttk.Frame(self)
        middle.pack(fill='both', expand=True, padx=10, pady=10)
        # Filters pane
        filter_pane = ttk.LabelFrame(middle, text='Filters', width=200)
        filter_pane.pack(side='left', fill='y', padx=5)
        ttk.Label(filter_pane, text='Category:').pack(anchor='w', padx=5, pady=2)
        self.category_var = tk.StringVar(value=self.settings.get('last_category',''))
        self.category_combo = ttk.Combobox(filter_pane, textvariable=self.category_var,
                                           values=self.categories, state='readonly')
        self.category_combo.pack(fill='x', padx=5)
        ttk.Button(filter_pane, text='Apply', command=self.filter_quotes).pack(pady=5)

        ttk.Label(filter_pane, text='Search Text:').pack(anchor='w', padx=5, pady=2)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(filter_pane, textvariable=self.search_var)
        search_entry.pack(fill='x', padx=5)
        ttk.Button(filter_pane, text='Search', command=self.search_quotes).pack(pady=5)


        list_pane = ttk.Frame(middle)
        list_pane.pack(side='right', fill='both', expand=True)
        self.listbox = tk.Listbox(list_pane, font=('Arial', 11))
        self.listbox.pack(fill='both', expand=True)
        self.listbox.bind('<<ListboxSelect>>', self.on_select)


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

        ttk.Button(bottom, text='➕ Add', command=self.add_quote).grid(row=2, column=0, pady=5)
        ttk.Button(bottom, text='✏️ Edit', command=self.edit_quote).grid(row=2, column=1)
        ttk.Button(bottom, text='🗑️ Delete', command=self.delete_quote).grid(row=2, column=2)
        ttk.Button(bottom, text='💾 Save All', command=self.save_all).grid(row=2, column=3)

   
    def apply_theme(self):
        theme = self.settings.get('theme','light')
        colors = LIGHT_THEME if theme=='light' else DARK_THEME
        self.configure(bg=colors['bg'])
        for widget in self.winfo_children():
            try:
                widget.configure(bg=colors['bg'], fg=colors['fg'])
            except:
                pass

    def toggle_theme(self):
        current = self.settings.get('theme','light')
        self.settings['theme'] = 'dark' if current=='light' else 'light'
        save_json_file(SETTINGS_FILE, self.settings)
        self.apply_theme()

 
    def show_random_quote(self):
        if not self.quotes:
            self.quote_label.config(text="No quotes available!")
            return
        idx = random.randrange(len(self.quotes))
        self.display_quote(idx)

    def show_next_quote(self):
        self._current = (self._current + 1) % len(self.quotes)
        self.display_quote(self._current)

    def show_prev_quote(self):
        self._current = (self._current - 1) % len(self.quotes)
        self.display_quote(self._current)

    def display_quote(self, index):
        self._current = index
        q = self.quotes[index]
        bg = random.choice(PASTEL_COLORS)
        self.quote_label.config(text=f'“{q["quote"]}”\n\n— {q["author"]}', bg=bg)


    def add_quote(self):
        quote = self.new_quote_var.get().strip()
        author = self.new_author_var.get().strip()
        category = self.new_category_var.get().strip()
        if not (quote and author and category):
            messagebox.showwarning("Error","All fields are required.")
            return
        new_q = { 'quote':quote, 'author':author, 'category':category, 'rating':0 }
        self.quotes.append(new_q)
        self.categories = sorted({q['category'] for q in self.quotes})
        self.authors = sorted({q['author'] for q in self.quotes})
        self.category_combo['values'] = self.categories
        self.listbox.insert(tk.END, f"“{quote}” — {author}")
        self.clear_inputs()
        logging.info(f"Added quote: {quote}")

    def edit_quote(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("Edit","Select a quote from the list first.")
            return
        idx = sel[0]
        q = self.filtered[idx]
        # Populate fields for editing
        self.new_quote_var.set(q['quote'])
        self.new_author_var.set(q['author'])
        self.new_category_var.set(q['category'])
 
        self._edit_index = self.quotes.index(q)
        self.root_save = ttk.Button(self, text='💾 Save Edit', command=self.save_edit)
        self.root_save.pack()

    def save_edit(self):
        idx = self._edit_index
        self.quotes[idx]['quote'] = self.new_quote_var.get().strip()
        self.quotes[idx]['author'] = self.new_author_var.get().strip()
        self.quotes[idx]['category'] = self.new_category_var.get().strip()
        self.refresh_list()
        self.clear_inputs()
        self.root_save.destroy()
        logging.info(f"Edited quote at index {idx}")

    def delete_quote(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("Delete","Select a quote to delete.")
            return
        idx = sel[0]
        q = self.filtered.pop(idx)
        self.quotes.remove(q)
        self.listbox.delete(idx)
        logging.info(f"Deleted quote: {q}")

    def clear_inputs(self):
        self.new_quote_var.set('')
        self.new_author_var.set('')
        self.new_category_var.set('')

    def filter_quotes(self):
        cat = self.category_var.get().strip()
        self.settings['last_category'] = cat
        save_json_file(SETTINGS_FILE, self.settings)
        self.filtered = [q for q in self.quotes if q['category']==cat] if cat else list(self.quotes)
        self.refresh_list()

    def search_quotes(self):
        term = self.search_var.get().strip().lower()
        self.filtered = [q for q in self.quotes if term in q['quote'].lower() or term in q['author'].lower()]
        self.refresh_list()

    def refresh_list(self):
        self.listbox.delete(0, tk.END)
        for q in self.filtered:
            self.listbox.insert(tk.END, f"“{q['quote']}” — {q['author']}")

    def on_select(self, event):
        pass 
    def rate_current(self):
        rating = tk.simpledialog.askinteger("Rate Quote","Rate 1-5 stars:",minvalue=1,maxvalue=5)
        if rating:
            self.quotes[self._current]['rating'] = rating
            logging.info(f"Rated quote {self._current} as {rating}")
            messagebox.showinfo("Thanks!",f"Quote rated {rating} stars.")

    def copy_to_clipboard(self):
        text = self.quote_label.cget('text')
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("Copied","Quote copied to clipboard.")

  
    def export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV Files','*.csv')])
        if path and export_to_csv(path, self.quotes):
            messagebox.showinfo("Exported","Quotes exported successfully.")

    def import_csv(self):
        path = filedialog.askopenfilename(filetypes=[('CSV Files','*.csv')])
        if path:
            imported = import_from_csv(path)
            self.quotes.extend(imported)
            self.categories = sorted({q['category'] for q in self.quotes})
            self.category_combo['values'] = self.categories
            logging.info(f"Imported {len(imported)} quotes from CSV")
            messagebox.showinfo("Imported",f"{len(imported)} quotes imported.")
            self.filter_quotes()


    def save_all(self):
        if save_json_file(DATA_FILE, self.quotes):
            messagebox.showinfo("Saved","All changes saved.")

    def show_about(self):
        messagebox.showinfo("About","Advanced Quote Manager\nVersion 1.0\nBy Your Name")

    def show_stats(self):
        total = len(self.quotes)
        cats = len(self.categories)
        authors = len(self.authors)
        rated = sum(1 for q in self.quotes if q.get('rating',0)>0)
        stats = f"Total Quotes: {total}\nCategories: {cats}\nAuthors: {authors}\nRated: {rated}"
        messagebox.showinfo("Stats", stats)


if __name__ == '__main__':

    if not os.path.exists(DATA_FILE): save_json_file(DATA_FILE, [])
    if not os.path.exists(SETTINGS_FILE): save_json_file(SETTINGS_FILE, {'theme':'light','last_category':''})
    app = QuoteApp()
    app.mainloop()
