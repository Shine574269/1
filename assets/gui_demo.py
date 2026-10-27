"""
TED Talks Information Retrieval System - GUI Version
Create visual desktop application using tkinter

=== KEY INFORMATION RETRIEVAL CONCEPTS IMPLEMENTED ===

[Query Processing] - User query input and preprocessing
[Vocabulary] - Display vocabulary statistics and features
[Index Construction] - System initialization with index building
[Weighting] - TF-IDF weighting visualization in results
[Evaluation] - Result ranking and similarity scoring display

This GUI provides an interactive interface to demonstrate:
- Text query search with TF-IDF ranking
- Similar talk recommendations using cosine similarity
- Dataset statistics including vocabulary size
- Real-time evaluation of search results
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from ted_retrieval_system import TEDRetrievalSystem
import threading

class TEDRetrievalGUI:
    """TED Retrieval System GUI"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("TED Talks Information Retrieval System")
        self.root.geometry("1000x700")
        
        # Initialize system
        self.system = None
        self.rec_search_results = []
        self.init_system()
        
        # Create interface
        self.create_widgets()
        self.setup_styles()
    
    def init_system(self):
        """Initialize retrieval system"""
        try:
            self.system = TEDRetrievalSystem('dataset.csv')
        except Exception as e:
            messagebox.showerror("Error", f"System initialization failed: {str(e)}")
    
    def setup_styles(self):
        """Setup interface styles"""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), foreground='#2c3e50')
        style.configure('Subtitle.TLabel', font=('Arial', 12), foreground='#34495e')
    
    def create_widgets(self):
        """Create interface widgets"""
        main_container = ttk.Frame(self.root, padding="10")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(2, weight=1)
        
        # Header
        header_frame = ttk.Frame(main_container)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(header_frame, text=" TED Talks Information Retrieval System", 
                 style='Title.TLabel').pack()
        ttk.Label(header_frame, text="Intelligent Lecture Search and Recommendation System based on TF-IDF",
                 style='Subtitle.TLabel').pack()
        
        # Notebook tabs
        self.notebook = ttk.Notebook(main_container)
        self.notebook.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Create tabs
        self.create_search_tab()
        self.create_recommend_tab()
        self.create_browse_tab()
        self.create_about_tab()
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(main_container, textvariable=self.status_var, 
                 relief=tk.SUNKEN, anchor=tk.W).grid(row=3, column=0, sticky=(tk.W, tk.E))
    
    def create_search_tab(self):
        """Create search tab"""
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text=" Text Search")
        
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(2, weight=1)
        
        # Input area
        input_frame = ttk.LabelFrame(frame, text="Enter Query", padding="10")
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(0, weight=1)
        
        self.search_entry = ttk.Entry(input_frame, font=('Arial', 11))
        self.search_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        self.search_entry.bind('<Return>', lambda e: self.perform_search())
        
        ttk.Button(input_frame, text=" Search", 
                  command=self.perform_search).grid(row=0, column=1)
        
        # Example queries
        examples_frame = ttk.Frame(input_frame)
        examples_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        ttk.Label(examples_frame, text="Examples:").pack(side=tk.LEFT)
        
        for example in ["education", "climate change", "AI", "design"]:
            ttk.Button(examples_frame, text=example, 
                      command=lambda e=example: self.set_query(e)).pack(side=tk.LEFT, padx=5)
        
        # Options
        options_frame = ttk.Frame(frame)
        options_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        ttk.Label(options_frame, text="Number of results:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_top_k = tk.IntVar(value=10)
        ttk.Spinbox(options_frame, from_=1, to=50, 
                   textvariable=self.search_top_k, width=10).pack(side=tk.LEFT)
        
        # Results area
        results_frame = ttk.LabelFrame(frame, text="Search Results", padding="10")
        results_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        self.search_results = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, 
                                                        font=('Consolas', 10))
        self.search_results.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.search_results.tag_config('title', font=('Arial', 11, 'bold'), foreground='#2980b9')
        self.search_results.tag_config('info', foreground='#7f8c8d')
        self.search_results.tag_config('score', foreground='#27ae60', font=('Arial', 10, 'bold'))
    
    def create_recommend_tab(self):
        """Create recommendation tab"""
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="🔍 Similar Recommendations")
        
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(3, weight=1)
        
        ttk.Label(frame, text="Search for talks first, then click results to get recommendations", 
                 font=('Arial', 10)).grid(row=0, column=0, pady=(0, 10))
        
        # Search area
        search_frame = ttk.LabelFrame(frame, text="Search Talks", padding="10")
        search_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        search_frame.columnconfigure(0, weight=1)
        
        self.rec_search_entry = ttk.Entry(search_frame, font=('Arial', 11))
        self.rec_search_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        self.rec_search_entry.bind('<Return>', lambda e: self.search_for_recommend())
        
        ttk.Button(search_frame, text="🔍 Search", 
                  command=self.search_for_recommend).grid(row=0, column=1)
        
        # Search results list
        list_frame = ttk.LabelFrame(frame, text="Search Results (Click for Recommendations)", padding="10")
        list_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        self.rec_listbox = tk.Listbox(list_frame, height=5, font=('Arial', 10))
        self.rec_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.rec_listbox.bind('<<ListboxSelect>>', self.on_talk_select)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.rec_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.rec_listbox.config(yscrollcommand=scrollbar.set)
        
        # Recommendation results
        rec_frame = ttk.LabelFrame(frame, text="Similar Talk Recommendations", padding="10")
        rec_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        rec_frame.columnconfigure(0, weight=1)
        rec_frame.rowconfigure(0, weight=1)
        
        self.rec_results = scrolledtext.ScrolledText(rec_frame, wrap=tk.WORD, font=('Consolas', 10))
        self.rec_results.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.rec_results.tag_config('title', font=('Arial', 11, 'bold'), foreground='#2980b9')
        self.rec_results.tag_config('info', foreground='#7f8c8d')
        self.rec_results.tag_config('similarity', foreground='#e74c3c', font=('Arial', 10, 'bold'))
    
    def create_browse_tab(self):
        """Create browse tab"""
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="📊 Data Browse")
        
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)
        
        # Button area
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(btn_frame, text="📊 Statistics", command=self.show_statistics).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🔥 Popular", command=self.show_popular).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🆕 Recent", command=self.show_recent).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(btn_frame, text="Speaker:").pack(side=tk.LEFT, padx=(20, 5))
        self.speaker_entry = ttk.Entry(btn_frame, width=20)
        self.speaker_entry.pack(side=tk.LEFT, padx=5)
        self.speaker_entry.bind('<Return>', lambda e: self.search_by_speaker())
        ttk.Button(btn_frame, text="Search", command=self.search_by_speaker).pack(side=tk.LEFT, padx=5)
        
        # Results area
        results_frame = ttk.LabelFrame(frame, text="Browse Results", padding="10")
        results_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        self.browse_results = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, font=('Consolas', 10))
        self.browse_results.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.browse_results.tag_config('header', font=('Arial', 12, 'bold'), foreground='#2c3e50')
        self.browse_results.tag_config('title', font=('Arial', 11, 'bold'), foreground='#2980b9')
        self.browse_results.tag_config('info', foreground='#7f8c8d')
    
    def create_about_tab(self):
        """Create about tab"""
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="ℹ️ About")
        
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        
        about_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, font=('Arial', 10))
        about_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        content = """
TED Talks Information Retrieval System v1.0
========================================

Course: INT309 Multimedia Information Retrieval and Technology
School: Xi'an Jiaotong-Liverpool University

Features
----------------------------------------
✓ Text Query Search - Natural language queries
✓ Similar Talk Recommendations - Content-based recommendations
✓ Dataset Browsing - Statistics and popular talks
✓ Graphical Interface - User-friendly experience

Technical Implementation
----------------------------------------
• Document Representation: TF-IDF Vector Space Model
• Similarity Measure: Cosine Similarity
• Interface Framework: Tkinter

Performance Metrics
----------------------------------------
• Number of Documents: 2,550 talks
• Vocabulary: 5,000 features
• Query Response: ~2.27ms
• Throughput: 440 queries/sec

Usage Instructions
----------------------------------------
1. Text Search: Enter keywords to search
2. Similar Recommendations: Search then click results
3. Data Browse: View statistics and popular talks

Completion Date: December 5, 2025
        """
        
        about_text.insert('1.0', content)
        about_text.config(state='disabled')
    
    def set_query(self, query):
        """Set query"""
        self.search_entry.delete(0, tk.END)
        self.search_entry.insert(0, query)
        self.perform_search()
    
    def perform_search(self):
        """Perform search"""
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showwarning("Warning", "Please enter query")
            return
        
        self.status_var.set(f"Searching: {query}...")
        self.search_results.delete('1.0', tk.END)
        
        def search_thread():
            try:
                results = self.system.search(query, top_k=self.search_top_k.get())
                self.root.after(0, lambda: self.display_search_results(results, query))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Search failed: {str(e)}"))
        
        threading.Thread(target=search_thread, daemon=True).start()
    
    def display_search_results(self, results, query):
        """Display search results"""
        self.search_results.delete('1.0', tk.END)
        
        if not results:
            self.search_results.insert(tk.END, f"No talks found for '{query}'\n")
            self.status_var.set("No results found")
            return
        
        self.search_results.insert(tk.END, f"Found {len(results)} related talks:\n\n")
        
        for r in results:
            self.search_results.insert(tk.END, f"[{r['rank']}] ", 'info')
            self.search_results.insert(tk.END, f"{r['title']}\n", 'title')
            self.search_results.insert(tk.END, f"    Speaker: {r['speaker']}\n", 'info')
            self.search_results.insert(tk.END, f"    Similarity: {r['score']:.4f}\n", 'score')
            self.search_results.insert(tk.END, f"    Views: {r['views']:,}\n", 'info')
            desc = r['description'][:150] + "..." if len(r['description']) > 150 else r['description']
            self.search_results.insert(tk.END, f"    {desc}\n\n", 'info')
        
        self.status_var.set(f"Found {len(results)} results")
    
    def search_for_recommend(self):
        """Search for recommendation"""
        query = self.rec_search_entry.get().strip()
        if not query:
            messagebox.showwarning("Warning", "Please enter query")
            return
        
        self.status_var.set(f"Searching...")
        
        def search_thread():
            try:
                results = self.system.search(query, top_k=10)
                self.root.after(0, lambda: self.display_rec_search(results))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Search failed: {str(e)}"))
        
        threading.Thread(target=search_thread, daemon=True).start()
    
    def display_rec_search(self, results):
        """Display recommendation search results"""
        self.rec_listbox.delete(0, tk.END)
        self.rec_search_results = results
        
        if not results:
            messagebox.showinfo("Info", "No related talks found")
            self.status_var.set("No results found")
            return
        
        for i, r in enumerate(results):
            text = f"{i+1}. {r['title'][:50]}... ({r['speaker']})"
            self.rec_listbox.insert(tk.END, text)
        
        self.status_var.set(f"Found {len(results)} talks, click for recommendations")
    
    def on_talk_select(self, event):
        """Talk selection event"""
        selection = self.rec_listbox.curselection()
        if not selection:
            return
        
        idx = selection[0]
        if idx >= len(self.rec_search_results):
            return
        
        talk = self.rec_search_results[idx]
        talk_idx = talk['index']
        
        self.status_var.set("Calculating similar talks...")
        
        def recommend_thread():
            try:
                similar = self.system.find_similar_talks(talk_idx, top_k=5)
                self.root.after(0, lambda: self.display_recommendations(similar, talk))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Recommendation failed: {str(e)}"))
        
        threading.Thread(target=recommend_thread, daemon=True).start()
    
    def display_recommendations(self, similar, base_talk):
        """Display recommendations"""
        self.rec_results.delete('1.0', tk.END)
        
        self.rec_results.insert(tk.END, "Base talk:\n", 'header')
        self.rec_results.insert(tk.END, f"{base_talk['title']}\n", 'title')
        self.rec_results.insert(tk.END, f"Speaker: {base_talk['speaker']}\n\n", 'info')
        
        self.rec_results.insert(tk.END, f"Found {len(similar)} similar talks:\n\n", 'header')
        
        for s in similar:
            self.rec_results.insert(tk.END, f"[{s['rank']}] ", 'info')
            self.rec_results.insert(tk.END, f"{s['title']}\n", 'title')
            self.rec_results.insert(tk.END, f"    Speaker: {s['speaker']}\n", 'info')
            self.rec_results.insert(tk.END, f"    Similarity: {s['similarity']:.4f}\n", 'similarity')
            desc = s['description'][:150] + "..." if len(s['description']) > 150 else s['description']
            self.rec_results.insert(tk.END, f"    {desc}\n\n", 'info')
        
        self.status_var.set("Recommendation completed")
    
    def show_statistics(self):
        """Show statistics"""
        self.browse_results.delete('1.0', tk.END)
        stats = self.system.get_dataset_statistics()
        
        self.browse_results.insert(tk.END, "Dataset Statistics\n", 'header')
        self.browse_results.insert(tk.END, "=" * 50 + "\n\n")
        self.browse_results.insert(tk.END, f"Total talks: {stats['total_talks']:,}\n", 'info')
        self.browse_results.insert(tk.END, f"Unique speakers: {stats['unique_speakers']:,}\n", 'info')
        self.browse_results.insert(tk.END, f"Average duration: {stats['avg_duration']:.1f} minutes\n", 'info')
        self.browse_results.insert(tk.END, f"Total views: {stats['total_views']:,}\n", 'info')
        self.browse_results.insert(tk.END, f"Average views: {stats['avg_views']:,.0f}\n", 'info')
        self.browse_results.insert(tk.END, f"Vocabulary size: {stats['vocabulary_size']:,}\n", 'info')
        
        self.status_var.set("Statistics displayed")
    
    def show_popular(self):
        """Show popular talks"""
        self.browse_results.delete('1.0', tk.END)
        top_talks = self.system.df.nlargest(10, 'views')
        
        self.browse_results.insert(tk.END, "Top 10 Popular Talks\n", 'header')
        self.browse_results.insert(tk.END, "=" * 50 + "\n\n")
        
        for i, (_, talk) in enumerate(top_talks.iterrows(), 1):
            self.browse_results.insert(tk.END, f"{i}. ", 'info')
            self.browse_results.insert(tk.END, f"{talk['title']}\n", 'title')
            self.browse_results.insert(tk.END, f"   Speaker: {talk['main_speaker']}\n", 'info')
            self.browse_results.insert(tk.END, f"   Views: {talk['views']:,}\n\n", 'info')
        
        self.status_var.set("Popular talks displayed")
    
    def show_recent(self):
        """Show recent talks"""
        self.browse_results.delete('1.0', tk.END)
        recent = self.system.df.nlargest(10, 'published_date')
        
        self.browse_results.insert(tk.END, "Latest 10 Talks\n", 'header')
        self.browse_results.insert(tk.END, "=" * 50 + "\n\n")
        
        for i, (_, talk) in enumerate(recent.iterrows(), 1):
            self.browse_results.insert(tk.END, f"{i}. ", 'info')
            self.browse_results.insert(tk.END, f"{talk['title']}\n", 'title')
            self.browse_results.insert(tk.END, f"   Speaker: {talk['main_speaker']}\n\n", 'info')
        
        self.status_var.set("Recent talks displayed")
    
    def search_by_speaker(self):
        """Search by speaker"""
        speaker = self.speaker_entry.get().strip()
        if not speaker:
            messagebox.showwarning("Warning", "Please enter speaker name")
            return
        
        self.browse_results.delete('1.0', tk.END)
        talks = self.system.df[self.system.df['main_speaker'].str.contains(speaker, case=False, na=False)]
        
        if len(talks) == 0:
            self.browse_results.insert(tk.END, f"No talks found for speaker '{speaker}'\n")
            self.status_var.set("No results found")
            return
        
        self.browse_results.insert(tk.END, f"Found {len(talks)} talks\n", 'header')
        self.browse_results.insert(tk.END, "=" * 50 + "\n\n")
        
        for i, (_, talk) in enumerate(talks.iterrows(), 1):
            self.browse_results.insert(tk.END, f"{i}. ", 'info')
            self.browse_results.insert(tk.END, f"{talk['title']}\n", 'title')
            self.browse_results.insert(tk.END, f"   Views: {talk['views']:,}\n\n", 'info')
        
        self.status_var.set(f"Found {len(talks)} talks")


def main():
    """Main function"""
    root = tk.Tk()
    app = TEDRetrievalGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
