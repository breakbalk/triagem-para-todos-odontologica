/**
 * Tela inicial depois do login (Sprint 1).
 * Sprint 2: botão "Nova triagem" e lista (igual ao site).
 */
import React, { useState, useCallback } from "react";
import { View, Text, StyleSheet, TouchableOpacity, Alert } from "react-native";
import { useFocusEffect } from "@react-navigation/native";
import Button from "../components/Button";
import * as api from "../services/api";

export default function HomeScreen({ navigation }) {
  var [user, setUser] = useState(null);

  useFocusEffect(
    useCallback(function () {
      var carregar = async function () {
        var r = await api.quemSou();
        if (r.dados.ok && r.dados.user) {
          setUser(r.dados.user);
        } else {
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

  return (
    <View style={styles.container}>
      <Text style={styles.logo}>COE</Text>
      <Text style={styles.bemvindo}>Olá, {user.nome}!</Text>
      <Text style={styles.info}>Sprint 1 concluída: login, cadastro e recuperação de senha funcionando.</Text>
      <Text style={styles.info}>Na Sprint 2 você abre a triagem por aqui.</Text>

      {user.is_admin ? (
        <TouchableOpacity onPress={() => Alert.alert("Admin", "Painel web: /pages/admin.html no navegador.")}>
          <Text style={styles.admin}>Você é administrador</Text>
        </TouchableOpacity>
      ) : null}

      <View style={{ flex: 1 }} />
      <Button title="SAIR" onPress={sair} />
    </View>
  );
}

var styles = StyleSheet.create({
  center: { flex: 1, justifyContent: "center", alignItems: "center" },
  container: { flex: 1, padding: 24, paddingTop: 56, backgroundColor: "#f4f4fb" },
  logo: { fontSize: 32, fontWeight: "800", color: "#353375" },
  bemvindo: { fontSize: 20, marginTop: 12, color: "#222" },
  info: { marginTop: 16, color: "#555", lineHeight: 22 },
  admin: { marginTop: 20, color: "#2e7d4a", fontWeight: "700" },
});
