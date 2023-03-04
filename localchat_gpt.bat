@echo off
cd /d "%~dp0"
pip install -r requirements.txt
streamlit run app.py