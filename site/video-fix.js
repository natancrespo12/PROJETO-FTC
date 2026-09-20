/*
 * Correção do player de vídeo da campanha.
 *
 * O support.js re-renderiza o DOM (templates data-dc-tpl) e nesse processo
 * remove o atributo `controls` do <video> e todos os handlers inline
 * (onclick/onplay). Por isso o vídeo parecia uma imagem e o clique no botão
 * não fazia nada.
 *
 * Este script roda de forma independente e resistente à re-renderização:
 *  1) Reativa os controles nativos do vídeo (e mantém reativados).
 *  2) Dispara o play via delegação de evento no document (captura), que
 *     sobrevive à recriação do botão e não depende de handlers inline.
 */
(function () {
  "use strict";
  var VIDEO_SEL = 'video[src*="15.14.10"]';

  function getVideo() {
    return document.querySelector(VIDEO_SEL);
  }

  function ensureControls() {
    var v = getVideo();
    if (v && !v.controls) v.controls = true;
  }

  // Reativa os controles agora e continua garantindo por ~12s (cobre a
  // hidratação tardia do support.js), depois para para não ficar em loop.
  ensureControls();
  document.addEventListener("DOMContentLoaded", ensureControls);
  window.addEventListener("load", ensureControls);
  var tries = 0;
  var iv = setInterval(function () {
    ensureControls();
    if (++tries > 48) clearInterval(iv);
  }, 250);

  // Play por delegação no document (fase de captura) — funciona mesmo que o
  // botão seja recriado e mesmo sem onclick inline.
  document.addEventListener(
    "click",
    function (e) {
      var btn = e.target && e.target.closest ? e.target.closest(".play-overlay") : null;
      if (!btn) return;
      var v = getVideo();
      if (!v) return;
      v.controls = true;
      var hide = function () {
        btn.style.opacity = "0";
        btn.style.pointerEvents = "none";
      };
      var p = v.play();
      if (p && typeof p.then === "function") {
        p.then(hide).catch(function () {
          /* se o navegador bloquear, os controles nativos assumem */
        });
      } else {
        hide();
      }
    },
    true
  );

  // Reesconde o overlay caso o vídeo comece a tocar por outro caminho.
  document.addEventListener(
    "play",
    function (e) {
      if (e.target && e.target.matches && e.target.matches(VIDEO_SEL)) {
        var btn = document.querySelector(".play-overlay");
        if (btn) {
          btn.style.opacity = "0";
          btn.style.pointerEvents = "none";
        }
      }
    },
    true
  );
})();
