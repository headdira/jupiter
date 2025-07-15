@echo off
echo ================================
echo   Iniciando o Júpiter...
echo ================================
echo.

:: Passo 1: Navegar para a pasta do projeto
cd jupiter

:: Passo 2: Instalar dependência (caso não esteja instalada)
pip install requests

:: Passo 3: Rodar consulta
echo Rodando consulta.py...
python consulta.py

:: Passo 4: Atualizar painel de dispositivos
echo Atualizando painel...
python commit.py

:: Pausa para próxima etapa (logística)
echo.
echo ================================
echo   Etapas iniciais concluídas!
echo ================================
echo Atualize a planilha de logística antes de continuar.
pause

:: Passo 5: Rodar logística
echo Rodando logistica.py...
python logistica.py

:: Passo 6: Atualizar painel da logística
echo Atualizando painel logístico...
python commit2.py

echo.
echo ================================
echo     Júpiter executado com sucesso!
echo ================================
pause
