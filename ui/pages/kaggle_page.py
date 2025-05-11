import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import threading
import tempfile
import importlib.util

# Check for pandas
if importlib.util.find_spec("pandas") is not None:
    import pandas as pd
else:
    pd = None
    
# Check for numpy
if importlib.util.find_spec("numpy") is not None:
    import numpy as np
else:
    np = None

# Check for matplotlib
matplotlib_available = importlib.util.find_spec("matplotlib") is not None
if matplotlib_available:
    import matplotlib
    matplotlib.use('TkAgg')
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
else:
    matplotlib = None
    plt = None
    FigureCanvasTkAgg = None
    Figure = None

# Import the base page class
from ui.pages.base_page import BasePage

# Import kaggle helper module
from utils.kaggle_helper import (
    check_api_credentials, 
    setup_credentials, 
    get_dataset_list,
    get_dataset_files,
    download_dataset_file,
    load_dataset_to_dataframe
)


class KagglePage(BasePage):
    """Page for fetching and visualizing data from Kaggle."""
    
    def __init__(self, parent, controller):
        super().__init__(parent, title="Kaggle Data Explorer")
        self.controller = controller
        self.current_dataset = None
        self.current_dataset_ref = None
        self.current_file = None
        self.current_df = None
        self.temp_dir = tempfile.mkdtemp()
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the UI components for the Kaggle page."""
        # Main container frame
        self.main_frame = ttk.Frame(self.content_frame, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Check Kaggle credentials before proceeding
        if not check_api_credentials():
            self.setup_credentials_ui()
        else:
            self.setup_main_ui()
    
    def setup_credentials_ui(self):
        """Show UI for setting up Kaggle API credentials."""
        # Clear the main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        # Create a frame for API setup
        cred_frame = ttk.Frame(self.main_frame, padding=20)
        cred_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header = ttk.Label(
            cred_frame, 
            text="Kaggle API Setup", 
            font=("Helvetica", 16)
        )
        header.pack(pady=(0, 20))
        
        # Description
        description = ttk.Label(
            cred_frame,
            text=(
                "To use the Kaggle API, you need to provide your API credentials.\n"
                "You can find your API key on your Kaggle account page:\n"
                "https://www.kaggle.com/account"
            ),
            justify=tk.LEFT
        )
        description.pack(pady=(0, 15), fill=tk.X)
        
        # Username field
        username_frame = ttk.Frame(cred_frame)
        username_frame.pack(fill=tk.X, pady=5)
        
        username_label = ttk.Label(username_frame, text="Username:", width=15)
        username_label.pack(side=tk.LEFT)
        
        self.username_var = tk.StringVar()
        username_entry = ttk.Entry(username_frame, textvariable=self.username_var, width=40)
        username_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # API key field
        key_frame = ttk.Frame(cred_frame)
        key_frame.pack(fill=tk.X, pady=5)
        
        key_label = ttk.Label(key_frame, text="API Key:", width=15)
        key_label.pack(side=tk.LEFT)
        
        self.key_var = tk.StringVar()
        key_entry = ttk.Entry(key_frame, textvariable=self.key_var, width=40, show="*")
        key_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Submit button
        submit_btn = ttk.Button(
            cred_frame, 
            text="Save Credentials", 
            command=self.save_credentials
        )
        submit_btn.pack(pady=20)
        
        # Instructions
        instructions = ttk.Label(
            cred_frame,
            text=(
                "Instructions to get your Kaggle API key:\n\n"
                "1. Log in to your Kaggle account\n"
                "2. Go to 'Account' page (click on your profile picture)\n"
                "3. Scroll down to the 'API' section\n"
                "4. Click 'Create New API Token'\n"
                "5. This will download a kaggle.json file\n"
                "6. Open the file and copy the username and key values here"
            ),
            justify=tk.LEFT
        )
        instructions.pack(pady=10, fill=tk.X)
    
    def save_credentials(self):
        """Save Kaggle API credentials."""
        username = self.username_var.get().strip()
        key = self.key_var.get().strip()
        
        if not username or not key:
            messagebox.showerror(
                "Error", 
                "Please enter both username and API key."
            )
            return
            
        # Save credentials
        if setup_credentials(username, key):
            messagebox.showinfo(
                "Success", 
                "Kaggle API credentials saved successfully!"
            )
            # Switch to the main UI
            self.setup_main_ui()
        else:
            messagebox.showerror(
                "Error", 
                "Failed to save credentials. Please try again."
            )
    
    def setup_main_ui(self):
        """Set up the main UI for Kaggle data exploration."""
        # Clear the main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()
            
        # Create splitter layout
        self.paned_window = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Search and dataset selection
        self.left_panel = ttk.Frame(self.paned_window, padding=10)
        self.paned_window.add(self.left_panel, weight=30)
        
        # Right panel - Dataset viewer
        self.right_panel = ttk.Frame(self.paned_window, padding=10)
        self.paned_window.add(self.right_panel, weight=70)
        
        # Set up left panel
        self.setup_search_panel()
        
        # Set up right panel
        self.setup_empty_viewer()
    
    def setup_search_panel(self):
        """Set up the search panel for Kaggle datasets."""
        # Search frame
        search_frame = ttk.LabelFrame(self.left_panel, text="Search Datasets", padding=10)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Search term
        ttk.Label(search_frame, text="Search term:").pack(anchor=tk.W, pady=(0, 2))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(fill=tk.X, pady=(0, 5))
        
        # Filters section
        filters_frame = ttk.Frame(search_frame)
        filters_frame.pack(fill=tk.X, pady=5)
        
        # File type filter
        ttk.Label(filters_frame, text="File type:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.file_type_var = tk.StringVar()
        file_type = ttk.Combobox(filters_frame, textvariable=self.file_type_var, width=10)
        file_type['values'] = ('Any', 'csv', 'json', 'xlsx', 'sqlite', 'parquet')
        file_type.current(0)
        file_type.grid(row=0, column=1, sticky=tk.W, pady=2)
        
        # Size filter
        ttk.Label(filters_frame, text="Max size (MB):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.max_size_var = tk.StringVar(value="100")
        size_entry = ttk.Entry(filters_frame, textvariable=self.max_size_var, width=12)
        size_entry.grid(row=1, column=1, sticky=tk.W, pady=2)
        
        # Results limit
        ttk.Label(filters_frame, text="Max results:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.max_results_var = tk.StringVar(value="20")
        results_entry = ttk.Entry(filters_frame, textvariable=self.max_results_var, width=12)
        results_entry.grid(row=2, column=1, sticky=tk.W, pady=2)
        
        # Search button
        search_btn = ttk.Button(
            search_frame, 
            text="Search Datasets", 
            command=self.search_datasets
        )
        search_btn.pack(fill=tk.X, pady=(10, 0))
        
        # Dataset list frame
        list_frame = ttk.LabelFrame(self.left_panel, text="Datasets", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create Treeview for datasets
        self.dataset_tree = ttk.Treeview(
            list_frame, 
            columns=('Size', 'Downloads'),
            show='headings',
            selectmode='browse'
        )
        self.dataset_tree.heading('Size', text='Size (MB)')
        self.dataset_tree.heading('Downloads', text='Downloads')
        self.dataset_tree.column('Size', width=80, anchor='e')
        self.dataset_tree.column('Downloads', width=80, anchor='e')
        
        # Add scrollbar to treeview
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.dataset_tree.yview)
        self.dataset_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.dataset_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.dataset_tree.bind('<<TreeviewSelect>>', self.on_dataset_select)
    
    def setup_empty_viewer(self):
        """Set up the empty dataset viewer panel."""
        # Remove existing widgets
        for widget in self.right_panel.winfo_children():
            widget.destroy()
            
        # Create a message to prompt user to select a dataset
        message_frame = ttk.Frame(self.right_panel, padding=20)
        message_frame.pack(fill=tk.BOTH, expand=True)
        
        message = ttk.Label(
            message_frame,
            text="Select a dataset from the list to view its contents.",
            font=("Helvetica", 12),
            foreground="gray"
        )
        message.pack(expand=True)
    
    def setup_dataset_viewer(self):
        """Set up the dataset viewer panel."""
        # Remove existing widgets
        for widget in self.right_panel.winfo_children():
            widget.destroy()
            
        # Dataset info at the top
        info_frame = ttk.Frame(self.right_panel, padding=5)
        info_frame.pack(fill=tk.X)
        
        # Dataset title
        title = ttk.Label(
            info_frame, 
            text=self.current_dataset.get('title', 'Unknown Dataset'),
            font=("Helvetica", 12, "bold")
        )
        title.pack(anchor=tk.W)
        
        # Dataset subtitle/description
        if 'subtitle' in self.current_dataset and self.current_dataset['subtitle']:
            subtitle = ttk.Label(
                info_frame,
                text=self.current_dataset['subtitle'],
                wraplength=600
            )
            subtitle.pack(anchor=tk.W, pady=(0, 5))
        
        # Dataset info
        info_text = f"Owner: {self.current_dataset.get('owner', 'Unknown')} | "
        info_text += f"Size: {self.current_dataset.get('sizeMB', 0)} MB | "
        info_text += f"Downloads: {self.current_dataset.get('downloadCount', 0)} | "
        info_text += f"Votes: {self.current_dataset.get('voteCount', 0)}"
        
        info = ttk.Label(info_frame, text=info_text)
        info.pack(anchor=tk.W, pady=(0, 10))
        
        # Dataset files list
        files_frame = ttk.LabelFrame(self.right_panel, text="Files", padding=5)
        files_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Create a Treeview for files
        self.files_tree = ttk.Treeview(
            files_frame, 
            columns=('Size',),
            show='headings',
            selectmode='browse',
            height=3
        )
        self.files_tree.heading('Size', text='Size (MB)')
        self.files_tree.column('Size', width=80, anchor='e')
        
        # Add scrollbar to files treeview
        files_scrollbar = ttk.Scrollbar(files_frame, orient="vertical", command=self.files_tree.yview)
        self.files_tree.configure(yscrollcommand=files_scrollbar.set)
        
        # Pack files treeview and scrollbar
        self.files_tree.pack(side=tk.LEFT, fill=tk.X, expand=True)
        files_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.files_tree.bind('<<TreeviewSelect>>', self.on_file_select)
        
        # Load and display files
        self.load_dataset_files()
        
        # DataFrame view placeholder (will be filled when a file is selected)
        self.df_frame = ttk.LabelFrame(self.right_panel, text="Data Preview", padding=5)
        self.df_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Add a message to prompt user to select a file
        message = ttk.Label(
            self.df_frame,
            text="Select a file from the list to preview its contents.",
            foreground="gray"
        )
        message.pack(expand=True)
        
        # Visualization frame (will be filled when data is loaded)
        self.viz_frame = ttk.LabelFrame(self.right_panel, text="Visualization", padding=5)
        self.viz_frame.pack(fill=tk.BOTH, expand=True)
        
        message = ttk.Label(
            self.viz_frame,
            text="Load a dataset to create visualizations.",
            foreground="gray"
        )
        message.pack(expand=True)
    
    def search_datasets(self):
        """Search for Kaggle datasets based on user input."""
        search_term = self.search_var.get().strip()
        
        # Get filter values
        max_size_str = self.max_size_var.get().strip()
        try:
            max_size = int(max_size_str) if max_size_str else None
        except ValueError:
            max_size = 100  # Default to 100 MB
            
        max_results_str = self.max_results_var.get().strip()
        try:
            max_results = int(max_results_str) if max_results_str else 20
        except ValueError:
            max_results = 20  # Default to 20 results
            
        file_type = self.file_type_var.get()
        if file_type == 'Any':
            file_type = None
            
        # Clear existing items in treeview
        for item in self.dataset_tree.get_children():
            self.dataset_tree.delete(item)
            
        # Show loading message
        loading_item = self.dataset_tree.insert('', 'end', text='Loading...', values=('', ''))
        self.update_idletasks()
        
        # Define thread function
        def search_thread():
            # Fetch datasets
            datasets = get_dataset_list(
                search_term=search_term,
                max_size_mb=max_size,
                file_type=file_type,
                max_results=max_results
            )
            
            # Update UI in main thread
            self.after(10, lambda: self.update_dataset_list(datasets, loading_item))
            
        # Start search in a separate thread
        thread = threading.Thread(target=search_thread)
        thread.daemon = True
        thread.start()
    
    def update_dataset_list(self, datasets, loading_item):
        """Update the dataset list with search results."""
        # Remove loading item
        self.dataset_tree.delete(loading_item)
        
        # Track the datasets to be able to look them up by ID later
        self.datasets = {}
        
        if not datasets:
            self.dataset_tree.insert('', 'end', text='No datasets found', values=('', ''))
            return
            
        # Add datasets to treeview
        for dataset in datasets:
            item_id = self.dataset_tree.insert(
                '', 'end', 
                text=dataset['title'],
                values=(
                    f"{dataset.get('sizeMB', 0):.1f}",
                    f"{dataset.get('downloadCount', 0):,}"
                )
            )
            # Store reference to look up by item ID
            self.datasets[item_id] = dataset
    
    def on_dataset_select(self, event):
        """Handle dataset selection event."""
        selected_items = self.dataset_tree.selection()
        if not selected_items:
            return
            
        # Get the selected dataset
        item_id = selected_items[0]
        self.current_dataset = self.datasets.get(item_id)
        
        if not self.current_dataset:
            return
            
        self.current_dataset_ref = self.current_dataset.get('ref')
        
        # Update the UI with the selected dataset
        self.setup_dataset_viewer()
    
    def load_dataset_files(self):
        """Load and display files for the selected dataset."""
        if not self.current_dataset_ref:
            return
            
        # Clear existing items in files treeview
        for item in self.files_tree.get_children():
            self.files_tree.delete(item)
            
        # Show loading message
        loading_item = self.files_tree.insert('', 'end', text='Loading...', values=(''))
        self.update_idletasks()
        
        # Define thread function
        def load_files_thread():
            # Fetch files
            files = get_dataset_files(self.current_dataset_ref)
            
            # Update UI in main thread
            self.after(10, lambda: self.update_files_list(files, loading_item))
            
        # Start load in a separate thread
        thread = threading.Thread(target=load_files_thread)
        thread.daemon = True
        thread.start()
    
    def update_files_list(self, files, loading_item):
        """Update the files list for the selected dataset."""
        # Remove loading item
        self.files_tree.delete(loading_item)
        
        # Track the files to be able to look them up by ID later
        self.files = {}
        
        if not files:
            self.files_tree.insert('', 'end', text='No files found', values=(''))
            return
            
        # Add files to treeview
        for file in files:
            item_id = self.files_tree.insert(
                '', 'end', 
                text=file['name'],
                values=(f"{file.get('sizeMB', 0):.1f}")
            )
            # Store reference to look up by item ID
            self.files[item_id] = file
    
    def on_file_select(self, event):
        """Handle file selection event."""
        selected_items = self.files_tree.selection()
        if not selected_items:
            return
            
        # Get the selected file
        item_id = selected_items[0]
        self.current_file = self.files.get(item_id)
        
        if not self.current_file or not self.current_dataset_ref:
            return
            
        # Get the filename
        filename = self.current_file.get('name')
        if not filename:
            return
            
        # Show loading indicator in DataFrame frame
        for widget in self.df_frame.winfo_children():
            widget.destroy()
            
        loading_label = ttk.Label(
            self.df_frame,
            text=f"Downloading and loading {filename}...",
            foreground="blue"
        )
        loading_label.pack(expand=True)
        self.update_idletasks()
        
        # Define thread function
        def download_thread():
            # Download and load file
            file_path = download_dataset_file(
                self.current_dataset_ref,
                filename,
                output_dir=self.temp_dir
            )
            
            if file_path:
                df = load_dataset_to_dataframe(file_path)
                self.current_df = df
                
                # Update UI in main thread
                self.after(10, lambda: self.display_dataframe(df))
            else:
                self.after(10, lambda: self.show_download_error())
            
        # Start download in a separate thread
        thread = threading.Thread(target=download_thread)
        thread.daemon = True
        thread.start()
    
    def display_dataframe(self, df):
        """Display a pandas DataFrame."""
        # Clear the DataFrame frame
        for widget in self.df_frame.winfo_children():
            widget.destroy()
            
        if df is None:
            error_label = ttk.Label(
                self.df_frame,
                text="Error loading the file. Format may not be supported.",
                foreground="red"
            )
            error_label.pack(expand=True)
            return
            
        # Check if pandas is available
        if pd is None:
            error_label = ttk.Label(
                self.df_frame,
                text="Pandas is not available. Please install with: pip install pandas",
                foreground="red"
            )
            error_label.pack(expand=True)
            return
            
        # Create a frame for the DataFrame preview
        preview_frame = ttk.Frame(self.df_frame)
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        # Show DataFrame info
        info_text = f"Rows: {len(df)}, Columns: {len(df.columns)}"
        info_label = ttk.Label(preview_frame, text=info_text)
        info_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Create Treeview for DataFrame
        columns = list(df.columns)
        tree = ttk.Treeview(
            preview_frame, 
            columns=columns,
            show='headings',
            selectmode='browse',
            height=10
        )
        
        # Set column headings
        for col in columns:
            tree.heading(col, text=str(col))
            # Adjust column width based on data type
            if pd.api.types.is_numeric_dtype(df[col]):
                tree.column(col, width=80, anchor='e')
            else:
                tree.column(col, width=150, anchor='w')
        
        # Add data rows (limit to first 1000 rows)
        display_rows = min(1000, len(df))
        for i in range(display_rows):
            values = [str(df.iloc[i][col]) for col in columns]
            tree.insert('', 'end', values=values)
            
        # Add scrollbars
        y_scrollbar = ttk.Scrollbar(preview_frame, orient="vertical", command=tree.yview)
        x_scrollbar = ttk.Scrollbar(preview_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        
        # Pack tree and scrollbars
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Show visualization options
        self.setup_visualization_options(df)
    
    def show_download_error(self):
        """Show an error message for failed download."""
        # Clear the DataFrame frame
        for widget in self.df_frame.winfo_children():
            widget.destroy()
            
        error_label = ttk.Label(
            self.df_frame,
            text="Failed to download or open the file.",
            foreground="red"
        )
        error_label.pack(expand=True)
    
    def setup_visualization_options(self, df):
        """Set up visualization options for the loaded DataFrame."""
        # Clear the visualization frame
        for widget in self.viz_frame.winfo_children():
            widget.destroy()
            
        if df is None or len(df) == 0:
            message = ttk.Label(
                self.viz_frame,
                text="No data available for visualization.",
                foreground="gray"
            )
            message.pack(expand=True)
            return
            
        # Controls frame
        controls_frame = ttk.Frame(self.viz_frame)
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Visualization type
        ttk.Label(controls_frame, text="Chart Type:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.chart_type_var = tk.StringVar()
        chart_type = ttk.Combobox(controls_frame, textvariable=self.chart_type_var, width=15)
        chart_type['values'] = ('Histogram', 'Bar Chart', 'Scatter Plot', 'Line Chart', 'Box Plot')
        chart_type.current(0)
        chart_type.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # X-axis selector (for numeric columns)
        ttk.Label(controls_frame, text="X-axis:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        
        self.x_var = tk.StringVar()
        x_columns = [col for col in df.columns]
        x_selector = ttk.Combobox(controls_frame, textvariable=self.x_var, width=15)
        x_selector['values'] = x_columns
        if x_columns:
            x_selector.current(0)
        x_selector.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        
        # Y-axis selector (for scatter, line)
        ttk.Label(controls_frame, text="Y-axis:").grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)
        
        self.y_var = tk.StringVar()
        numeric_columns = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]
        y_selector = ttk.Combobox(controls_frame, textvariable=self.y_var, width=15)
        y_selector['values'] = numeric_columns
        if numeric_columns:
            y_selector.current(0)
        y_selector.grid(row=0, column=5, padx=5, pady=5, sticky=tk.W)
        
        # Plot button
        plot_btn = ttk.Button(
            controls_frame, 
            text="Generate Plot", 
            command=self.generate_plot
        )
        plot_btn.grid(row=0, column=6, padx=15, pady=5, sticky=tk.W)
        
        # Export button
        export_btn = ttk.Button(
            controls_frame, 
            text="Export Data", 
            command=self.export_data
        )
        export_btn.grid(row=0, column=7, padx=5, pady=5, sticky=tk.W)
        
        # Plot container
        self.plot_container = ttk.Frame(self.viz_frame)
        self.plot_container.pack(fill=tk.BOTH, expand=True)
        
        message = ttk.Label(
            self.plot_container,
            text="Select options and click 'Generate Plot' to create a visualization.",
            foreground="gray"
        )
        message.pack(expand=True)
    
    def generate_plot(self):
        """Generate a visualization based on user selections."""
        if self.current_df is None:
            return
            
        df = self.current_df
        chart_type = self.chart_type_var.get()
        x_col = self.x_var.get()
        y_col = self.y_var.get()
        
        # Clear the plot container
        for widget in self.plot_container.winfo_children():
            widget.destroy()
            
        # Check if matplotlib is available
        if not matplotlib_available or Figure is None:
            error_label = ttk.Label(
                self.plot_container,
                text="Matplotlib is not available. Please install with: pip install matplotlib",
                foreground="red"
            )
            error_label.pack(expand=True)
            
            # Display data as text instead
            if pd is not None and df is not None:
                text_frame = ttk.Frame(self.plot_container)
                text_frame.pack(fill=tk.BOTH, expand=True, pady=10)
                
                data_text = tk.Text(text_frame, height=20, width=50)
                data_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                
                scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=data_text.yview)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                data_text.config(yscrollcommand=scrollbar.set)
                
                # Display data summary
                data_text.insert(tk.END, f"Data Summary for: {x_col}\n\n")
                if pd.api.types.is_numeric_dtype(df[x_col]):
                    data_text.insert(tk.END, df[x_col].describe().to_string())
                else:
                    data_text.insert(tk.END, df[x_col].value_counts().to_string())
                data_text.config(state=tk.DISABLED)
            
            return
            
        try:
            # Create figure and axis
            fig = Figure(figsize=(10, 6), dpi=100)
            ax = fig.add_subplot(111)
            
            # Generate plot based on chart type
            if chart_type == 'Histogram':
                if x_col not in df.columns:
                    raise ValueError(f"Column '{x_col}' not found in DataFrame")
                    
                if not pd.api.types.is_numeric_dtype(df[x_col]):
                    ax.text(0.5, 0.5, "Histogram requires numeric data", ha='center', va='center', transform=ax.transAxes)
                else:
                    ax.hist(df[x_col].dropna(), bins=30, alpha=0.7)
                    ax.set_xlabel(x_col)
                    ax.set_ylabel('Frequency')
                    ax.set_title(f'Histogram of {x_col}')
                    
            elif chart_type == 'Bar Chart':
                if x_col not in df.columns:
                    raise ValueError(f"Column '{x_col}' not found in DataFrame")
                
                # For categorical data, show value counts
                if pd.api.types.is_numeric_dtype(df[x_col]):
                    # For numeric data, bin it first
                    bins = pd.cut(df[x_col], bins=10)
                    value_counts = bins.value_counts().sort_index()
                    ax.bar(range(len(value_counts)), value_counts.values, tick_label=[str(x) for x in value_counts.index])
                    ax.set_xlabel(x_col)
                    if plt:
                        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
                else:
                    # For categorical data
                    value_counts = df[x_col].value_counts().sort_index()
                    ax.bar(range(len(value_counts)), value_counts.values, tick_label=value_counts.index)
                    ax.set_xlabel(x_col)
                    if plt:
                        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
                    
                ax.set_ylabel('Count')
                ax.set_title(f'Bar Chart of {x_col}')
                
            elif chart_type == 'Scatter Plot':
                if x_col not in df.columns or y_col not in df.columns:
                    raise ValueError(f"Columns '{x_col}' or '{y_col}' not found in DataFrame")
                    
                if not pd.api.types.is_numeric_dtype(df[x_col]) or not pd.api.types.is_numeric_dtype(df[y_col]):
                    ax.text(0.5, 0.5, "Scatter plot requires numeric data for both axes", 
                            ha='center', va='center', transform=ax.transAxes)
                else:
                    ax.scatter(df[x_col], df[y_col], alpha=0.5)
                    ax.set_xlabel(x_col)
                    ax.set_ylabel(y_col)
                    ax.set_title(f'Scatter Plot of {y_col} vs {x_col}')
                    
            elif chart_type == 'Line Chart':
                if x_col not in df.columns or y_col not in df.columns:
                    raise ValueError(f"Columns '{x_col}' or '{y_col}' not found in DataFrame")
                    
                if not pd.api.types.is_numeric_dtype(df[y_col]):
                    ax.text(0.5, 0.5, "Line chart requires numeric data for Y-axis", 
                            ha='center', va='center', transform=ax.transAxes)
                else:
                    # If X is categorical or datetime, sort the data
                    if pd.api.types.is_numeric_dtype(df[x_col]):
                        plot_df = df.sort_values(by=x_col)
                        ax.plot(plot_df[x_col], plot_df[y_col])
                    else:
                        # For non-numeric x-axis, treat as categorical
                        categories = df[x_col].unique()
                        category_means = [df[df[x_col] == cat][y_col].mean() for cat in categories]
                        ax.plot(range(len(categories)), category_means, marker='o')
                        ax.set_xticks(range(len(categories)))
                        ax.set_xticklabels(categories)
                        if plt:
                        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
                        
                    ax.set_xlabel(x_col)
                    ax.set_ylabel(y_col)
                    ax.set_title(f'Line Chart of {y_col} by {x_col}')
                    
            elif chart_type == 'Box Plot':
                if x_col not in df.columns:
                    raise ValueError(f"Column '{x_col}' not found in DataFrame")
                    
                if not pd.api.types.is_numeric_dtype(df[x_col]):
                    ax.text(0.5, 0.5, "Box plot requires numeric data", 
                            ha='center', va='center', transform=ax.transAxes)
                else:
                    ax.boxplot(df[x_col].dropna())
                    ax.set_ylabel(x_col)
                    ax.set_title(f'Box Plot of {x_col}')
                    ax.set_xticks([1])
                    ax.set_xticklabels([x_col])
            
            # Set grid
            ax.grid(True, linestyle='--', alpha=0.7)
            
            # Tight layout
            fig.tight_layout()
            
            # Create canvas
            canvas = FigureCanvasTkAgg(fig, master=self.plot_container)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            error_label = ttk.Label(
                self.plot_container,
                text=f"Error generating plot: {str(e)}",
                foreground="red"
            )
            error_label.pack(expand=True)
    
    def export_data(self):
        """Export the current DataFrame to a file."""
        if self.current_df is None:
            messagebox.showerror("Error", "No data to export.")
            return
            
        # Ask for filename
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[
                ("CSV files", "*.csv"),
                ("Excel files", "*.xlsx"),
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            return
            
        try:
            # Export based on file extension
            if file_path.lower().endswith('.csv'):
                self.current_df.to_csv(file_path, index=False)
            elif file_path.lower().endswith('.xlsx'):
                self.current_df.to_excel(file_path, index=False)
            elif file_path.lower().endswith('.json'):
                self.current_df.to_json(file_path, orient='records')
            else:
                # Default to CSV
                self.current_df.to_csv(file_path, index=False)
                
            messagebox.showinfo("Success", f"Data exported successfully to {file_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export data: {str(e)}")