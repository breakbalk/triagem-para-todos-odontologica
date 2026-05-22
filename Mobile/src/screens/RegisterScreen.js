/**
 * RF01 — Cadastro (Sprint 1). Sprint 4: mensagens e layout unificados.
 */
import React, { useState } from "react";
import { View, Text, StyleSheet, TouchableOpacity, Alert, ScrollView, KeyboardAvoidingView, Platform } from "react-native";
import Input from "../components/Input";
import Button from "../components/Button";
import ScreenHeader from "../components/ScreenHeader";
import * as api from "../services/api";
import { colors, spacing } from "../theme";

export default function RegisterScreen({ navigation }) {
  var [nome, setNome] = useState("");
  var [telefone, setTelefone] = useState("");
  var [email, setEmail] = useState("");
  var [senha, setSenha] = useState("");
  var [confirma, setConfirma] = useState("");
  var [loading, setLoading] = useState(false);

  async function registrar() {
    if (nome.trim().length < 3) {
      Alert.alert("Cadastro", "Informe o nome completo (mínimo 3 caracteres).");
      return;
    }
    if (!email.trim()) {
      Alert.alert("Cadastro", "Informe um e-mail válido.");
      return;
    }
    if (senha !== confirma) {
      Alert.alert("Cadastro", "As senhas não coincidem.");
      return;
    }
    if (senha.length < 6) {
      Alert.alert("Cadastro", "A senha deve ter no mínimo 6 caracteres.");
      return;
    }

    setLoading(true);
    var r = await api.cadastro(nome.trim(), email.trim(), senha, telefone.trim());
    setLoading(false);

    if (!r.okHttp) {
      Alert.alert("Cadastro", r.dados.error ? r.dados.error : "Não foi possível criar a conta.");
      return;
    }

    Alert.alert("Conta criada", "Bem-vindo! Você já pode usar o aplicativo.", [
      {
        text: "OK",
        onPress: function () {
          navigation.reset({ index: 0, routes: [{ name: "Home" }] });
        },
      },
    ]);
  }

  return (
    <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === "ios" ? "padding" : undefined}>
      <ScrollView contentContainerStyle={styles.container} keyboardShouldPersistTaps="handled">
        <ScreenHeader title="Criar conta" subtitle="Cadastre-se para realizar triagens pela COE." />

        <Input label="Nome completo" value={nome} onChangeText={setNome} autoCapitalize="words" />
        <Input label="Telefone (opcional)" value={telefone} onChangeText={setTelefone} keyboardType="phone-pad" />
        <Input label="E-mail" value={email} onChangeText={setEmail} keyboardType="email-address" />
        <Input label="Senha" value={senha} onChangeText={setSenha} secureTextEntry hint="Mínimo de 6 caracteres." />
        <Input label="Confirmar senha" value={confirma} onChangeText={setConfirma} secureTextEntry />

        <Button title="CADASTRAR" onPress={registrar} loading={loading} />

        <TouchableOpacity style={styles.linkBox} onPress={() => navigation.navigate("Login")}>
          <Text style={styles.link}>Já tenho conta</Text>
        </TouchableOpacity>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

var styles = StyleSheet.create({
  container: { flexGrow: 1, padding: spacing.screen, paddingTop: 16, backgroundColor: colors.bg },
  linkBox: { marginTop: 20 },
  link: { color: colors.primary, fontWeight: "700", textAlign: "center" },
});
