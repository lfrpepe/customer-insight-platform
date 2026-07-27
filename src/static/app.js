/**
 * Utilitários compartilhados pelas telas de captura (Fase 5).
 */

/**
 * Mostra um toast fixo no topo da tela, que aparece e some sozinho.
 * Reinicia a animação a cada chamada — mesmo em envios seguidos rápidos
 * (ex.: Pinpad/Totem usados em sequência), cada envio gera seu próprio
 * toast visível, em vez de uma mensagem inline fácil de não notar.
 */
function mostrarToast(mensagem, tipo) {
  let toast = document.getElementById("toast");
  if (!toast) {
    toast = document.createElement("div");
    toast.id = "toast";
    document.body.appendChild(toast);
  }

  toast.textContent = mensagem;
  toast.className = "toast " + tipo;

  // Força reflow para garantir que a transição rode de novo mesmo se o
  // toast já estava com a classe "mostrar" de uma chamada anterior.
  void toast.offsetWidth;
  toast.classList.add("mostrar");

  clearTimeout(toast._timeoutId);
  toast._timeoutId = setTimeout(() => {
    toast.classList.remove("mostrar");
  }, 2500);
}

/**
 * Configura um picker de 1 a 5 estrelas dentro do elemento com o id
 * informado. Hover ilumina até a estrela sobrevoada; clique fixa a
 * seleção e dispara a animação de "pop".
 *
 * Uso:
 *   const estrelas = configurarEstrelas("nota-picker");
 *   estrelas.valor       // nota atual (0 = nenhuma selecionada)
 *   estrelas.reset()     // limpa a seleção (após envio com sucesso)
 */
function configurarEstrelas(containerId) {
  const container = document.getElementById(containerId);
  const botoes = Array.from(container.querySelectorAll("button"));
  let selecionada = 0;

  function pintar(ateIndice) {
    botoes.forEach((btn, i) => {
      btn.classList.toggle("ativa", i < ateIndice);
    });
  }

  botoes.forEach((btn, i) => {
    btn.addEventListener("mouseenter", () => pintar(i + 1));
    btn.addEventListener("mouseleave", () => pintar(selecionada));
    btn.addEventListener("click", () => {
      selecionada = i + 1;
      pintar(selecionada);
      btn.classList.remove("selecionada");
      void btn.offsetWidth;
      btn.classList.add("selecionada");
    });
  });

  return {
    get valor() {
      return selecionada;
    },
    reset() {
      selecionada = 0;
      pintar(0);
    },
  };
}
