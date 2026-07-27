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
 * Aplica máscara visual "(DDD) NNNNN-NNNN" enquanto o usuário digita.
 * É só formatação de exibição — o backend recebe o valor e normaliza para
 * somente dígitos de qualquer forma (ver validators/cliente.py), então
 * não há necessidade de "desfazer" a máscara antes de enviar.
 */
function aplicarMascaraTelefone(inputId) {
  const input = document.getElementById(inputId);
  input.addEventListener("input", () => {
    const digitos = input.value.replace(/\D/g, "").slice(0, 11);
    let formatado = digitos;

    if (digitos.length > 2 && digitos.length <= 7) {
      formatado = `(${digitos.slice(0, 2)}) ${digitos.slice(2)}`;
    } else if (digitos.length > 7) {
      formatado = `(${digitos.slice(0, 2)}) ${digitos.slice(2, 7)}-${digitos.slice(7)}`;
    }

    input.value = formatado;
  });
}

function aplicarMascaraCPF(inputId) {
  const input = document.getElementById(inputId);
  input.addEventListener("input", () => {
    const digitos = input.value.replace(/\D/g, "").slice(0, 11);
    let formatado = digitos;

    if (digitos.length > 3) {
      formatado = `${digitos.slice(0, 3)}.${digitos.slice(3)}`;
    }
    if (digitos.length > 6) {
      formatado = `${digitos.slice(0, 3)}.${digitos.slice(3, 6)}.${digitos.slice(6)}`;
    }
    if (digitos.length > 9) {
      formatado = `${digitos.slice(0, 3)}.${digitos.slice(3, 6)}.${digitos.slice(6, 9)}-${digitos.slice(9)}`;
    }

    input.value = formatado;
  });
}

function extrairMensagemErro(detalhe) {
  if (typeof detalhe === "string") {
    return detalhe;
  }
  if (Array.isArray(detalhe)) {
    return detalhe.map((item) => item.msg).join(" ");
  }
  return "Não foi possível processar a solicitação.";
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
