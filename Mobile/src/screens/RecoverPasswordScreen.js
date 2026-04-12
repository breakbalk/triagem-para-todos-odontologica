/**
 * RF03 — Recuperar senha (Sprint 1).
 * Passo 1: pede o e-mail. Em modo demo o servidor devolve demo_token no JSON.
 * Passo 2: cola o token e define nova senha.
 */
import React, { useState } from "react";
import { View, Text, StyleSheet, TouchableOpacity, Alert, ScrollView, KeyboardAvoidingView, Platform } from "react-native";
import Input from "../components/Input";
import Button from "../components/Button";
import * as api from "../services/api";

export default function RecoverPasswordScreen({ navigation }) {
  var [passo, setPasso] = useState(1);
  var [email, setEmail] = useState("");
  var [token, setToken] = useState("");
  var [nova, setNova] = useState("");
  var [loading, setLoading] = useState(false);

  async function pedirToken() {
    setLoading(true);
    var r = await api.esqueciSenha(email.trim());
    setLoading(false);

    if (!r.okHttp) {
      Alert.alert("Erro", r.dados.error || "Falha.");
      return;
    }

    Alert.alert("Próximo passo", r.dados.message || "Ok.");
    if (r.dados.demo_token) {
      setToken(r.dados.demo_token);
      setPasso(2);
    }
  }

  async function salvarNovaSenha() {
    setLoading(true);
    var r = await api.redefinirSenha(email.trim(), token.trim(), nova);
    setLoading(false);

    if (!r.okHttp) {
      Alert.alert("Erro", r.dados.error || "Falha.");
      return;
    }

    Alert.alert("Sucesso", "Faça login com a nova senha.");
    navigation.navigate("Login");
  }

  return (
    <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === "ios" ? "padding" : undefined}>
      <ScrollView contentContainerStyle={styles.container} keyboardShouldPersistTaps="handled">
        <Text style={styles.titulo}>Recuperar senha</Text>

        {passo === 1 ? (
          <View>
            <Input label="E-mail cadastrado" value={email} onChangeText={setEmail} keyboardType="email-address" />
            <Button title="ENVIAR" onPress={pedirToken} loading={loading} />
          </View>
        ) : (
          <View>
            <Text style={styles.hint}>Cole o token (modo demo) e a nova senha.</Text>
            <Input label="Token" value={token} onChangeText={setToken} />
            <Input label="Nova senha" value={nova} onChangeText={setNova} secureTextEntry />
            <Button title="REDEFINIR" onPress={salvarNovaSenha} loading={loading} />
          </View>
        )}

        <TouchableOpacity style={styles.linkBox} onPress={() => navigation.navigate("Login")}>
          <Text style={styles.link}>Voltar ao login</Text>
        </TouchableOpacity>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

var styles = StyleSheet.create({
  container: { flexGrow: 1, padding: 24, paddingTop: 48, backgroundColor: "#f4f4fb" },
  titulo: { fontSize: 24, fontWeight: "800", color: "#353375", marginBottom: 16 },
  hint: { color: "#555", marginBottom: 12 },
  linkBox: { marginTop: 24 },
  link: { color: "#353375", fontWeight: "700", textAlign: "center" },
});
