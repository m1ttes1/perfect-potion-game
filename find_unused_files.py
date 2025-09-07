"""
Script para identificar arquivos não utilizados no projeto.
Gera um relatório com os arquivos que podem ser removidos com segurança.
"""
import os
import re
import sys
import shutil
from pathlib import Path
from datetime import datetime

def get_all_files(directory, extensions=None, exclude_dirs=None):
    """Retorna todos os arquivos no diretório, com opção de filtrar por extensão e excluir diretórios."""
    if exclude_dirs is None:
        exclude_dirs = {'__pycache__', '.git', '.idea', 'venv', 'env', 'node_modules'}
    
    all_files = []
    for root, dirs, files in os.walk(directory):
        # Remove diretórios da lista de exclusão
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if extensions and not any(file.lower().endswith(ext.lower()) for ext in extensions):
                continue
            all_files.append(Path(root) / file)
    
    return all_files

def get_used_assets(project_dir):
    """Analisa o código-fonte para encontrar referências a arquivos de assets."""
    used_assets = set()
    code_extensions = {'.py', '.json', '.html', '.css', '.js'}
    
    # Expressão regular para encontrar referências a arquivos em strings
    asset_patterns = [
        r"['\"](assets/.*?\.(?:png|jpg|jpeg|gif|wav|mp3|ogg|ttf|otf))['\"]",
        r"load\(['\"](.*?\.(?:png|jpg|jpeg|gif|wav|mp3|ogg|ttf|otf))['\"]\)"
    ]
    
    # Analisa todos os arquivos de código
    for file_path in get_all_files(project_dir, code_extensions):
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                # Verifica cada padrão de referência a assets
                for pattern in asset_patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        # Se o match for uma tupla (grupo de captura), pega o primeiro grupo
                        if isinstance(match, tuple):
                            match = match[0]
                        
                        # Tenta criar um caminho a partir do match
                        try:
                            # Tenta como caminho relativo ao projeto
                            asset_path = Path(project_dir) / match.replace('/', os.sep)
                            if not asset_path.exists():
                                # Tenta como caminho relativo à pasta assets
                                asset_path = Path(project_dir) / 'assets' / match.replace('/', os.sep)
                            
                            if asset_path.exists():
                                used_assets.add(asset_path.resolve())
                        except Exception as e:
                            print(f"[AVISO] Erro ao processar caminho '{match}': {e}")
                            
        except Exception as e:
            print(f"[AVISO] Nao foi possivel ler o arquivo {file_path}: {e}")
    
    return used_assets

def find_unused_assets(project_dir):
    """Encontra arquivos de assets que não são referenciados no código."""
    print("Procurando por arquivos de assets...")
    assets_dir = Path(project_dir) / 'assets'
    
    if not assets_dir.exists():
        print(f"[ERRO] Diretorio de assets nao encontrado: {assets_dir}")
        return []
    
    # Obtém todos os arquivos de assets
    asset_extensions = {
        '.png', '.jpg', '.jpeg', '.gif',  # Imagens
        '.wav', '.mp3', '.ogg',           # Áudio
        '.ttf', '.otf', '.woff', '.woff2' # Fontes
    }
    
    all_assets = set(get_all_files(assets_dir, asset_extensions))
    print(f"Encontrados {len(all_assets)} arquivos de assets.")
    
    print("Analisando referencias nos arquivos de codigo...")
    used_assets = get_used_assets(project_dir)
    print(f"Encontradas {len(used_assets)} referencias a assets no codigo.")
    
    # Calcula a diferença para encontrar os não utilizados
    unused_assets = all_assets - used_assets
    
    # Retorna os resultados organizados por diretório
    return sorted(unused_assets, key=lambda x: str(x).lower())

def create_backup(project_dir):
    """Cria um backup dos arquivos que serão removidos."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path(project_dir) / 'backups' / f'backup_{timestamp}'
    
    print(f"\nCriando backup em: {backup_dir}")
    
    # Garante que o diretório de backup existe
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    return backup_dir

def remove_unused_assets(unused_assets, dry_run=True):
    """Remove os arquivos não utilizados ou apenas simula a remoção."""
    if not unused_assets:
        print("Nenhum arquivo para remover.")
        return
    
    backup_dir = create_backup(Path(unused_assets[0]).parent.parent.parent)
    
    print("\n=== ARQUIVOS A SEREM REMOVIDOS ===")
    for i, asset in enumerate(unused_assets, 1):
        rel_path = os.path.relpath(asset, backup_dir.parent.parent)
        print(f"{i}. {rel_path}")
    
    if dry_run:
        print("\n[OPCAO SECA] Nenhum arquivo foi removido.")
        print("Execute com --remove para realmente remover os arquivos.")
        return
    
    # Cria backup e remove os arquivos
    removed_count = 0
    for asset in unused_assets:
        try:
            # Cria a estrutura de diretórios no backup
            rel_path = os.path.relpath(asset, backup_dir.parent.parent)
            backup_path = backup_dir / rel_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Move o arquivo para o backup
            shutil.move(str(asset), str(backup_path))
            removed_count += 1
            
            # Tenta remover diretórios vazios
            try:
                parent = asset.parent
                while parent != backup_dir.parent.parent and not any(parent.iterdir()):
                    parent.rmdir()
                    parent = parent.parent
            except OSError:
                pass  # Não conseguiu remover o diretório (não está vazio)
                
        except Exception as e:
            print(f"[ERRO] Nao foi possivel remover {asset}: {e}")
    
    print(f"\n[SUCESSO] {removed_count} arquivos movidos para o backup em: {backup_dir}")

def main():
    project_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Analisando projeto em: {project_dir}")
    
    # Verifica se deve remover os arquivos ou apenas listar
    dry_run = '--remove' not in sys.argv
    
    unused_assets = find_unused_assets(project_dir)
    
    if not unused_assets:
        print("\nNenhum arquivo nao utilizado encontrado!")
        return
    
    print(f"\n=== ARQUIVOS NAO UTILIZADOS ENCONTRADOS ({len(unused_assets)}) ===")
    
    # Agrupa por diretório para melhor visualização
    by_dir = {}
    for asset in unused_assets:
        rel_path = os.path.relpath(asset, project_dir)
        dir_name = str(Path(rel_path).parent)
        if dir_name not in by_dir:
            by_dir[dir_name] = []
        by_dir[dir_name].append(Path(rel_path).name)
    
    # Exibe os resultados agrupados
    for dir_name, files in sorted(by_dir.items()):
        print(f"\n{dir_name}/")
        for file in sorted(files):
            print(f"  - {file}")
    
    print(f"\nTotal de arquivos nao utilizados: {len(unused_assets)}")
    
    # Calcula o tamanho total dos arquivos não utilizados
    total_size = sum(f.stat().st_size for f in unused_assets if f.exists())
    print(f"Espaco total que pode ser liberado: {total_size / (1024*1024):.2f} MB")
    
    # Se não for uma execução de remoção, mostra instruções
    if dry_run:
        print("\nPara remover estes arquivos, execute o script com a opcao --remove")
        print("Exemplo: python find_unused_files.py --remove")
    else:
        print("\n=== REMOVENDO ARQUIVOS ===")
        remove_unused_assets(unused_assets, dry_run=False)

if __name__ == "__main__":
    main()
