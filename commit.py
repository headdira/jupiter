import os
import subprocess
import shutil

# Caminhos
REPO_DIR = r"C:\Users\Loovi\Documents\jupiter-v2\api-rastreamento"
SOURCE_FILE = r"C:\Users\Loovi\Documents\jupiter-v2\data\devices_data.json"
DEST_FILE = os.path.join(REPO_DIR, "devices_data.json")  # Agora vai direto na raiz do repositório

# Mensagem do commit
COMMIT_MESSAGE = "Atualiza devices_data.json automaticamente via script"

def run_git_command(command, cwd):
    result = subprocess.run(command, cwd=cwd, shell=True, text=True, capture_output=True)
    if result.returncode != 0:
        print(f"Erro: {result.stderr}")
        raise Exception(f"Comando falhou: {command}")
    else:
        print(result.stdout)

def push_file_to_github():
    if not os.path.exists(REPO_DIR):
        raise FileNotFoundError(f"Diretório do repositório não encontrado: {REPO_DIR}")

    if not os.path.exists(SOURCE_FILE):
        raise FileNotFoundError(f"Arquivo de origem não encontrado: {SOURCE_FILE}")

    print("Iniciando push do arquivo para o GitHub...")

    # Copiar o arquivo diretamente para a raiz do repositório
    shutil.copyfile(SOURCE_FILE, DEST_FILE)
    print(f"Arquivo copiado de {SOURCE_FILE} para {DEST_FILE}")

    # Git pull, add, commit e push
    os.chdir(REPO_DIR)
    run_git_command("git pull origin master", cwd=REPO_DIR)
    run_git_command("git add devices_data.json", cwd=REPO_DIR)
    run_git_command(f'git commit -m "{COMMIT_MESSAGE}"', cwd=REPO_DIR)
    run_git_command("git push origin master", cwd=REPO_DIR)

    print("Arquivo enviado com sucesso para o GitHub!")

if __name__ == "__main__":
    push_file_to_github()
