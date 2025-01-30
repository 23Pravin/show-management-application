# Show Management Application

A desktop application built with PySide2 and JSON Server for managing shows with image attachments.

## Features

- List shows with their codes
- Add new shows with validation
- Attach images to shows
- View show details and images
- Server-side image storage
- Real-time updates

## Prerequisites

- Python 3.7 or higher
- Node.js and npm
- PySide2
- JSON Server

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd pipe-project
```

2. Install Python dependencies:
```bash
pip install PySide2 requests
```

3. Install JSON Server:
```bash
npm install
```

## Project Structure

```
pipe-project/
├── public/
│   └── images/        # Stored show images
├── show_list.py       # Main application
├── rename_images.py   # Utility for image management
├── db.json           # Database file
├── package.json      # Node.js configuration
└── README.md
```

## Running the Application

1. Start the JSON Server:
```bash
npm start
```

2. Run the Python application:
```bash
python show_list.py
```

## Usage

### Adding a Show
1. Click "Add Show" button
2. Enter show name (alphanumeric and underscore only)
3. Enter show code (uppercase letter followed by numbers)
4. Select an image (optional)
5. Click "Add" to save

### Viewing Shows
- Shows are listed in the left pane
- Click on a show to view details and image in the right pane
- Images are automatically numbered and stored on the server

## Input Validation

- Show Name: Can only contain letters, numbers, and underscores
- Show Code: Must start with an uppercase letter followed by numbers
- Example valid inputs:
  - Name: "Show_1", "MyShow123"
  - Code: "S1", "T123"

## Development

The application uses:
- PySide2 for the GUI
- JSON Server for data storage
- RESTful API for data operations
- Server-side image storage

## License

[Your License Here]
