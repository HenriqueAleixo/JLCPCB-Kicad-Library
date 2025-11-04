"""
Script para criar o pacote ZIP da biblioteca JLCPCB para distribuição via Package Manager
"""

import os
import json
import zipfile
from pathlib import Path
from datetime import datetime

LIBRARY_PATH = Path(__file__).parent.absolute()
OUTPUT_DIR = LIBRARY_PATH / "release"

def create_package_zip():
    """Cria o arquivo ZIP com a estrutura necessária para o Package Manager"""
    
    # Criar diretório de saída
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Ler metadata
    with open(LIBRARY_PATH / "metadata.json", 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    version = metadata['versions'][0]['version']
    zip_filename = OUTPUT_DIR / f"JLCPCB-Kicad-Library-{version}.zip"
    
    print(f"📦 Criando pacote: {zip_filename}")
    print()
    
    # Arquivos e pastas a incluir
    includes = [
        'metadata.json',
        'LICENSE',
        'README.md',
        'symbols',
        'footprints',
        '3dmodels',
        'resources'
    ]
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for item in includes:
            item_path = LIBRARY_PATH / item
            
            if not item_path.exists():
                print(f"⚠ Pulando {item} (não encontrado)")
                continue
            
            if item_path.is_file():
                # Adicionar arquivo
                arcname = item_path.name
                zipf.write(item_path, arcname)
                print(f"✓ Adicionado: {arcname}")
            
            elif item_path.is_dir():
                # Adicionar diretório recursivamente
                file_count = 0
                for root, dirs, files in os.walk(item_path):
                    for file in files:
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(LIBRARY_PATH)
                        zipf.write(file_path, arcname)
                        file_count += 1
                print(f"✓ Adicionado: {item}/ ({file_count} arquivos)")
    
    # Obter tamanho do arquivo
    zip_size = zip_filename.stat().st_size
    zip_size_mb = zip_size / (1024 * 1024)
    
    print()
    print("=" * 70)
    print(f"✅ Pacote criado com sucesso!")
    print(f"   Arquivo: {zip_filename.name}")
    print(f"   Tamanho: {zip_size_mb:.2f} MB ({zip_size:,} bytes)")
    print("=" * 70)
    print()
    print("Próximos passos:")
    print(f"1. Vá para https://github.com/HenriqueAleixo/JLCPCB-Kicad-Library/releases/new")
    print(f"2. Crie uma nova release com a tag: v{version}")
    print(f"3. Faça upload do arquivo: {zip_filename.name}")
    print(f"4. Atualize o repository.json com o link da release")
    print()

if __name__ == "__main__":
    create_package_zip()
