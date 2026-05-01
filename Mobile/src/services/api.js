/**
 * Chamadas HTTP para o backend COE.
 *
 * O navegador usa cookie de sessão; no celular guardamos o mobile_token
 * (vem no JSON do login/cadastro) e mandamos no header Authorization.
 */
import AsyncStorage from "@react-native-async-storage/async-storage";
import { API_BASE } from "../config";

var CHAVE_TOKEN = "coe_mobile_token";
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
  return await postJSON("/api/triagem", corpo, t);
}

export async function listarMinhasTriagens() {
  var t = await lerToken();
  if (!t) {
    return { okHttp: false, dados: { ok: false, error: "Sessão expirada. Faça login novamente." } };
  }
  return await getJSON("/api/triagem/minhas", t);
}
