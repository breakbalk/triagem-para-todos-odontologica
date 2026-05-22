import React from "react";
import { StyleSheet, Text, View, ScrollView } from "react-native";
import Button from "../components/Button";
import Banner from "../components/Banner";
import ScreenHeader from "../components/ScreenHeader";
import StatusBadge from "../components/StatusBadge";
import { colors, spacing } from "../theme";
import { nomeServico, nomePeriodo, statusTriagem } from "../utils/labels";

export default function SuccessScreen({ navigation, route }) {
  var t = route.params && route.params.triagem ? route.params.triagem : null;
  var ehLocal = t && t.source === "local";

  function voltarHome() {
    navigation.reset({ index: 0, routes: [{ name: "Home" }] });
  }

  if (!t) {
    return (
      <View style={styles.container}>
        <ScreenHeader title="Triagem registrada" subtitle="Não foi possível exibir o resumo desta solicitação." />
        <Button title="IR PARA HOME" onPress={voltarHome} />
      </View>
    );
  }

  var st = statusTriagem(t.status);

  return (
    <ScrollView contentContainerStyle={styles.scroll}>
      <View style={styles.iconWrap}>
        <Text style={styles.icon}>{ehLocal ? "⏳" : "✓"}</Text>
      </View>
      <ScreenHeader
        title={ehLocal ? "Triagem salva no aparelho" : "Triagem enviada com sucesso"}
        subtitle={
          ehLocal
            ? "Seus dados estão guardados e serão enviados quando houver conexão."
            : "Guarde o protocolo abaixo para acompanhar sua solicitação na clínica."
        }
      />

      <View style={styles.card}>
        <Text style={styles.protocoloLabel}>Protocolo</Text>
        <Text style={styles.protocolo}>{t.protocolo || "—"}</Text>
        <View style={styles.divider} />
        <Text style={styles.item}>
          <Text style={styles.k}>Nome: </Text>
          {t.nome || "—"}
        </Text>
        <Text style={styles.item}>
          <Text style={styles.k}>Telefone: </Text>
          {t.telefone || "—"}
        </Text>
        <Text style={styles.item}>
          <Text style={styles.k}>Serviço: </Text>
          {nomeServico(t.servico)}
        </Text>
        <Text style={styles.item}>
          <Text style={styles.k}>Período: </Text>
          {nomePeriodo(t.periodo)}
        </Text>
        <StatusBadge label={st.label} tone={st.tone} />
      </View>

      {ehLocal ? (
        <Banner
          tone="warning"
          message="Sem conexão no envio: esta triagem foi salva localmente e será sincronizada quando a API estiver disponível."
        />
      ) : (
        <Banner tone="success" message="Dados recebidos pelo servidor. Você pode acompanhar o status na tela Início." />
      )}

      <Button title="IR PARA HOME" onPress={voltarHome} />
    </ScrollView>
  );
}

var styles = StyleSheet.create({
  container: { flex: 1, padding: spacing.screen, paddingTop: 24, backgroundColor: colors.bg },
  scroll: { flexGrow: 1, padding: spacing.screen, paddingTop: 16, paddingBottom: 32, backgroundColor: colors.bg },
  iconWrap: { alignItems: "center", marginBottom: 8 },
  icon: { fontSize: 48 },
  card: {
    backgroundColor: colors.card,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.screen,
    marginTop: 8,
    marginBottom: 8,
  },
  protocolo: { fontSize: 20, fontWeight: "800", color: colors.primary, textAlign: "center" },
  protocoloLabel: { textAlign: "center", color: colors.textMuted, marginTop: 4, marginBottom: 12 },
  divider: { height: 1, backgroundColor: colors.border, marginBottom: 12 },
  item: { marginBottom: 8, color: colors.text, lineHeight: 22 },
  k: { fontWeight: "700", color: colors.primary },
});
