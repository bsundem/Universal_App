"""
Kaggle data exploration page.
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import tempfile
import importlib.util

# Check for pandas
if importlib.util.find_spec("pandas") is not None:
    import pandas as pd
else:
    pd = None

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

# Import the content page class
from ui.pages.content_page import ContentPage
from utils.logging import get_logger

# Import Kaggle services
from services.kaggle.kaggle_service import kaggle_service
from services.kaggle.kaggle_data_manager import kaggle_data_manager


# Get logger for this module
logger = get_logger(__name__)


class KagglePage(ContentPage):
    """Page for fetching and visualizing data from Kaggle."""

    def __init__(self, parent, controller):
        super().__init__(parent, title="Kaggle Data Explorer")
        self.controller = controller
        self.current_dataset = None
        self.current_dataset_ref = None
        self.current_file = None
        self.current_df = None
        # Use the same temp directory as the service
        self.temp_dir = kaggle_service.temp_dir
        logger.info("KagglePage initialized")
        
    def setup_ui(self):
        """Set up the UI components for the Kaggle page."""
        # Main container frame
        self.main_frame = ttk.Frame(self.content_frame, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Check Kaggle credentials before proceeding
        if not kaggle_service.check_api_credentials():
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
            
        # Save credentials using the service
        if kaggle_service.setup_credentials(username, key):
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
        logger.info(f"Searching for Kaggle datasets with term: '{search_term}'")

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

        logger.debug(f"Search filters - Max size: {max_size}MB, Results limit: {max_results}, File type: {file_type or 'Any'}")

        # Clear existing items in treeview
        for item in self.dataset_tree.get_children():
            self.dataset_tree.delete(item)

        # Show loading message
        loading_item = self.dataset_tree.insert('', 'end', text='Loading...', values=('', ''))
        self.update_idletasks()
        
        # Use the Kaggle service to search asynchronously
        kaggle_service.search_datasets_async(
            callback=lambda datasets: self.after(10, lambda: self.update_dataset_list(datasets, loading_item)),
            search_term=search_term,
            max_size_mb=max_size,
            file_type=file_type,
            max_results=max_results
        )
    
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
        logger.info(f"Dataset selected: {self.current_dataset.get('title')}")

        # Update the UI with the selected dataset
        self.setup_dataset_viewer()
    
    def show(self):
        """Show the Kaggle page."""
        super().show()
        logger.debug("KagglePage shown")

    def hide(self):
        """Hide the Kaggle page."""
        super().hide()
        logger.debug("KagglePage hidden")

    def load_dataset_files(self):
        """Load and display files for the selected dataset."""
        if not self.current_dataset_ref:
            return

        logger.info(f"Loading files for dataset: {self.current_dataset.get('title')}")

        # Clear existing items in files treeview
        for item in self.files_tree.get_children():
            self.files_tree.delete(item)

        # Show loading message
        loading_item = self.files_tree.insert('', 'end', text='Loading...', values=(''))
        self.update_idletasks()
        
        # Use the Kaggle service to get files asynchronously
        kaggle_service.get_dataset_files_async(
            callback=lambda files: self.after(10, lambda: self.update_files_list(files, loading_item)),
            dataset_ref=self.current_dataset_ref
        )
    
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

        logger.info(f"File selected: {filename} from dataset: {self.current_dataset.get('title')}")
            
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
        
        # Use the Kaggle service to download and load the file asynchronously
        kaggle_service.download_and_load_file_async(
            callback=lambda df: self.after(10, lambda: self.display_dataframe(df)),
            dataset_ref=self.current_dataset_ref,
            filename=filename,
            output_dir=self.temp_dir
        )
    
    def display_dataframe(self, df):
        """Display a pandas DataFrame."""
        # Save the current dataframe
        self.current_df = df

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

        # Check dependencies using the data manager
        dependencies = kaggle_data_manager.check_dependencies()
        if not dependencies.get("pandas", False):
            error_label = ttk.Label(
                self.df_frame,
                text="Pandas is not available. Please install with: pip install pandas",
                foreground="red"
            )
            error_label.pack(expand=True)
            return

        # Get DataFrame information from the data manager
        df_info = kaggle_data_manager.get_dataframe_info(df)

        # Create a frame for the DataFrame preview
        preview_frame = ttk.Frame(self.df_frame)
        preview_frame.pack(fill=tk.BOTH, expand=True)

        # Show DataFrame info
        if "error" not in df_info:
            info_text = f"Rows: {df_info.get('rows', 0)}, Columns: {df_info.get('columns', 0)}"
            info_text += f" | Memory: {df_info.get('memory_usage', 0):.2f} MB"
            missing_count = sum(df_info.get('missing_values', {}).values())
            if missing_count > 0:
                info_text += f" | Missing values: {missing_count}"
        else:
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
            # Use column type information from data manager if available
            if not "error" in df_info and col in df_info.get('dtypes', {}):
                col_type = df_info['dtypes'][col]
                if 'int' in col_type or 'float' in col_type:
                    tree.column(col, width=80, anchor='e')
                else:
                    tree.column(col, width=150, anchor='w')
            else:
                # Fallback to direct checking
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
            logger.warning("Cannot generate plot: No dataframe loaded")
            return

        df = self.current_df
        chart_type = self.chart_type_var.get()
        x_col = self.x_var.get()
        y_col = self.y_var.get()

        logger.info(f"Generating {chart_type} with x={x_col}, y={y_col}")

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

            # Use the data manager to get column summary and display it as text
            if pd is not None and df is not None:
                text_frame = ttk.Frame(self.plot_container)
                text_frame.pack(fill=tk.BOTH, expand=True, pady=10)

                data_text = tk.Text(text_frame, height=20, width=50)
                data_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

                scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=data_text.yview)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                data_text.config(yscrollcommand=scrollbar.set)

                # Get column summary using the data manager
                summary_result = kaggle_data_manager.get_column_summary(df, x_col)
                if summary_result.get("success", False):
                    summary = summary_result["summary"]
                    data_text.insert(tk.END, f"Data Summary for: {x_col}\n\n")

                    # Format and display the summary
                    for key, value in summary.items():
                        if isinstance(value, dict):
                            data_text.insert(tk.END, f"{key}:\n")
                            for subkey, subvalue in value.items():
                                data_text.insert(tk.END, f"  {subkey}: {subvalue}\n")
                        else:
                            data_text.insert(tk.END, f"{key}: {value}\n")
                else:
                    data_text.insert(tk.END, f"Error getting summary: {summary_result.get('error', 'Unknown error')}")

                data_text.config(state=tk.DISABLED)

            return

        try:
            # Use the data manager to prepare plot data
            plot_data = kaggle_data_manager.generate_plot_data(
                df,
                chart_type,
                x_col,
                y_col,
                bins=30,  # For histogram
                top_n=20,  # For bar chart
                sample_size=1000  # For scatter plot
            )

            # Check for errors
            if "error" in plot_data:
                error_label = ttk.Label(
                    self.plot_container,
                    text=f"Error: {plot_data['error']}",
                    foreground="red"
                )
                error_label.pack(expand=True)
                return

            # Create figure and axis
            fig = Figure(figsize=(10, 6), dpi=100)
            ax = fig.add_subplot(111)

            # Generate plot based on chart type
            if chart_type == 'Histogram':
                if "data" in plot_data:
                    hist_data = plot_data["data"]
                    bin_edges = hist_data["bin_edges"]
                    bin_centers = hist_data["bin_centers"]
                    counts = hist_data["counts"]

                    # Create histogram
                    ax.bar(bin_centers, counts, width=(bin_edges[1] - bin_edges[0]), alpha=0.7)
                    ax.set_xlabel(x_col)
                    ax.set_ylabel('Frequency')
                    ax.set_title(f'Histogram of {x_col}')

            elif chart_type == 'Bar Chart':
                if "data" in plot_data:
                    bar_data = plot_data["data"]
                    labels = bar_data["labels"]
                    values = bar_data["values"]

                    # Create bar chart
                    ax.bar(range(len(values)), values, tick_label=labels)
                    ax.set_xlabel(x_col)
                    ax.set_ylabel('Count')
                    ax.set_title(f'Bar Chart of {x_col}')

                    # Rotate labels if many categories
                    if len(labels) > 5:
                        if plt:
                            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

            elif chart_type == 'Scatter Plot':
                if "data" in plot_data:
                    scatter_data = plot_data["data"]
                    x_values = scatter_data["x"]
                    y_values = scatter_data["y"]
                    correlation = scatter_data.get("correlation", 0)

                    # Create scatter plot
                    ax.scatter(x_values, y_values, alpha=0.5)
                    ax.set_xlabel(x_col)
                    ax.set_ylabel(y_col)
                    ax.set_title(f'Scatter Plot of {y_col} vs {x_col} (r={correlation:.2f})')

            elif chart_type == 'Line Chart':
                if "data" in plot_data:
                    line_data = plot_data["data"]
                    x_values = line_data["x"]
                    y_values = line_data["y"]
                    x_is_numeric = line_data.get("x_is_numeric", True)

                    # Create line chart
                    if x_is_numeric:
                        ax.plot(x_values, y_values)
                    else:
                        # For categorical x-axis
                        ax.plot(range(len(x_values)), y_values, marker='o')
                        ax.set_xticks(range(len(x_values)))
                        ax.set_xticklabels(x_values)
                        if plt:
                            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

                    ax.set_xlabel(x_col)
                    ax.set_ylabel(y_col)
                    ax.set_title(f'Line Chart of {y_col} by {x_col}')

            elif chart_type == 'Box Plot':
                if "data" in plot_data:
                    box_data = plot_data["data"]

                    # Create boxplot manually since we have the statistics
                    box_stats = {
                        'medians': [box_data["median"]],
                        'q1': [box_data["q1"]],
                        'q3': [box_data["q3"]],
                        'whislo': [box_data["whisker_low"]],
                        'whishi': [box_data["whisker_high"]],
                        'fliers': [box_data["outliers"]]
                    }
                    ax.bxp([box_stats], showfliers=True)
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
            logger.warning("Cannot export data: No dataframe loaded")
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
            logger.debug("Export cancelled by user")
            return

        logger.info(f"Exporting data to: {file_path}")

        # Use the data manager to export the data
        result = kaggle_data_manager.export_dataframe(self.current_df, file_path)

        if result.get("success", False):
            # Show success message with details
            rows = result.get("rows", 0)
            columns = result.get("columns", 0)
            format = result.get("format", "unknown")
            messagebox.showinfo(
                "Success",
                f"Data exported successfully to {file_path}\n"
                f"Format: {format}\n"
                f"Rows: {rows}, Columns: {columns}"
            )
        else:
            # Show error message
            error_msg = result.get("error", "Unknown error")
            messagebox.showerror("Error", f"Failed to export data: {error_msg}")