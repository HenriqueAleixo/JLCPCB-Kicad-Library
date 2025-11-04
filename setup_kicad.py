"""
Script para configurar automaticamente as bibliotecas JLCPCB no KiCad
Adiciona os símbolos, footprints e modelos 3D aos arquivos de configuração do KiCad
"""

import os
import json
from pathlib import Path

# Caminho base da biblioteca
LIBRARY_PATH = Path(__file__).parent.absolute()

# Caminhos do KiCad (Windows)
KICAD_USER_PATH = Path.home() / "Documents" / "KiCad"
KICAD_8_PATH = Path(os.environ.get("APPDATA", "")) / "kicad" / "8.0"
KICAD_9_PATH = Path(os.environ.get("APPDATA", "")) / "kicad" / "9.0"

# Detectar qual versão do KiCad está instalada
def get_kicad_config_path():
    if KICAD_9_PATH.exists():
        return KICAD_9_PATH
    elif KICAD_8_PATH.exists():
        return KICAD_8_PATH
    else:
        # Criar diretório padrão para KiCad 8
        KICAD_8_PATH.mkdir(parents=True, exist_ok=True)
        return KICAD_8_PATH

def create_sym_lib_table_entry(nickname, uri):
    """Cria uma entrada para sym-lib-table"""
    return f'  (lib (name "{nickname}")(type "KiCad")(uri "{uri}")(options "")(descr ""))\n'

def create_fp_lib_table_entry(nickname, uri):
    """Cria uma entrada para fp-lib-table"""
    return f'  (lib (name "{nickname}")(type "KiCad")(uri "{uri}")(options "")(descr ""))\n'

def backup_file(filepath):
    """Faz backup de um arquivo existente"""
    if filepath.exists():
        backup_path = filepath.with_suffix(filepath.suffix + ".backup")
        import shutil
        shutil.copy2(filepath, backup_path)
        print(f"✓ Backup criado: {backup_path}")

def read_existing_table(filepath):
    """Lê uma tabela existente e retorna as entradas"""
    if not filepath.exists():
        return []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extrai as entradas lib
    entries = []
    for line in content.split('\n'):
        if '(lib (name' in line:
            entries.append(line.strip())
    
    return entries

def write_sym_lib_table(config_path, library_path):
    """Escreve ou atualiza o arquivo sym-lib-table"""
    sym_lib_table_path = config_path / "sym-lib-table"
    
    # Fazer backup
    backup_file(sym_lib_table_path)
    
    # Ler entradas existentes
    existing_entries = read_existing_table(sym_lib_table_path)
    
    # Obter todas as bibliotecas de símbolos
    symbols_path = library_path / "symbols"
    symbol_files = sorted(symbols_path.glob("*.kicad_sym"))
    
    # Criar novas entradas
    new_entries = []
    for symbol_file in symbol_files:
        nickname = symbol_file.stem
        # Verificar se já existe
        if not any(f'(name "{nickname}")' in entry for entry in existing_entries):
            uri = str(symbol_file).replace("\\", "/")
            new_entries.append(create_sym_lib_table_entry(nickname, uri))
    
    if not new_entries and not existing_entries:
        # Arquivo novo
        with open(sym_lib_table_path, 'w', encoding='utf-8') as f:
            f.write("(sym_lib_table\n")
            for symbol_file in symbol_files:
                nickname = symbol_file.stem
                uri = str(symbol_file).replace("\\", "/")
                f.write(create_sym_lib_table_entry(nickname, uri))
            f.write(")\n")
        print(f"✓ Criado novo sym-lib-table com {len(symbol_files)} bibliotecas")
    elif new_entries:
        # Atualizar arquivo existente
        with open(sym_lib_table_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Adicionar novas entradas antes do fechamento
        content = content.rstrip()
        if content.endswith(')'):
            content = content[:-1]  # Remove o último )
        
        with open(sym_lib_table_path, 'w', encoding='utf-8') as f:
            f.write(content)
            for entry in new_entries:
                f.write(entry)
            f.write(")\n")
        print(f"✓ Adicionadas {len(new_entries)} bibliotecas ao sym-lib-table")
    else:
        print("✓ Todas as bibliotecas de símbolos já estão configuradas")

def write_fp_lib_table(config_path, library_path):
    """Escreve ou atualiza o arquivo fp-lib-table"""
    fp_lib_table_path = config_path / "fp-lib-table"
    
    # Fazer backup
    backup_file(fp_lib_table_path)
    
    # Ler entradas existentes
    existing_entries = read_existing_table(fp_lib_table_path)
    
    # Caminho da biblioteca de footprints
    footprints_path = library_path / "footprints" / "JLCPCB.pretty"
    nickname = "JLCPCB"
    
    # Verificar se já existe
    if any(f'(name "{nickname}")' in entry for entry in existing_entries):
        print("✓ Biblioteca de footprints JLCPCB já está configurada")
        return
    
    uri = str(footprints_path).replace("\\", "/")
    
    if not existing_entries:
        # Arquivo novo
        with open(fp_lib_table_path, 'w', encoding='utf-8') as f:
            f.write("(fp_lib_table\n")
            f.write(create_fp_lib_table_entry(nickname, uri))
            f.write(")\n")
        print("✓ Criado novo fp-lib-table")
    else:
        # Atualizar arquivo existente
        with open(fp_lib_table_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Adicionar nova entrada antes do fechamento
        content = content.rstrip()
        if content.endswith(')'):
            content = content[:-1]
        
        with open(fp_lib_table_path, 'w', encoding='utf-8') as f:
            f.write(content)
            f.write(create_fp_lib_table_entry(nickname, uri))
            f.write(")\n")
        print("✓ Adicionada biblioteca de footprints ao fp-lib-table")

def configure_3d_models_path(library_path):
    """Configura a variável de ambiente para modelos 3D"""
    models_3d_path = library_path / "3dmodels" / "JLCPCB.3dshapes"
    
    print("\n📦 Configuração de Modelos 3D:")
    print(f"   Adicione manualmente no KiCad:")
    print(f"   Preferências → Configurar Caminhos")
    print(f"   Nome: JLCPCB_3DMODELS")
    print(f"   Caminho: {models_3d_path}")

def main():
    print("=" * 70)
    print("Configuração das Bibliotecas JLCPCB para KiCad")
    print("=" * 70)
    print()
    
    # Detectar configuração do KiCad
    config_path = get_kicad_config_path()
    print(f"📁 Diretório de configuração do KiCad: {config_path}")
    print(f"📁 Diretório da biblioteca: {LIBRARY_PATH}")
    print()
    
    # Configurar símbolos
    print("🔧 Configurando bibliotecas de símbolos...")
    write_sym_lib_table(config_path, LIBRARY_PATH)
    print()
    
    # Configurar footprints
    print("🔧 Configurando biblioteca de footprints...")
    write_fp_lib_table(config_path, LIBRARY_PATH)
    print()
    
    # Informações sobre modelos 3D
    configure_3d_models_path(LIBRARY_PATH)
    print()
    
    print("=" * 70)
    print("✅ Configuração concluída!")
    print("=" * 70)
    print()
    print("Próximos passos:")
    print("1. Reinicie o KiCad se estiver aberto")
    print("2. As bibliotecas estarão disponíveis no seletor de símbolos/footprints")
    print("3. Configure manualmente o caminho dos modelos 3D conforme indicado acima")
    print()

if __name__ == "__main__":
    main()
