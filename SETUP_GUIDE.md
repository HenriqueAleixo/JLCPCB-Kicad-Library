# Guia de Setup - Repositório Customizado KiCad

## 📋 Passos para configurar sua biblioteca customizada

### 1️⃣ Criar o repositório de pacotes no GitHub

1. Vá para https://github.com/new
2. Crie um novo repositório:
   - Nome: `Kicad-Library`
   - Descrição: "Custom KiCad package repository"
   - Público
   - Sem README (vamos adicionar depois)

3. Clone o repositório:
```powershell
cd c:\Users\Aleixo\Documents\projetos
git clone https://github.com/HenriqueAleixo/Kicad-Library.git
cd Kicad-Library
```

4. Copie os arquivos necessários:
```powershell
Copy-Item ..\JLCPCB-Kicad-Library\repository.json .
Copy-Item ..\JLCPCB-Kicad-Library\REPOSITORY_README.md README.md
```

5. Faça o commit e push:
```powershell
git add .
git commit -m "Initial commit - KiCad package repository"
git push origin main
```

### 2️⃣ Fazer push da biblioteca JLCPCB

Volte para o repositório da biblioteca:
```powershell
cd ..\JLCPCB-Kicad-Library
```

Adicione os arquivos modificados (NÃO adicione símbolos gerados automaticamente):
```powershell
git add .github/
git add *.py
git add requirements.txt
git add README.md
git add metadata.json
git add repository.json
git status
```

Faça commit e push:
```powershell
git commit -m "Setup custom KiCad package repository"
git push origin main
```

### 3️⃣ Executar o GitHub Action manualmente

1. Vá para: https://github.com/HenriqueAleixo/JLCPCB-Kicad-Library/actions
2. Clique em "Update Library"
3. Clique em "Run workflow" → "Run workflow"
4. Aguarde o workflow terminar (vai demorar uns 5-10 minutos)
5. Verifique se a release foi criada em: https://github.com/HenriqueAleixo/JLCPCB-Kicad-Library/releases

### 4️⃣ Atualizar o repository.json com o SHA256 correto

Depois que a release for criada:

1. Baixe o arquivo ZIP da release
2. Calcule o SHA256:
```powershell
Get-FileHash .\JLCPCB-KiCad-Library-2025.11.04.zip -Algorithm SHA256
```

3. Edite o `repository.json` no repositório `Kicad-Library`:
   - Substitua `"download_sha256": ""` pelo hash correto
   - Atualize `download_size` com o tamanho real do arquivo

4. Commit e push:
```powershell
git add repository.json
git commit -m "Update SHA256 and download size"
git push origin main
```

### 5️⃣ Instalar no KiCad

1. Feche o KiCad se estiver aberto
2. Abra o KiCad
3. Vá em `Plugin and Content Manager`
4. Clique em `Manage...` (canto inferior esquerdo)
5. Adicione o repositório:
   ```
   https://raw.githubusercontent.com/HenriqueAleixo/Kicad-Library/main/repository.json
   ```
6. Clique em `Save`
7. Selecione `HenriqueAleixo's KiCad Repository` no dropdown
8. Clique em `JLCPCB KiCad Library`
9. Clique em `Install`
10. Clique em `Apply Pending Changes`

### 6️⃣ Usar a biblioteca

Agora você pode usar os componentes:
- Símbolos: JLCPCB-Capacitors, JLCPCB-Resistors, etc.
- Footprints: Biblioteca JLCPCB
- Modelos 3D: Incluídos automaticamente

## 🔄 Atualizações Automáticas

O GitHub Actions rodará automaticamente todos os dias às 06:00 UTC e:
- Baixará os dados mais recentes da JLCPCB
- Atualizará os símbolos e footprints
- Criará uma nova release
- O KiCad vai notificar quando houver atualizações disponíveis

## 🛠️ Customizações

Para adicionar seus próprios componentes:
1. Edite `handmadeLibrarySymbols.py`
2. Adicione suas funções de geração de símbolos
3. Commit e push
4. O GitHub Actions vai processar automaticamente

---

**Dúvidas?** Verifique os logs do GitHub Actions em:
https://github.com/HenriqueAleixo/JLCPCB-Kicad-Library/actions
