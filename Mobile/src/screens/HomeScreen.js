/**
 * Tela inicial depois do login (Sprint 1).
 * Sprint 2: botão "Nova triagem" e lista (igual ao site).
 */
import React, { useState, useCallback } from "react";
import { View, Text, StyleSheet, TouchableOpacity, Alert, ScrollView } from "react-native";
import { useFocusEffect } from "@react-navigation/native";
import Button from "../components/Button";
import * as api from "../services/api";

export default function HomeScreen({ navigation }) {
  var [user, setUser] = useState(null);
  var [triagens, setTriagens] = useState([]);
  var [loadingTriagens, setLoadingTriagens] = useState(true);

  useFocusEffect(
    useCallback(function () {
      var carregar = async function () {
        var r = await api.quemSou();
        if (r.dados.ok && r.dados.user) {
          setUser(r.dados.user);
          setLoadingTriagens(true);
          var tr = await api.listarMinhasTriagens();
          if (tr.okHttp && tr.dados.ok && Array.isArray(tr.dados.triagens)) {
            setTriagens(tr.dados.triagens);
          } else {
            setTriagens([]);
          }
          setLoadingTriagens(false);
        } else {
          await api.apagarToken();
          navigation.reset({ index: 0, routes: [{ name: "Login" }] });
        }
      };
      carregar();
    }, [navigation])
  );

  async function sair() {
    await api.logout();
    navigation.reset({ index: 0, routes: [{ name: "Login" }] });
  }

  if (!user) {
    return (
      <View style={styles.center}>
        <Text>Carregando...</Text>
      </View>
    );
  }

  function nomeServico(s) {
    if (s === "tratamento_geral") return "Tratamento geral";
    if (s === "protese") return "Prótese";
    if (s === "pediatria") return "Pediatria";
    if (s === "emergencia") return "Emergência";
    return s || "—";
  }

  function nomePeriodo(p) {
    if (p === "matutino") return "Matutino";
    if (p === "vespertino") return "Vespertino";
    if (p === "noturno") return "Noturno";
    return p || "—";
  }

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.logo}>COE</Text>
      <Text style={styles.bemvindo}>Olá, {user.nome}!</Text>
      <Text style={styles.info}>Faça uma nova triagem ou acompanhe suas solicitações recentes.</Text>

      <Button title="NOVA TRIAGEM" onPress={function () { navigation.navigate("Triage"); }} />

      <Text style={styles.secao}>Minhas triagens</Text>
      {loadingTriagens ? <Text style={styles.info}>Carregando histórico...</Text> : null}
      {!loadingTriagens && triagens.length === 0 ? (
        <Text style={styles.info}>Você ainda não possui triagens registradas.</Text>
      ) : null}
      {!loadingTriagens &&
        triagens.slice(0, 5).map(function (t, idx) {
          return (
            <View key={(t.protocolo || "triagem") + "-" + idx} style={styles.card}>
              <Text style={styles.cardLine}>
                <Text style={styles.k}>Protocolo:</Text> {t.protocolo || "—"}
              </Text>
              <Text style={styles.cardLine}>
                <Text style={styles.k}>Serviço:</Text> {nomeServico(t.servico)}
              </Text>
              <Text style={styles.cardLine}>
                <Text style={styles.k}>Período:</Text> {nomePeriodo(t.periodo)}
              </Text>
              <Text style={styles.cardLine}>
                <Text style={styles.k}>Status:</Text> {t.status || "Pendente"}
              </Text>
            </View>
          );
        })}

      {user.is_admin ? (
        <TouchableOpacity onPress={() => Alert.alert("Admin", "Painel web: /pages/admin.html no navegador.")}>
          <Text style={styles.admin}>Você é administrador</Text>
        </TouchableOpacity>
      ) : null}

      <View style={{ height: 8 }} />
      <Button title="SAIR" onPress={sair} />
    </ScrollView>
  );
}

var styles = StyleSheet.create({
  center: { flex: 1, justifyContent: "center", alignItems: "center" },
  container: { flexGrow: 1, padding: 24, paddingTop: 56, backgroundColor: "#f4f4fb" },
  logo: { fontSize: 32, fontWeight: "800", color: "#353375" },
  bemvindo: { fontSize: 20, marginTop: 12, color: "#222" },
  info: { marginTop: 12, color: "#555", lineHeight: 22 },
  secao: { marginTop: 18, marginBottom: 8, color: "#353375", fontWeight: "800", fontSize: 16 },
  card: {
    backgroundColor: "#fff",
    borderColor: "#ddd",
    borderWidth: 1,
    borderRadius: 12,
    padding: 12,
    marginBottom: 8,
  },
  cardLine: { color: "#222", marginBottom: 4 },
  k: { fontWeight: "700", color: "#353375" },
  admin: { marginTop: 16, color: "#2e7d4a", fontWeight: "700" },
});
