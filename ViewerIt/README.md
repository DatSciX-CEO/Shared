<div align="center">

# ViewerIt
### The Next-Generation Data Intelligence Platform

[![Version](https://img.shields.io/badge/version-2.0.0-00f5ff?style=for-the-badge)](https://github.com/yourusername/viewerit)
[![License](https://img.shields.io/badge/license-MIT-ff00ff?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/backend-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/frontend-React-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://reactjs.org)
[![AI](https://img.shields.io/badge/AI-Ollama-white?style=for-the-badge&logo=ollama&logoColor=black)](https://ollama.ai)

<p align="center">
  <br>
  <b>ViewerIt</b> is an enterprise-grade data comparison and analysis solution designed for the complexities of modern eDiscovery and data science. Merging high-performance data processing with cutting-edge local AI inference, ViewerIt delivers unparalleled insights into your datasets through a visually immersive, cyberpunk-inspired interface.
  <br>
</p>

</div>

---

## 🚀 Why ViewerIt?

In the data-driven world of eDiscovery, precision is paramount. ViewerIt transcends traditional "diff" tools by offering a holistic view of your data landscape. Whether reconciling financial records, verifying migration integrity, or analyzing schema evolution, ViewerIt provides the robust tooling professionals demand.

### Core Capabilities

| Feature | Description |
|---------|-------------|
| **Multi-Dimensional Comparison** | Compare 3+ datasets simultaneously. Generate complex reconciliation matrices and identify records present across any combination of files. |
| **AI-Driven Intelligence** | Leverage local LLMs (via **Ollama**) for semantic analysis. Get smart join suggestions, natural language difference explanations, and automated pattern detection without data leaving your machine. |
| **Deep Schema Analytics** | Instantly visualize column alignment, detect type incompatibilities, and receive automated mapping suggestions for heterogeneous datasets. |
| **Data Quality Assurance** | Automated grading (A-F) of your datasets based on completeness, uniqueness, validity, and statistical outlier analysis. |
| **Immersive Visualization** | A high-performance React frontend featuring interactive dashboards, distribution charts, and Venn diagrams for intuitive data storytelling. |

---

## ⚡ Technical Architecture

ViewerIt is built on a modern, scalable stack designed for performance and extensibility.

*   **Backend:** Python 3.11+ using **FastAPI** for high-throughput asynchronous processing.
*   **Frontend:** **React 18** with **Vite**, tailored with a custom responsive UI system.
*   **Comparison Engine:** Powered by `datacompy` and `pandas` for vectorized operations on large datasets.
*   **AI Layer:** Seamless integration with **Ollama** for privacy-preserving local inference.
*   **Visualization:** Integrated **Recharts** and **Streamlit** components for rich data plotting.

---

## 🛠️ Quick Start

Get up and running in seconds. ViewerIt includes a unified launcher for seamless deployment.

### Prerequisites

*   **Python 3.11+**
*   **Node.js 18+**
*   *(Optional)* **Ollama** for AI features

### Automated Setup (Recommended)

Simply run the unified launcher. It handles dependency installation and service orchestration.

```powershell
# Clone the repository
git clone https://github.com/yourusername/viewerit.git
cd ViewerIt

# Install and Launch
python run.py --install --open
```

### Manual Configuration

For custom deployments or development environments:

1.  **Backend Setup**
    ```bash
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    ```

2.  **Frontend Setup**
    ```bash
    cd frontend
    npm install
    npm run build
    ```

3.  **Launch**
    ```bash
    # Terminal 1: API Server
    .\start_backend.ps1

    # Terminal 2: UI
    .\start_frontend.ps1
    ```

---

## 🔌 API Reference

ViewerIt exposes a comprehensive REST API for integration with existing workflows.

*   **Documentation:** `http://localhost:8000/docs`
*   **Spec:** `openapi.json` available at root endpoint.

**Key Endpoints:**

*   `POST /compare/multi`: Execute multi-file reconciliation strategies.
*   `POST /quality/check`: Run statistical quality assurance audits.
*   `POST /ai/analyze`: Invoke LLM analysis on comparison contexts.
*   `POST /schema/analyze`: Perform structural compatibility checks.

---

## 🤖 AI Integration Guide

ViewerIt is "AI-First" but "Privacy-Focused". We support any model compatible with Ollama.

1.  Install [Ollama](https://ollama.ai).
2.  Pull your preferred model:
    ```bash
    ollama pull llama3.2
    ```
3.  ViewerIt automatically detects available models and exposes them in the UI for tasks like:
    *   *Difference Explanation*
    *   *Join Key Recommendation*
    *   *Data Anomaly Summarization*

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

<div align="center">
  <sub>Built with 💻 and ☕ by the DatSciX Team.</sub>
</div>