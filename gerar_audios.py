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
