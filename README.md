# LinkZilla
LinkZilla é uma ferramenta que facilita a visualização da saída do GoSpider, tornando a navegação por URLs extraídas de um site muito mais simples e intuitiva.

### Descrição
O LinkZilla organiza e apresenta os links extraídos do GoSpider de maneira mais acessível, categorizando-os por pastas e URLs. Além disso, oferece a opção de exibição visual interativa com o parâmetro --visual, permitindo ao usuário clicar nas pastas e visualizar os links de forma mais fluida.

### Funcionalidades
Organiza e exibe os links extraídos de GoSpider em grupos baseados nas pastas.

Permite visualizar a saída do GoSpider de forma ordenada e categorizada.

Com o parâmetro --visual, oferece uma interface interativa para explorar as pastas e links com facilidade.

### Como Usar
Requisitos
Python 3.x

Bibliotecas: curses, urllib.parse, collections

### Instalação
Clone o repositório:

``git clone https://github.com/Thome07/LinkZilla``
``cd LinkZilla``

### Executando a Ferramenta
Se você quiser visualizar a saída do GoSpider de forma organizada no terminal, execute o script passando o caminho do arquivo de saída:

``python linkzilla.py caminho_para_o_arquivo_saida_goSpider.txt``

Se quiser utilizar a interface visual, adicione o parâmetro --visual:

``python linkzilla.py caminho_para_o_arquivo_saida_goSpider.txt --visual``
Isso abrirá uma interface onde você pode interagir com as pastas e clicar para visualizar os links dentro delas.

Exemplo de Saída
Sem o parâmetro --visual, a saída será organizada no terminal da seguinte forma:

/pasta1
  http://exemplo.com/pasta1/link1
  http://exemplo.com/pasta1/link2

/pasta2
  http://exemplo.com/pasta2/link3
  http://exemplo.com/pasta2/link4
Com o parâmetro --visual, você verá uma interface interativa para explorar os links de maneira mais amigável.

### Licença
Este projeto está licenciado sob a MIT License.
