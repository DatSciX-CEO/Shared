<div align="center">

# ViewerIt
### The Next-Generation Data Intelligence Platform

[![Version](https://img.shields.io/badge/version-2.1.0-00f5ff?style=for-the-badge)](https://github.com/yourusername/viewerit)
[![License](https://img.shields.io/badge/license-MIT-ff00ff?style=for-the-badge)](LICENSE)
[![Rust](https://img.shields.io/badge/core-Rust-orange?style=for-the-badge&logo=rust&logoColor=white)](https://www.rust-lang.org)
[![Python](https://img.shields.io/badge/backend-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/frontend-React-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://reactjs.org)
[![AI](https://img.shields.io/badge/AI-Ollama-white?style=for-the-badge&logo=ollama&logoColor=black)](https://ollama.ai)

<p align="center">
  <br>
  <b>ViewerIt</b> is an enterprise-grade data comparison and analysis solution designed for the complexities of modern eDiscovery and data science. Merging <b>high-performance Rust-native processing</b> with cutting-edge local AI inference, ViewerIt delivers unparalleled insights into your datasets through a visually immersive, cyberpunk-inspired interface.
  <br>
</p>

</div>

---

## 🚀 Why ViewerIt?

In the data-driven world of eDiscovery, precision is paramount. ViewerIt transcends traditional "diff" tools by offering a holistic view of your data landscape. With our new **Rust-accelerated core**, we provide the raw speed needed to process millions of records while maintaining the flexibility of a Python-based AI orchestration layer.

### Core Capabilities

| Feature | Description |
|---------|-------------|
| **Multi-Dimensional Comparison** | Compare 3+ datasets simultaneously. Generate complex reconciliation matrices and identify records present across any combination of files. |
| **Rust-Native Performance** | **New in v2.1:** Native `viewerit_core` module providing 10x-50x speedups on large-scale set operations, record reconciliation, and presence matrix building. |
| **AI-Driven Intelligence** | Leverage local LLMs (via **Ollama**) for semantic analysis. Get smart join suggestions, natural language difference explanations, and automated pattern detection without data leaving your machine. |
| **Deep Schema Analytics** | Instantly visualize column alignment, detect type incompatibilities, and receive automated mapping suggestions for heterogeneous datasets. |
| **Data Quality Assurance** | Automated grading (A-F) of your datasets based on completeness, uniqueness, validity, and statistical outlier analysis. |
| **Immersive Visualization** | A high-performance React frontend featuring interactive dashboards, distribution charts, and Venn diagrams for intuitive data storytelling. |

---

## ⚡ Technical Architecture: "Rust Core, Python Shell"

ViewerIt leverages a hybrid architecture to achieve both extreme performance and developer agility.

*   **Compute Core:** **Rust 2021** utilizing `PyO3` for seamless Python bindings. It employs `rayon` for data-parallelism and `ahash` for hyper-fast set operations.
*   **Orchestration Layer:** **Python 3.11 - 3.14** using **FastAPI** for high-throughput asynchronous API handling.
*   **Frontend:** **React 19** with **Vite** and **Tailwind CSS 4**, featuring a custom cyberpunk "CyberCard" UI system.
*   **AI Layer:** Native integration with **Ollama** for privacy-preserving local inference.
*   **Data Engine:** Hybrid approach using `polars` and `pandas` for vectorized operations, optimized by Rust for massive set intersections.

---

## 🛠️ Quick Start

Get up and running in seconds. ViewerIt includes a unified launcher for seamless deployment.

### Prerequisites

*   **Python 3.11+** (Supports up to 3.14)
*   **Rust Toolchain** (For building the performance core)
*   **Node.js 18+**
*   *(Optional)* **Ollama** for AI features

### Automated Setup (Recommended)

Simply run the unified launcher. It handles dependency installation, Rust core compilation, and service orchestration.

```powershell
# Clone the repository
git clone https://github.com/yourusername/viewerit.git
cd ViewerIt

# Install, Build Rust Core, and Launch
python run.py --install --open
```

### Manual Configuration

For custom deployments or development environments:

1.  **Backend & Rust Core Setup**
    ```bash
    # Create and activate environment
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    
    # Install dependencies
    pip install -r requirements.txt
    
    # Build the Rust Performance Extension
    .\build_extension.bat
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

## 🏎️ Performance Integration

ViewerIt automatically detects the presence of the Rust `viewerit_core` module.

*   **Accelerated Path:** When built, `MultiFileComparator` and `ChunkedProcessor` offload heavy computation to Rust, enabling parallelized processing across all CPU cores.
*   **Graceful Fallback:** If the Rust module is unavailable, the system automatically reverts to native Python logic, ensuring zero downtime across different environments.
*   **Compatibility:** Fully tested on **Python 3.14** using ABI3 forward compatibility flags.

---

## 🔌 API Reference

ViewerIt exposes a comprehensive REST API for integration with existing workflows.

*   **Documentation:** `http://localhost:8000/docs`
*   **Spec:** `openapi.json` available at root endpoint.

**Key Endpoints:**

*   `POST /compare/multi`: Execute multi-file reconciliation strategies (Rust Accelerated).
*   `POST /compare/chunked`: Set-based comparison for massive files (Rust Accelerated).
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
  <sub>Built with 💻, 🦀 and ☕ by the DatSciX Team.</sub>
</div>
