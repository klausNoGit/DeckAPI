![yugioh](logo.jpg)

# Deck-API

O projeto **Deck-API** é uma estrutura de dados desenvolvida em **Python** para consumir informações de diferentes fontes sobre o jogo de cartas Yu-Gi-Oh TCG. Nosso objetivo é fornecer uma estrutura de fácil compreensão para desenvolvedores e usuários em geral, permitindo a criação de listas de decks completas e repletas de recursos calculados diretamente no núcleo do projeto.

# Conceitos Primitivos

Para utilizar a API de forma eficaz e aproveitá-la ao máximo, é importante entender alguns conceitos fundamentais do jogo. Esses conceitos são essenciais tanto para jogadores quanto para quem deseja contribuir com o projeto.

Abaixo, você encontrará os principais conceitos abordados:

- Deck-list
- Deck principal (main)
- Deck extra (extra)
- Deck auxiliar (side)
- Link do deck
- Arquivo do deck
- Código da carta

# Deck-list

Uma deck-list é simplesmente a lista de cartas (incluindo nome e quantidade) que compõem um baralho jogável em Yu-Gi-Oh. Independentemente do formato utilizado em campeonatos ou partidas casuais, aqui está um exemplo de deck para o formato Yu-Gi-Oh TCG Padrão:

```
Main Deck:
Dark Magician x3
Magician of Dark Illusion x1
Apprentice Illusion Magician x3
Skull Meister x3
Magician's Rod x3
Effect Veiler x3
Magicians' Souls x2
Magician of Chaos x1
The Eye of Timaeus x2
Dark Magic Attack x1
Dark Magic Inheritance x3
Twin Twisters x3
Secrets of Dark Magic x2
Illusion Magic x1
Dark Magical Circle x3
Magician Navigation x2
Destined Rivals x1
Eternal Soul x3


Extra Deck:
Dark Magician the Dragon Knight x3
Master of Chaos x1
Amulet Dragon x3
Dark Magician the Knight of Dragon Magic x1
Dark Paladin x2
The Dark Magicians x2
Dark Cavalry x2
Dark Magician Girl the Dragon Knight x1


Side Deck:
Lava Golem x3
D.D. Crow x3
Magician of Chaos x1
Dark Ruler No More x1
Cosmic Cyclone x3
Ballista Squad x1
Light-Imprisoning Mirror x3
```

Note que a deck-list do exemplo utiliza os componentes **"Main Deck", "Extra Deck" e "Side Deck"**.
Vale ressaltar que, no momento do lançamento deste README.md, esse deck está validado para torneios ou duelos casuais no formato convencional do Yu-Gi-Oh TCG. Nossa estrutura de dados foi projetada para fornecer recursos relacionados a esses componentes.

## Deck Principal (Main)

O Main Deck deve conter no mínimo 40 cartas e no máximo 60 cartas, conforme as regras do formato de jogo exigido. Na deck-list anterior, o deck atende a essa exigência, com 40 cartas. Em outros formatos, esses valores podem variar. Por exemplo, no formato Speed Duel, o deck principal deve ter no mínimo 20 cartas e no máximo 30.

## Deck Extra (Extra)

O Extra Deck, por outro lado, é limitado a um máximo de 15 cartas. O valor mínimo pode ser 0, permitindo que jogadores optem por não incluir nenhuma carta no Extra Deck, o que não é considerado incorreto.

## Deck Side (side)

Mais comumente utilizado em **Matches de 3**, o **Side Deck** (ou deck auxiliar) contém no máximo 15 cartas, assim como o Extra Deck. No entanto, seu objetivo é permitir a reorganização da estratégia do deck à medida que as partidas se desenvolvem, ajustando-se para enfrentar diferentes adversários.

## Link do Deck

O Link do Deck é uma URL criptografada em base64, composta por números **inteiros de 32 bits** que representam os códigos das cartas. O objetivo dessa URL é fornecer uma forma compacta de representar o deck mencionado anteriormente.
Veja abaixo um exemplo:

```
ydke://r/TMAq/0zAKv9MwCd/oYAqj50gGo+dIBqPnSAbLJCQSyyQkEsskJBGEYbABhGGwAYRhsALIyzAWyMswFsjLMBUe80QVHvNEF6tzbAm47GwBuOxsA/k8jABDUfAIQ1HwCENR8AiPWnQIj1p0CI9adAgQdjAMEHYwDH01jBAiP0AIIj9ACCI/QAuPkeADj5HgA6V9ZAQrQ5gIK0OYCCtDmAg==!ep18AnqdfAJ6nXwCUukRBc83fgTPN34Ezzd+BFX0WADhBd8F4QXfBdaQ/gLWkP4COcpgBDnKYAS4vp0C!7I8BAOyPAQDsjwEATvd1AU73dQFO93UB6tzbAiaQQgOEJX4AhCV+AIQlfgBkn80EIe4tAyHuLQMh7i0D!
```

![decklist](decklist.png)

Este link YDKE foi extraído do ProjetoIgnis (EdoPro). Em outros softwares, também é possível obter **links semelhantes**, que podem ser facilmente lidos e processados. Este projeto se baseia nesse link e no arquivo do deck para realizar suas funções.

## Arquivo do Deck

O arquivo de uma deck list em Yu-Gi-Oh possui o sequinte formato interno:

```
#created by Player
#main
48452496
27260347
.
.
.
94259633
#extra
27204311
.
.
.
27204311
!side
27204311
27204311
.
.
.
0045474
58921041
82732705
```

Essa é a deck list de código do exemplo anterior, perceba que o padrão mínimo é
esse:

```
#created by Player
#main
#extra
!side
```

O formato do arquivo é **YDK**, e todos os códigos mencionados acima são os valores de 32 bits descriptografados para cada carta. As cartas que se repetem têm múltiplos códigos, com um limite máximo de 3 cartas por nome/código.

## Código da Carta

Cada carta possui um código único de 32 bits. Isso significa que nenhum código pode ser repetido. Mesmo cartas com o mesmo nome, como versões alternativas, possuem códigos diferentes, geralmente variando em +1 ou -1 em relação ao código da versão original. O código da carta é uma ferramenta útil para garantir precisão, tanto em buscas binárias quanto na unificação das cartas.

# Informações Adicionais

Se você deseja contribuir com o projeto, entre em contato através do e-mail yugiohsuport@gmail.com para obter mais detalhes. Também é possível abrir uma issue para relatar dúvidas, problemas ou bugs encontrados.

# Como Contribuir

Contribuir para este projeto é simples e muito bem-vindo! Aqui estão algumas maneiras pelas quais você pode ajudar:

- Relatar Bugs:
> Se você encontrar um bug ou comportamento inesperado, abra uma issue detalhando o problema para que possamos corrigir.
- Sugerir Novos Recursos:
> Se você tem ideias para novos recursos ou melhorias, sinta-se à vontade para sugerir uma issue. Adoramos ouvir sugestões de usuários!

Contribuições de Código: Se você deseja contribuir com código, siga estas etapas:

- Faça um fork deste repositório.
- Realize suas modificações e teste-as.
- Envie um pull request com uma descrição clara das alterações realizadas.

## Documentação

> Se você identificar algo que possa ser melhorado na documentação, seja código ou texto explicativo, sinta-se à vontade para enviar uma contribuição.
> Feedback e Melhoria Contínua: Compartilhe seu feedback sobre o uso da API, sugestões de melhorias ou qualquer outra ideia que possa aprimorar o projeto.

# Licença

Este projeto está licenciado sob a MIT License. Isso significa que você pode usar, modificar e distribuir o código livremente, desde que inclua a mesma licença em qualquer trabalho derivado.

# Código de Conduta

Para garantir um ambiente colaborativo e respeitoso, pedimos que todos os colaboradores sigam as diretrizes do código de conduta. Seja sempre respeitoso, educado e compreensivo com todos os participantes.

# Agradecimentos

Agradecemos a todos que ajudaram a construir e melhorar este projeto, seja por contribuições de código, relatórios de bugs ou sugestões de melhorias.