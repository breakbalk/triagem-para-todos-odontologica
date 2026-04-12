/**
 * RF01 — Cadastro (Sprint 1).
 */
import React, { useState } from "react";
import { View, Text, StyleSheet, TouchableOpacity, Alert, ScrollView, KeyboardAvoidingView, Platform } from "react-native";
import Input from "../components/Input";
import Button from "../components/Button";
import * as api from "../services/api";

export default function RegisterScreen({ navigation }) {
  var [nome, setNome] = useState("");
  var [telefone, setTelefone] = useState("");
  var [email, setEmail] = useState("");
  var [senha, setSenha] = useState("");
  var [confirma, setConfirma] = useState("");
  var [loading, setLoading] = useState(false);

  async function registrar() {
    if (nome.trim().length < 3) {
      Alert.alert("Cadastro", "Nome com pelo menos 3 letras.");
      return;
    }
    if (senha !== confirma) {
      Alert.alert("Cadastro", "As senhas não coincidem.");
      return;
    }
    if (senha.length < 6) {
      Alert.alert("Cadastro", "Senha com no mínimo 6 caracteres.");
      return;
    }

    setLoading(true);
    var r = await api.cadastro(nome.trim(), email.trim(), senha, telefone.trim());
    setLoading(false);

    if (!r.okHttp) {
      Alert.alert("Cadastro", r.dados.error ? r.dados.error : "Erro.");
      return;
    }

    navigation.reset({ index: 0, routes: [{ name: "Home" }] });
  }

  return (
    <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === "ios" ? "padding" : undefined}>
      <ScrollView contentContainerStyle={styles.container} keyboardShouldPersistTaps="handled">
        <Text style={styles.titulo}>Criar conta</Text>

        <Input label="Nome completo" value={nome} onChangeText={setNome} autoCapitalize="words" />
        <Input label="Telefone (opcional)" value={telefone} onChangeText={setTelefone} keyboardType="phone-pad" />
        <Input label="E-mail" value={email} onChangeText={setEmail} keyboardType="email-address" />
        <Input label="Senha" value={senha} onChangeText={setSenha} secureTextEntry />
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
  container: { flexGrow: 1, padding: 24, paddingTop: 48, backgroundColor: "#f4f4fb" },
  titulo: { fontSize: 24, fontWeight: "800", color: "#353375", marginBottom: 20 },
  linkBox: { marginTop: 20 },
  link: { color: "#353375", fontWeight: "700", textAlign: "center" },
});
