import React from "react";
import { StyleSheet, Text, View } from "react-native";
import Button from "../components/Button";

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

export default function SuccessScreen({ navigation, route }) {
  var t = route.params && route.params.triagem ? route.params.triagem : null;

  function voltarHome() {
    navigation.reset({ index: 0, routes: [{ name: "Home" }] });
  }

  if (!t) {
    return (
      <View style={styles.container}>
        <Text style={styles.titulo}>Triagem enviada</Text>
        <Text style={styles.item}>Não foi possível carregar o resumo desta solicitação.</Text>
        <View style={{ height: 24 }} />
        <Button title="VOLTAR PARA HOME" onPress={voltarHome} />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Text style={styles.titulo}>Triagem enviada com sucesso</Text>
      <Text style={styles.item}>
        <Text style={styles.k}>Protocolo: </Text>
        {t.protocolo || "—"}
      </Text>
      <Text style={styles.item}>
        <Text style={styles.k}>Nome: </Text>
        {t.nome || "—"}
      </Text>
      <Text style={styles.item}>
        <Text style={styles.k}>Telefone: </Text>
        {t.telefone || "—"}
      </Text>
      <Text style={styles.item}>
        <Text style={styles.k}>Serviço: </Text>
        {SERVICO_LABEL[t.servico] || t.servico || "—"}
      </Text>
      <Text style={styles.item}>
        <Text style={styles.k}>Período: </Text>
        {PERIODO_LABEL[t.periodo] || t.periodo || "—"}
      </Text>
      <Text style={styles.item}>
        <Text style={styles.k}>Status: </Text>
        {t.status || "Pendente"}
      </Text>
      {t.source === "local" ? (
        <Text style={styles.localInfo}>
          Sem conexão no envio: esta triagem foi salva localmente e será sincronizada quando a API estiver disponível.
        </Text>
      ) : null}

      <View style={{ flex: 1 }} />
      <Button title="IR PARA HOME" onPress={voltarHome} />
    </View>
  );
}

var styles = StyleSheet.create({
  container: { flex: 1, padding: 24, paddingTop: 32, backgroundColor: "#f4f4fb" },
  titulo: { fontSize: 24, fontWeight: "800", color: "#2e7d4a", marginBottom: 18 },
  item: { marginBottom: 10, color: "#222", lineHeight: 22 },
  k: { fontWeight: "700", color: "#353375" },
  localInfo: { marginTop: 6, color: "#8a5a00", fontWeight: "600" },
});
