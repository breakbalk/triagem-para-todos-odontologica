import React from "react";
import { Text, View, StyleSheet } from "react-native";
import { colors } from "../theme";

export default function ScreenHeader({ title, subtitle, showLogo }) {
  return (
    <View style={styles.wrap}>
      {showLogo ? <Text style={styles.logo}>COE</Text> : null}
      {title ? <Text style={showLogo ? styles.titleAfterLogo : styles.title}>{title}</Text> : null}
      {subtitle ? <Text style={styles.sub}>{subtitle}</Text> : null}
    </View>
  );
}

var styles = StyleSheet.create({
  wrap: { marginBottom: 8 },
  logo: { fontSize: 36, fontWeight: "800", color: colors.primary, textAlign: "center" },
  title: { fontSize: 26, fontWeight: "800", color: colors.primary },
  titleAfterLogo: { fontSize: 20, marginTop: 8, fontWeight: "700", color: colors.text, textAlign: "center" },
  sub: { color: colors.textMuted, marginTop: 6, lineHeight: 22, textAlign: "center" },
});
