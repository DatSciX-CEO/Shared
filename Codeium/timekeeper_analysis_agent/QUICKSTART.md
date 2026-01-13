# Timekeeper Analysis Agent - Quick Start Checklist

## ⚡ 5-Minute Setup

### Step 1: Install Ollama
- [ ] Download from https://ollama.ai/download
- [ ] Install and run `ollama serve`
- [ ] Pull model: `ollama pull mistral-small3.1`
- [ ] Verify: `ollama show mistral-small3.1` (check for "tools" capability)

### Step 2: Setup Python Environment
```bash
cd timekeeper_analysis_agent

# Create venv
python -m venv venv

# Activate
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Run Application
```bash
# Launch Streamlit UI (easiest)
python main.py --ui streamlit

# OR Interactive CLI
python main.py

# OR Batch analysis
python main.py --file your_data.csv
```

## ✅ Verification Checklist

### Before First Run
- [ ] Ollama is running (`ollama serve` in terminal)
- [ ] Model is downloaded (`ollama list` shows mistral-small3.1)
- [ ] Virtual environment is activated (see `(venv)` in prompt)
- [ ] Dependencies installed (`pip list` shows google-adk, pandas, streamlit)

### Data File Requirements
Your CSV/Excel/Parquet file must have:
- [ ] `timekeeper_id` column
- [ ] `date` column (YYYY-MM-DD format)
- [ ] `hours` column (numeric)
- [ ] `rate` column (numeric)

Optional but helpful:
- [ ] `matter_id`, `task_code`, `client_id`, `description`

### Example Data Format
```csv
timekeeper_id,date,hours,rate,matter_id
TK001,2025-01-15,8.5,250,M123
TK001,2025-01-16,7.0,250,M123
TK002,2025-01-15,6.5,200,M456
```

## 🚀 First Analysis

### Using Streamlit UI

1. **Start the app**:
   ```bash
   python main.py --ui streamlit
   ```

2. **Upload file**: Click "Upload Timekeeper Data File"

3. **Select analysis**: Choose "Comprehensive Analysis"

4. **Run**: Click "🚀 Start Analysis"

5. **Review**: Results appear in chat-style interface

6. **Export**: Click export button for report

### Using CLI

```bash
$ python main.py

You: Please analyze C:\data\timekeepers.csv

Agent: I'll analyze your timekeeper data...
[Results stream here]

You: What are the top productivity issues?

Agent: Based on the analysis...
```

## 🛠️ Common Issues & Solutions

### "Cannot connect to Ollama"
**Fix**:
```bash
# Start Ollama
ollama serve
```

### "Model not found"
**Fix**:
```bash
ollama pull mistral-small3.1
```

### "Module not found"
**Fix**:
```bash
# Make sure venv is activated
pip install -r requirements.txt
```

### "Infinite tool loop"
**Fix**: Ensure using `ollama_chat` provider in config.yaml:
```yaml
ollama:
  provider: "ollama_chat"  # NOT "ollama"
```

## 📊 What You'll Get

### Productivity Analysis
- ✅ Utilization rates per timekeeper
- ✅ Billable percentage trends
- ✅ High/low performers identification
- ✅ Efficiency gap quantification

### Billing Anomaly Detection
- ✅ Rate variance detection (>30%)
- ✅ Hours spike identification (>2x avg)
- ✅ Pattern anomalies
- ✅ Compliance concerns flagging

### Resource Optimization
- ✅ Current vs target utilization (80%)
- ✅ Reallocation recommendations
- ✅ Capacity forecasting
- ✅ Bench time reduction strategies

### Final Report
- ✅ Executive summary
- ✅ Detailed findings by category
- ✅ Prioritized action items
- ✅ Supporting data and metrics

## 📖 Next Steps

After successful first run:

1. **Review Results**: Check all analysis sections
2. **Customize Config**: Edit `config/config.yaml` for your thresholds
3. **Explore Features**: Try different analysis types
4. **Export Reports**: Generate reports in multiple formats
5. **Integrate**: Add to your regular workflow

## 🆘 Need Help?

- **Setup Guide**: See `SETUP.md` for detailed instructions
- **Project Summary**: See `PROJECT_SUMMARY.md` for architecture
- **README**: See `README.md` for feature overview
- **ADK Docs**: https://google.github.io/adk-docs
- **Ollama Docs**: https://ollama.ai/docs

## 📝 Example Workflow

```bash
# 1. Start Ollama (once)
ollama serve

# 2. Navigate to project
cd timekeeper_analysis_agent

# 3. Activate environment
venv\Scripts\activate

# 4. Run analysis
python main.py --ui streamlit

# 5. Upload your data file in browser

# 6. Click "Start Analysis"

# 7. Review results and export report
```

## ✨ Pro Tips

1. **Large Files**: Use Parquet format for faster loading
2. **Quick Tests**: Use "Productivity Only" for faster initial runs
3. **Custom Models**: Adjust in config.yaml for different models
4. **Batch Mode**: Use for automated/scheduled analyses
5. **Session History**: CLI maintains context across queries

---

**Ready to Start?** Run `python main.py --ui streamlit` and upload your first file!

**Questions?** Review the detailed documentation in `SETUP.md`