import React, { useMemo, useState } from "react";
import { Alert, KeyboardAvoidingView, Platform, ScrollView, StyleSheet, Text, TouchableOpacity, View } from "react-native";
import Input from "../components/Input";
import Button from "../components/Button";
import * as api from "../services/api";

var SERVICOS = [
  { value: "tratamento_geral", label: "Tratamento geral" },
  { value: "protese", label: "Prótese" },
  { value: "pediatria", label: "Pediatria" },
  { value: "emergencia", label: "Emergência" },
];

var PERIODOS = [
  { value: "matutino", label: "Matutino" },
  { value: "vespertino", label: "Vespertino" },
  { value: "noturno", label: "Noturno" },
];

var TEL_RE = /^\(\d{2}\) \d{5}-\d{4}$/;

function mascaraTelefone(v) {
  var digitos = (v || "").replace(/\D/g, "").slice(0, 11);
  if (digitos.length <= 2) return digitos;
  var comDdd = "(" + digitos.slice(0, 2) + ") " + digitos.slice(2);
  if (digitos.length <= 7) return comDdd;
  return "(" + digitos.slice(0, 2) + ") " + digitos.slice(2, 7) + "-" + digitos.slice(7);
}

export default function TriageScreen({ navigation }) {
  var [nome, setNome] = useState("");
  var [telefone, setTelefone] = useState("");
  var [servico, setServico] = useState("");
  var [periodo, setPeriodo] = useState("");
  var [sintomas, setSintomas] = useState("");
  var [loading, setLoading] = useState(false);

  var telefoneLimpo = useMemo(function () {
    return (telefone || "").trim();
  }, [telefone]);

  function validar() {
    if (nome.trim().length < 3) return "Informe o nome completo.";
    if (!TEL_RE.test(telefoneLimpo)) return "Telefone inválido. Use o formato (DD) 99999-9999.";
    if (!servico) return "Selecione o tipo de serviço.";
    if (!periodo) return "Selecione o período.";
    return "";
  }

  async function enviar() {
    var erro = validar();
    if (erro) {
      Alert.alert("Triagem", erro);
      return;
    }
    setLoading(true);
    var r = await api.criarTriagem({
      nome: nome.trim(),
      telefone: telefoneLimpo,
      servico: servico,
      periodo: periodo,
      sintomas: sintomas.trim(),
    });
    setLoading(false);

    if (!r.okHttp) {
      Alert.alert("Triagem", r.dados.error ? r.dados.error : "Erro ao enviar triagem.");
      if (r.dados && r.dados.error && r.dados.error.toLowerCase().indexOf("login") >= 0) {
        navigation.reset({ index: 0, routes: [{ name: "Login" }] });
      }
      return;
    }

    if (r.dados && r.dados.source === "local") {
      Alert.alert("Triagem", r.dados.message || "Triagem salva localmente.");
    }
    navigation.replace("Success", { triagem: r.dados.triagem });
  }

  return (
    <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === "ios" ? "padding" : undefined}>
      <ScrollView contentContainerStyle={styles.container} keyboardShouldPersistTaps="handled">
        <Text style={styles.titulo}>Nova triagem</Text>
        <Text style={styles.subtitulo}>Preencha os dados para pré-agendamento.</Text>

        <Input label="Nome completo" value={nome} onChangeText={setNome} autoCapitalize="words" />
        <Input
          label="Telefone"
          value={telefone}
          onChangeText={function (txt) {
            setTelefone(mascaraTelefone(txt));
          }}
          keyboardType="phone-pad"
        />

        <Text style={styles.label}>Serviço</Text>
        <View style={styles.rowWrap}>
          {SERVICOS.map(function (s) {
            var ativo = servico === s.value;
            return (
              <TouchableOpacity key={s.value} onPress={function () { setServico(s.value); }} style={[styles.chip, ativo ? styles.chipOn : null]}>
                <Text style={[styles.chipTxt, ativo ? styles.chipTxtOn : null]}>{s.label}</Text>
              </TouchableOpacity>
            );
          })}
        </View>

        <Text style={styles.label}>Período</Text>
        <View style={styles.rowWrap}>
          {PERIODOS.map(function (p) {
            var ativo = periodo === p.value;
            return (
              <TouchableOpacity key={p.value} onPress={function () { setPeriodo(p.value); }} style={[styles.chip, ativo ? styles.chipOn : null]}>
                <Text style={[styles.chipTxt, ativo ? styles.chipTxtOn : null]}>{p.label}</Text>
              </TouchableOpacity>
            );
          })}
        </View>

        <Input
          label="Sintomas (opcional)"
          value={sintomas}
          onChangeText={setSintomas}
          autoCapitalize="sentences"
        />

        <Button title="ENVIAR TRIAGEM" onPress={enviar} loading={loading} />
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

var styles = StyleSheet.create({
  container: { flexGrow: 1, padding: 24, paddingTop: 24, backgroundColor: "#f4f4fb" },
  titulo: { fontSize: 26, fontWeight: "800", color: "#353375" },
  subtitulo: { color: "#555", marginTop: 6, marginBottom: 18 },
  label: { color: "#353375", fontWeight: "700", marginBottom: 8, marginTop: 8, fontSize: 14 },
  rowWrap: { flexDirection: "row", flexWrap: "wrap", marginBottom: 6 },
  chip: {
    backgroundColor: "#fff",
    borderWidth: 1,
    borderColor: "#ccc",
    borderRadius: 999,
    paddingVertical: 10,
    paddingHorizontal: 14,
    marginRight: 8,
    marginBottom: 8,
  },
  chipOn: { backgroundColor: "#353375", borderColor: "#353375" },
  chipTxt: { color: "#333", fontWeight: "600" },
  chipTxtOn: { color: "#F4E7BB" },
});
