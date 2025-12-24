# 🔮 ViewerIt - Cyberpunk eDiscovery Data Comparator

A sophisticated data comparison platform for eDiscovery professionals, featuring a Cyberpunk-themed UI, AI-powered analysis via Ollama, and embedded Streamlit visualizations.

![ViewerIt](https://img.shields.io/badge/ViewerIt-v1.0.0-00f5ff?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0iIzAwZjVmZiIgZD0iTTEzIDNMNCAxNGgzdjdoNnYtN2g0eiIvPjwvc3ZnPg==)
![License](https://img.shields.io/badge/License-MIT-ff00ff?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11+-f0ff00?style=for-the-badge&logo=python)
![React](https://img.shields.io/badge/React-18-00f5ff?style=for-the-badge&logo=react)

## ✨ Features

### Data Comparison
- **Multi-format Support**: CSV, Excel, Parquet, JSON, DAT (Concordance), and more
- **Deep Comparison**: Row-by-row and column-by-column analysis using datacompy
- **Statistics**: Null counts, data types, unique values, and memory usage
- **Difference Detection**: Find rows and columns that exist in one file but not the other

### AI-Powered Analysis
- **Ollama Integration**: Use local LLMs for intelligent data analysis
- **Model Selection**: Choose from any Ollama model you have installed
- **Smart Suggestions**: AI can suggest join columns and explain differences

### Visualization
- **Embedded Streamlit**: Interactive charts and graphs
- **Distribution Analysis**: Histograms and box plots for numeric columns
- **Column Comparison**: Side-by-side statistics

### Cyberpunk UI
- **Neon Aesthetics**: Cyan, magenta, and yellow accents
- **Glitch Effects**: Animated text with cyberpunk feel
- **Dark Theme**: Easy on the eyes for long analysis sessions
- **Responsive Design**: Works on any screen size

## 🚀 Quick Start

### Prerequisites

1. **Python 3.11+**: [Download Python](https://python.org)
2. **Node.js 18+**: [Download Node.js](https://nodejs.org)
3. **Ollama** (optional, for AI features): [Download Ollama](https://ollama.ai)

### Installation

1. **Clone or navigate to the project**:
   ```powershell
   cd C:\Shared\ViewerIt
   ```

2. **Create Python virtual environment**:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

3. **Install frontend dependencies**:
   ```powershell
   cd frontend
   npm install
   cd ..
   ```

4. **(Optional) Pull an Ollama model**:
   ```powershell
   ollama pull llama3.2
   ```

### Running the Application

**Option 1: Start All Services**
```powershell
.\start_all.ps1
```

**Option 2: Start Individually**

In separate terminals:

```powershell
# Terminal 1: Backend
.\start_backend.ps1

# Terminal 2: Streamlit
.\start_streamlit.ps1

# Terminal 3: Frontend
.\start_frontend.ps1
```

### Access the Application

- **Main App**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs
- **Streamlit**: http://localhost:8501

## 📁 Project Structure

```
ViewerIt/
├── backend/                    # FastAPI Backend
│   ├── main.py                 # API endpoints
│   ├── services/
│   │   ├── file_handler.py     # File upload/parsing
│   │   ├── comparator.py       # Data comparison logic
│   │   └── ai_service.py       # Ollama integration
│   └── uploads/                # Temporary file storage
├── frontend/                   # React + Vite Frontend
│   ├── src/
│   │   ├── components/         # Cyberpunk UI components
│   │   ├── hooks/              # API integration hooks
│   │   └── App.tsx             # Main application
│   └── index.html
├── streamlit_app/              # Embedded Visualization
│   └── viz_report.py
├── requirements.txt            # Python dependencies
└── start_*.ps1                 # Startup scripts
```

## 🔧 API Reference

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/upload` | Upload files for comparison |
| GET | `/files/{session_id}` | List files in session |
| GET | `/files/{session_id}/{filename}/info` | Get file metadata |
| GET | `/files/{session_id}/{filename}/preview` | Preview file contents |
| POST | `/compare` | Run comparison between two files |
| GET | `/ai/models` | List available Ollama models |
| POST | `/ai/analyze` | Analyze comparison with AI |

## 🎨 Customization

### Theme Colors (CSS Variables)

Edit `frontend/src/index.css`:

```css
@theme {
  --color-neon-cyan: #00f5ff;
  --color-neon-magenta: #ff00ff;
  --color-neon-pink: #ff0080;
  --color-neon-yellow: #f0ff00;
}
```

### Adding New File Formats

Edit `backend/services/file_handler.py`:

```python
SUPPORTED_FORMATS = {
    ".csv": "CSV",
    ".xlsx": "Excel",
    ".your_format": "Your Format Name",
}
```

## 🤖 AI Features

ViewerIt uses Ollama for local AI inference. Supported use cases:

1. **Comparison Analysis**: "Why are these datasets different?"
2. **Pattern Detection**: "What patterns do you see in the mismatches?"
3. **Join Column Suggestions**: AI recommends which columns to use as keys
4. **Difference Explanations**: AI explains specific column differences

### Supported Models

Any model available in Ollama:
- `llama3.2` (recommended)
- `mistral`
- `phi3`
- `gemma2`
- And more...

## 📊 Supported File Formats

| Format | Extension | Notes |
|--------|-----------|-------|
| CSV | `.csv` | UTF-8 encoded |
| Excel | `.xlsx`, `.xls` | All sheets loaded |
| Parquet | `.parquet` | Apache Parquet |
| JSON | `.json` | Records or table orientation |
| DAT | `.dat` | Concordance format (¶ delimited) |
| Text | `.txt` | Auto-detects delimiter |

## 🛠️ Development

### Backend Development
```powershell
cd backend
uvicorn main:app --reload
```

### Frontend Development
```powershell
cd frontend
npm run dev
```

### Running Tests
```powershell
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 📝 License

MIT License - Feel free to use and modify for your eDiscovery workflows.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Backend framework
- [Vite](https://vitejs.dev/) + [React](https://react.dev/) - Frontend
- [Tailwind CSS](https://tailwindcss.com/) - Styling
- [Streamlit](https://streamlit.io/) - Visualization
- [Ollama](https://ollama.ai/) - Local AI inference
- [datacompy](https://github.com/capitalone/datacompy) - Data comparison

---

<p align="center">
  <strong>⚡ Built for eDiscovery professionals who demand precision ⚡</strong>
</p>

