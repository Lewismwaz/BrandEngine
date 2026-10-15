"""
Modern CustomTkinter GUI for the Brand Name Generator
"""
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import threading
import queue
from datetime import datetime
from typing import List, Dict
import time

from generator import NameGenerator
from scoring import NameScorer
from domains import DomainChecker
from exporters import Exporter
from database import DatabaseManager
from config import DOMAIN_EXTENSIONS, NAMING_STYLES, THEMES


class BrandGeneratorGUI:
    """Main GUI application class"""
    
    def __init__(self):
        # Initialize components
        self.generator = NameGenerator()
        self.domain_checker = DomainChecker()
        self.exporter = Exporter()
        self.db = DatabaseManager()
        
        # Setup window
        self.window = ctk.CTk()
        self.window.title("Brand Name Generator")
        self.window.geometry("1200x800")
        self.window.minsize(1000, 700)
        
        # Set appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Variables
        self.generated_brands = []
        self.current_filtered_brands = []
        self.is_generating = False
        self.progress_queue = queue.Queue()
        
        # Setup UI
        self._setup_ui()
        self._setup_events()
        
        # Load saved settings if any
        self._load_settings()
    
    def _setup_ui(self):
        """Setup the complete user interface"""
        
        # Main container
        self.main_frame = ctk.CTkFrame(self.window)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left panel - Controls
        self.controls_frame = ctk.CTkFrame(self.main_frame, width=300)
        self.controls_frame.pack(side="left", fill="y", padx=(0, 10))
        self.controls_frame.pack_propagate(False)
        
        # Right panel - Results
        self.results_frame = ctk.CTkFrame(self.main_frame)
        self.results_frame.pack(side="right", fill="both", expand=True)
        
        self._setup_controls()
        self._setup_results()
    
    def _setup_controls(self):
        """Setup the control panel"""
        
        # Title
        title_label = ctk.CTkLabel(
            self.controls_frame,
            text="Brand Generator",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(10, 20))
        
        # Style selection
        style_label = ctk.CTkLabel(self.controls_frame, text="Naming Style:")
        style_label.pack(anchor="w", padx=10)
        
        self.style_var = ctk.StringVar(value="mixed")
        style_options = ["mixed"] + list(NAMING_STYLES.keys())
        self.style_menu = ctk.CTkOptionMenu(
            self.controls_frame,
            values=style_options,
            variable=self.style_var
        )
        self.style_menu.pack(fill="x", padx=10, pady=(0, 15))
        
        # Count
        count_label = ctk.CTkLabel(self.controls_frame, text="Number of Names:")
        count_label.pack(anchor="w", padx=10)
        
        self.count_var = ctk.StringVar(value="100")
        self.count_entry = ctk.CTkEntry(
            self.controls_frame,
            textvariable=self.count_var,
            width=100
        )
        self.count_entry.pack(fill="x", padx=10, pady=(0, 15))
        
        # Length range
        length_frame = ctk.CTkFrame(self.controls_frame)
        length_frame.pack(fill="x", padx=10, pady=(0, 15))
        
        ctk.CTkLabel(length_frame, text="Min Length:").grid(row=0, column=0, sticky="w")
        self.min_length_var = ctk.StringVar(value="3")
        self.min_length_entry = ctk.CTkEntry(
            length_frame,
            textvariable=self.min_length_var,
            width=60
        )
        self.min_length_entry.grid(row=0, column=1, padx=(5, 10))
        
        ctk.CTkLabel(length_frame, text="Max Length:").grid(row=0, column=2, sticky="w")
        self.max_length_var = ctk.StringVar(value="12")
        self.max_length_entry = ctk.CTkEntry(
            length_frame,
            textvariable=self.max_length_var,
            width=60
        )
        self.max_length_entry.grid(row=0, column=3, padx=(5, 0))
        
        # Domain checking
        self.check_domains_var = ctk.BooleanVar(value=True)
        self.check_domains_cb = ctk.CTkCheckBox(
            self.controls_frame,
            text="Check Domain Availability",
            variable=self.check_domains_var
        )
        self.check_domains_cb.pack(anchor="w", padx=10, pady=(0, 10))
        
        # Domain extensions
        extensions_label = ctk.CTkLabel(self.controls_frame, text="Domain Extensions:")
        extensions_label.pack(anchor="w", padx=10)
        
        self.extensions_frame = ctk.CTkFrame(self.controls_frame)
        self.extensions_frame.pack(fill="x", padx=10, pady=(0, 15))
        
        self.extensions_vars = {}
        for i, ext in enumerate(DOMAIN_EXTENSIONS):
            var = ctk.BooleanVar(value=True)
            self.extensions_vars[ext] = var
            cb = ctk.CTkCheckBox(
                self.extensions_frame,
                text=ext,
                variable=var,
                width=80
            )
            cb.grid(row=i//3, column=i%3, sticky="w", padx=5, pady=2)
        
        # Generate button
        self.generate_btn = ctk.CTkButton(
            self.controls_frame,
            text="Generate Names",
            command=self._generate_names_thread,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.generate_btn.pack(fill="x", padx=10, pady=(10, 5))
        
        # Stop button
        self.stop_btn = ctk.CTkButton(
            self.controls_frame,
            text="Stop",
            command=self._stop_generation,
            height=40,
            fg_color="red",
            hover_color="darkred",
            state="disabled"
        )
        self.stop_btn.pack(fill="x", padx=10, pady=(0, 10))
        
        # Progress bar
        self.progress_var = ctk.DoubleVar(value=0)
        self.progress_bar = ctk.CTkProgressBar(
            self.controls_frame,
            variable=self.progress_var
        )
        self.progress_bar.pack(fill="x", padx=10, pady=(0, 10))
        
        # Status label
        self.status_label = ctk.CTkLabel(
            self.controls_frame,
            text="Ready",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(pady=(0, 10))
        
        # Action buttons
        action_frame = ctk.CTkFrame(self.controls_frame)
        action_frame.pack(fill="x", padx=10, pady=(5, 5))
        
        ctk.CTkButton(
            action_frame,
            text="Export CSV",
            command=self._export_csv,
            width=80
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            action_frame,
            text="Export Excel",
            command=self._export_excel,
            width=80
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            action_frame,
            text="Clear",
            command=self._clear_results,
            width=80
        ).pack(side="left", padx=5)
        
        # Theme toggle
        self.theme_var = ctk.StringVar(value="dark")
        theme_label = ctk.CTkLabel(self.controls_frame, text="Theme:")
        theme_label.pack(anchor="w", padx=10, pady=(10, 0))
        
        theme_menu = ctk.CTkOptionMenu(
            self.controls_frame,
            values=["dark", "light"],
            variable=self.theme_var,
            command=self._change_theme
        )
        theme_menu.pack(fill="x", padx=10, pady=(0, 10))
    
    def _setup_results(self):
        """Setup the results display area"""
        
        # Toolbar
        toolbar_frame = ctk.CTkFrame(self.results_frame)
        toolbar_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        ctk.CTkLabel(
            toolbar_frame,
            text="Generated Names",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(side="left", padx=(0, 20))
        
        # Search
        self.search_var = ctk.StringVar()
        self.search_var.trace('w', self._filter_results)
        search_entry = ctk.CTkEntry(
            toolbar_frame,
            textvariable=self.search_var,
            placeholder_text="Search names...",
            width=200
        )
        search_entry.pack(side="left", padx=10)
        
        # Score filter
        ctk.CTkLabel(toolbar_frame, text="Min Score:").pack(side="left", padx=(10, 5))
        self.score_filter_var = ctk.StringVar(value="0")
        score_filter = ctk.CTkEntry(
            toolbar_frame,
            textvariable=self.score_filter_var,
            width=60
        )
        score_filter.pack(side="left")
        score_filter.bind('<KeyRelease>', self._filter_results)
        
        # Results count
        self.count_label = ctk.CTkLabel(toolbar_frame, text="0 names")
        self.count_label.pack(side="right", padx=10)
        
        # Results table
        self._setup_table()
    
    def _setup_table(self):
        """Setup the results table"""
        
        # Create scrollable frame
        self.table_frame = ctk.CTkScrollableFrame(self.results_frame)
        self.table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Headers
        headers = ["Name", "Style", "Score", "Domain", "Length"]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(
                self.table_frame,
                text=header,
                font=ctk.CTkFont(weight="bold"),
                width=150 if i == 0 else 100
            )
            label.grid(row=0, column=i, padx=5, pady=5, sticky="w")
        
        # Store row widgets for updating
        self.row_widgets = []
        
        # Add initial message
        message_label = ctk.CTkLabel(
            self.table_frame,
            text="Generate brand names to see results here",
            font=ctk.CTkFont(size=14, slant="italic")
        )
        message_label.grid(row=1, column=0, columnspan=5, pady=20)
        self.message_label = message_label
    
    def _setup_events(self):
        """Setup event handlers"""
        self.window.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _generate_names_thread(self):
        """Start name generation in a separate thread"""
        if self.is_generating:
            return
        
        # Validate inputs
        try:
            count = int(self.count_var.get())
            min_length = int(self.min_length_var.get())
            max_length = int(self.max_length_var.get())
            
            if count <= 0 or count > 1000000:
                raise ValueError("Count must be between 1 and 1,000,000")
            if min_length < 1 or max_length > 50 or min_length > max_length:
                raise ValueError("Invalid length parameters")
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
            return
        
        # Disable generate button, enable stop button
        self.generate_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.is_generating = True
        self.progress_var.set(0)
        
        # Clear previous results
        self._clear_results()
        
        # Get selected extensions
        selected_extensions = [
            ext for ext, var in self.extensions_vars.items() 
            if var.get()
        ]
        
        # Start generation thread
        self.generation_thread = threading.Thread(
            target=self._generate_names,
            args=(count, min_length, max_length, selected_extensions),
            daemon=True
        )
        self.generation_thread.start()
        
        # Start progress update
        self._update_progress()
    
    def _generate_names(self, count, min_length, max_length, extensions):
        """Generate names (runs in background thread)"""
        try:
            # Get style
            style = self.style_var.get()
            
            # Generate names with progress callback
            def progress_callback(progress, generated_count):
                self.progress_queue.put(('progress', progress, generated_count))
                self.status_label.configure(text=f"Generating... {generated_count} names")
            
            brands = self.generator.generate_names(
                style=style,
                count=count,
                min_length=min_length,
                max_length=max_length,
                progress_callback=progress_callback
            )
            
            # Check domains if enabled
            if self.check_domains_var.get() and extensions:
                self.status_label.configure(text="Checking domain availability...")
                self._check_domain_availability(brands, extensions)
            
            # Store and display results
            self.generated_brands = brands
            self.progress_queue.put(('complete', brands))
            
        except Exception as e:
            self.progress_queue.put(('error', str(e)))
    
    def _check_domain_availability(self, brands, extensions):
        """Check domain availability for brands"""
        # Get unique names
        names = list(set([b['name'].lower().replace(' ', '').replace('-', '') 
                         for b in brands]))
        
        # Check in batches to avoid overwhelming
        batch_size = 50
        for i in range(0, len(names), batch_size):
            batch = names[i:i+batch_size]
            results = self.domain_checker.check_domains_batch(batch, extensions)
            
            # Update brands with domain info
            for brand in brands:
                clean_name = brand['name'].lower().replace(' ', '').replace('-', '')
                available_domains = []
                for ext in extensions:
                    domain = f"{clean_name}{ext}"
                    if results.get(domain, False):
                        available_domains.append(domain)
                
                brand['domains_checked'] = [f"{clean_name}{ext}" for ext in extensions]
                brand['domain_available'] = 'yes' if available_domains else 'no'
                brand['available_domains'] = available_domains
                
                # Update score based on domain availability
                if brand['domain_available'] == 'yes':
                    brand['score'] = min(100, brand.get('score', 0) + 15)
            
            # Update progress
            progress = (i + batch_size) / len(names) * 100
            self.progress_queue.put(('domain_progress', progress))
    
    def _update_progress(self):
        """Update progress from queue"""
        try:
            while True:
                msg = self.progress_queue.get_nowait()
                
                if msg[0] == 'progress':
                    _, progress, count = msg
                    self.progress_var.set(progress / 100)
                    self.status_label.configure(text=f"Generating... {count} names")
                
                elif msg[0] == 'domain_progress':
                    _, progress = msg
                    self.progress_var.set(50 + (progress / 2) / 100)
                    self.status_label.configure(text=f"Checking domains... {progress:.0f}%")
                
                elif msg[0] == 'complete':
                    _, brands = msg
                    self._display_results(brands)
                    self.generate_btn.configure(state="normal")
                    self.stop_btn.configure(state="disabled")
                    self.is_generating = False
                    self.progress_var.set(100)
                    self.status_label.configure(
                        text=f"Complete! Generated {len(brands)} names"
                    )
                    
                    # Save to database
                    self._save_to_database(brands)
                
                elif msg[0] == 'error':
                    _, error = msg
                    self.generate_btn.configure(state="normal")
                    self.stop_btn.configure(state="disabled")
                    self.is_generating = False
                    self.progress_var.set(0)
                    self.status_label.configure(text="Error")
                    messagebox.showerror("Generation Error", error)
        
        except queue.Empty:
            pass
        
        # Schedule next update
        if self.is_generating:
            self.window.after(100, self._update_progress)
    
    def _stop_generation(self):
        """Stop the generation process"""
        if self.is_generating:
            self.generator.stop_generation()
            self.is_generating = False
            self.generate_btn.configure(state="normal")
            self.stop_btn.configure(state="disabled")
            self.status_label.configure(text="Stopped")
            self.progress_var.set(0)
    
    def _display_results(self, brands):
        """Display generated brands in the table"""
        # Clear existing rows
        for widgets in self.row_widgets:
            for widget in widgets:
                widget.destroy()
        self.row_widgets.clear()
        
        # Hide message
        if hasattr(self, 'message_label'):
            self.message_label.grid_remove()
        
        # Sort by score
        sorted_brands = sorted(brands, key=lambda x: x.get('score', 0), reverse=True)
        self.current_filtered_brands = sorted_brands
        
        # Display rows
        for i, brand in enumerate(sorted_brands[:1000]):  # Limit display
            # Name
            name_label = ctk.CTkLabel(
                self.table_frame,
                text=brand['name'],
                font=ctk.CTkFont(size=13, weight="bold"),
                width=150,
                anchor="w"
            )
            name_label.grid(row=i+1, column=0, padx=5, pady=2, sticky="w")
            
            # Style
            style_label = ctk.CTkLabel(
                self.table_frame,
                text=brand.get('style', 'mixed'),
                width=100,
                anchor="w"
            )
            style_label.grid(row=i+1, column=1, padx=5, pady=2, sticky="w")
            
            # Score
            score = brand.get('score', 0)
            score_color = "green" if score >= 70 else "orange" if score >= 50 else "red"
            score_label = ctk.CTkLabel(
                self.table_frame,
                text=f"{score:.1f}",
                text_color=score_color,
                width=100,
                anchor="w"
            )
            score_label.grid(row=i+1, column=2, padx=5, pady=2, sticky="w")
            
            # Domain
            domain_text = "✓ Available" if brand.get('domain_available') == 'yes' else "✗ Taken"
            domain_color = "green" if brand.get('domain_available') == 'yes' else "gray"
            domain_label = ctk.CTkLabel(
                self.table_frame,
                text=domain_text,
                text_color=domain_color,
                width=100,
                anchor="w"
            )
            domain_label.grid(row=i+1, column=3, padx=5, pady=2, sticky="w")
            
            # Length
            length_label = ctk.CTkLabel(
                self.table_frame,
                text=str(brand.get('length', len(brand['name']))),
                width=100,
                anchor="w"
            )
            length_label.grid(row=i+1, column=4, padx=5, pady=2, sticky="w")
            
            self.row_widgets.append([name_label, style_label, score_label, 
                                    domain_label, length_label])
        
        # Update count
        self.count_label.configure(text=f"{len(brands)} names")
    
    def _filter_results(self, *args):
        """Filter displayed results based on search and score"""
        if not self.generated_brands:
            return
        
        search_text = self.search_var.get().lower()
        try:
            min_score = float(self.score_filter_var.get()) if self.score_filter_var.get() else 0
        except ValueError:
            return
        
        filtered = self.generated_brands
        
        if search_text:
            filtered = [b for b in filtered if search_text in b['name'].lower()]
        
        if min_score > 0:
            filtered = [b for b in filtered if b.get('score', 0) >= min_score]
        
        self.current_filtered_brands = filtered
        self._display_results(filtered)
    
    def _save_to_database(self, brands):
        """Save brands to database"""
        try:
            # Convert to database format
            db_brands = []
            for brand in brands:
                db_brands.append({
                    'name': brand['name'],
                    'style': brand.get('style', 'mixed'),
                    'score': brand.get('score', 0),
                    'domain_available': brand.get('domain_available'),
                    'domains_checked': brand.get('domains_checked', []),
                    'metadata': {
                        'length': brand.get('length', len(brand['name'])),
                        'available_domains': brand.get('available_domains', [])
                    }
                })
            
            self.db.add_brands_batch(db_brands)
        except Exception as e:
            print(f"Error saving to database: {e}")
    
    def _export_csv(self):
        """Export current results to CSV"""
        if not self.current_filtered_brands:
            messagebox.showwarning("No Data", "No brands to export")
            return
        
        try:
            filepath = self.exporter.export_to_csv(self.current_filtered_brands)
            messagebox.showinfo("Export Successful", f"Exported to: {filepath}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))
    
    def _export_excel(self):
        """Export current results to Excel"""
        if not self.current_filtered_brands:
            messagebox.showwarning("No Data", "No brands to export")
            return
        
        try:
            filepath = self.exporter.export_to_excel(self.current_filtered_brands)
            messagebox.showinfo("Export Successful", f"Exported to: {filepath}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))
    
    def _clear_results(self):
        """Clear all displayed results"""
        self.generated_brands = []
        self.current_filtered_brands = []
        
        # Clear rows
        for widgets in self.row_widgets:
            for widget in widgets:
                widget.destroy()
        self.row_widgets.clear()
        
        # Show message
        if hasattr(self, 'message_label'):
            self.message_label.grid()
        
        self.count_label.configure(text="0 names")
        self.progress_var.set(0)
        self.status_label.configure(text="Ready")
    
    def _change_theme(self, theme):
        """Change the application theme"""
        ctk.set_appearance_mode(theme)
        self._save_settings()
    
    def _load_settings(self):
        """Load saved settings"""
        # This would load from a config file in a real implementation
        pass
    
    def _save_settings(self):
        """Save current settings"""
        # This would save to a config file in a real implementation
        pass
    
    def _on_closing(self):
        """Handle window closing"""
        if self.is_generating:
            if messagebox.askyesno("Confirm", "Generation in progress. Are you sure you want to exit?"):
                self._stop_generation()
                self.window.destroy()
        else:
            self.window.destroy()
    
    def run(self):
        """Run the application"""
        self.window.mainloop()