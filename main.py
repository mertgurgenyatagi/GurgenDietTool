import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import simpledialog
import csv
import os
import io
import pandas as pd
from tksheet import Sheet

# Shared nutrient fields (name, unit)
NUTRIENT_FIELDS = [
    ("Name", ""),
    ("Amount", "g"),
    ("Calories / Energy", "kcal"),
    ("Protein", "g"),
    ("Total Fat", "g"),
    ("Saturated Fat", "g"),
    ("Monounsaturated Fat", "g"),
    ("Polyunsaturated Fat", "g"),
    ("Trans Fat", "g"),
    ("Cholesterol", "mg"),
    ("Carbohydrates", "g"),
    ("Dietary Fiber", "g"),
    ("Soluble Fiber", "g"),
    ("Insoluble Fiber", "g"),
    ("Total Sugars", "g"),
    ("Added Sugars", "g"),
    ("Sodium", "mg"),
    ("Potassium", "mg"),
    ("Calcium", "mg"),
    ("Iron", "mg"),
    ("Magnesium", "mg"),
    ("Zinc", "mg"),
    ("Phosphorus", "mg"),
    ("Iodine", "µg"),
    ("Vitamin A", "µg"),
    ("Vitamin C", "mg"),
    ("Vitamin D", "µg"),
    ("Vitamin E", "mg"),
    ("Vitamin K", "µg"),
    ("Vitamin B1 (Thiamine)", "mg"),
    ("Vitamin B2 (Riboflavin)", "mg"),
    ("Vitamin B3 (Niacin)", "mg"),
    ("Vitamin B6", "mg"),
    ("Vitamin B9 (Folate)", "µg"),
    ("Vitamin B12", "µg"),
    ("Omega-3 Fatty Acids", "g"),
    ("Omega-6 Fatty Acids", "g")
]

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("GurgenDietTool")
        self.geometry("800x600")
        
        # Set application icon
        try:
            # Load PNG icon using PhotoImage
            icon = tk.PhotoImage(file="icons/apple.png")
            self.iconphoto(False, icon)
        except Exception as e:
            # Fallback if icon file is not found
            print(f"Could not load icon: {e}")

        # Store food items and CSV file path
        self.food_items = []
        self.csv_file = "data/food_items.csv"

        # Store plans and CSV path
        self.plans_dir = "plans"
        if not os.path.exists(self.plans_dir):
            os.makedirs(self.plans_dir)

        # Dialog management - prevent duplicate dialogs
        self._dialog_lock = False
        self._last_dialog_time = 0

        # Load existing food items and plans from CSV
        self.food_items = self.load_food_items()
        self.load_plans()

        # Main menu frame
        self.menu_frame = ttk.Frame(self)
        self.menu_frame.pack(expand=True)

        # Title
        title_label = ttk.Label(self.menu_frame, text="Gürgen Diet Tool", 
                               font=('Helvetica', 24, 'bold'))
        title_label.pack(pady=30)

        # Style for buttons
        style = ttk.Style()
        style.configure("TButton", font=('Helvetica', 16), padding=10)

        # Buttons
        plans_button = ttk.Button(self.menu_frame, text="Plans", command=self.show_plans, width=20)
        plans_button.pack(pady=10)

        food_items_button = ttk.Button(self.menu_frame, text="Food Items", command=self.show_food_items, width=20)
        food_items_button.pack(pady=10)

        settings_button = ttk.Button(self.menu_frame, text="Settings", command=self.show_settings, width=20)
        settings_button.pack(pady=10)

        # Main content frame
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=10)

    def show_plans(self):
        self.hide_menu()
        self.clear_main_frame()

        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill="x", pady=10)

        title_label = ttk.Label(header_frame, text="Plans", font=('Helvetica', 18, 'bold'))
        title_label.pack(side="left")

        new_button = ttk.Button(header_frame, text="New Plan", command=self.show_new_plan)
        new_button.pack(side="right")

        back_button = ttk.Button(header_frame, text="Back", command=self.show_menu)
        back_button.pack(side="right", padx=(0, 10))

        list_frame = ttk.Frame(self.main_frame)
        list_frame.pack(fill="both", expand=True)

        # Plans will be displayed as buttons
        self.plans_container = ttk.Frame(list_frame)
        self.plans_container.pack(pady=10)

        self.refresh_plans_list()

    def show_food_items(self):
        self.hide_menu()
        self.clear_main_frame()
        
        # Food Items page header
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill="x", pady=10)
        
        title_label = ttk.Label(header_frame, text="Food Items", font=('Helvetica', 18, 'bold'))
        title_label.pack(side="left")
        
        new_button = ttk.Button(header_frame, text="New", command=self.show_new_food_item)
        new_button.pack(side="right")
        
        delete_button = ttk.Button(header_frame, text="Delete", command=self.delete_selected_food_item)
        delete_button.pack(side="right", padx=(0, 10))
        
        back_button = ttk.Button(header_frame, text="Back", command=self.show_menu)
        back_button.pack(side="right", padx=(0, 10))
        
        # Food items list
        list_frame = ttk.Frame(self.main_frame)
        list_frame.pack(fill="both", expand=True)
        
        # Create Treeview for food items list (show all fields)
        self.display_columns = [
            "Name", "Amount", "Calories / Energy", "Protein", "Total Fat",
            "Saturated Fat", "Monounsaturated Fat", "Polyunsaturated Fat",
            "Trans Fat", "Cholesterol", "Carbohydrates", "Dietary Fiber",
            "Soluble Fiber", "Insoluble Fiber", "Total Sugars", "Added Sugars",
            "Sodium", "Potassium", "Calcium", "Iron", "Magnesium", "Zinc",
            "Phosphorus", "Iodine", "Vitamin A", "Vitamin C", "Vitamin D",
            "Vitamin E", "Vitamin K", "Vitamin B1 (Thiamine)", 
            "Vitamin B2 (Riboflavin)", "Vitamin B3 (Niacin)", "Vitamin B6",
            "Vitamin B9 (Folate)", "Vitamin B12", "Omega-3 Fatty Acids",
            "Omega-6 Fatty Acids"
        ]

        self.food_tree = ttk.Treeview(list_frame, columns=self.display_columns, show="headings", height=15)

        # Configure columns (narrower widths for many columns)
        for i, col in enumerate(self.display_columns):
            self.food_tree.heading(col, text=col)
            if i == 0:
                self.food_tree.column(col, width=160, anchor='w')
            else:
                self.food_tree.column(col, width=100, anchor='center')
        
        # Scrollbars for the list (vertical + horizontal)
        vscrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.food_tree.yview)
        hscrollbar = ttk.Scrollbar(list_frame, orient="horizontal", command=self.food_tree.xview)
        self.food_tree.configure(yscrollcommand=vscrollbar.set, xscrollcommand=hscrollbar.set)

        self.food_tree.pack(side="top", fill="both", expand=True)
        vscrollbar.pack(side="right", fill="y")
        hscrollbar.pack(side="bottom", fill="x")
        
        # Enable fast horizontal scrolling with shift+wheel
        def _on_tree_mousewheel(event):
            if event.state & 0x0001:  # Shift key pressed
                # Fast horizontal scrolling - 30 units per scroll (2x faster)
                if event.delta > 0:
                    self.food_tree.xview_scroll(-30, "units")
                else:
                    self.food_tree.xview_scroll(30, "units")
                return "break"
            else:
                # Fast vertical scrolling - 5 units per scroll
                if event.delta > 0:
                    self.food_tree.yview_scroll(-5, "units")
                else:
                    self.food_tree.yview_scroll(5, "units")
                return "break"
        
        # Add horizontal scrolling for touchpad horizontal gestures
        def _on_tree_horizontal_scroll(event):
            # Horizontal touchpad scrolling - very fast (44 units, 2x faster)
            if event.delta > 0:
                self.food_tree.xview_scroll(-44, "units")
            else:
                self.food_tree.xview_scroll(44, "units")
            return "break"
        
        def _on_tree_enter(event):
            self.food_tree.focus_set()
            self.food_tree.bind_all('<MouseWheel>', _on_tree_mousewheel)
            # Bind horizontal scroll events for touchpad
            self.food_tree.bind_all('<Shift-MouseWheel>', _on_tree_horizontal_scroll)
            
        def _on_tree_leave(event):
            try:
                self.food_tree.unbind_all('<MouseWheel>')
                self.food_tree.unbind_all('<Shift-MouseWheel>')
            except:
                pass
                
        self.food_tree.bind('<Enter>', _on_tree_enter)
        self.food_tree.bind('<Leave>', _on_tree_leave)
        
        # Populate the list with existing food items
        self.refresh_food_list()

    def show_new_food_item(self):
        self.clear_main_frame()
        
        # Create scrollable frame for the form
        canvas = tk.Canvas(self.main_frame)
        scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        # Enable mousewheel/touchpad scrolling when pointer is over the scrollable area
        self._enable_mousewheel_scrolling(canvas, scrollable_frame)
        
        # Header
        header_frame = ttk.Frame(scrollable_frame)
        header_frame.pack(fill="x", pady=10)
        
        title_label = ttk.Label(header_frame, text="New Food Item", font=('Helvetica', 18, 'bold'))
        title_label.pack(side="left")
        
        back_button = ttk.Button(header_frame, text="Back", command=self.show_food_items)
        back_button.pack(side="right")
        
        save_button = ttk.Button(header_frame, text="Save", command=self.save_food_item)
        save_button.pack(side="right", padx=(0, 10))
        
        # Form fields
        self.food_entries = {}

        # Use shared nutrient fields
        fields = NUTRIENT_FIELDS

        # Create form fields
        for field_name, unit in fields:
            field_frame = ttk.Frame(scrollable_frame)
            field_frame.pack(fill="x", padx=20, pady=5)

            label = ttk.Label(field_frame, text=field_name, width=25, anchor="w")
            label.pack(side="left")

            entry = ttk.Entry(field_frame, width=20)
            entry.pack(side="left", padx=(10, 5))

            if unit:
                unit_label = ttk.Label(field_frame, text=unit, width=15, anchor="w")
                unit_label.pack(side="left")

            self.food_entries[field_name] = entry

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def show_new_plan(self):
        # New plan form - only asks for plan name
        self.clear_main_frame()

        # Header inside the scrollable area
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill="x", pady=10)

        title_label = ttk.Label(header_frame, text="New Plan", font=('Helvetica', 18, 'bold'))
        title_label.pack(side="left")

        back_button = ttk.Button(header_frame, text="Back", command=self.show_plans)
        back_button.pack(side="right")

        save_button = ttk.Button(header_frame, text="Save", command=self.save_plan)
        save_button.pack(side="right", padx=(0, 10))

        # Form fields inside scrollable_frame
        form_frame = ttk.Frame(self.main_frame)
        form_frame.pack(fill="x", padx=20, pady=20)
        
        name_label = ttk.Label(form_frame, text="Plan Name:", font=('Helvetica', 12))
        name_label.pack(side="left", padx=(0, 10))
        
        self.plan_name_entry = ttk.Entry(form_frame, width=40, font=('Helvetica', 12))
        self.plan_name_entry.pack(side="left", expand=True, fill="x")
        self.plan_name_entry.focus()  # Set focus to the entry field
        
        # Bind Enter key to save function
        self.plan_name_entry.bind("<Return>", lambda event: self.save_plan())

    def save_plan(self):
        plan_name = self.plan_name_entry.get().strip()

        if not plan_name:
            messagebox.showerror('Error', 'Plan name is required')
            return
            
        # Sanitize filename
        safe_filename = "".join([c for c in plan_name if c.isalpha() or c.isdigit() or c.isspace()]).rstrip()
        plan_filepath = os.path.join(self.plans_dir, f"{safe_filename}.csv")
        
        if os.path.exists(plan_filepath):
            messagebox.showerror('Error', f'A plan with the name "{plan_name}" already exists.')
            return

        try:
            # Read the hardcoded rows from the template
            hardcoded_df = pd.read_csv("templates/plan_template.csv")
            
            # Create a new DataFrame for the plan
            plan_df = hardcoded_df.copy()
            
            # Save the new plan to its own CSV file
            plan_df.to_csv(plan_filepath, index=False)
            
            # No success popup - just reload and redirect
            self.load_plans() # Reload plans to include the new one
            self.show_plans()
            
        except Exception as e:
            messagebox.showerror('Error', f'Failed to create plan: {e}')

    def load_plans(self):
        self.plans = []
        for filename in os.listdir(self.plans_dir):
            if filename.endswith(".csv"):
                plan_name = os.path.splitext(filename)[0]
                self.plans.append({"Name": plan_name, "filepath": os.path.join(self.plans_dir, filename)})

    def refresh_plans_list(self):
        # Clear existing
        for child in getattr(self, 'plans_container').winfo_children():
            child.destroy()
        # Add a button for each plan
        for p in self.plans:
            name = p.get('Name', 'Unnamed')
            
            # Create a frame for each plan with open and delete buttons
            plan_frame = ttk.Frame(self.plans_container)
            plan_frame.pack(fill='x', pady=2)
            
            # Open plan button
            open_btn = ttk.Button(plan_frame, text=name, 
                               command=lambda plan=p: self.open_plan_spreadsheet(plan))
            open_btn.pack(side='left', fill='x', expand=True, padx=(0, 5))
            
            # Delete plan button
            delete_btn = ttk.Button(plan_frame, text="Delete", 
                                  command=lambda plan=p: self.delete_plan(plan))
            delete_btn.pack(side='right')

    def delete_plan(self, plan):
        """Delete a plan after confirmation."""
        result = messagebox.askyesno("Delete Plan", 
                                   f"Are you sure you want to delete the plan '{plan['Name']}'?")
        if result:
            try:
                # Delete the file
                os.remove(plan['filepath'])
                # Reload the plans list
                self.load_plans()
                self.refresh_plans_list()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete plan: {e}")

    def open_plan_spreadsheet(self, plan):
        """Opens the tksheet spreadsheet for the selected plan in the main window."""
        self.hide_menu()
        self.clear_main_frame()
        
        # Header with plan name and back button
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill="x", pady=10)
        
        title_label = ttk.Label(header_frame, text=f"Plan: {plan['Name']}", 
                               font=('Helvetica', 18, 'bold'))
        title_label.pack(side="left")
        
        back_button = ttk.Button(header_frame, text="Back", command=self.show_plans)
        back_button.pack(side="right")

        # --- Spreadsheet Controls ---
        controls_frame = ttk.Frame(self.main_frame)
        controls_frame.pack(pady=5, fill='x')

        # Store the plan for the button callback
        self._current_plan = plan
        
        add_food_button = ttk.Button(controls_frame, text="Add Food Item", 
                                     command=self._on_add_food_clicked)
        add_food_button.pack(side='left', padx=(0, 10))
        
        # Store reference to the button for enabling/disabling
        self.add_food_button = add_food_button
        
        # Disable button focus and key events to prevent accidental triggering
        add_food_button.configure(takefocus=False)
        
        delete_food_button = ttk.Button(controls_frame, text="Delete Selected Item",
                                       command=self.delete_selected_food_from_sheet)
        delete_food_button.pack(side='left', padx=(0, 10))

        # --- tksheet Widget ---
        sheet_frame = ttk.Frame(self.main_frame)
        sheet_frame.pack(fill="both", expand=True)
        
        self.sheet = Sheet(sheet_frame,
                           show_toolbar=True,
                           show_top_left=False,
                           show_x_scrollbar=True,
                           show_y_scrollbar=True,
                           show_bottom_right_corner=True)
        self.sheet.pack(fill="both", expand=True)
        
        # Enable editing capabilities
        self.sheet.enable_bindings(("single_select", "row_select", "column_select", "drag_select", 
                                   "column_width_resize", "double_click_column_resize", "row_height_resize", 
                                   "column_height_resize", "arrowkeys", "right_click_popup_menu", 
                                   "rc_select", "rc_insert_column", "rc_delete_column", "rc_insert_row", 
                                   "rc_delete_row", "copy", "cut", "paste", "delete", "select_all", 
                                   "edit_cell"))

        self.load_plan_data_to_sheet(plan['filepath'])

    def load_plan_data_to_sheet(self, filepath):
        """Loads data from the plan's CSV into the tksheet widget."""
        try:
            self.current_plan_df = pd.read_csv(filepath)
            
            # Load nutrient modes for color coding
            self.load_nutrient_modes()
            
            # Prepare data for tksheet
            headers = self.current_plan_df.columns.tolist()
            data = self.current_plan_df.values.tolist()
            
            # The CSV now has: Row 0 = Recommended values
            # We need to add: Row 1 = Summation (calculated), then food items start from Row 2
            recommended_row = data[0] if len(data) > 0 else [0] * len(headers)
            summation_row = [""] * len(headers)  # Will be calculated, start empty
            
            # Any additional rows are existing food items
            food_item_data = data[1:] if len(data) > 1 else []

            # Set up the sheet
            self.sheet.headers(headers)
            self.sheet.set_sheet_data(food_item_data, reset_col_positions=True, reset_row_positions=True)
            
            # Insert special rows at the top
            self.sheet.insert_row(idx=0)
            self.sheet.set_row_data(0, values=recommended_row)
            self.sheet.insert_row(idx=1)
            self.sheet.set_row_data(1, values=summation_row)
            
            # Set row headers to distinguish special rows
            row_headers = ["Recommended", "Summation"] + [f"Item {i+1}" for i in range(len(food_item_data))]
            self.sheet.row_index(row_headers)
            
            # Make "Recommended" and "Summation" rows read-only
            self.sheet.readonly_rows([0, 1])
            
            # Configure column editability for food items (rows 2+)
            if 'Amount' in headers:
                amount_col_index = headers.index('Amount')
                name_col_index = headers.index('Name') if 'Name' in headers else -1
                
                # Make all columns read-only except Amount and Name for food item rows
                for row_idx in range(2, self.sheet.get_total_rows()):
                    for col_idx in range(len(headers)):
                        try:
                            if col_idx == amount_col_index or col_idx == name_col_index:
                                # Explicitly make Amount and Name columns editable
                                self.sheet.readonly(rows=[row_idx], columns=[col_idx], readonly=False)
                            else:
                                # Make all other columns read-only
                                self.sheet.readonly(rows=[row_idx], columns=[col_idx], readonly=True)
                        except TypeError:
                            # Try alternative API syntax
                            try:
                                if col_idx == amount_col_index or col_idx == name_col_index:
                                    self.sheet.readonly((row_idx, col_idx), readonly=False)
                                else:
                                    self.sheet.readonly((row_idx, col_idx), readonly=True)
                            except:
                                print(f"Could not set readonly for cell ({row_idx}, {col_idx})")

            # Bind multiple event types for data changes to update summation
            try:
                self.sheet.extra_bindings("end_edit_table", self.update_summation_and_row)
                self.sheet.extra_bindings("end_edit_cell", self.update_summation_and_row)
                self.sheet.extra_bindings("cell_edited", self.update_summation_and_row)
            except Exception as e:
                print(f"Error adding event bindings: {e}")
            
            self.update_summation_row_tksheet()
            self.apply_color_coding()  # Apply color coding after initial load

        except Exception as e:
            messagebox.showerror("Error", f"Could not load plan file into sheet: {e}", parent=self)

    def load_nutrient_modes(self):
        """Load nutrient modes from data/nutrient_modes.csv"""
        try:
            modes_df = pd.read_csv("data/nutrient_modes.csv")
            self.nutrient_modes = {}
            
            # Get headers and modes
            headers = modes_df.columns.tolist()
            modes = modes_df.iloc[0].tolist() if len(modes_df) > 0 else []
            
            # Create mapping with proper header matching
            for i, header in enumerate(headers):
                if i < len(modes):
                    # Map both with and without units for compatibility
                    self.nutrient_modes[header] = modes[i]
                    # Also map with units if they exist in the plan headers
                    for plan_header in self.current_plan_df.columns:
                        if header in plan_header:
                            self.nutrient_modes[plan_header] = modes[i]
            
        except Exception as e:
            print(f"Warning: Could not load nutrient modes: {e}")
            self.nutrient_modes = {}

    def apply_color_coding(self):
        """Apply color coding to the recommended values based on nutrient modes and summation."""
        try:
            headers = self.sheet.headers()
            
            # Get recommended and summation values
            recommended_data = self.sheet.get_row_data(0)
            summation_data = self.sheet.get_row_data(1)
            
            if not recommended_data or not summation_data:
                return
            
            for col_idx, header in enumerate(headers):
                if col_idx >= len(recommended_data) or col_idx >= len(summation_data):
                    continue
                    
                # Skip Name and Amount columns
                if header in ['Name', 'Amount']:
                    continue
                
                # Get the mode for this nutrient
                mode = self.nutrient_modes.get(header, 'irrelevant')
                
                try:
                    recommended_val = float(recommended_data[col_idx]) if recommended_data[col_idx] else 0
                    summation_val = float(summation_data[col_idx]) if summation_data[col_idx] else 0
                except (ValueError, TypeError):
                    continue
                
                # Determine color based on mode and comparison
                color = None
                
                if mode == 'good':
                    if recommended_val > summation_val:
                        color = '#FF6B6B'  # Red - not meeting good nutrient target
                    elif recommended_val < summation_val:
                        color = '#51CF66'  # Green - exceeding good nutrient target
                elif mode == 'harmful':
                    if recommended_val > summation_val:
                        color = '#51CF66'  # Green - staying below harmful limit
                    elif recommended_val < summation_val:
                        color = '#FF6B6B'  # Red - exceeding harmful limit
                # mode == 'irrelevant' keeps default color (no change)
                
                # Apply the color to the recommended value cell
                if color:
                    self.sheet.highlight_cells(row=0, column=col_idx, bg=color)
                else:
                    # Reset to default if irrelevant
                    self.sheet.dehighlight_cells(row=0, column=col_idx)
                    
        except Exception as e:
            print(f"Warning: Could not apply color coding: {e}")

    def save_plan_data(self, filepath):
        """Saves the current state of the tksheet back to the CSV file."""
        try:
            # Get all data from the sheet, including the special rows
            all_data = self.sheet.get_sheet_data()
            
            # The first row is "Recommended", the rest are food items
            # We skip the "Summation" row when saving
            recommended_row = all_data[0]
            food_item_rows = all_data[2:]
            
            # Combine into a list of lists for the DataFrame
            data_to_save = [recommended_row] + food_item_rows
            
            # Create a new DataFrame
            df_to_save = pd.DataFrame(data_to_save, columns=self.sheet.headers())
            
            # Save to CSV
            df_to_save.to_csv(filepath, index=False)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save plan: {e}", parent=self)

    def _on_add_food_clicked(self):
        """Handle add food button click with proper method binding."""
        if hasattr(self, '_current_plan'):
            self.add_food_item_with_lock(self._current_plan)

    def add_food_item_with_lock(self, plan):
        """Add food item with duplicate prevention."""
        import time, random
        call_id = random.randint(1000, 9999)
        current_time = time.time()
        
        # Check if we're already processing a food item addition
        if self._dialog_lock:
            return
            
        # Check if this is a very rapid duplicate call (within 100ms)
        if current_time - self._last_dialog_time < 0.1:
            return
            
        # Set locks immediately
        self._dialog_lock = True
        self._last_dialog_time = current_time
        
        # Disable the button to prevent additional clicks
        button_was_disabled = False
        if hasattr(self, 'add_food_button'):
            try:
                self.add_food_button.configure(state='disabled')
                button_was_disabled = True
            except tk.TclError:
                pass
        
        try:
            self.show_food_item_selection_dialog(plan)
        except Exception as e:
            print(f"Error in dialog: {e}")
        finally:
            # Reset locks and re-enable button if it was disabled
            self._dialog_lock = False
            if button_was_disabled and hasattr(self, 'add_food_button'):
                try:
                    self.add_food_button.configure(state='normal')
                except tk.TclError:
                    pass
            # Ensure focus goes to the sheet instead of staying on the button
            if hasattr(self, 'sheet'):
                try:
                    self.sheet.focus_set()
                except tk.TclError:
                    pass

    def show_food_item_selection_dialog(self, plan):
        """Shows an inline food selection interface."""
        # Destroy any ghost Toplevel windows to eliminate any potential issues
        for widget in self.winfo_children():
            if isinstance(widget, tk.Toplevel):
                try:
                    widget.destroy()
                except:
                    pass
        
        # Clear the main window and show food selection interface
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # Title
        title_label = ttk.Label(self.main_frame, text=f"Select Food Item for {plan}", 
                               font=('Helvetica', 18, 'bold'))
        title_label.pack(pady=20)
        
        # Load food items
        food_items = self.load_food_items()
        if not food_items:
            messagebox.showinfo("No Food Items", "There are no food items to add. Please create some first.")
            self.open_plan_spreadsheet(plan)  # Go back to spreadsheet
            return
        
        # Create listbox for food selection
        listbox_frame = ttk.Frame(self.main_frame)
        listbox_frame.pack(pady=20, padx=20, fill='both', expand=True)
        
        listbox = tk.Listbox(listbox_frame, height=15, font=('Helvetica', 12))
        scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=listbox.yview)
        listbox.configure(yscrollcommand=scrollbar.set)
        
        food_item_names = [item['Name'] for item in food_items]
        for name in food_item_names:
            listbox.insert(tk.END, name)
        
        listbox.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        listbox.focus()
        
        # Buttons frame
        buttons_frame = ttk.Frame(self.main_frame)
        buttons_frame.pack(pady=20)
        
        def on_select_item():
            selected_indices = listbox.curselection()
            if not selected_indices:
                messagebox.showwarning("No Selection", "Please select a food item.")
                return
            
            selected_index = selected_indices[0]
            selected_food_item = food_items[selected_index]
            
            # Ask for amount
            amount = simpledialog.askfloat("Servings", "Enter number of servings:", 
                                         minvalue=0.1, maxvalue=100.0, parent=self)
            
            if amount is not None:
                # Go back to spreadsheet and add the item
                self.open_plan_spreadsheet(plan)
                self.add_food_item_to_tksheet(selected_food_item, amount)
            else:
                # Just go back to spreadsheet
                self.open_plan_spreadsheet(plan)
        
        def on_cancel():
            self.open_plan_spreadsheet(plan)
        
        # Bind Enter and double-click
        listbox.bind("<Return>", lambda event: on_select_item())
        listbox.bind("<Double-Button-1>", lambda event: on_select_item())
        
        # Buttons
        select_button = ttk.Button(buttons_frame, text="Select", command=on_select_item)
        select_button.pack(side='left', padx=(0, 10))
        
        cancel_button = ttk.Button(buttons_frame, text="Cancel", command=on_cancel)
        cancel_button.pack(side='left')

    def add_food_item_to_tksheet(self, food_item, amount):
        """Adds a new row for the selected food item to the tksheet."""
        headers = self.sheet.headers()
        new_row = ["" for _ in headers]
        
        # Create a mapping between plan headers and food item keys
        def get_food_value(plan_header, food_item):
            # Direct match first
            if plan_header in food_item:
                return food_item[plan_header]
            
            # Handle common variations between plan and food item column names
            mappings = {
                'Calories / Energy (kcal)': 'Calories / Energy',
                'Protein (g)': 'Protein',
                'Total Fat (g)': 'Total Fat',
                'Saturated Fat (g)': 'Saturated Fat',
                'Monounsaturated Fat (g)': 'Monounsaturated Fat',
                'Polyunsaturated Fat (g)': 'Polyunsaturated Fat',
                'Trans Fat (g)': 'Trans Fat',
                'Cholesterol (mg)': 'Cholesterol',
                'Carbohydrates (g)': 'Carbohydrates',
                'Dietary Fiber (g)': 'Dietary Fiber',
                'Soluble Fiber (g)': 'Soluble Fiber',
                'Insoluble Fiber (g)': 'Insoluble Fiber',
                'Total Sugars (g)': 'Total Sugars',
                'Added Sugars (g)': 'Added Sugars',
                'Sodium (mg)': 'Sodium',
                'Potassium (mg)': 'Potassium',
                'Calcium (mg)': 'Calcium',
                'Iron (mg)': 'Iron',
                'Magnesium (mg)': 'Magnesium',
                'Zinc (mg)': 'Zinc',
                'Phosphorus (mg)': 'Phosphorus',
                'Iodine (µg)': 'Iodine',
                'Vitamin A (µg)': 'Vitamin A',
                'Vitamin C (mg)': 'Vitamin C',
                'Vitamin D (µg)': 'Vitamin D',
                'Vitamin E (mg)': 'Vitamin E',
                'Vitamin K (µg)': 'Vitamin K',
                'Vitamin B1 (Thiamine) (mg)': 'Vitamin B1 (Thiamine)',
                'Vitamin B2 (Riboflavin) (mg)': 'Vitamin B2 (Riboflavin)',
                'Vitamin B3 (Niacin) (mg)': 'Vitamin B3 (Niacin)',
                'Vitamin B6 (mg)': 'Vitamin B6',
                'Vitamin B9 (Folate) (µg)': 'Vitamin B9 (Folate)',
                'Vitamin B12 (µg)': 'Vitamin B12',
                'Omega-3 Fatty Acids (g)': 'Omega-3 Fatty Acids',
                'Omega-6 Fatty Acids (g)': 'Omega-6 Fatty Acids'
            }
            
            # Try the mapping
            food_key = mappings.get(plan_header)
            if food_key and food_key in food_item:
                return food_item[food_key]
            
            return "0"  # Default if not found
        
        for i, col_name in enumerate(headers):
            if col_name == 'Name':
                new_row[i] = food_item.get('Name', '')
            elif col_name == 'Amount':
                new_row[i] = f"{amount:.2f}"
            else:
                base_value = get_food_value(col_name, food_item)
                try:
                    # Since our food items are already per serving (Amount=1), multiply directly by amount
                    calculated_value = float(base_value) * amount
                    new_row[i] = f"{calculated_value:.2f}"
                except (ValueError, TypeError):
                    new_row[i] = "0.00"
        
        # Add the new row to the sheet
        self.sheet.insert_row()
        new_row_index = self.sheet.get_total_rows() - 1
        self.sheet.set_row_data(new_row_index, values=new_row)
        
        # Store the base data (per 100g) for recalculations
        # We need a way to map sheet row index to this data
        if not hasattr(self, 'sheet_base_data'):
            self.sheet_base_data = {}
        self.sheet_base_data[new_row_index] = food_item
        
        self.update_summation_row_tksheet()
        self.update_row_headers()
        
        # Auto-save after adding food item
        if hasattr(self, '_current_plan') and 'filepath' in self._current_plan:
            self.save_plan_data(self._current_plan['filepath'])

    def recalculate_row(self, row_index, new_amount):
        """Recalculate a specific row based on new amount."""
        base_food_item = self.sheet_base_data.get(row_index)
        if not base_food_item:
            print(f"No base data for row {row_index}")
            return

        headers = self.sheet.headers()
        
        # Create mapping function
        def get_food_value(plan_header, food_item):
            if plan_header in food_item:
                return food_item[plan_header]
            
            mappings = {
                'Calories / Energy (kcal)': 'Calories / Energy',
                'Protein (g)': 'Protein',
                'Total Fat (g)': 'Total Fat',
                'Saturated Fat (g)': 'Saturated Fat',
                'Monounsaturated Fat (g)': 'Monounsaturated Fat',
                'Polyunsaturated Fat (g)': 'Polyunsaturated Fat',
                'Trans Fat (g)': 'Trans Fat',
                'Cholesterol (mg)': 'Cholesterol',
                'Carbohydrates (g)': 'Carbohydrates',
                'Dietary Fiber (g)': 'Dietary Fiber',
                'Soluble Fiber (g)': 'Soluble Fiber',
                'Insoluble Fiber (g)': 'Insoluble Fiber',
                'Total Sugars (g)': 'Total Sugars',
                'Added Sugars (g)': 'Added Sugars',
                'Sodium (mg)': 'Sodium',
                'Potassium (mg)': 'Potassium',
                'Calcium (mg)': 'Calcium',
                'Iron (mg)': 'Iron',
                'Magnesium (mg)': 'Magnesium',
                'Zinc (mg)': 'Zinc',
                'Phosphorus (mg)': 'Phosphorus',
                'Iodine (µg)': 'Iodine',
                'Vitamin A (µg)': 'Vitamin A',
                'Vitamin C (mg)': 'Vitamin C',
                'Vitamin D (µg)': 'Vitamin D',
                'Vitamin E (mg)': 'Vitamin E',
                'Vitamin K (µg)': 'Vitamin K',
                'Vitamin B1 (Thiamine) (mg)': 'Vitamin B1 (Thiamine)',
                'Vitamin B2 (Riboflavin) (mg)': 'Vitamin B2 (Riboflavin)',
                'Vitamin B3 (Niacin) (mg)': 'Vitamin B3 (Niacin)',
                'Vitamin B6 (mg)': 'Vitamin B6',
                'Vitamin B9 (Folate) (µg)': 'Vitamin B9 (Folate)',
                'Vitamin B12 (µg)': 'Vitamin B12',
                'Omega-3 Fatty Acids (g)': 'Omega-3 Fatty Acids',
                'Omega-6 Fatty Acids (g)': 'Omega-6 Fatty Acids'
            }
            
            food_key = mappings.get(plan_header)
            if food_key and food_key in food_item:
                return food_item[food_key]
            
            return "0"

        # Recalculate the entire row
        updated_row_values = []
        for i, col_name in enumerate(headers):
            if col_name == 'Name':
                updated_row_values.append(base_food_item.get('Name', ''))
            elif col_name == 'Amount':
                updated_row_values.append(f"{new_amount:.2f}")
            else:
                base_value = get_food_value(col_name, base_food_item)
                try:
                    calculated_value = float(base_value) * new_amount
                    updated_row_values.append(f"{calculated_value:.2f}")
                except (ValueError, TypeError):
                    updated_row_values.append("0.00")
        
        # Update the row in the sheet
        self.sheet.set_row_data(row_index, values=updated_row_values, redraw=True)

    def update_summation_and_row(self, event=None):
        """Callback for when a cell is edited. Updates the row and the summation."""
        if not event or (event.get('eventname') != 'end_edit_table' and event.get('eventname') != 'end_edit_cell'):
            return
            
        # For end_edit_table events, get row and column from the event data
        if hasattr(event, 'row') and hasattr(event, 'column'):
            row_index, col_index, new_value = event.row, event.column, event.value
        elif 'loc' in event and hasattr(event['loc'], 'row'):
            row_index, col_index = event['loc'].row, event['loc'].column
            new_value = event.get('value', '')
        else:
            return
        
        # We only care about edits in the 'Amount' column for food item rows
        headers = self.sheet.headers()
        if headers[col_index] != 'Amount' or row_index < 2: # 0=Rec, 1=Sum
            return

        try:
            new_amount = float(new_value)
        except ValueError:
            # Revert to old value if input is not a valid float
            # (tksheet might handle this, but good to be safe)
            return

        # Get the base data for this row
        base_food_item = self.sheet_base_data.get(row_index)
        if not base_food_item:
            return

        # Create the same mapping function as in add_food_item_to_tksheet
        def get_food_value(plan_header, food_item):
            if plan_header in food_item:
                return food_item[plan_header]
            
            mappings = {
                'Calories / Energy (kcal)': 'Calories / Energy',
                'Protein (g)': 'Protein',
                'Total Fat (g)': 'Total Fat',
                'Saturated Fat (g)': 'Saturated Fat',
                'Monounsaturated Fat (g)': 'Monounsaturated Fat',
                'Polyunsaturated Fat (g)': 'Polyunsaturated Fat',
                'Trans Fat (g)': 'Trans Fat',
                'Cholesterol (mg)': 'Cholesterol',
                'Carbohydrates (g)': 'Carbohydrates',
                'Dietary Fiber (g)': 'Dietary Fiber',
                'Soluble Fiber (g)': 'Soluble Fiber',
                'Insoluble Fiber (g)': 'Insoluble Fiber',
                'Total Sugars (g)': 'Total Sugars',
                'Added Sugars (g)': 'Added Sugars',
                'Sodium (mg)': 'Sodium',
                'Potassium (mg)': 'Potassium',
                'Calcium (mg)': 'Calcium',
                'Iron (mg)': 'Iron',
                'Magnesium (mg)': 'Magnesium',
                'Zinc (mg)': 'Zinc',
                'Phosphorus (mg)': 'Phosphorus',
                'Iodine (µg)': 'Iodine',
                'Vitamin A (µg)': 'Vitamin A',
                'Vitamin C (mg)': 'Vitamin C',
                'Vitamin D (µg)': 'Vitamin D',
                'Vitamin E (mg)': 'Vitamin E',
                'Vitamin K (µg)': 'Vitamin K',
                'Vitamin B1 (Thiamine) (mg)': 'Vitamin B1 (Thiamine)',
                'Vitamin B2 (Riboflavin) (mg)': 'Vitamin B2 (Riboflavin)',
                'Vitamin B3 (Niacin) (mg)': 'Vitamin B3 (Niacin)',
                'Vitamin B6 (mg)': 'Vitamin B6',
                'Vitamin B9 (Folate) (µg)': 'Vitamin B9 (Folate)',
                'Vitamin B12 (µg)': 'Vitamin B12',
                'Omega-3 Fatty Acids (g)': 'Omega-3 Fatty Acids',
                'Omega-6 Fatty Acids (g)': 'Omega-6 Fatty Acids'
            }
            
            food_key = mappings.get(plan_header)
            if food_key and food_key in food_item:
                return food_item[food_key]
            
            return "0"

        # Recalculate the entire row
        updated_row_values = []
        for i, col_name in enumerate(headers):
            if col_name == 'Name':
                updated_row_values.append(base_food_item.get('Name', ''))
            elif col_name == 'Amount':
                updated_row_values.append(f"{new_amount:.2f}")
            else:
                base_value = get_food_value(col_name, base_food_item)
                try:
                    # Since our food items are already per serving (Amount=1), multiply directly by new amount
                    calculated_value = float(base_value) * new_amount
                    updated_row_values.append(f"{calculated_value:.2f}")
                except (ValueError, TypeError):
                    updated_row_values.append("0.00")
        
        # Update the row in the sheet without triggering this callback again
        self.sheet.set_row_data(row_index, values=updated_row_values, redraw=True)
        
        # Finally, update the summation
        self.update_summation_row_tksheet()
        
        # Auto-save after amount edit
        if hasattr(self, '_current_plan') and 'filepath' in self._current_plan:
            self.save_plan_data(self._current_plan['filepath'])

    def delete_selected_food_from_sheet(self):
        """Delete the currently selected row from the spreadsheet (if it's a food item)."""
        try:
            selected_rows = self.sheet.get_selected_rows()
            if not selected_rows:
                messagebox.showwarning("No Selection", "Please select a food item row to delete.")
                return
            
            # Filter out the special rows (Recommended=0, Summation=1)
            food_item_rows = [row for row in selected_rows if row >= 2]
            
            if not food_item_rows:
                messagebox.showwarning("Invalid Selection", "You can only delete food item rows, not the recommended or summation rows.")
                return
            
            # Get the food item name for confirmation
            selected_row = food_item_rows[0]  # Take the first selected food item row
            row_data = self.sheet.get_row_data(selected_row)
            food_name = row_data[0] if row_data else "Unknown"
            
            # Confirm deletion
            result = messagebox.askyesno("Delete Food Item", 
                                       f"Are you sure you want to remove '{food_name}' from this plan?")
            if result:
                # Delete the row
                self.sheet.delete_row(selected_row)
                
                # Remove from our base data tracking
                if hasattr(self, 'sheet_base_data') and selected_row in self.sheet_base_data:
                    del self.sheet_base_data[selected_row]
                
                # Update row indices in base data (shift down after deletion)
                if hasattr(self, 'sheet_base_data'):
                    new_base_data = {}
                    for row_idx, data in self.sheet_base_data.items():
                        if row_idx > selected_row:
                            new_base_data[row_idx - 1] = data
                        else:
                            new_base_data[row_idx] = data
                    self.sheet_base_data = new_base_data
                
                # Update summation and row headers
                self.update_summation_row_tksheet()
                self.update_row_headers()
                
                # Auto-save after deletion
                if hasattr(self, '_current_plan') and 'filepath' in self._current_plan:
                    self.save_plan_data(self._current_plan['filepath'])
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete food item: {e}")

    def update_summation_row_tksheet(self):
        """Calculates and updates the 'Summation' row in the tksheet."""
        headers = self.sheet.headers()
        total_rows = self.sheet.get_total_rows()
        
        if total_rows <= 2: # Only special rows exist
            return
            
        summation_values = [""] * len(headers)  # Start with empty strings
        
        # Get all food item data (rows from index 2 onwards)
        try:
            all_data = self.sheet.get_sheet_data()
            food_item_data = all_data[2:] if len(all_data) > 2 else []
        except:
            # Fallback: get data row by row if get_sheet_data fails
            food_item_data = []
            for row_idx in range(2, total_rows):
                try:
                    row_data = self.sheet.get_row_data(row_idx)
                    if row_data:
                        food_item_data.append(row_data)
                except:
                    continue

        for col_idx, col_name in enumerate(headers):
            if col_name == 'Name':
                summation_values[col_idx] = ""  # Keep Name blank in summation
            elif col_name == 'Amount':
                # Sum all amounts
                total_amount = 0.0
                for row in food_item_data:
                    if row and len(row) > col_idx and row[col_idx]:
                        try:
                            total_amount += float(row[col_idx])
                        except (ValueError, TypeError):
                            pass
                summation_values[col_idx] = f"{total_amount:.2f}" if total_amount > 0 else ""
            else:
                # Sum all other nutrient values
                total = 0.0
                for row in food_item_data:
                    if row and len(row) > col_idx and row[col_idx]:
                        try:
                            total += float(row[col_idx])
                        except (ValueError, TypeError):
                            pass
                summation_values[col_idx] = f"{total:.2f}" if total > 0 else ""

        # Update the summation row (index 1)
        self.sheet.set_row_data(1, values=summation_values, redraw=True)
        
        # Update color coding after summation changes
        self.apply_color_coding()

    def update_row_headers(self):
        """Updates the row headers after adding/removing items."""
        total_rows = self.sheet.get_total_rows()
        food_item_count = total_rows - 2
        row_headers = ["Recommended", "Summation"] + [f"Item {i+1}" for i in range(food_item_count)]
        self.sheet.row_index(row_headers, redraw=True)

    # Old spreadsheet functions removed - replaced with tksheet implementation

    def _enable_mousewheel_scrolling(self, canvas, inner_frame):
        """Enable mousewheel/touchpad scrolling for a canvas when pointer is over inner_frame.
        
        Uses direct canvas binding for better Windows touchpad compatibility.
        """
        def _on_mousewheel(event):
            # Handle Windows mousewheel events
            if hasattr(event, 'delta'):
                # Windows: event.delta is typically ±120 for mouse wheel, but touchpad gives smaller values
                delta = event.delta
                if delta > 0:
                    canvas.yview_scroll(-1, "units")
                elif delta < 0:
                    canvas.yview_scroll(1, "units")
                return "break"
            
            # Handle Linux/X11 button events
            if hasattr(event, 'num'):
                if event.num == 4:
                    canvas.yview_scroll(-1, "units")
                elif event.num == 5:
                    canvas.yview_scroll(1, "units")
                return "break"

        def _on_enter(event):
            # Focus the canvas and bind wheel events directly to it
            canvas.focus_set()
            canvas.bind_all('<MouseWheel>', _on_mousewheel)
            canvas.bind_all('<Button-4>', _on_mousewheel)
            canvas.bind_all('<Button-5>', _on_mousewheel)

        def _on_leave(event):
            # Unbind wheel events when leaving
            try:
                canvas.unbind_all('<MouseWheel>')
                canvas.unbind_all('<Button-4>')
                canvas.unbind_all('<Button-5>')
            except:
                pass

        # Bind enter/leave to the inner frame
        inner_frame.bind('<Enter>', _on_enter)
        inner_frame.bind('<Leave>', _on_leave)
        
        # Also bind to canvas for better coverage
        canvas.bind('<Enter>', _on_enter)
        canvas.bind('<Leave>', _on_leave)

    def save_food_item(self):
        # Get values from form
        food_item = {}
        for field_name, entry in self.food_entries.items():
            value = entry.get().strip()
            food_item[field_name] = value
        
        # Validate required fields
        if not food_item.get("Name"):
            messagebox.showerror("Error", "Name is required")
            return
        
        # Add to food items list
        self.food_items.append(food_item)
        
        # Save to CSV file
        self.save_food_items_to_csv()
        
        # Show success message
        messagebox.showinfo("Success", "Food item saved successfully!")
        
        # Go back to food items list
        self.show_food_items()

    def save_food_items_to_csv(self):
        """Save all food items to CSV file"""
        if not self.food_items:
            return
        
        # Define the field names (columns)
        fieldnames = [
            "Name", "Amount", "Calories / Energy", "Protein", "Total Fat",
            "Saturated Fat", "Monounsaturated Fat", "Polyunsaturated Fat",
            "Trans Fat", "Cholesterol", "Carbohydrates", "Dietary Fiber",
            "Soluble Fiber", "Insoluble Fiber", "Total Sugars", "Added Sugars",
            "Sodium", "Potassium", "Calcium", "Iron", "Magnesium", "Zinc",
            "Phosphorus", "Iodine", "Vitamin A", "Vitamin C", "Vitamin D",
            "Vitamin E", "Vitamin K", "Vitamin B1 (Thiamine)", 
            "Vitamin B2 (Riboflavin)", "Vitamin B3 (Niacin)", "Vitamin B6",
            "Vitamin B9 (Folate)", "Vitamin B12", "Omega-3 Fatty Acids",
            "Omega-6 Fatty Acids"
        ]
        
        try:
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for item in self.food_items:
                    writer.writerow(item)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save to CSV: {str(e)}")

    def delete_selected_food_item(self):
        """Delete the selected food item from the list."""
        selected_items = self.food_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select a food item to delete.")
            return
        
        # Get the selected item
        selected_item = selected_items[0]
        item_values = self.food_tree.item(selected_item, 'values')
        food_name = item_values[0]  # Name is the first column
        
        # Confirm deletion
        result = messagebox.askyesno("Delete Food Item", 
                                   f"Are you sure you want to delete '{food_name}'?")
        if result:
            try:
                # Remove from the tree view
                self.food_tree.delete(selected_item)
                
                # Update the CSV file by rewriting it with remaining items
                remaining_items = []
                for item_id in self.food_tree.get_children():
                    values = self.food_tree.item(item_id, 'values')
                    # Create a dictionary from the values
                    item_dict = dict(zip(self.display_columns, values))
                    remaining_items.append(item_dict)
                
                # Save the updated list
                self.save_food_items_to_csv(remaining_items)
                
                messagebox.showinfo("Success", f"Food item '{food_name}' has been deleted.")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete food item: {e}")

    def save_food_items_to_csv(self, items):
        """Save the food items list to CSV file."""
        try:
            with open(self.csv_file, mode='w', newline='', encoding='utf-8') as file:
                if items:
                    # Write header
                    fieldnames = list(items[0].keys())
                    writer = csv.DictWriter(file, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    # Write units row
                    units_row = {}
                    for field in fieldnames:
                        if field == 'Name':
                            units_row[field] = ''
                        elif field == 'Amount':
                            units_row[field] = 'g'
                        else:
                            # Find the unit for this field from NUTRIENT_FIELDS
                            unit = ''
                            for nutrient_name, nutrient_unit in NUTRIENT_FIELDS:
                                if field == nutrient_name:
                                    unit = nutrient_unit
                                    break
                            units_row[field] = unit
                    writer.writerow(units_row)
                    
                    # Write data rows
                    writer.writerows(items)
                else:
                    # If no items, just write headers and units
                    fieldnames = [field[0] for field in NUTRIENT_FIELDS]
                    writer = csv.DictWriter(file, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    # Write units row
                    units_row = {field[0]: field[1] for field in NUTRIENT_FIELDS}
                    writer.writerow(units_row)
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save food items: {e}")

    def load_food_items(self):
        """Load food items from the CSV file, ensuring it always returns a list."""
        if not os.path.exists(self.csv_file):
            return []  # Return an empty list if the file doesn't exist

        try:
            with open(self.csv_file, mode='r', newline='', encoding='utf-8') as file:
                # Use DictReader to read the file directly
                dict_reader = csv.DictReader(file)
                return list(dict_reader)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while loading food items: {e}")
            return []

    def refresh_food_list(self):
        # Reload food items from CSV
        self.food_items = self.load_food_items()
        
        # Clear existing items
        for item in self.food_tree.get_children():
            self.food_tree.delete(item)
        
        # Add food items to the list with all columns
        for food_item in self.food_items:
            values = [food_item.get(col, "") for col in self.display_columns]
            self.food_tree.insert("", "end", values=values)

    def show_settings(self):
        self.hide_menu()
        self.clear_main_frame()
        label = ttk.Label(self.main_frame, text="Settings Page")
        label.pack()
        back_button = ttk.Button(self.main_frame, text="Back", command=self.show_menu)
        back_button.pack(pady=10)

    def show_menu(self):
        # Hide the main content frame completely when showing menu
        self.main_frame.pack_forget()
        self.clear_main_frame()
        # Show the menu frame centered
        self.menu_frame.pack_forget()
        self.menu_frame.pack(expand=True)

    def hide_menu(self):
        self.menu_frame.pack_forget()
        # Restore the main content frame
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=10)

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()
