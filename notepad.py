import tkinter as tk
from tkinter import messagebox, filedialog, font as tkfont, colorchooser, simpledialog
from spellchecker import SpellChecker
import pyttsx3
import re
from datetime import datetime
import json
import os

# Initialize spell checker and text-to-speech
spell = SpellChecker()
spell.word_frequency.load_words(['mera', 'naam', 'ahsan', 'kaise', 'ho'])
engine = pyttsx3.init()

class EnhancedNotepadPro:
    def __init__(self, root):
        self.root = root
        self.root.title("📝 Enhanced Notepad Pro")
        self.root.geometry("1000x700")
        
        self.current_file = None
        self.dark_mode = False
        self.font_size = 14
        self.font_family = "Consolas"
        self.recent_files = []
        self.max_recent = 10
        self.config_file = "notepad_config.json"
        self.bookmarks = {}
        self.find_index = '1.0'
        self.show_line_numbers = True
        self.modified = False
        
        # Load settings
        self.load_settings()
        
        # Create UI
        self.create_menu()
        self.create_toolbar()
        self.create_text_area()
        self.create_status_bar()
        
        # Bind shortcuts
        self.bind_shortcuts()
        
        # Track changes
        self.text_area.bind('<KeyRelease>', self.update_status)
        self.text_area.bind('<ButtonRelease>', self.update_status)
        self.text_area.bind('<<Modified>>', self.on_modified)
        
        # Auto-save
        self.auto_save_interval = 180000  # 3 minutes
        self.schedule_auto_save()
        
        # Apply theme
        self.apply_theme()
        
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As", command=self.save_as_file)
        file_menu.add_separator()
        
        self.recent_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Recent Files", menu=self.recent_menu)
        self.update_recent_menu()
        
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # Edit Menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=self.cut, accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=self.copy, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=self.paste, accelerator="Ctrl+V")
        edit_menu.add_command(label="Select All", command=self.select_all, accelerator="Ctrl+A")
        edit_menu.add_separator()
        edit_menu.add_command(label="Find", command=self.find_text, accelerator="Ctrl+F")
        edit_menu.add_command(label="Replace", command=self.replace_text, accelerator="Ctrl+H")
        edit_menu.add_separator()
        edit_menu.add_command(label="Insert Date/Time", command=self.insert_datetime, accelerator="F5")
        
        # Format Menu
        format_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Format", menu=format_menu)
        format_menu.add_command(label="Font", command=self.change_font)
        format_menu.add_command(label="Increase Font", command=self.increase_font, accelerator="Ctrl++")
        format_menu.add_command(label="Decrease Font", command=self.decrease_font, accelerator="Ctrl+-")
        format_menu.add_separator()
        format_menu.add_command(label="Dark Mode", command=self.toggle_dark_mode, accelerator="Ctrl+D")
        
        # Tools Menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Spell Check", command=self.check_spelling)
        tools_menu.add_command(label="Grammar Check", command=self.grammar_check)
        tools_menu.add_separator()
        tools_menu.add_command(label="Speak Text", command=self.speak_text)
        tools_menu.add_command(label="Voice Settings", command=self.configure_voice)
        tools_menu.add_separator()
        tools_menu.add_command(label="Word Count", command=self.show_word_count)
        tools_menu.add_separator()
        tools_menu.add_command(label="UPPERCASE", command=self.to_uppercase)
        tools_menu.add_command(label="lowercase", command=self.to_lowercase)
        tools_menu.add_command(label="Title Case", command=self.to_titlecase)
        
        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Shortcuts", command=self.show_shortcuts)
        help_menu.add_command(label="About", command=self.show_about)
        
    def create_toolbar(self):
        self.toolbar = tk.Frame(self.root, bd=2, relief=tk.GROOVE, bg='#f0f0f0')
        self.toolbar.pack(side=tk.TOP, fill=tk.X)
        
        btn_style = {'padx': 8, 'pady': 5, 'relief': tk.FLAT, 'bg': '#e0e0e0'}
        
        tk.Button(self.toolbar, text="New", command=self.new_file, **btn_style).pack(side=tk.LEFT, padx=2)
        tk.Button(self.toolbar, text="Open", command=self.open_file, **btn_style).pack(side=tk.LEFT, padx=2)
        tk.Button(self.toolbar, text="Save", command=self.save_file, **btn_style).pack(side=tk.LEFT, padx=2)
        
        tk.Frame(self.toolbar, width=2, bd=1, relief=tk.SUNKEN).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        tk.Button(self.toolbar, text="Undo", command=self.undo, **btn_style).pack(side=tk.LEFT, padx=2)
        tk.Button(self.toolbar, text="Redo", command=self.redo, **btn_style).pack(side=tk.LEFT, padx=2)
        
        tk.Frame(self.toolbar, width=2, bd=1, relief=tk.SUNKEN).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        tk.Label(self.toolbar, text="Size:", bg='#f0f0f0').pack(side=tk.LEFT, padx=5)
        
        self.font_size_var = tk.StringVar(value=str(self.font_size))
        font_sizes = [8, 10, 12, 14, 16, 18, 20, 24, 28, 32]
        size_menu = tk.OptionMenu(self.toolbar, self.font_size_var, *font_sizes, 
                                   command=self.change_font_size)
        size_menu.config(relief=tk.FLAT, bg='#e0e0e0')
        size_menu.pack(side=tk.LEFT, padx=2)
        
        tk.Frame(self.toolbar, width=2, bd=1, relief=tk.SUNKEN).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        tk.Button(self.toolbar, text="Spell Check", command=self.check_spelling, **btn_style).pack(side=tk.LEFT, padx=2)
        tk.Button(self.toolbar, text="Speak", command=self.speak_text, **btn_style).pack(side=tk.LEFT, padx=2)
        
    def create_text_area(self):
        text_frame = tk.Frame(self.root)
        text_frame.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
        
        v_scrollbar = tk.Scrollbar(text_frame)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text_area = tk.Text(text_frame, wrap=tk.WORD, 
                                font=(self.font_family, self.font_size),
                                undo=True, maxundo=-1,
                                yscrollcommand=v_scrollbar.set,
                                relief=tk.FLAT,
                                padx=10, pady=10)
        self.text_area.pack(expand=True, fill=tk.BOTH)
        
        v_scrollbar.config(command=self.text_area.yview)
        
        self.text_area.tag_configure('found', background='yellow', foreground='black')
        self.text_area.tag_configure('misspelled', foreground='red', underline=True)
        
    def create_status_bar(self):
        self.status_frame = tk.Frame(self.root, bd=1, relief=tk.SUNKEN)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_bar = tk.Label(self.status_frame, text="Ready | Line: 1 | Col: 1", 
                                   anchor=tk.W, padx=5)
        self.status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.modified_label = tk.Label(self.status_frame, text="", width=10)
        self.modified_label.pack(side=tk.RIGHT)
        
    def bind_shortcuts(self):
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-f>', lambda e: self.find_text())
        self.root.bind('<Control-h>', lambda e: self.replace_text())
        self.root.bind('<Control-a>', lambda e: self.select_all())
        self.root.bind('<Control-plus>', lambda e: self.increase_font())
        self.root.bind('<Control-minus>', lambda e: self.decrease_font())
        self.root.bind('<Control-d>', lambda e: self.toggle_dark_mode())
        self.root.bind('<F5>', lambda e: self.insert_datetime())
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def new_file(self):
        if self.modified:
            response = messagebox.askyesnocancel("Save Changes", "Do you want to save changes?")
            if response:
                self.save_file()
            elif response is None:
                return
        
        self.text_area.delete(1.0, tk.END)
        self.current_file = None
        self.modified = False
        self.root.title("Enhanced Notepad Pro - New File")
        
    def open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    self.text_area.delete(1.0, tk.END)
                    self.text_area.insert(tk.END, file.read())
                self.current_file = file_path
                self.modified = False
                self.root.title(f"Enhanced Notepad Pro - {os.path.basename(file_path)}")
                self.add_to_recent(file_path)
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {str(e)}")
            
    def save_file(self):
        if self.current_file:
            try:
                with open(self.current_file, "w", encoding="utf-8") as file:
                    file.write(self.text_area.get(1.0, tk.END)[:-1])
                self.modified = False
                self.modified_label.config(text="")
                messagebox.showinfo("Save", "File saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {str(e)}")
        else:
            self.save_as_file()
            
    def save_as_file(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(self.text_area.get(1.0, tk.END)[:-1])
                self.current_file = file_path
                self.modified = False
                self.root.title(f"Enhanced Notepad Pro - {os.path.basename(file_path)}")
                self.add_to_recent(file_path)
                messagebox.showinfo("Save", "File saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {str(e)}")
    
    def add_to_recent(self, file_path):
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        self.recent_files.insert(0, file_path)
        if len(self.recent_files) > self.max_recent:
            self.recent_files.pop()
        self.update_recent_menu()
        self.save_settings()
    
    def update_recent_menu(self):
        self.recent_menu.delete(0, tk.END)
        if self.recent_files:
            for file_path in self.recent_files:
                self.recent_menu.add_command(
                    label=os.path.basename(file_path), 
                    command=lambda f=file_path: self.open_recent(f)
                )
        else:
            self.recent_menu.add_command(label="No recent files", state=tk.DISABLED)
    
    def open_recent(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, file.read())
            self.current_file = file_path
            self.modified = False
            self.root.title(f"Enhanced Notepad Pro - {os.path.basename(file_path)}")
        except:
            messagebox.showerror("Error", "File not found!")
    
    def on_modified(self, event=None):
        if self.text_area.edit_modified():
            self.modified = True
            self.modified_label.config(text="Modified")
            self.text_area.edit_modified(False)
    
    def on_closing(self):
        if self.modified:
            response = messagebox.askyesnocancel("Save Changes", "Save before closing?")
            if response:
                self.save_file()
                self.save_settings()
                self.root.destroy()
            elif response is False:
                self.save_settings()
                self.root.destroy()
        else:
            self.save_settings()
            self.root.destroy()
    
    def undo(self):
        try:
            self.text_area.edit_undo()
        except:
            pass
    
    def redo(self):
        try:
            self.text_area.edit_redo()
        except:
            pass
    
    def cut(self):
        self.text_area.event_generate("<<Cut>>")
    
    def copy(self):
        self.text_area.event_generate("<<Copy>>")
    
    def paste(self):
        self.text_area.event_generate("<<Paste>>")
    
    def select_all(self):
        self.text_area.tag_add(tk.SEL, "1.0", tk.END)
        self.text_area.mark_set(tk.INSERT, "1.0")
        return 'break'
    
    def find_text(self):
        search_window = tk.Toplevel(self.root)
        search_window.title("Find")
        search_window.geometry("400x150")
        
        tk.Label(search_window, text="Find what:").pack(pady=5)
        search_entry = tk.Entry(search_window, width=40)
        search_entry.pack(pady=5)
        search_entry.focus()
        
        def find_all():
            self.text_area.tag_remove('found', '1.0', tk.END)
            search_text = search_entry.get()
            
            if search_text:
                idx = '1.0'
                count = 0
                while True:
                    idx = self.text_area.search(search_text, idx, nocase=1, stopindex=tk.END)
                    if not idx:
                        break
                    lastidx = f'{idx}+{len(search_text)}c'
                    self.text_area.tag_add('found', idx, lastidx)
                    idx = lastidx
                    count += 1
                
                messagebox.showinfo("Find", f"Found {count} occurrence(s)")
        
        tk.Button(search_window, text="Find All", command=find_all, width=15).pack(pady=10)
    
    def replace_text(self):
        replace_window = tk.Toplevel(self.root)
        replace_window.title("Replace")
        replace_window.geometry("400x200")
        
        tk.Label(replace_window, text="Find:").pack(pady=5)
        find_entry = tk.Entry(replace_window, width=40)
        find_entry.pack(pady=5)
        
        tk.Label(replace_window, text="Replace with:").pack(pady=5)
        replace_entry = tk.Entry(replace_window, width=40)
        replace_entry.pack(pady=5)
        
        def replace_all():
            content = self.text_area.get(1.0, tk.END)
            new_content = content.replace(find_entry.get(), replace_entry.get())
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(1.0, new_content)
            messagebox.showinfo("Replace", "Replacement complete!")
        
        tk.Button(replace_window, text="Replace All", command=replace_all, width=15).pack(pady=10)
    
    def insert_datetime(self):
        now = datetime.now()
        datetime_str = now.strftime("%Y-%m-%d %H:%M:%S")
        self.text_area.insert(tk.INSERT, datetime_str)
    
    def change_font(self):
        font_window = tk.Toplevel(self.root)
        font_window.title("Font")
        font_window.geometry("300x200")
        
        tk.Label(font_window, text="Font Family:").pack(pady=5)
        
        font_listbox = tk.Listbox(font_window, height=8)
        for family in ['Consolas', 'Arial', 'Courier', 'Times', 'Verdana']:
            font_listbox.insert(tk.END, family)
        font_listbox.pack(pady=5)
        
        def apply_font():
            selection = font_listbox.curselection()
            if selection:
                self.font_family = font_listbox.get(selection[0])
                self.text_area.config(font=(self.font_family, self.font_size))
                font_window.destroy()
        
        tk.Button(font_window, text="Apply", command=apply_font).pack(pady=10)
    
    def change_font_size(self, size):
        self.font_size = int(size)
        self.text_area.config(font=(self.font_family, self.font_size))
    
    def increase_font(self):
        self.font_size += 2
        self.font_size_var.set(str(self.font_size))
        self.text_area.config(font=(self.font_family, self.font_size))
    
    def decrease_font(self):
        if self.font_size > 8:
            self.font_size -= 2
            self.font_size_var.set(str(self.font_size))
            self.text_area.config(font=(self.font_family, self.font_size))
    
    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()
    
    def apply_theme(self):
        if self.dark_mode:
            self.text_area.config(bg='#1e1e1e', fg='#d4d4d4', insertbackground='white')
        else:
            self.text_area.config(bg='white', fg='black', insertbackground='black')
    
    def speak_text(self):
        text = self.text_area.get(1.0, tk.END).strip()
        if text:
            try:
                engine.say(text)
                engine.runAndWait()
            except Exception as e:
                messagebox.showerror("Error", f"Speech error: {str(e)}")
        else:
            messagebox.showinfo("Speak", "No text to speak!")
    
    def configure_voice(self):
        voice_window = tk.Toplevel(self.root)
        voice_window.title("Voice Settings")
        voice_window.geometry("400x250")
        
        tk.Label(voice_window, text="Speech Rate:").pack(pady=10)
        rate_var = tk.IntVar(value=engine.getProperty('rate'))
        rate_slider = tk.Scale(voice_window, from_=50, to=300, orient=tk.HORIZONTAL, 
                              variable=rate_var, length=300)
        rate_slider.pack()
        
        def apply_settings():
            engine.setProperty('rate', rate_var.get())
            messagebox.showinfo("Success", "Voice settings applied!")
            voice_window.destroy()
        
        tk.Button(voice_window, text="Apply", command=apply_settings).pack(pady=10)
    
    def check_spelling(self):
        text = self.text_area.get(1.0, tk.END)
        words = re.findall(r'\b\w+\b', text)
        misspelled = spell.unknown(words)
        
        self.text_area.tag_remove('misspelled', '1.0', tk.END)
        
        if misspelled:
            for word in misspelled:
                idx = '1.0'
                while True:
                    idx = self.text_area.search(word, idx, nocase=1, stopindex=tk.END)
                    if not idx:
                        break
                    lastidx = f'{idx}+{len(word)}c'
                    self.text_area.tag_add('misspelled', idx, lastidx)
                    idx = lastidx
            
            misspelled_list = list(misspelled)[:20]
            msg = "Misspelled words:\n\n" + ", ".join(misspelled_list)
            if len(misspelled) > 20:
                msg += f"\n\n...and {len(misspelled) - 20} more"
            messagebox.showinfo("Spell Check", msg)
        else:
            messagebox.showinfo("Spell Check", "No spelling errors!")
    
    def grammar_check(self):
        text = self.text_area.get(1.0, tk.END).strip()
        if not text:
            messagebox.showinfo("Grammar Check", "No text to check!")
            return
        
        issues = []
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and not sentence[0].isupper():
                issues.append(f"Capitalize: '{sentence[:30]}...'")
        
        if issues:
            msg = f"Found {len(issues)} issue(s):\n\n" + "\n".join(issues[:10])
            messagebox.showinfo("Grammar Check", msg)
        else:
            messagebox.showinfo("Grammar Check", "No issues found!")
    
    def show_word_count(self):
        text = self.text_area.get(1.0, tk.END)
        words = len(re.findall(r'\b\w+\b', text))
        chars = len(text) - 1
        lines = text.count('\n')
        
        stats = f"""Statistics:

Words: {words}
Characters: {chars}
Lines: {lines}"""
        
        messagebox.showinfo("Word Count", stats)
    
    def to_uppercase(self):
        try:
            selected = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.text_area.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.text_area.insert(tk.INSERT, selected.upper())
        except:
            text = self.text_area.get(1.0, tk.END)
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(1.0, text.upper())
    
    def to_lowercase(self):
        try:
            selected = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.text_area.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.text_area.insert(tk.INSERT, selected.lower())
        except:
            text = self.text_area.get(1.0, tk.END)
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(1.0, text.lower())
    
    def to_titlecase(self):
        try:
            selected = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.text_area.delete(tk.SEL_FIRST, tk.SEL_LAST)
            self.text_area.insert(tk.INSERT, selected.title())
        except:
            text = self.text_area.get(1.0, tk.END)
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(1.0, text.title())
    
    def update_status(self, event=None):
        try:
            line, col = self.text_area.index(tk.INSERT).split('.')
            text = self.text_area.get(1.0, tk.END)
            words = len(re.findall(r'\b\w+\b', text))
            self.status_bar.config(text=f"Line: {line} | Col: {col} | Words: {words}")
        except:
            pass
    
    def schedule_auto_save(self):
        if self.modified and self.current_file:
            try:
                with open(self.current_file, "w", encoding="utf-8") as file:
                    file.write(self.text_area.get(1.0, tk.END)[:-1])
            except:
                pass
        self.root.after(self.auto_save_interval, self.schedule_auto_save)
    
    def save_settings(self):
        settings = {
            'recent_files': self.recent_files,
            'font_family': self.font_family,
            'font_size': self.font_size,
            'dark_mode': self.dark_mode
        }
        try:
            with open(self.config_file, 'w') as f:
                json.dump(settings, f)
        except:
            pass
    
    def load_settings(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    settings = json.load(f)
                    self.recent_files = settings.get('recent_files', [])
                    self.font_family = settings.get('font_family', 'Consolas')
                    self.font_size = settings.get('font_size', 14)
                    self.dark_mode = settings.get('dark_mode', False)
        except:
            pass
    
    def show_shortcuts(self):
        shortcuts = """Keyboard Shortcuts:

Ctrl+N - New File
Ctrl+O - Open File
Ctrl+S - Save File
Ctrl+F - Find
Ctrl+H - Replace
Ctrl+A - Select All
Ctrl++ - Zoom In
Ctrl+- - Zoom Out
Ctrl+D - Dark Mode
F5 - Insert Date/Time"""
        messagebox.showinfo("Shortcuts", shortcuts)
    
    def show_about(self):
        about = """Enhanced Notepad Pro
Version 3.0

A professional text editor with:
- Spell & Grammar Check
- Text-to-Speech
- Dark Mode
- Auto-save
- And much more!

Built with Python & Tkinter"""
        messagebox.showinfo("About", about)

# Main
if __name__ == "__main__":
    root = tk.Tk()
    app = EnhancedNotepadPro(root)
    root.mainloop()
