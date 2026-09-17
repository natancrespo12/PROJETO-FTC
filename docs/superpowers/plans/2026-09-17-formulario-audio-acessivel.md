# Formulário acessível por áudio ("Modo Inclusão") — Plano de Implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Permitir que pessoas que não leem usem o formulário anônimo de autoavaliação, ouvindo cada pergunta (e suas alternativas) em voz neural de boa qualidade, através de um "Modo Inclusão".

**Architecture:** Áudios MP3 são pré-gerados com `edge-tts` (voz `pt-BR-AntonioNeural`) e guardados em `site/audio/`. A reprodução é integrada de forma **nativa** no componente React do runtime `support.js` (métodos na classe `Component` + marcação no template `<x-dc>` de `Formulario.dc.html`), porque o React re-renderiza a cada `setState` e apagaria qualquer DOM injetado por fora.

**Tech Stack:** HTML + runtime próprio baseado em React (`support.js`), Python 3.14 + `edge-tts` 7.2.8 (geração de áudio), MP3, Web Audio (`new Audio()`).

## Global Constraints

- Editar **apenas** `Formulario.dc.html`. Nenhuma outra página muda.
- **Não** gravar voz da pessoa. Sem backend. Nada é enviado pela rede além do que já existe.
- Voz obrigatória: `pt-BR-AntonioNeural`.
- Preservar 100% do comportamento atual: radios, envio, `localStorage["ei-form"]`, botão "Sair rápido", tecla `Escape`.
- Bindings do template: usar somente `onClick="{{ metodo }}"` (referência de método, sem argumento) e `<sc-if value="{{ bool }}">` — padrões já comprovados no arquivo. **Não** depender de interpolação de texto/estilo dinâmico via `{{ }}` (não comprovada neste runtime).
- Diretório de trabalho: `D:\PROJETO FTC\site\` (cópia descompactada do ZIP).
- Segurança: ao "Sair rápido" ou `Escape`, qualquer áudio deve parar imediatamente.

---

## Estrutura de arquivos

- `D:\PROJETO FTC\gerar_audios.py` — **novo.** Script de geração dos MP3 (guardado para reajustar textos depois).
- `D:\PROJETO FTC\site\audio\*.mp3` — **novos.** `intro, q1..q7, enviado` (9 arquivos).
- `D:\PROJETO FTC\site\Formulario.dc.html` — **modificado.** Template + classe `Component`.
- Demais arquivos do site — inalterados.

---

## Task 1: Preparar ambiente e gerar os áudios

**Files:**
- Create: `D:\PROJETO FTC\gerar_audios.py`
- Create (output): `D:\PROJETO FTC\site\audio\intro.mp3`, `q1.mp3` … `q7.mp3`, `enviado.mp3`

**Interfaces:**
- Consumes: nada.
- Produces: 9 arquivos MP3 em `site/audio/`, nomeados exatamente `intro,q1,q2,q3,q4,q5,q6,q7,enviado`. Esses nomes são a interface consumida pela Task 2 (o método `ouvir(id)` carrega `audio/<id>.mp3`).

- [ ] **Step 1: Descompactar o site para a pasta de trabalho**

Run (bash):
```bash
cd "/d/PROJETO FTC" && rm -rf site && unzip -o "Site de Prevenção à Violência.zip" -d site
```
Expected: cria `D:\PROJETO FTC\site\` com `Formulario.dc.html`, `support.js`, `uploads/`, etc.

- [ ] **Step 2 (opcional, recomendado): iniciar git para ter histórico**

Run (bash):
```bash
cd "/d/PROJETO FTC" && git init && printf 'node_modules/\n*.zip\n' > .gitignore && git add -A && git commit -m "chore: baseline do site antes do modo inclusão"
```
Expected: repositório criado e commit inicial. (Se o usuário não quiser git, pule este passo e ignore os passos de `git commit` seguintes.)

- [ ] **Step 3: Criar o script de geração de áudio**

Create `D:\PROJETO FTC\gerar_audios.py`:
```python
"""Gera os áudios do formulário com edge-tts (voz pt-BR-AntonioNeural).
Uso:  py gerar_audios.py
Regenera todos os MP3 em site/audio/. Edite TEXTOS para ajustar a narração.
"""
import asyncio
import os
import edge_tts

VOZ = "pt-BR-AntonioNeural"
SAIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "site", "audio")

TEXTOS = {
    "intro": (
        "Isso é cuidado, ou violência? Este é um formulário anônimo, feito para "
        "ajudar você a refletir sobre situações de violência nos relacionamentos. "
        "Você não precisa se identificar, e não precisa responder nenhuma pergunta "
        "que cause desconforto. Se alguma situação fizer parte da sua realidade, "
        "saiba que você não está sozinha, e que existe ajuda. Para ouvir cada "
        "pergunta, toque no botão de ouvir ao lado dela."
    ),
    "q1": (
        "Pergunta 1. Você está, ou já esteve, em um relacionamento afetivo? "
        "As opções são: Sim, atualmente. Sim, anteriormente. Ou não."
    ),
    "q2": (
        "Pergunta 2. Você já deixou de fazer algo que queria, por medo da reação "
        "do seu parceiro ou parceira? As opções são: Nunca. Às vezes. "
        "Frequentemente. Ou sempre."
    ),
    "q3": (
        "Pergunta 3. Você já teve sua privacidade invadida, como celular, "
        "mensagens, redes sociais ou localização, sem a sua vontade? "
        "As opções são: Nunca. Às vezes. Frequentemente. Ou sempre."
    ),
    "q4": (
        "Pergunta 4. Você já foi empurrado ou empurrada, segurado à força, "
        "agarrado, puxado, apertado, ou agredido? As opções são: Nunca. "
        "Uma vez. Algumas vezes. Ou muitas vezes."
    ),
    "q5": (
        "Pergunta 5. Você já teve medo de dizer não, ou de discordar do seu "
        "parceiro ou parceira, por medo do que poderia acontecer? "
        "As opções são: Nunca. Às vezes. Frequentemente. Ou sempre."
    ),
    "q6": (
        "Pergunta 6. Depois de responder essas perguntas, você reconhece alguma "
        "dessas situações como algo que acontece, ou já aconteceu, com você? "
        "As opções são: Sim. Talvez, não tenho certeza. Não. "
        "Ou prefiro não responder."
    ),
    "q7": (
        "Pergunta 7. Você gostaria de receber informações sobre onde buscar "
        "ajuda? As opções são: Sim. Não. Ou prefiro não responder."
    ),
    "enviado": (
        "Obrigado por parar para pensar sobre isso. Medo de reação, invasão de "
        "privacidade, dificuldade de dizer não, e contato físico forçado, não são "
        "detalhes de um relacionamento: são sinais de violência. Se você "
        "reconheceu alguma dessas situações, procurar informação já é um passo. "
        "Você pode ligar para o cento e oitenta: é gratuito, sigiloso, e funciona "
        "vinte e quatro horas. Em caso de risco imediato, ligue para o cento e "
        "noventa."
    ),
}


async def gerar():
    os.makedirs(SAIDA, exist_ok=True)
    for nome, texto in TEXTOS.items():
        caminho = os.path.join(SAIDA, nome + ".mp3")
        comunicador = edge_tts.Communicate(texto, VOZ)
        await comunicador.save(caminho)
        print("gerado:", caminho)


if __name__ == "__main__":
    asyncio.run(gerar())
```

- [ ] **Step 4: Rodar o script**

Run (bash):
```bash
cd "/d/PROJETO FTC" && py gerar_audios.py
```
Expected: 9 linhas `gerado: ...\site\audio\<nome>.mp3`, sem erros.

- [ ] **Step 5: Verificar que os 9 arquivos existem e têm tamanho > 0**

Run (bash):
```bash
cd "/d/PROJETO FTC/site/audio" && ls -l && for f in intro q1 q2 q3 q4 q5 q6 q7 enviado; do test -s "$f.mp3" && echo "OK $f" || echo "FALTA $f"; done
```
Expected: 9 linhas `OK ...`, nenhum `FALTA`.

- [ ] **Step 6: Ouvir 1 arquivo para confirmar a voz (manual)**

Abra `D:\PROJETO FTC\site\audio\q1.mp3` no player do Windows. Esperado: voz masculina neutra (Antonio) lendo a pergunta 1 e as opções, com boa dicção.

- [ ] **Step 7: Commit**

Run (bash):
```bash
cd "/d/PROJETO FTC" && git add gerar_audios.py "site/audio" && git commit -m "feat(audio): gera narração das perguntas com edge-tts (Antonio)"
```

---

## Task 2: Modo Inclusão — lógica do componente + botões de ouvir por pergunta

**Files:**
- Modify: `D:\PROJETO FTC\site\Formulario.dc.html` (classe `Component` no `<script data-dc-script>` e template `<x-dc>`)

**Interfaces:**
- Consumes: arquivos `audio/<id>.mp3` da Task 1.
- Produces (expostos por `renderVals()` para o template):
  - `modoInclusao: boolean`, `modoInclusaoOff: boolean`, `estaTocando: boolean`
  - `toggleInclusao: () => void`, `pararAudio: () => void`, `ouvirTudo: () => void`
  - `ouvirIntro, ouvir1 … ouvir7: () => void`
  - (mantém os já existentes: `quickExit, sair, enviado, aberto, enviar, on1..on7`)

- [ ] **Step 1: Substituir a classe `Component` inteira**

Em `Formulario.dc.html`, substitua todo o bloco `class Component extends DCLogic { … }` (linhas ~134–168) por:
```javascript
class Component extends DCLogic {
  state = {
    respostas: {},
    enviado: false,
    modoInclusao: (() => { try { return localStorage.getItem("ei-modo-inclusao") === "1"; } catch (e) { return false; } })(),
    tocando: null,
  };
  _audio = null;

  componentDidMount() {
    this._onKey = (e) => {
      if ((this.props.quickExit ?? true) && e.key === "Escape") this.sair();
    };
    window.addEventListener("keydown", this._onKey);
  }
  componentWillUnmount() {
    window.removeEventListener("keydown", this._onKey);
    this.pararAudio();
  }

  sair = () => {
    this.pararAudio();
    const url = "https://www.google.com/search?q=previs%C3%A3o+do+tempo";
    try { window.top.location.replace(url); } catch (e) { window.location.replace(url); }
  };

  set = (k) => (e) => {
    const v = e.target.value;
    this.setState((s) => ({ respostas: Object.assign({}, s.respostas, { [k]: v }) }));
  };

  pararAudio = () => {
    if (this._audio) { try { this._audio.pause(); } catch (e) {} }
    this._audio = null;
    if (this.state.tocando) this.setState({ tocando: null });
  };

  ouvir = (id) => {
    this.pararAudio();
    const a = new Audio("audio/" + id + ".mp3");
    this._audio = a;
    a.onended = () => { if (this._audio === a) { this._audio = null; this.setState({ tocando: null }); } };
    a.onerror = () => { if (this._audio === a) { this._audio = null; this.setState({ tocando: null }); } };
    this.setState({ tocando: id });
    a.play().catch(() => {});
  };

  ouvirTudo = () => {
    this.pararAudio();
    const seq = ["intro", "q1", "q2", "q3", "q4", "q5", "q6", "q7"];
    let i = 0;
    const tocarProx = () => {
      if (i >= seq.length) { this._audio = null; this.setState({ tocando: null }); return; }
      const id = seq[i++];
      const a = new Audio("audio/" + id + ".mp3");
      this._audio = a;
      a.onended = () => { if (this._audio === a) tocarProx(); };
      a.onerror = () => { if (this._audio === a) tocarProx(); };
      this.setState({ tocando: id });
      a.play().catch(() => {});
    };
    tocarProx();
  };

  ouvirIntro = () => this.ouvir("intro");
  ouvir1 = () => this.ouvir("q1");
  ouvir2 = () => this.ouvir("q2");
  ouvir3 = () => this.ouvir("q3");
  ouvir4 = () => this.ouvir("q4");
  ouvir5 = () => this.ouvir("q5");
  ouvir6 = () => this.ouvir("q6");
  ouvir7 = () => this.ouvir("q7");

  toggleInclusao = () => {
    const novo = !this.state.modoInclusao;
    try { localStorage.setItem("ei-modo-inclusao", novo ? "1" : "0"); } catch (e) {}
    if (!novo) this.pararAudio();
    this.setState({ modoInclusao: novo });
  };

  enviar = () => {
    const externo = this.props.formularioExterno;
    if (externo) { window.open(externo, "_blank", "noopener"); }
    try { localStorage.setItem("ei-form", JSON.stringify(this.state.respostas)); } catch (e) {}
    this.setState({ enviado: true });
    if (this.state.modoInclusao) this.ouvir("enviado");
  };

  renderVals() {
    return {
      quickExit: this.props.quickExit ?? true,
      sair: this.sair,
      enviado: this.state.enviado,
      aberto: !this.state.enviado,
      enviar: this.enviar,
      modoInclusao: this.state.modoInclusao,
      modoInclusaoOff: !this.state.modoInclusao,
      estaTocando: !!this.state.tocando,
      toggleInclusao: this.toggleInclusao,
      pararAudio: this.pararAudio,
      ouvirTudo: this.ouvirTudo,
      ouvirIntro: this.ouvirIntro,
      ouvir1: this.ouvir1, ouvir2: this.ouvir2, ouvir3: this.ouvir3, ouvir4: this.ouvir4,
      ouvir5: this.ouvir5, ouvir6: this.ouvir6, ouvir7: this.ouvir7,
      on1: this.set("q1"), on2: this.set("q2"), on3: this.set("q3"), on4: this.set("q4"),
      on5: this.set("q5"), on6: this.set("q6"), on7: this.set("q7"),
    };
  }
}
```

- [ ] **Step 2: Adicionar o botão fixo de Modo Inclusão no template**

Em `Formulario.dc.html`, logo **antes** de `</div>` que fecha o wrapper principal (a linha `</div>` imediatamente antes de `</x-dc>`, ~linha 130), insira:
```html
  <div style="position:fixed;right:16px;bottom:16px;z-index:100">
    <sc-if value="{{ modoInclusaoOff }}" hint-placeholder-val="{{ true }}">
      <button type="button" onClick="{{ toggleInclusao }}" style="display:flex;align-items:center;gap:10px;background:#6B3FA0;color:#FFFFFF;font-family:'Jost',sans-serif;font-size:15px;font-weight:500;border:none;padding:16px 22px;border-radius:999px;cursor:pointer;box-shadow:0 6px 20px rgba(35,26,46,0.28)">🔊 Ouvir o formulário</button>
    </sc-if>
    <sc-if value="{{ modoInclusao }}" hint-placeholder-val="{{ false }}">
      <button type="button" onClick="{{ toggleInclusao }}" style="display:flex;align-items:center;gap:10px;background:#231A2E;color:#FFFFFF;font-family:'Jost',sans-serif;font-size:15px;font-weight:500;border:1px solid #6B3FA0;padding:16px 22px;border-radius:999px;cursor:pointer;box-shadow:0 6px 20px rgba(35,26,46,0.28)">🔊 Modo áudio ligado — desativar</button>
    </sc-if>
  </div>
```

- [ ] **Step 3: Adicionar o botão "Ouvir a página toda" no topo do bloco de perguntas**

Em `Formulario.dc.html`, dentro do `<sc-if value="{{ aberto }}"...>`, logo após a abertura `<div style="display:grid;gap:clamp(20px,3vw,28px)">` (~linha 59), insira:
```html
          <sc-if value="{{ modoInclusao }}" hint-placeholder-val="{{ true }}">
            <div style="display:flex;flex-wrap:wrap;gap:12px;align-items:center;background:#FBF7FF;border:1px dashed #6B3FA0;border-radius:8px;padding:16px">
              <button type="button" onClick="{{ ouvirTudo }}" style="display:flex;align-items:center;gap:10px;background:#6B3FA0;color:#FFFFFF;font-family:'Jost',sans-serif;font-size:16px;font-weight:500;border:none;padding:14px 22px;border-radius:999px;cursor:pointer;min-height:52px">▶ Ouvir a página toda</button>
              <sc-if value="{{ estaTocando }}" hint-placeholder-val="{{ false }}">
                <button type="button" onClick="{{ pararAudio }}" style="display:flex;align-items:center;gap:8px;background:#FFFFFF;color:#231A2E;font-family:'Jost',sans-serif;font-size:16px;font-weight:500;border:1px solid #231A2E;padding:14px 22px;border-radius:999px;cursor:pointer;min-height:52px">■ Parar</button>
              </sc-if>
            </div>
          </sc-if>
```

- [ ] **Step 4: Adicionar o botão "▶ Ouvir" em cada uma das 7 perguntas**

Em cada `<div role="group" ...>` das perguntas, insira, **logo após** o `<p ...>` do enunciado (antes do primeiro `<label>`), o bloco correspondente. Use `ouvir1` na pergunta 1, `ouvir2` na 2, e assim por diante:
```html
            <sc-if value="{{ modoInclusao }}" hint-placeholder-val="{{ true }}">
              <button type="button" onClick="{{ ouvir1 }}" style="display:inline-flex;align-items:center;gap:10px;align-self:start;background:#EDE6F2;color:#6B3FA0;font-family:'Jost',sans-serif;font-size:16px;font-weight:500;border:1px solid #6B3FA0;padding:12px 20px;border-radius:999px;cursor:pointer;min-height:48px">▶ Ouvir a pergunta</button>
            </sc-if>
```
Repita para as perguntas 2 a 7 trocando **apenas** `ouvir1` por `ouvir2`, `ouvir3`, `ouvir4`, `ouvir5`, `ouvir6`, `ouvir7`, respectivamente. (Repetido na íntegra de propósito — não escreva "igual à pergunta 1".)

- [ ] **Step 5: Servir o site localmente**

Run (bash, deixe rodando):
```bash
cd "/d/PROJETO FTC/site" && py -m http.server 8080
```
Expected: `Serving HTTP on :: port 8080`.

- [ ] **Step 6: Verificar no navegador (manual)**

Abra `http://localhost:8080/Formulario.dc.html`. Esperado:
1. A página renderiza normalmente (título, 7 perguntas, botão Enviar).
2. Botão fixo roxo **"🔊 Ouvir o formulário"** no canto inferior direito.
3. Ao clicar nele: vira "Modo áudio ligado — desativar"; aparece a caixa **"▶ Ouvir a página toda"** e um botão **▶ Ouvir a pergunta** em cada uma das 7 perguntas.
4. Clicar **▶ Ouvir a pergunta** na pergunta 3 → toca a voz do Antonio lendo a pergunta 3 e as opções.
5. Recarregar a página (F5) → o modo continua ligado (persistência).
6. Sem erros no console (F12).

- [ ] **Step 7: Commit**

Run (bash):
```bash
cd "/d/PROJETO FTC" && git add "site/Formulario.dc.html" && git commit -m "feat(form): modo inclusão com áudio por pergunta"
```

---

## Task 3: Ouvir tudo em sequência, parar ao sair, e áudio da confirmação

**Files:**
- Verify/adjust: `D:\PROJETO FTC\site\Formulario.dc.html` (comportamentos já codados na Task 2 — esta task valida o fluxo completo de ponta a ponta).

**Interfaces:**
- Consumes: métodos `ouvirTudo`, `pararAudio`, `enviar`, `sair` da Task 2; `enviado.mp3` da Task 1.
- Produces: nada novo (task de verificação integrada).

- [ ] **Step 1: Verificar "Ouvir a página toda" (manual)**

Com o servidor da Task 2 rodando e o Modo Inclusão ligado, clique **▶ Ouvir a página toda**. Esperado: toca `intro`, depois `q1`, `q2`, … `q7` em sequência, sem sobreposição, encadeando sozinho ao fim de cada faixa.

- [ ] **Step 2: Verificar botão "■ Parar" (manual)**

Durante a reprodução, clique **■ Parar**. Esperado: o áudio para imediatamente e o botão Parar some.

- [ ] **Step 3: Verificar "Sair rápido" e Escape param o áudio (manual)**

Inicie "Ouvir a página toda" e, enquanto toca, pressione `Escape` (e, em outro teste, clique "Sair rápido" no topo). Esperado: a navegação sai para a página de disfarce **e** o áudio para na hora (não continua tocando em background). Volte para a página depois.

- [ ] **Step 4: Verificar áudio da confirmação ao enviar (manual)**

Com o Modo Inclusão ligado, marque algumas respostas e clique **"Enviar respostas"**. Esperado: aparece a tela "Obrigado por parar para pensar sobre isso" **e** toca `enviado.mp3` automaticamente. Com o modo desligado, o envio funciona normalmente **sem** tocar áudio.

- [ ] **Step 5: Verificar que o formulário original segue intacto (manual)**

Com o Modo Inclusão **desligado**: marque respostas nos 7 grupos, clique Enviar, confirme a tela de agradecimento. Abra DevTools → Application → Local Storage → confirme a chave `ei-form` com o JSON das respostas. Esperado: comportamento idêntico ao original.

- [ ] **Step 6: Commit (se algum ajuste foi necessário)**

Run (bash):
```bash
cd "/d/PROJETO FTC" && git add -A && git commit -m "test(form): valida fluxo completo do modo inclusão" --allow-empty
```

---

## Task 4: Reempacotar o entregável

**Files:**
- Create: `D:\PROJETO FTC\Site de Prevenção à Violência - acessivel.zip`

**Interfaces:**
- Consumes: `site/` finalizado (com `audio/` e `Formulario.dc.html` modificado).
- Produces: ZIP atualizado para entrega.

- [ ] **Step 1: Gerar o ZIP atualizado a partir da pasta `site/`**

Run (bash):
```bash
cd "/d/PROJETO FTC/site" && rm -f "../Site de Prevenção à Violência - acessivel.zip" && zip -r "../Site de Prevenção à Violência - acessivel.zip" . -x ".git/*"
```
Expected: cria o ZIP na raiz `D:\PROJETO FTC\`.

- [ ] **Step 2: Conferir o conteúdo do ZIP**

Run (bash):
```bash
cd "/d/PROJETO FTC" && unzip -l "Site de Prevenção à Violência - acessivel.zip" | grep -E "audio/|Formulario"
```
Expected: lista `Formulario.dc.html` e os 9 arquivos em `audio/`.

- [ ] **Step 3: Commit final**

Run (bash):
```bash
cd "/d/PROJETO FTC" && git add -A && git commit -m "chore: reempacota site com modo inclusão" --allow-empty
```

---

## Notas para o executor

- Se `py` não funcionar no bash do Windows, tente `python`.
- Se o navegador bloquear algum áudio: confirme que a reprodução partiu de um clique (é o caso em todos os botões). O encadeamento do "Ouvir tudo" é permitido por já haver gesto do usuário.
- Se um MP3 não tocar: verifique no DevTools → Network se `audio/qN.mp3` retornou 200 e se o servidor local está na pasta `site/` (caminhos são relativos a `Formulario.dc.html`).
