$ErrorActionPreference = 'Stop'
Set-Location (Join-Path $PSScriptRoot 'rag-chunking-embeddings-vectordb/rag-chunking-embeddings-vectordb')
$env:HF_HOME = Join-Path $PSScriptRoot '.cache/huggingface'
$env:PYTHONUTF8 = '1'
$env:HF_HUB_OFFLINE = '1'
& '.venv/Scripts/python.exe' -m streamlit run app.py --server.port 8501 --server.address 127.0.0.1 --browser.gatherUsageStats false
