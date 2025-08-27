# GurgenDietTool

A comprehensive nutrition planning and tracking application built with Python and tkinter.

## Features

- **Food Database Management**: Add and manage nutritional information for food items
- **Diet Plan Creation**: Create custom meal plans with automatic nutritional calculations
- **Serving-Based Calculations**: Work with realistic serving sizes instead of 100g portions
- **Professional Spreadsheet Interface**: Excel-like interface using tksheet
- **Color-Coded Nutrition**: Visual indicators for nutritional adequacy
- **Auto-Save Functionality**: All changes are automatically saved
- **Real-Time Calculations**: Instant updates when modifying serving amounts

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/mertgurgenyatagi/GurgenDietTool.git
   cd GurgenDietTool
   ```

2. Install required dependencies:
   ```bash
   pip install tkinter pandas tksheet
   ```

3. Run the application:
   ```bash
   python main.py
   ```

## Project Structure

```
GurgenDietTool/
├── main.py                    # Main application file
├── GurgenDietTool.spec        # PyInstaller build configuration
├── data/                      # Data files
│   ├── food_items.csv         # Food nutritional database (template)
│   ├── nutrient_modes.csv     # Color coding configuration
│   └── units.csv              # Unit definitions
├── templates/                 # Template files
│   └── plan_template.csv      # Template for new plans
├── icons/                     # Application icons
│   ├── apple.png              # Application icon (PNG)
│   └── apple.ico              # Windows executable icon
├── plans/                     # User meal plans (gitignored)
└── README.md                  # Documentation
```

## Usage

1. **View Food Items**: Browse the nutritional database
2. **Create New Plan**: Set up a new meal plan
3. **Add Food Items**: Select foods and specify serving amounts
4. **Edit Amounts**: Modify serving sizes with automatic recalculation
5. **Track Progress**: Monitor nutritional goals with color-coded indicators

## Building Executable

To create a standalone executable:

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Build the executable:
   ```bash
   pyinstaller GurgenDietTool.spec
   ```

3. Find the executable in the `dist/` directory

## File Management

- **Food Database**: `data/food_items.csv` - Central nutritional database (custom data not tracked)
- **Plans**: `plans/` directory - Individual meal plans (gitignored for privacy)
- **Templates**: `templates/plan_template.csv` - Template for new plans
- **Configuration**: `data/nutrient_modes.csv` - Color coding rules
- **Icons**: `icons/` directory - Application branding assets

## Development

Built with:
- **Python 3.x**
- **tkinter** - GUI framework
- **pandas** - Data manipulation
- **tksheet** - Professional spreadsheet widget

## License

This project is licensed under the MIT License.
