/**
 * Chamadas HTTP para o backend COE.
 *
 * O navegador usa cookie de sessão; no celular guardamos o mobile_token
 * (vem no JSON do login/cadastro) e mandamos no header Authorization.
 */
import AsyncStorage from "@react-native-async-storage/async-storage";
import { API_BASE } from "../config";

var CHAVE_TOKEN = "coe_mobile_token";
var CHAVE_CACHE_TRIAGENS = "coe_triagens_cache";
var CHAVE_FILA_TRIAGENS = "coe_triagens_pendentes";
var TIMEOUT_MS = 15000;

function fetchComTimeout(url, opcoes) {
  var ctrl = new AbortController();
  var id = setTimeout(function () {
    ctrl.abort();
  }, TIMEOUT_MS);
  var mesclado = opcoes || {};
  mesclado.signal = ctrl.signal;
  return fetch(url, mesclado).finally(function () {
    clearTimeout(id);
  });
}

export async function salvarToken(token) {
  await AsyncStorage.setItem(CHAVE_TOKEN, token);
}

export async function lerToken() {
  return await AsyncStorage.getItem(CHAVE_TOKEN);
}

export async function apagarToken() {
  await AsyncStorage.removeItem(CHAVE_TOKEN);
}

async function salvarJSON(chave, valor) {
  await AsyncStorage.setItem(chave, JSON.stringify(valor));
}

async function lerJSON(chave, padrao) {
  try {
    var raw = await AsyncStorage.getItem(chave);
    if (!raw) return padrao;
    return JSON.parse(raw);
  } catch (_e) {
    return padrao;
  }
}

/** POST JSON. Se mandar token, o servidor sabe quem é o usuário. */
export async function postJSON(caminho, corpo, token) {
  try {
    var headers = { "Content-Type": "application/json" };
    if (token) headers["Authorization"] = "Bearer " + token;

    var res = await fetchComTimeout(API_BASE + caminho, {
      method: "POST",
      headers: headers,
      body: JSON.stringify(corpo),
    });
    var dados = await res.json();
    return { okHttp: res.ok, dados: dados };
  } catch (e) {
    return { okHttp: false, dados: { error: "Sem conexão com o servidor. Veja se o Flask está rodando no PC." } };
  }
}

/** GET JSON */
export async function getJSON(caminho, token) {
  try {
    var headers = {};
    if (token) headers["Authorization"] = "Bearer " + token;

    var res = await fetchComTimeout(API_BASE + caminho, {
      method: "GET",
      headers: headers,
    });
    var dados = await res.json();
    return { okHttp: res.ok, dados: dados };
  } catch (e) {
    return { okHttp: false, dados: { ok: false, user: null } };
  }
}

/** Login: grava token automaticamente se vier na resposta */
export async function login(email, senha) {
  var r = await postJSON("/api/auth/login", { email: email, senha: senha }, null);
  if (r.okHttp && r.dados.mobile_token) {
    await salvarToken(r.dados.mobile_token);
  }
  return r;
}

export async function cadastro(nome, email, senha, telefone) {
  var r = await postJSON(
    "/api/auth/register",
    { nome: nome, email: email, senha: senha, telefone: telefone || "" },
    null
  );
  if (r.okHttp && r.dados.mobile_token) {
    await salvarToken(r.dados.mobile_token);
  }
  return r;
}

export async function logout() {
  var t = await lerToken();
  if (t) {
    await postJSON("/api/auth/logout", {}, t);
  }
  await apagarToken();
}

export async function esqueciSenha(email) {
  return await postJSON("/api/auth/forgot-password", { email: email }, null);
}

export async function redefinirSenha(email, token, novaSenha) {
  return await postJSON(
    "/api/auth/reset-password",
    { email: email, token: token, nova_senha: novaSenha },
    null
  );
}

export async function quemSou() {
  var t = await lerToken();
  if (!t) return { okHttp: true, dados: { ok: false, user: null } };
  return await getJSON("/api/auth/me", t);
}

export async function criarTriagem(corpo) {
  var t = await lerToken();
  if (!t) {
    return { okHttp: false, dados: { ok: false, error: "Sessão expirada. Faça login novamente." } };
  }

  var r = await postJSON("/api/triagem", corpo, t);
  if (r.okHttp && r.dados && r.dados.ok && r.dados.triagem) {
    var triagemServidor = Object.assign({ source: "server" }, r.dados.triagem);
    await salvarTriagemNoCache(triagemServidor);
    return {
      okHttp: true,
      dados: {
        ok: true,
        triagem: triagemServidor,
        source: "server",
      },
    };
  }

  // Fallback Sprint 3: se não subir para API, salva local como pendente.
  var local = await enfileirarTriagemPendente(corpo);
  return {
    okHttp: true,
    dados: {
      ok: true,
      triagem: local,
      source: "local",
      message: "Sem conexão. Triagem salva no aparelho e será reenviada automaticamente.",
    },
  };
}

export async function listarMinhasTriagens() {
  var t = await lerToken();
  if (!t) {
    return { okHttp: false, dados: { ok: false, error: "Sessão expirada. Faça login novamente." } };
  }
  var r = await getJSON("/api/triagem/minhas", t);
  if (r.okHttp && r.dados && r.dados.ok && Array.isArray(r.dados.triagens)) {
    var triagensServidor = r.dados.triagens.map(function (item) {
      return Object.assign({ source: "server" }, item);
    });
    await salvarJSON(CHAVE_CACHE_TRIAGENS, triagensServidor);
    return {
      okHttp: true,
      dados: {
        ok: true,
        triagens: triagensServidor,
        source: "server",
      },
    };
  }
  var cache = await lerJSON(CHAVE_CACHE_TRIAGENS, []);
  return {
    okHttp: true,
    dados: {
      ok: true,
      triagens: cache,
      source: "local",
      message: "Mostrando dados locais (sem conexão com servidor).",
    },
  };
}

function protocoloLocal() {
  var d = new Date();
  var p2 = function (n) {
    return n < 10 ? "0" + n : "" + n;
  };
  var base =
    d.getFullYear() +
    p2(d.getMonth() + 1) +
    p2(d.getDate()) +
    p2(d.getHours()) +
    p2(d.getMinutes()) +
    p2(d.getSeconds());
  return "LOCAL-" + base;
}

async function salvarTriagemNoCache(triagem) {
  var lista = await lerJSON(CHAVE_CACHE_TRIAGENS, []);
  var nova = [triagem].concat(lista);
  await salvarJSON(CHAVE_CACHE_TRIAGENS, nova);
}

async function enfileirarTriagemPendente(corpo) {
  var agora = new Date().toISOString();
  var triagemLocal = {
    protocolo: protocoloLocal(),
    nome: corpo.nome || "",
    telefone: corpo.telefone || "",
    servico: corpo.servico || "",
    periodo: corpo.periodo || "",
    sintomas: corpo.sintomas || "",
    status: "Pendente (local)",
    data_solicitacao: agora,
    source: "local",
  };
  var fila = await lerJSON(CHAVE_FILA_TRIAGENS, []);
  fila.push(corpo);
  await salvarJSON(CHAVE_FILA_TRIAGENS, fila);
  await salvarTriagemNoCache(triagemLocal);
  return triagemLocal;
}

export async function sincronizarTriagensPendentes() {
  var t = await lerToken();
  if (!t) {
    return { ok: false, enviados: 0, pendentes: 0 };
  }
  var fila = await lerJSON(CHAVE_FILA_TRIAGENS, []);
  if (!fila.length) {
    return { ok: true, enviados: 0, pendentes: 0 };
  }

  var restantes = [];
  var enviados = 0;
  for (var i = 0; i < fila.length; i++) {
    var corpo = fila[i];
    var r = await postJSON("/api/triagem", corpo, t);
    if (r.okHttp && r.dados && r.dados.ok && r.dados.triagem) {
      enviados += 1;
      await salvarTriagemNoCache(Object.assign({ source: "server" }, r.dados.triagem));
    } else {
      restantes.push(corpo);
    }
  }
  await salvarJSON(CHAVE_FILA_TRIAGENS, restantes);
  return { ok: true, enviados: enviados, pendentes: restantes.length };
}
