IF NOT EXIST localgpt (
    python -m venv localgpt
)
call localgpt\Scripts\activate.bat
cd /d "%~dp0"
python -m pip install -r requirements.txt
python -m streamlit run app.py
