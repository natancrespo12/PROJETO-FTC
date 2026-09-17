# Formulário acessível por áudio — "Modo Inclusão"

**Data:** 2026-09-17
**Projeto:** Site de Prevenção à Violência (Essência Inteira)
**Autor:** brainstorming com Claude

## Problema

A página `Formulario.dc.html` é uma autoavaliação anônima sobre violência no
relacionamento (7 perguntas de múltipla escolha). Hoje ela só funciona por
leitura. Pessoas que **não sabem ler nem escrever** ficam de fora. Precisamos
tornar o formulário utilizável por quem não lê, lendo as perguntas e as
alternativas em voz alta — na mesma voz de boa qualidade já usada no projeto
METACELL.

## Objetivo

Adicionar um **"Modo Inclusão"** ao formulário: um botão que, ao ser ativado,
permite ouvir cada pergunta (com suas alternativas) e ouvir a página inteira em
sequência, com voz neural natural em português.

## Decisões tomadas (brainstorming)

1. **Escopo:** apenas a página `Formulario.dc.html` por enquanto. As demais
   páginas (Essência Inteira, Depoimento, Podcasts) podem receber o mesmo
   tratamento depois.
2. **Gravação de voz da pessoa nas respostas:** FORA DE ESCOPO agora. Motivos:
   o site é anônimo e local-only (sem backend para onde enviar), e gravar a voz
   de uma possível vítima é sensível/identificável. Foco em *ouvir*, que já
   resolve o uso por quem não lê. Pode ser revisitado depois com um plano seguro.
3. **Comportamento do botão de inclusão:** liga o "Modo Inclusão" — mostra um
   botão grande **▶ Ouvir** em cada pergunta, controles maiores, e um botão para
   **ouvir a página toda**.
4. **Voz:** edge-tts `pt-BR-AntonioNeural` (a "amostra-1-antonio-atual" que já
   era a escolhida do METACELL). Voz masculina, neutra, boa dicção.

## Contexto técnico

- O site usa um runtime próprio (`support.js`) que é **baseado em React**. Ele
  lê o bloco `<x-dc>` como template e a classe `class Component extends DCLogic`
  (no `<script type="text/x-dc" data-dc-script>`) fornece valores para os
  bindings `{{ }}` via `renderVals()`.
- **Consequência:** o React re-renderiza a cada `setState`. Qualquer DOM
  injetado "por fora" (via script externo) seria apagado no próximo render.
  Portanto a integração precisa ser **nativa**: métodos na classe `Component`
  e marcação no template do próprio `Formulario.dc.html`.
- `edge-tts` 7.2.8 já está instalado (Python 3.14). Geração de MP3 é local,
  gratuita e sem chave de API. Não requer ffmpeg (saída já é MP3).
- No uso final, o React continua vindo de CDN (como já é hoje), então a página
  precisa de internet para renderizar — mas os MP3s ficam locais junto do site.

## Arquitetura da solução

### Componente A — Geração de áudios (build, executado uma vez)

Script `gerar_audios.py` (guardado no projeto para regenerar/ajustar texto):

- Usa `edge-tts` com voz `pt-BR-AntonioNeural`.
- Gera em `site/audio/`:
  - `intro.mp3` — título ("Isso é cuidado ou violência?") + parágrafo de
    abertura explicando que é anônimo e opcional.
  - `q1.mp3` … `q7.mp3` — cada um lê **a pergunta seguida de todas as
    alternativas**, com pausas naturais. Ex.: *"Pergunta 1. Você está ou já
    esteve em um relacionamento afetivo? As opções são: Sim, atualmente. Sim,
    anteriormente. Não."*
  - `enviado.mp3` — lê a tela de confirmação + canais de ajuda (180 / 190).
- O texto de cada áudio fica num dicionário no topo do script, fácil de editar.
- **Interface:** entrada = textos no script; saída = arquivos MP3 em `site/audio/`.
- **Dependências:** `edge-tts`, internet (a geração usa o serviço de voz da
  Microsoft; o *uso* do site depois não precisa).

### Componente B — Modo Inclusão (nativo no componente React)

Alterações em `Formulario.dc.html`:

**Estado (`state`):**
- `modoInclusao: boolean` — inicializado a partir de `localStorage`
  (`ei-modo-inclusao`) para persistir a escolha entre visitas.
- `tocando: string | null` — id do áudio em reprodução (ex.: `"q3"`), usado para
  destacar a pergunta atual.

**Métodos:**
- `toggleInclusao()` — inverte `modoInclusao`, grava no `localStorage`.
- `ouvir(id)` — para o áudio anterior e toca `audio/<id>.mp3` via `new Audio()`;
  atualiza `tocando`; ao terminar limpa `tocando`.
- `ouvir1()`…`ouvir7()`, `ouvirIntro()` — atalhos para `ouvir(id)` (o binding
  `{{ }}` espera referência de método sem argumento, seguindo o padrão já usado
  por `on1`…`on7`).
- `ouvirTudo()` — toca `intro → q1 → … → q7` em sequência, encadeando pelo
  evento `ended`; destaca cada pergunta conforme toca.
- `pararAudio()` — para qualquer reprodução e limpa `tocando`.
- Integração com **"Sair rápido"** e `Escape`: `sair()` chama `pararAudio()`
  antes de trocar de página (segurança — nenhum áudio continua tocando).
- Ao `enviar()`: se `modoInclusao` estiver ligado, toca `enviado.mp3`.

**Template (`<x-dc>`):**
- **Botão fixo** de Modo Inclusão (canto inferior direito): alto contraste,
  ícone 🔊 + rótulo "Ouvir / Modo inclusão". `onClick="{{ toggleInclusao }}"`.
  Mostra estado ligado/desligado.
- Dentro de cada bloco de pergunta (`role="group"`), um botão grande
  **▶ Ouvir**, exibido só quando `modoInclusao` está ligado (via `sc-if`),
  com `onClick` para o `ouvirN` correspondente. Alvo de toque ≥ 44px.
- Um botão **▶ Ouvir a página toda** no topo do bloco de perguntas, também sob
  `sc-if` do modo inclusão.
- Quando `modoInclusao` ligado: destaque visual (borda/realce) no bloco cuja
  pergunta está `tocando`.

### Fluxo de dados

1. Pessoa abre a página → estado lê `localStorage` → modo pode já estar ligado.
2. Clica no botão fixo 🔊 → `toggleInclusao` → aparecem os ▶ Ouvir.
3. Clica ▶ numa pergunta → `ouvir("qN")` → `new Audio('audio/qN.mp3').play()`.
4. Clica ▶ Ouvir a página toda → sequência intro→q1→…→q7.
5. Marca as alternativas normalmente (radios já existentes).
6. Envia → confirmação; se modo ligado, toca `enviado.mp3`.
7. A qualquer momento "Sair rápido"/Esc → para áudio + sai.

## Tratamento de erros

- **Autoplay bloqueado:** toda reprodução parte de um clique do usuário, então
  não há bloqueio. `ouvirTudo` inicia por clique; o encadeamento seguinte é
  permitido por já haver gesto do usuário.
- **Arquivo de áudio ausente / falha de rede:** `Audio.onerror` limpa `tocando`
  silenciosamente (não quebra o formulário). Opcional: log discreto no console.
- **Troca rápida de faixa:** `ouvir()` sempre para/descarta o `Audio` anterior
  antes de criar o novo, evitando sobreposição.

## Testes / verificação

- Servir `site/` via `http://` local e abrir `Formulario.dc.html`.
- Verificar: botão fixo aparece; ligar modo mostra os ▶; cada ▶ toca o MP3
  correto; "Ouvir a página toda" encadeia; destaque acompanha a faixa;
  "Sair rápido" e Esc param o áudio; estado persiste ao recarregar; envio toca
  `enviado.mp3`; formulário original continua funcionando (radios, envio,
  localStorage das respostas).

## Arquivos afetados

- **Editado:** `site/Formulario.dc.html` (template + classe `Component`).
- **Novos:** `site/audio/intro.mp3`, `q1.mp3`…`q7.mp3`, `enviado.mp3`;
  `gerar_audios.py`.
- Nenhuma outra página é alterada.

## Fora de escopo

- Gravação de respostas em áudio pela pessoa.
- Acessibilidade por áudio nas demais páginas do site.
- Backend / envio de respostas para servidor.
