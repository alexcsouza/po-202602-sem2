# po-202602-sem2
Seminário 2 - Pesquisa Operacional - 2026-02

## Dependências
Para instalar as dependências do projeto use o comando:
    $ pdflatex --output-directory=doc/ doc/model.tex

Para atualizar as dependências no arquivo `requirementes.txt`, instale a lib desejada e em seguida, utilize o comando `pip freeze`. 

    $ python -m pip install matplotlib numpy
    $ python -m pip freeze > requirements.txt

## Gerando doc
Gerar a documentação requer a instalação do LATEX (pacote `texlive` no linux). O comando abaixo gera o arquivo `model.pdf` na pasta `./doc` caso o arquivo não exista.

    $ pdflatex --output-directory=doc/ doc/model.tex