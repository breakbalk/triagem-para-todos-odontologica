/**
 * RF02 — Login com e-mail e senha (Sprint 1).
 * Se der certo, o token é salvo e vamos para a Home.
 */
import React, { useState } from "react";
import { View, Text, StyleSheet, TouchableOpacity, Alert, ScrollView, KeyboardAvoidingView, Platform } from "react-native";
import Input from "../components/Input";
import Button from "../components/Button";
import * as api from "../services/api";

export default function LoginScreen({ navigation }) {
  var [email, setEmail] = useState("");
  var [senha, setSenha] = useState("");
  var [loading, setLoading] = useState(false);

  async function entrar() {
    setLoading(true);
    var r = await api.login(email.trim(), senha);
    setLoading(false);

    if (!r.okHttp) {
      var msg = r.dados.error ? r.dados.error : "Erro ao entrar.";
      Alert.alert("Login", msg);
      return;
    }

    navigation.reset({ index: 0, routes: [{ name: "Home" }] });
  }

  return (
    <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === "ios" ? "padding" : undefined}>
      <ScrollView contentContainerStyle={styles.container} keyboardShouldPersistTaps="handled">
        <Text style={styles.logo}>COE</Text>
        <Text style={styles.sub}>Clínica Odontológica de Ensino</Text>

        <Input label="E-mail" value={email} onChangeText={setEmail} keyboardType="email-address" />
        <Input label="Senha" value={senha} onChangeText={setSenha} secureTextEntry />

        <Button title="ENTRAR" onPress={entrar} loading={loading} />

        <TouchableOpacity style={styles.linkBox} onPress={() => navigation.navigate("Cadastro")}>
          <Text style={styles.link}>Criar conta</Text>
        </TouchableOpacity>
        <TouchableOpacity onPress={() => navigation.navigate("Recuperar")}>
          <Text style={styles.link}>Esqueci a senha</Text>
        </TouchableOpacity>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

var styles = StyleSheet.create({
  container: {
    flexGrow: 1,
    padding: 24,
    paddingTop: 60,
    backgroundColor: "#f4f4fb",
  },
  logo: { fontSize: 40, fontWeight: "800", color: "#353375", textAlign: "center" },
  sub: { textAlign: "center", color: "#444", marginBottom: 28 },
  linkBox: { marginTop: 20 },
  link: { color: "#353375", fontWeight: "700", textAlign: "center", marginTop: 12 },
});
