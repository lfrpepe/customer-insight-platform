function reagir(botao) {
  var span = botao.querySelector('.contagem');
  var ativo = botao.classList.toggle('ativo');
  var atual = parseInt(span.textContent, 10);
  span.textContent = ativo ? atual + 1 : atual - 1;
}
