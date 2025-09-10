@echo off
REM Vai nella cartella del progetto
cd C:\Users\ALBDEN\Documents\GitHub\machines-activity-monitor

REM Chiudi eventuali processi Streamlit rimasti appesi sulla porta 8501
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8501') do taskkill /F /PID %%a >nul 2>&1

REM Avvia l'app Streamlit
python -m streamlit run streamlit_app.py --server.address 192.168.50.34 --server.port 8501