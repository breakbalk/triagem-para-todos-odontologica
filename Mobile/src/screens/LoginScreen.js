/**
 * RF02 — Login com e-mail e senha (Sprint 1). Sprint 4: validação e UI unificada.
 */
import React, { useState } from "react";
import { View, Text, StyleSheet, TouchableOpacity, Alert, ScrollView, KeyboardAvoidingView, Platform } from "react-native";
import Input from "../components/Input";
import Button from "../components/Button";
import ScreenHeader from "../components/ScreenHeader";
import * as api from "../services/api";
import { colors, spacing } from "../theme";

export default function LoginScreen({ navigation }) {
  var [email, setEmail] = useState("");
  var [senha, setSenha] = useState("");
  var [loading, setLoading] = useState(false);

  async function entrar() {
    if (!email.trim()) {
      Alert.alert("Login", "Informe seu e-mail.");
      return;
    }
    if (!senha) {
      Alert.alert("Login", "Informe sua senha.");
      return;
    }
    setLoading(true);
    var r = await api.login(email.trim(), senha);
    setLoading(false);

    if (!r.okHttp) {
      var msg = r.dados.error ? r.dados.error : "Não foi possível entrar. Verifique e-mail e senha.";
      Alert.alert("Login", msg);
      return;
    }

    navigation.reset({ index: 0, routes: [{ name: "Home" }] });
  }

  return (
    <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === "ios" ? "padding" : undefined}>
      <ScrollView contentContainerStyle={styles.container} keyboardShouldPersistTaps="handled">
        <ScreenHeader showLogo subtitle="Clínica Odontológica de Ensino — UniEvangélica" />

        <Input label="E-mail" value={email} onChangeText={setEmail} keyboardType="email-address" placeholder="seu@email.com" />
        <Input label="Senha" value={senha} onChangeText={setSenha} secureTextEntry placeholder="••••••••" />

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
    padding: spacing.screen,
    paddingTop: 48,
    backgroundColor: colors.bg,
  },
  linkBox: { marginTop: 20 },
  link: { color: colors.primary, fontWeight: "700", textAlign: "center", marginTop: 12 },
});
