# Publicação dos fontes no GitHub

Destino único desta entrega: https://github.com/21VT/HooLeeSheet-

## Pelo navegador

1. Extraia dSantCreator-GitHub-organizado-3.3.1.zip.
2. Confira que README.md, dsant.py, sagaz/, apps/ e .agents/ estão no primeiro nível.
3. Abra o repositório e escolha Upload files.
4. Envie os arquivos e pastas internos, preservando os caminhos. Ative arquivos ocultos para incluir .agents/ e .github/.
5. Use o commit `Publicação inicial do projeto`.

O ZIP é para transporte e backup. O GitHub deve receber os arquivos extraídos para mostrar código, documentação e skills.

## Pelo Git (preserva todos os caminhos)

Na pasta extraída, com Git e GitHub CLI instalados:

```bash
gh auth login --hostname github.com --git-protocol https --web
gh auth setup-git
git init -b main
git config user.name "Vitor Santos"
git config user.email "331775346+21VT@users.noreply.github.com"
git add .
git commit -m "Publicação inicial do projeto"
git remote add origin https://github.com/21VT/HooLeeSheet-.git
git push -u origin main
```

Esse fluxo presume o repositório remoto vazio e login da conta com escrita. Se o Git recusar porque já há histórico, não use force: clone o remoto em outra pasta, copie os arquivos extraídos para o clone, revise `git status`, faça o commit e envie.

## Conferir

Na página Code devem aparecer README.md, dsant.py, sagaz/, apps/, docs/, knowledge/, materials/, tests/ e .agents/. O README renderizado deve mostrar a versão 3.3.1. Não basta o ZIP ou TAR aparecer na lista.
