/**
 * RF03 — Recuperar senha (Sprint 1). Sprint 4: textos e passos mais claros.
 */
import React, { useState } from "react";
import { View, Text, StyleSheet, TouchableOpacity, Alert, ScrollView, KeyboardAvoidingView, Platform } from "react-native";
import Input from "../components/Input";
import Button from "../components/Button";
import ScreenHeader from "../components/ScreenHeader";
import Banner from "../components/Banner";
import * as api from "../services/api";
import { spacing } from "../theme";

export default function RecoverPasswordScreen({ navigation }) {
  var [passo, setPasso] = useState(1);
  var [email, setEmail] = useState("");
  var [token, setToken] = useState("");
  var [nova, setNova] = useState("");
  var [loading, setLoading] = useState(false);

  async function pedirToken() {
    if (!email.trim()) {
      Alert.alert("Recuperar senha", "Informe o e-mail cadastrado.");
      return;
    }
    setLoading(true);
    var r = await api.esqueciSenha(email.trim());
    setLoading(false);

    if (!r.okHttp) {
      Alert.alert("Erro", r.dados.error || "Não foi possível processar o pedido.");
      return;
    }

    if (r.dados.demo_token) {
      setToken(r.dados.demo_token);
      setPasso(2);
      Alert.alert("Próximo passo", "Em ambiente de demonstração, o token foi preenchido automaticamente.");
    } else {
      Alert.alert("Verifique seu e-mail", r.dados.message || "Se o e-mail existir, você receberá instruções.");
    }
  }

  async function salvarNovaSenha() {
    if (!token.trim() || nova.length < 6) {
      Alert.alert("Recuperar senha", "Informe o token e uma nova senha com pelo menos 6 caracteres.");
      return;
    }
    setLoading(true);
    var r = await api.redefinirSenha(email.trim(), token.trim(), nova);
    setLoading(false);

    if (!r.okHttp) {
      Alert.alert("Erro", r.dados.error || "Não foi possível redefinir a senha.");
      return;
    }

    Alert.alert("Senha atualizada", "Faça login com a nova senha.", [
      { text: "OK", onPress: function () { navigation.navigate("Login"); } },
    ]);
  }

  return (
    <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === "ios" ? "padding" : undefined}>
      <ScrollView contentContainerStyle={styles.container} keyboardShouldPersistTaps="handled">
        <ScreenHeader
          title="Recuperar senha"
          subtitle={passo === 1 ? "Informe o e-mail da sua conta." : "Defina uma nova senha de acesso."}
        />

        {passo === 2 ? <Banner tone="info" message="Passo 2 de 2 — token e nova senha." /> : null}

        {passo === 1 ? (
          <View>
            <Input label="E-mail cadastrado" value={email} onChangeText={setEmail} keyboardType="email-address" />
            <Button title="ENVIAR" onPress={pedirToken} loading={loading} />
          </View>
        ) : (
          <View>
            <Input label="Token" value={token} onChangeText={setToken} hint="No modo demonstração, o token vem preenchido automaticamente." />
            <Input label="Nova senha" value={nova} onChangeText={setNova} secureTextEntry hint="Mínimo de 6 caracteres." />
            <Button title="REDEFINIR SENHA" onPress={salvarNovaSenha} loading={loading} />
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
  container: { flexGrow: 1, padding: spacing.screen, paddingTop: 16, backgroundColor: colors.bg },
  linkBox: { marginTop: 24 },
  link: { color: colors.primary, fontWeight: "700", textAlign: "center" },
});
