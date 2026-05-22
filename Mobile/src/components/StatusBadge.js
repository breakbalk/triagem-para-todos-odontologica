import React from "react";
import { Text, View, StyleSheet } from "react-native";
import { colors } from "../theme";

var TONE_STYLE = {
  success: { bg: colors.successBg, fg: colors.success },
  warning: { bg: colors.warningBg, fg: colors.warning },
  info: { bg: colors.infoBg, fg: colors.info },
  error: { bg: colors.errorBg, fg: colors.error },
};

export default function StatusBadge({ label, tone }) {
  var t = TONE_STYLE[tone] || TONE_STYLE.info;
  return (
    <View style={[styles.badge, { backgroundColor: t.bg }]}>
      <Text style={[styles.txt, { color: t.fg }]}>{label}</Text>
    </View>
  );
}

var styles = StyleSheet.create({
  badge: {
    alignSelf: "flex-start",
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 999,
    marginTop: 6,
  },
  txt: { fontSize: 12, fontWeight: "700" },
});
