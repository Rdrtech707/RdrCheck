@echo off

REM ===================================================
REM 1) Entrar na pasta onde o .bat está
REM ===================================================
cd /d %~dp0

REM ===================================================
REM 2) Ativar o ambiente virtual Python
REM ===================================================
call venv\Scripts\activate

REM ===================================================
REM 3) Iniciar Node.js em outra janela
REM    (assumindo que seu servidor fica em /backend)
REM ===================================================
cd backend
start "" cmd /k "node server.js"

REM Volta para o diretório raiz, onde está o app.py
cd ..

REM ===================================================
REM 4) Executar o Streamlit
REM ===================================================
streamlit run app.py

REM Opcional: manter a janela aberta (caso queira ver logs)
pause
