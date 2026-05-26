/**
 * web-app.js — JavaScript das páginas do COE.
 *
 * Ideia geral:
 * - Cada HTML tem <body data-page="login"> (ou cadastro, home, etc.).
 * - Quando a página carrega, o script olha data-page e roda só o que precisa.
 *
 * Como fala com o Python:
 * - Usamos fetch() para mandar JSON para /api/...
 * - credentials: "include" manda o cookie de sessão (quem está logado).
 */

// Nomes bonitos para mostrar na tela (o servidor usa os códigos da esquerda)
var SERVICO_LABEL = {
  tratamento_geral: "Tratamento geral",
  protese: "Prótese",
  pediatria: "Pediatria",
  emergencia: "Emergência",
};

var PERIODO_LABEL = {
  matutino: "Matutino",
  vespertino: "Vespertino",
  noturno: "Noturno",
};

/** Chaves legadas no localStorage (Sprint 4 — limpeza no logout). */
var CHAVES_STORAGE_LEGADAS = ["usuario_logado", "nivel_acesso", "coe_user", "token"];

function escapeHtml(texto) {
  return String(texto || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

/** Remove dados temporários do navegador (sessão da triagem + legado). */
function limparDadosLocais() {
  try {
    sessionStorage.removeItem("coe_last_triagem");
  } catch (_e) {
    /* ignore */
  }
  for (var i = 0; i < CHAVES_STORAGE_LEGADAS.length; i++) {
    try {
      localStorage.removeItem(CHAVES_STORAGE_LEGADAS[i]);
    } catch (_e2) {
      /* ignore */
    }
  }
}

/** RF logout: encerra sessão no servidor e limpa armazenamento local. */
async function fazerLogout() {
  try {
    await postJSON("/api/auth/logout", {});
  } catch (_e) {
    /* mesmo offline, limpa o cliente */
  }
  limparDadosLocais();
  window.location.href = "/pages/login.html";
}

function iniciarBotoesLogout() {
  var botoes = document.querySelectorAll('[data-action="logout"], .btn-exit');
  for (var i = 0; i < botoes.length; i++) {
    botoes[i].addEventListener("click", function (ev) {
      ev.preventDefault();
      if (window.confirm("Deseja sair e encerrar sua sessão com segurança?")) {
        fazerLogout();
      }
    });
  }
}

/**
 * POST com JSON. Devolve { okHttp, dados } onde okHttp é true se status 200-299.
 */
async function postJSON(url, corpo) {
  var resposta = await fetch(url, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(corpo),
  });
  var dados = await resposta.json();
  return { okHttp: resposta.ok, status: resposta.status, dados: dados };
}

/** GET simples (ex.: /api/auth/me) */
async function getJSON(url) {
  var resposta = await fetch(url, { credentials: "include" });
  var dados = await resposta.json();
  return { okHttp: resposta.ok, dados: dados };
}

function mostrarErro(texto, idElemento) {
  idElemento = idElemento || "msg";
  var el = document.getElementById(idElemento);
  if (el) {
    el.textContent = texto;
    el.hidden = false;
    el.classList.remove("msg-success");
    el.classList.add("msg-error");
  } else {
    alert(texto);
  }
}

function mostrarOk(texto, idElemento) {
  idElemento = idElemento || "msg";
  var el = document.getElementById(idElemento);
  if (el) {
    el.textContent = texto;
    el.hidden = false;
    el.classList.remove("msg-error");
    el.classList.add("msg-success");
  } else {
    alert(texto);
  }
}

function esconderMsg(idElemento) {
  idElemento = idElemento || "msg";
  var el = document.getElementById(idElemento);
  if (el) {
    el.hidden = true;
    el.textContent = "";
  }
}

// --- LOGIN (RF02) ---

function iniciarLogin() {
  var form = document.getElementById("form-login");
  if (!form) return;

  form.addEventListener("submit", async function (ev) {
    ev.preventDefault();
    esconderMsg();

    var email = document.getElementById("email").value.trim();
    var senha = document.getElementById("senha").value;
    var botao = form.querySelector(".btn-primary");
    if (botao) {
      botao.disabled = true;
      botao.textContent = "CARREGANDO...";
    }

    var r = await postJSON("/api/auth/login", { email: email, senha: senha });

    if (botao) {
      botao.disabled = false;
      botao.textContent = "LOGIN";
    }

    if (!r.okHttp) {
      var msg = r.dados.error ? r.dados.error : "Não foi possível entrar.";
      mostrarErro(msg);
      return;
    }

    var destino = r.dados.redirect_to || "/pages/home.html";
    window.location.href = destino;
  });
}

// --- CADASTRO (RF01) ---

function iniciarCadastro() {
  var form = document.getElementById("form-cadastro");
  if (!form) return;

  form.addEventListener("submit", async function (ev) {
    ev.preventDefault();
    esconderMsg();

    var nome = document.getElementById("username").value.trim();
    var email = document.getElementById("email").value.trim();
    var senha = document.getElementById("senha").value;
    var confirmar = document.getElementById("confirmar_senha").value;
    var telEl = document.getElementById("telefone");
    var telefone = telEl ? telEl.value.trim() : "";

    if (nome.length < 3) {
      mostrarErro("O nome deve ter pelo menos 3 caracteres.");
      return;
    }
    if (senha !== confirmar) {
      mostrarErro("As senhas não coincidem.");
      return;
    }
    if (senha.length < 6) {
      mostrarErro("A senha deve ter no mínimo 6 caracteres.");
      return;
    }

    var botao = form.querySelector(".btn-primary");
    if (botao) botao.disabled = true;

    var r = await postJSON("/api/auth/register", {
      nome: nome,
      email: email,
      senha: senha,
      telefone: telefone,
    });

    if (botao) botao.disabled = false;

    if (!r.okHttp) {
      var msg = r.dados.error ? r.dados.error : "Erro no cadastro.";
      mostrarErro(msg);
      return;
    }

    var destino = r.dados.redirect_to || "/pages/home.html";
    window.location.href = destino;
  });
}

// --- RECUPERAR SENHA (RF03) ---

function iniciarRecuperar() {
  var formEmail = document.getElementById("form-recover-email");
  var formReset = document.getElementById("form-recover-reset");
  var passo1 = document.getElementById("recover-step1");
  var passo2 = document.getElementById("recover-step2");

  if (formEmail) {
    formEmail.addEventListener("submit", async function (ev) {
      ev.preventDefault();
      esconderMsg("msg-recover");
      var email = document.getElementById("recover-email").value.trim();
      var r = await postJSON("/api/auth/forgot-password", { email: email });

      if (!r.okHttp) {
        mostrarErro(r.dados.error || "Erro.", "msg-recover");
        return;
      }

      mostrarOk(r.dados.message || "Ok.", "msg-recover");

      if (r.dados.demo_token && document.getElementById("recover-token")) {
        document.getElementById("recover-token").value = r.dados.demo_token;
        document.getElementById("recover-email-hidden").value = email;
        passo1.hidden = true;
        passo2.hidden = false;
      }
    });
  }

  if (formReset) {
    formReset.addEventListener("submit", async function (ev) {
      ev.preventDefault();
      esconderMsg("msg-recover");
      var email = document.getElementById("recover-email-hidden").value.trim();
      var token = document.getElementById("recover-token").value.trim();
      var nova = document.getElementById("recover-nova-senha").value;

      var r = await postJSON("/api/auth/reset-password", {
        email: email,
        token: token,
        nova_senha: nova,
      });

      if (!r.okHttp) {
        mostrarErro(r.dados.error || "Erro.", "msg-recover");
        return;
      }

      mostrarOk("Senha alterada. Indo para o login...", "msg-recover");
      setTimeout(function () {
        window.location.href = "/pages/login.html";
      }, 1200);
    });
  }
}

/** Se não estiver logado, manda para o login. Senão devolve o objeto user. */
async function precisaEstarLogado() {
  var r = await getJSON("/api/auth/me");
  if (!r.dados.ok || !r.dados.user) {
    window.location.href = "/pages/login.html";
    return null;
  }
  return r.dados.user;
}

// --- HOME ---

async function iniciarHome() {
  var user = await precisaEstarLogado();
  if (!user) return;

  var elNome = document.getElementById("home-nome");
  if (elNome) {
    var nomeExibir = (user.nome || "visitante").trim().split(" ")[0];
    elNome.textContent = nomeExibir;
  }

  var linkAdmin = document.getElementById("link-admin");
  if (linkAdmin) {
    var adminLike = user.is_admin || user.nivel_acesso === "admin" || user.nivel_acesso === "secretaria";
    linkAdmin.style.display = adminLike ? "inline-block" : "none";
  }

  var r = await getJSON("/api/triagem/minhas");
  if (!r.okHttp) {
    mostrarErro("Não foi possível carregar suas triagens.");
    return;
  }

  var ul = document.getElementById("lista-triagens");
  if (!ul) return;
  ul.innerHTML = "";

  var lista = r.dados.triagens;
  if (!lista || lista.length === 0) {
    ul.innerHTML =
      '<li class="empty-hint">Você ainda não enviou triagens. Clique em «Nova triagem».</li>';
    return;
  }

  for (var i = 0; i < lista.length; i++) {
    var t = lista[i];
    var li = document.createElement("li");
    var nomeServico = SERVICO_LABEL[t.servico] ? SERVICO_LABEL[t.servico] : t.servico;
    var nomePeriodo = PERIODO_LABEL[t.periodo] ? PERIODO_LABEL[t.periodo] : t.periodo;
    li.innerHTML =
      "<strong>" +
      escapeHtml(t.protocolo) +
      "</strong> — " +
      escapeHtml(nomeServico) +
      " — " +
      escapeHtml(nomePeriodo) +
      ' — <span class="triagem-status">' +
      escapeHtml(t.status) +
      "</span>";
    ul.appendChild(li);
  }
}

// --- TRIAGEM ---

async function iniciarTriagem() {
  // RN09: máscara de telefone para manter consistência visual no front.
  var campoTel = document.getElementById("triagem-telefone");
  if (campoTel) {
    campoTel.addEventListener("input", function () {
      mascaraTelefone(this);
    });
  }
  var user = await precisaEstarLogado();
  if (!user) return;

  var form = document.getElementById("form-triagem");
  if (!form) return;

  form.addEventListener("submit", async function (ev) {
    ev.preventDefault();
    esconderMsg();
    var telValue = document.getElementById("triagem-telefone").value;
    // RN09: validação severa no front (backend também valida).
    if (telValue.length < 15) {
      alert("Por favor, informe o telefone completo no formato (DD) 99999-9999");
      return;
    }

    var periodoRadio = document.querySelector('input[name="periodo"]:checked');
    var periodo = periodoRadio ? periodoRadio.value : "";

    var corpo = {
      nome: document.getElementById("triagem-nome").value.trim(),
      telefone: document.getElementById("triagem-telefone").value.trim(),
      servico: document.getElementById("triagem-servico").value,
      periodo: periodo,
      sintomas: "",
    };

    var ta = document.getElementById("triagem-sintomas");
    if (ta) corpo.sintomas = ta.value.trim();

    if (!periodo) {
      mostrarErro("Selecione o período de preferência.");
      return;
    }

    var botao = form.querySelector(".btn-primary");
    if (botao) botao.disabled = true;

    var r = await postJSON("/api/triagem", corpo);

    if (botao) botao.disabled = false;

    if (!r.okHttp) {
      mostrarErro(r.dados.error || "Erro ao enviar.");
      return;
    }

    sessionStorage.setItem("coe_last_triagem", JSON.stringify(r.dados.triagem));
    window.location.href = "/pages/confirmacao.html";
  });
}

// --- CONFIRMAÇÃO ---

async function iniciarConfirmacao() {
  var user = await precisaEstarLogado();
  if (!user) return;

  var box = document.getElementById("resumo-triagem");
  var destaque = document.getElementById("resumo-destaque");
  var elServico = document.getElementById("resumo-servico");
  var elPeriodo = document.getElementById("resumo-periodo");
  var raw = sessionStorage.getItem("coe_last_triagem");

  if (!box) return;

  if (!raw) {
    if (destaque) destaque.hidden = true;
    box.textContent =
      "Nenhum dado recente. Faça uma nova triagem ou veja o histórico na página inicial.";
    return;
  }

  var t;
  try {
    t = JSON.parse(raw);
  } catch (_err) {
    if (destaque) destaque.hidden = true;
    box.textContent = "Não foi possível ler os dados da triagem. Envie uma nova solicitação.";
    return;
  }
  var dataFmt = "—";
  if (t.data_solicitacao) {
    dataFmt = new Date(t.data_solicitacao).toLocaleString("pt-BR");
  }

  var nomeServico = SERVICO_LABEL[t.servico] ? SERVICO_LABEL[t.servico] : t.servico;
  var nomePeriodo = PERIODO_LABEL[t.periodo] ? PERIODO_LABEL[t.periodo] : t.periodo;

  /* RN15: destaque dinâmico da especialidade e do turno escolhidos */
  if (destaque && elServico && elPeriodo) {
    destaque.hidden = false;
    elServico.textContent = nomeServico;
    elPeriodo.textContent = "Turno preferido: " + nomePeriodo;
  }

  var html = "";
  html += "<p><strong>Protocolo:</strong> " + escapeHtml(t.protocolo) + "</p>";
  html += "<p><strong>Nome:</strong> " + escapeHtml(t.nome) + "</p>";
  html += "<p><strong>Telefone:</strong> " + escapeHtml(t.telefone) + "</p>";
  html += "<p><strong>Serviço confirmado:</strong> " + escapeHtml(nomeServico) + "</p>";
  html += "<p><strong>Período confirmado:</strong> " + escapeHtml(nomePeriodo) + "</p>";
  html += "<p><strong>Data da solicitação:</strong> " + escapeHtml(dataFmt) + "</p>";
  html += "<p><strong>Status:</strong> " + escapeHtml(t.status) + "</p>";
  if (t.sintomas) {
    html += "<p><strong>Observações:</strong> " + escapeHtml(t.sintomas) + "</p>";
  }
  html +=
    '<p class="resumo-nota">O horário definitivo será definido pela equipe da clínica após análise da triagem.</p>';
  box.innerHTML = html;
}

// --- ADMIN ---

async function iniciarAdmin() {
  var user = await precisaEstarLogado();
  if (!user) return;

  var adminLike = user.is_admin || user.nivel_acesso === "admin" || user.nivel_acesso === "secretaria";
  if (!adminLike) {
    mostrarErro("Acesso restrito.");
    setTimeout(function () {
      window.location.href = "/pages/home.html";
    }, 1200);
    return;
  }

  var r = await getJSON("/api/triagem/admin/todas");
  if (!r.okHttp) {
    mostrarErro(r.dados.error || "Erro.");
    return;
  }

  var tbody = document.querySelector("#admin-table tbody");
  if (!tbody) return;
  tbody.innerHTML = "";

  var lista = r.dados.triagens;
  for (var i = 0; i < lista.length; i++) {
    var t = lista[i];
    var tr = document.createElement("tr");
    var nomeServico = SERVICO_LABEL[t.servico] ? SERVICO_LABEL[t.servico] : t.servico;
    var nomePeriodo = PERIODO_LABEL[t.periodo] ? PERIODO_LABEL[t.periodo] : t.periodo;
    var dataStr = "";
    if (t.data_solicitacao) {
      dataStr = new Date(t.data_solicitacao).toLocaleString("pt-BR");
    }
    tr.innerHTML =
      "<td>" +
      escapeHtml(t.protocolo) +
      "</td><td>" +
      escapeHtml(t.user_id) +
      "</td><td>" +
      escapeHtml(t.nome) +
      "</td><td>" +
      escapeHtml(t.telefone) +
      "</td><td>" +
      escapeHtml(nomeServico) +
      "</td><td>" +
      escapeHtml(nomePeriodo) +
      "</td><td>" +
      formatarStatus(t.status, t.protocolo) +
      "</td><td>" +
      escapeHtml(dataStr) +
      "</td>";
    tbody.appendChild(tr);
  }
}

function iniciarModalDocumentos() {
  var btnDocumentos = document.querySelector(".menu-docs");
  var modal = document.getElementById("modal-documentos");
  var btnFechar = modal ? modal.querySelector(".modal-close-btn") : null;

  if (!btnDocumentos || !modal) return;

  btnDocumentos.addEventListener("click", function (e) {
    e.preventDefault();
    modal.classList.add("active");
  });

  if (btnFechar) {
    btnFechar.addEventListener("click", function () {
      modal.classList.remove("active");
    });
  }

  modal.addEventListener("click", function (e) {
    if (e.target === modal) {
      modal.classList.remove("active");
    }
  });
}

/** Ponto de entrada: roda depois que o HTML carregou. */
function iniciar() {
  iniciarBotoesLogout();
  iniciarModalDocumentos();

  var page = document.body.getAttribute("data-page");

  if (page === "login") iniciarLogin();
  else if (page === "cadastro") iniciarCadastro();
  else if (page === "recover") iniciarRecuperar();
  else if (page === "home") iniciarHome();
  else if (page === "triagem") iniciarTriagem();
  else if (page === "confirmacao") iniciarConfirmacao();
  else if (page === "admin") iniciarAdmin();
}

document.addEventListener("DOMContentLoaded", iniciar);

/**
 * Aplica a máscara (00) 00000-0000 no input de telefone
 */
function mascaraTelefone(input) {
  var v = input.value.replace(/\D/g, ""); // Remove tudo que não é dígito
  if (v.length > 11) v = v.slice(0, 11); // Limita a 11 dígitos (DD + 9 números)

  if (v.length > 2) {
    v = "(" + v.substring(0, 2) + ") " + v.substring(2);
  }
  if (v.length > 10) {
    v = v.substring(0, 10) + "-" + v.substring(10);
  }
  input.value = v;
}

// Filtro Global: Fica fora de qualquer função para não dar erro de chaves
document.addEventListener("keyup", (event) => {
    if (event.target.id === "admin-search") {
        const termo = event.target.value.toLowerCase();
        const linhas = document.querySelectorAll("#admin-table tbody tr");

        linhas.forEach(linha => {
            const celulas = Array.from(linha.querySelectorAll("td"));
            
            // Pegamos o texto de todas as células, mas tratamos a do Status (índice 6) diferente
            const textoBusca = celulas.map((td, index) => {
                if (index === 6) { // Coluna do Status
                    const select = td.querySelector("select");
                    return select ? select.options[select.selectedIndex].text : "";
                }
                return td.innerText;
            }).join(" ").toLowerCase();

            linha.style.display = textoBusca.includes(termo) ? "" : "none";
        });
    }
});

function formatarStatus(status, protocolo) {
    const opcoes = ["Pendente", "Em Atendimento", "Finalizado", "Cancelado"];
    var protoAttr = String(protocolo || "").replace(/'/g, "\\'");

    let html = `<select class="status-select" onchange="atualizarStatusBanco('${protoAttr}', this.value)">`;
    
    opcoes.forEach(opcao => {
        const selected = status === opcao ? "selected" : "";
        html += `<option value="${opcao}" ${selected}>${opcao}</option>`;
    });
    
    html += `</select>`;
    return html;
}

async function atualizarStatusBanco(protocolo, novoStatus) {
    try {
        var r = await postJSON("/atualizar_status", {
          protocolo: protocolo,
          status: novoStatus
        });
        if (!r.okHttp) {
          throw new Error(r.dados.error || "Erro no servidor");
        }
    } catch (error) {
        console.error("Falha na comunicação:", error);
        alert("Não foi possível salvar o status. " + (error && error.message ? error.message : ""));
    }
}