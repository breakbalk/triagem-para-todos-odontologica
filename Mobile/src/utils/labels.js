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

export function nomeServico(s) {
  return SERVICO_LABEL[s] || s || "—";
}

export function nomePeriodo(p) {
  return PERIODO_LABEL[p] || p || "—";
}

/** Estilo do badge de status no card da Home. */
export function statusTriagem(status) {
  var s = (status || "Pendente").toLowerCase();
  if (s.indexOf("local") >= 0) {
    return { label: status || "Pendente (local)", tone: "warning" };
  }
  if (s.indexOf("aprov") >= 0 || s.indexOf("conclu") >= 0) {
    return { label: status, tone: "success" };
  }
  if (s.indexOf("cancel") >= 0 || s.indexOf("recus") >= 0) {
    return { label: status, tone: "error" };
  }
  return { label: status || "Pendente", tone: "info" };
}
