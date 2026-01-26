# locker-dashboard

This is a Flask-based web application for managing lockers and loan records. The application allows users to view, create, and manage lockers and loans through a user-friendly interface.

## Project Structure

```
locker-dashboard
├── app.py                # Entry point of the Flask application
├── config.py             # Configuration settings for the application
├── requirements.txt      # List of dependencies
├── models                # Contains data models
│   ├── __init__.py       # Initializes the models package
│   ├── casier.py         # Defines the Casier model
│   └── emprunt.py        # Defines the Emprunt model
├── routes                # Contains route definitions
│   ├── __init__.py       # Initializes the routes package
│   ├── casiers.py        # Routes related to lockers
│   └── emprunts.py       # Routes related to loans
├── static                # Contains static files (CSS, JS, icons)
│   ├── css
│   │   └── style.css     # CSS styles for the application
│   ├── js
│   │   └── main.js       # JavaScript code for client-side functionality
│   └── icons             # Icon files used in the application
├── templates             # Contains HTML templates
│   ├── base.html         # Base template for the application
│   ├── dashboard.html    # Dashboard view
│   ├── compte.html       # Account management page
│   ├── contact.html      # Contact form page
│   └── le_projet.html    # Project information page
├── data                  # Contains CSV data files
│   ├── casiers.csv       # Data related to lockers
│   └── emprunts.csv      # Data related to loans
└── README.md             # Project documentation
```

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd locker-dashboard
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the application:
   ```
   python app.py
   ```

5. Open your web browser and navigate to `http://127.0.0.1:5000` to access the application.

## Usage

- Users can view the dashboard to see an overview of lockers and loans.
- Users can manage their accounts and contact support through the provided forms.
- The application allows for the creation and management of lockers and loan records.

## License

This project is licensed under the MIT License - see the LICENSE file for details.