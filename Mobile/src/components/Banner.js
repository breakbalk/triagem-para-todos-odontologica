import React from "react";
import { Text, View, StyleSheet } from "react-native";
import { colors } from "../theme";

var TONES = {
  success: { bg: colors.successBg, border: colors.success, text: colors.success },
  warning: { bg: colors.warningBg, border: colors.warning, text: colors.warning },
  info: { bg: colors.infoBg, border: colors.info, text: colors.info },
  error: { bg: colors.errorBg, border: colors.error, text: colors.error },
};

export default function Banner({ message, tone }) {
  if (!message) return null;
  var t = TONES[tone] || TONES.info;
  return (
    <View style={[styles.box, { backgroundColor: t.bg, borderColor: t.border }]}>
      <Text style={[styles.txt, { color: t.text }]}>{message}</Text>
    </View>
  );
}

var styles = StyleSheet.create({
  box: {
    borderWidth: 1,
    borderRadius: 12,
    padding: 12,
    marginTop: 12,
  },
  txt: { fontWeight: "600", lineHeight: 20, fontSize: 14 },
});
