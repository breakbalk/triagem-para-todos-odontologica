/**
 * Home — Sprint 4: feedback visual, pull-to-refresh, banners e badges de status.
 */
import React, { useState, useCallback } from "react";
import {
  View,
  Text,
  StyleSheet,
  Alert,
  ScrollView,
  ActivityIndicator,
  RefreshControl,
} from "react-native";
import { useFocusEffect } from "@react-navigation/native";
import Button from "../components/Button";
import Banner from "../components/Banner";
import StatusBadge from "../components/StatusBadge";
import ScreenHeader from "../components/ScreenHeader";
import * as api from "../services/api";
import { colors, spacing } from "../theme";
import { nomeServico, nomePeriodo, statusTriagem } from "../utils/labels";

export default function HomeScreen({ navigation }) {
  var [user, setUser] = useState(null);
  var [triagens, setTriagens] = useState([]);
  var [loadingTriagens, setLoadingTriagens] = useState(true);
  var [refreshing, setRefreshing] = useState(false);
  var [banner, setBanner] = useState(null);

  var carregar = useCallback(
    async function (silencioso) {
      if (!silencioso) setLoadingTriagens(true);
      try {
        var r = await api.quemSou();
        if (!(r.dados.ok && r.dados.user)) {
          await api.apagarToken();
          navigation.reset({ index: 0, routes: [{ name: "Login" }] });
          return;
        }
        setUser(r.dados.user);

        var sync = await api.sincronizarTriagensPendentes();
        var novoBanner = null;
        if (sync && sync.enviados > 0) {
          novoBanner = {
            tone: "success",
            message: "Sincronização concluída: " + sync.enviados + " triagem(ns) enviada(s).",
          };
        } else if (sync && sync.pendentes > 0) {
          novoBanner = {
            tone: "warning",
            message: "Há " + sync.pendentes + " triagem(ns) aguardando conexão para envio.",
          };
        }

        var tr = await api.listarMinhasTriagens();
        if (tr.okHttp && tr.dados.ok && Array.isArray(tr.dados.triagens)) {
          setTriagens(tr.dados.triagens);
          if (tr.dados.source === "local" && tr.dados.message) {
            novoBanner = { tone: "info", message: tr.dados.message };
          }
        } else {
          setTriagens([]);
          if (!novoBanner && tr.dados && tr.dados.error) {
            novoBanner = { tone: "error", message: tr.dados.error };
          }
        }
        setBanner(novoBanner);
      } finally {
        setLoadingTriagens(false);
        setRefreshing(false);
      }
    },
    [navigation]
  );

  useFocusEffect(
    useCallback(function () {
      carregar(false);
    }, [carregar])
  );

  function onRefresh() {
    setRefreshing(true);
    carregar(true);
  }

  function confirmarSaida() {
    Alert.alert("Sair", "Deseja encerrar sua sessão no aplicativo?", [
      { text: "Cancelar", style: "cancel" },
      {
        text: "Sair",
        style: "destructive",
        onPress: async function () {
          await api.logout();
          navigation.reset({ index: 0, routes: [{ name: "Login" }] });
        },
      },
    ]);
  }

  if (!user) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={styles.loadingTxt}>Carregando sua área...</Text>
      </View>
    );
  }

  var primeiroNome = (user.nome || "usuário").split(" ")[0];

  return (
    <ScrollView
      contentContainerStyle={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} colors={[colors.primary]} />}
    >
      <ScreenHeader showLogo title={"Olá, " + primeiroNome + "!"} subtitle="Faça uma nova triagem ou acompanhe suas solicitações recentes." />

      {banner ? <Banner message={banner.message} tone={banner.tone} /> : null}

      <Button title="NOVA TRIAGEM" onPress={function () { navigation.navigate("Triage"); }} />

      <Text style={styles.secao}>Minhas triagens</Text>
      {loadingTriagens && !refreshing ? (
        <View style={styles.loadingRow}>
          <ActivityIndicator color={colors.primary} />
          <Text style={styles.loadingRowTxt}>Atualizando histórico...</Text>
        </View>
      ) : null}
      {!loadingTriagens && triagens.length === 0 ? (
        <View style={styles.emptyBox}>
          <Text style={styles.emptyTitle}>Nenhuma triagem ainda</Text>
          <Text style={styles.info}>Toque em NOVA TRIAGEM para registrar sua primeira solicitação.</Text>
        </View>
      ) : null}
      {!loadingTriagens &&
        triagens.slice(0, 5).map(function (t, idx) {
          var st = statusTriagem(t.status);
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
              <StatusBadge label={st.label} tone={st.tone} />
            </View>
          );
        })}

      {triagens.length > 5 ? <Text style={styles.info}>Exibindo as 5 solicitações mais recentes.</Text> : null}

      {user.is_admin ? (
        <Text style={styles.admin} onPress={function () { Alert.alert("Administrador", "Painel completo disponível na versão web da COE."); }}>
          Acesso administrador (consulte a versão web)
        </Text>
      ) : null}

      <View style={{ height: 16 }} />
      <Button title="SAIR" onPress={confirmarSaida} variant="secondary" />
    </ScrollView>
  );
}

var styles = StyleSheet.create({
  center: { flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: colors.bg },
  loadingTxt: { marginTop: 12, color: colors.primary },
  container: { flexGrow: 1, padding: spacing.screen, paddingTop: 16, backgroundColor: colors.bg },
  secao: { marginTop: 20, marginBottom: 10, color: colors.primary, fontWeight: "800", fontSize: 16 },
  info: { marginTop: 8, color: colors.textMuted, lineHeight: 22 },
  loadingRow: { flexDirection: "row", alignItems: "center", marginTop: 8 },
  loadingRowTxt: { marginLeft: 10, color: colors.textMuted },
  emptyBox: {
    backgroundColor: colors.card,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: colors.border,
    padding: 16,
    marginTop: 4,
  },
  emptyTitle: { fontWeight: "700", color: colors.primary, marginBottom: 6 },
  card: {
    backgroundColor: colors.card,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 12,
    padding: spacing.card,
    marginBottom: 10,
  },
  cardLine: { color: colors.text, marginBottom: 4 },
  k: { fontWeight: "700", color: colors.primary },
  admin: { marginTop: 14, color: colors.success, fontWeight: "600", fontSize: 13 },
});
