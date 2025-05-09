# Overwatch Command Center - Initial Production Version

<p align="center">
  <img src="resources/images/logo.png" alt="Overwatch Command Center Logo" width="200"/> <!-- Assuming logo.png might be added by user later or is conceptual -->
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-0.1.0-blue.svg" alt="Version 0.1.0"/>
  <img src="https://img.shields.io/badge/python-3.11+-brightgreen.svg" alt="Python 3.11+"/>
  <img src="https://img.shields.io/badge/framework-Streamlit-ff4b4b.svg" alt="Framework: Streamlit"/>
</p>

## 🚀 Overview

**Overwatch Command Center** is a modular, enterprise-grade data operations platform designed to unify database management, analytics workflows, and model integration in a single, cohesive interface. This initial production version provides core functionalities with a focus on extensibility via a plugin architecture.

## ✨ Key Features (Initial Version)

- **Modular Architecture**: Built for extensibility, based on the provided program structure.
- **Streamlit UI**: Interactive user interface with a dark theme.
- **Database Connectivity**: Manage SQLite database connections, execute queries, and view results.
- **Data Analytics & EDA**: Upload CSV/Excel files or use data from database queries to perform Exploratory Data Analysis, including:
    - Descriptive statistics
    - Data type information
    - Missing value analysis
    - Correlation matrices
    - Visualizations (Histograms, Boxplots, Scatterplots, Bar Charts, Correlation Heatmaps)
- **Machine Learning Integration**: Automated model comparison for classification and regression tasks using LazyPredict on uploaded or queried data.
- **Plugin System**: Basic plugin architecture allowing for dynamic loading of custom Python modules.
    - Includes an example built-in plugin.

## 📋 Prerequisites

- Python 3.11 or higher
- Dependencies listed in `requirements.txt`

## 🔧 Installation & Running

1.  **Clone/Download**: Obtain the `overwatch_command_center` project directory.
2.  **Navigate to Project Directory**:
    ```bash
    cd path/to/overwatch_command_center
    ```
3.  **Create a Virtual Environment (Recommended)**:
    ```bash
    python3.11 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
4.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    *Note: If you encounter issues with `lazypredict` or its dependencies (like `lightgbm` or `xgboost`) on specific OS/architectures, you might need to install them via system package managers or pre-compiled wheels first.*

5.  **Run the Application**:
    ```bash
    streamlit run src/app/main.py
    ```
    The application should then be accessible in your web browser (typically at `http://localhost:8501`).

## 📁 Project Structure

The project follows the structure outlined in the initial `Overwatch.txt` document, with key directories including:

- **`src/`**: Main application source code.
  - **`app/`**: Streamlit application entry point (`main.py`) and page modules (`pages/`).
  - **`core/`**: Core business logic for database, analytics, and ML.
  - **`plugins/`**: Plugin system (interface, manager, built-in plugins).
  - **`ui/`**: UI components and theming (though much is handled by Streamlit directly or in `.streamlit/config.toml`).
  - **`utils/`**: Utility functions (currently minimal, can be expanded).
- **`data/`**: Directory for storing data like SQLite database files and user-uploaded credentials (encrypted `credentials.json.enc`).
- **`plugins_ext/`**: Directory for external plugins (user-created).
- **`.streamlit/`**: Streamlit configuration, including `config.toml` for theming.
- **`requirements.txt`**: Python dependencies.
- **`README.md`**: This file.

## 🔌 Extending with Plugins

1.  Create your plugin as a Python file or package that implements the `OverwatchPlugin` interface (see `src/plugins/interface.py`).
2.  Place your plugin file/package into the `plugins_ext/` directory.
3.  The Plugin Manager will attempt to discover and load it on startup.
    - An example plugin is provided in `src/plugins/builtin/example_plugin.py`.

## 🔐 Credential Management

Database credentials (for SQLite, this is just the file path) are stored encrypted in `data/credentials.json.enc`.
- An encryption key is required. The system will prompt if the `OVERWATCH_ENCRYPTION_KEY` environment variable is not set. For development, it can auto-generate one, but **for production, you must set and manage this key securely.**
  ```bash
  # Example for generating and setting the key in Linux/macOS for a session
  export OVERWATCH_ENCRYPTION_KEY=$(python3.11 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
  ```

## 🚀 Future Development (Based on `Overwatch.txt` and potential next steps)

- More database drivers (PostgreSQL, MySQL, MongoDB, Redis).
- Advanced workflow engine and scheduler.
- More sophisticated UI components and layouts, potentially using `streamlit-option-menu` or similar for enhanced navigation as seen in user examples.
- User authentication and role-based access control.
- Enhanced security features.
- Comprehensive logging and monitoring.
- Desktop executable packaging (e.g., using PyInstaller or Nuitka).

This initial version provides a solid foundation for these future enhancements.

