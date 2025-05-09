# 🌠 Overwatch Command Center - Your Unified Data Operations Hub 🌌

<p align="center">
  <img src="resources/images/logo.png" alt="Overwatch Command Center Logo" width="200"/> </p>

<p align="center">
  <img src="https://img.shields.io/badge/version-0.1.0-blue.svg" alt="Version 0.1.0"/>
  <img src="https://img.shields.io/badge/python-3.11+-brightgreen.svg" alt="Python 3.11+"/>
  <img src="https://img.shields.io/badge/framework-Streamlit-ff4b4b.svg" alt="Framework: Streamlit"/>
  <img src="https://img.shields.io/badge/status-alpha-yellow.svg" alt="Status: Alpha"/>
  </p>

## 🚀 Elevate Your Data Operations!

**Overwatch Command Center** is your all-in-one, enterprise-ready solution for seamless data operations. Born from the need to unify database management, advanced analytics, and machine learning workflows, Overwatch provides a modular, extensible, and intuitive Streamlit-powered interface. Take control of your data landscape from a single command center!

---

## ✨ Core Capabilities (v0.1.0 - "Genesis")

This initial production version lays a robust foundation with a focus on modularity and core data tasks:

* **🌌 Unified & Modular Architecture**: Designed for growth and customization. Easily integrate new functionalities through a dynamic plugin system.
* **🎨 Interactive Streamlit UI**: A sleek, dark-themed, and user-friendly web interface that makes complex operations intuitive.
* **🗄️ Versatile Database Management**:
    * Securely connect to SQLite databases (more drivers planned!).
    * Execute SQL queries directly through the interface.
    * View and export query results effortlessly.
    * Encrypted credential storage for enhanced security.
* **📊 Insightful Analytics & EDA**:
    * Upload CSV/Excel files or leverage data directly from your database connections.
    * Perform comprehensive Exploratory Data Analysis (EDA):
        * Descriptive Statistics
        * Data Type Information
        * Missing Value Analysis & Visualization
        * Correlation Matrices (Pearson) & Heatmaps
        * Rich Visualizations: Histograms, Boxplots, Scatterplots, Bar Charts.
* **🤖 Automated Machine Learning Integration**:
    * Utilize `LazyPredict` for rapid baseline model comparison for both classification and regression tasks.
    * Select target variables and problem types with ease.
    * Preprocesses data (categorical encoding, train-test split) automatically.
    * View and download comprehensive model performance metrics.
* **🔌 Dynamic Plugin System**:
    * Extend Overwatch's capabilities by creating and loading custom Python plugins.
    * Plugins can add new pages, sidebar elements, or backend functionalities.
    * Includes a built-in example plugin to guide your development.
    * Automatic discovery and loading of plugins from designated directories.

---

## 📋 Prerequisites

* **Python**: Version 3.11 or higher.
* **Dependencies**: All necessary packages are listed in `requirements.txt`. Key dependencies include `streamlit`, `pandas`, `lazypredict`, `sqlalchemy`, `cryptography`, and various plotting libraries.

---

## 🛠️ Installation & Launch

Get your Overwatch Command Center up and running in a few simple steps:

1.  **Clone or Download the Repository**:
    ```bash
    # If using Git
    git clone <your-repository-url>
    cd Overwatch # Or your project's root directory name
    ```

2.  **Navigate to Project Directory**:
    ```bash
    cd path/to/overwatch_command_center
    ```

3.  **Create and Activate a Virtual Environment (Recommended)**:
    ```bash
    python3.11 -m venv venv
    # On macOS/Linux
    source venv/bin/activate
    # On Windows
    .\venv\Scripts\activate
    ```

4.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    * **Note**: Some `lazypredict` sub-dependencies (like `lightgbm` or `xgboost`) might have specific installation needs depending on your OS and architecture. If you encounter issues, try installing these problematic packages individually using system package managers (like `apt` or `brew`) or pre-compiled wheels before running `pip install -r requirements.txt` again.

5.  **Set Up Encryption Key (Crucial for Security)**:
    The application uses an encryption key for managing credentials. For production, **you MUST set and manage this key securely as an environment variable.**
    ```bash
    # Example for generating and setting the key in Linux/macOS for a development session:
    export OVERWATCH_ENCRYPTION_KEY=$(python3.11 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
    # For Windows (PowerShell):
    # $env:OVERWATCH_ENCRYPTION_KEY = (python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
    ```
    If the `OVERWATCH_ENCRYPTION_KEY` environment variable is not set, the application will prompt and can auto-generate one for development convenience, but this is **NOT secure for production environments.**

6.  **Run the Application**:
    ```bash
    streamlit run src/app/main.py
    ```
    The application should automatically open in your default web browser (typically at `http://localhost:8501`).

---

## 📁 Project Structure Overview

The project is organized for clarity and scalability:

overwatch_command_center/
├── .streamlit/
│   └── config.toml         # Streamlit theme and app configurations
├── data/                   # For SQLite DBs, uploaded credentials (encrypted)
│   └── credentials.json.enc # Encrypted storage for connection details
├── docs/                   # (Optional) Detailed documentation, diagrams
├── plugins_ext/            # Directory for your custom external plugins
├── resources/
│   └── images/
│       └── logo.png        # Application logo
├── src/                    # Main application source code
│   ├── app/                # Streamlit application UI
│   │   ├── main.py         # Main Streamlit app entry point
│   │   └── pages/          # Individual page modules (Home, DB, Analytics, ML)
│   │       ├── init.py
│   │       ├── analytics.py
│   │       ├── database_manager.py
│   │       ├── home.py
│   │       └── model_integration.py
│   ├── core/               # Core business logic
│   │   ├── init.py
│   │   ├── analytics/      # Analytics, EDA, and ML logic
│   │   │   ├── init.py
│   │   │   ├── ml/
│   │   │   │   ├── init.py
│   │   │   │   └── lazy_utils.py # LazyPredict integration
│   │   │   ├── statistics.py
│   │   │   └── visualization.py
│   │   └── database/       # Database connection, credential management
│   │       ├── init.py
│   │       ├── connection.py     # Base connection class
│   │       ├── credentials.py    # Credential encryption and storage
│   │       └── drivers/
│   │           ├── init.py
│   │           └── sqlite.py     # SQLite driver
│   ├── plugins/            # Plugin system core and built-in plugins
│   │   ├── init.py
│   │   ├── builtin/        # Example and standard built-in plugins
│   │   │   ├── init.py
│   │   │   └── example_plugin.py
│   │   ├── interface.py    # Plugin abstract base class and metadata
│   │   └── manager.py      # Plugin discovery and loading logic
│   └── utils/              # Utility functions (expand as needed)
│       └── init.py
├── tests/                  # (Future) Unit and integration tests
├── README.md               # This file!
└── requirements.txt        # Python dependencies


---

## 🔌 Extending with Plugins

Overwatch's power lies in its extensibility. Create your own plugins to add custom features:

1.  **Understand the Interface**: Your plugin should be a Python class that inherits from `OverwatchPlugin` found in `src/plugins/interface.py`.
2.  **Implement Required Methods**:
    * `metadata`: A property returning `PluginMetadata` (name, version, description, author, icon).
    * `initialize(app_context)`: Called when the plugin loads. `app_context` provides access to shared resources like `st.session_state`.
    * `render_page_content()`: If your plugin adds a new page, this method defines its UI.
    * `render_sidebar_contribution()`: Optionally add elements (like navigation buttons) to the main sidebar.
    * `on_unload()`: Cleanup actions when the plugin is unloaded.
3.  **Develop Your Plugin**: Create your plugin as a Python file (e.g., `my_custom_plugin.py`) or a Python package.
    * Refer to the example: `src/plugins/builtin/example_plugin.py`.
4.  **Deploy Your Plugin**: Place your plugin file or package directory into the `plugins_ext/` directory.
5.  **Launch Overwatch**: The Plugin Manager will automatically discover and load your plugin on startup.

---

## 🔐 Secure Credential Management

Database connection details (like SQLite file paths) are stored encrypted in `data/credentials.json.enc` using Fernet encryption.
* **Encryption Key**: As mentioned in the installation, the `OVERWATCH_ENCRYPTION_KEY` environment variable is paramount.
    * **Production**: This key **MUST** be set securely and be persistent. Treat it like any other sensitive credential.
    * **Development**: If not set, a key will be generated for convenience, but this is **not suitable for production use.**
* The `CredentialManager` handles the encryption and decryption seamlessly.

---

## 🚀 Future Roadmap & Vision

Overwatch is just getting started! Here's a glimpse of what's on the horizon:

* **More Database Drivers**: Support for PostgreSQL, MySQL, MongoDB, Redis, and more.
* **Advanced Workflow Engine**: Design and schedule complex data processing pipelines.
* **Sophisticated UI/UX**: Enhanced navigation (already uses `streamlit-option-menu`), custom themes, and more interactive components.
* **User Authentication & RBAC**: Secure user login and role-based access control.
* **Enhanced Security Layers**: Further security hardening across the platform.
* **Comprehensive Logging & Monitoring**: Detailed activity logs and performance monitoring.
* **Desktop Executable**: Packaging for offline or standalone deployment (e.g., using PyInstaller or Nuitka).
* **Deeper AI/ML Integration**: Support for more MLOps practices, model deployment, and monitoring.
* **Community Plugins**: A repository for sharing and discovering community-built plugins.

---

<p align="center">
  ✨ Thank you for exploring Overwatch Command Center! ✨
</p>