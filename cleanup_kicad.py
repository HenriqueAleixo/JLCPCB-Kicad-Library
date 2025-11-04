"""
Script para remover as configurações manuais da biblioteca JLCPCB do KiCad
"""

import os
from pathlib import Path

# Caminhos do KiCad
KICAD_9_PATH = Path(os.environ.get("APPDATA", "")) / "kicad" / "9.0"

def remove_jlcpcb_from_table(filepath, lib_prefix="JLCPCB"):
    """Remove entradas da biblioteca JLCPCB de uma tabela"""
    if not filepath.exists():
        print(f"⚠ Arquivo não encontrado: {filepath}")
        return
    
    # Fazer backup
    backup_path = filepath.with_suffix(filepath.suffix + ".cleanup_backup")
    import shutil
    shutil.copy2(filepath, backup_path)
    print(f"✓ Backup criado: {backup_path}")
    
    # Ler e filtrar conteúdo
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_lines = []
    removed_count = 0
    
    for line in lines:
        # Pular linhas que contêm referências à biblioteca JLCPCB
        if '(lib (name "JLCPCB' in line or 'JLCPCB-Kicad-Library' in line:
            removed_count += 1
            continue
        new_lines.append(line)
    
    # Escrever de volta
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"✓ Removidas {removed_count} entradas de {filepath.name}")

def main():
    print("=" * 70)
    print("Limpeza das Configurações Manuais JLCPCB")
    print("=" * 70)
    print()
    
    # Remover do sym-lib-table
    sym_lib_table = KICAD_9_PATH / "sym-lib-table"
    if sym_lib_table.exists():
        print("🔧 Removendo bibliotecas de símbolos...")
        remove_jlcpcb_from_table(sym_lib_table)
    
    # Remover do fp-lib-table
    fp_lib_table = KICAD_9_PATH / "fp-lib-table"
    if fp_lib_table.exists():
        print("🔧 Removendo biblioteca de footprints...")
        remove_jlcpcb_from_table(fp_lib_table)
    
    print()
    print("=" * 70)
    print("✅ Limpeza concluída!")
    print("=" * 70)
    print()
    print("Agora você pode instalar a biblioteca pelo Package Manager do KiCad")
    print()

if __name__ == "__main__":
    main()
