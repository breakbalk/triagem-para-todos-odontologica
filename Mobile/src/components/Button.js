import React from "react";
import { Text, TouchableOpacity, StyleSheet, ActivityIndicator } from "react-native";
import { colors } from "../theme";

export default function Button({ title, onPress, disabled, loading, variant }) {
  var isSecondary = variant === "secondary";
  var isOutline = variant === "outline";

  return (
    <TouchableOpacity
      style={[
        styles.btn,
        isSecondary ? styles.btnSecondary : null,
        isOutline ? styles.btnOutline : null,
        disabled || loading ? styles.btnOff : null,
      ]}
      onPress={onPress}
      disabled={disabled || loading}
      activeOpacity={0.8}
    >
      {loading ? (
        <ActivityIndicator color={isSecondary || isOutline ? colors.primary : colors.accent} />
      ) : (
        <Text style={[styles.txt, isOutline ? styles.txtOutline : null, isSecondary ? styles.txtSecondary : null]}>{title}</Text>
      )}
    </TouchableOpacity>
  );
}

var styles = StyleSheet.create({
  btn: {
    backgroundColor: colors.primary,
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: "center",
    marginTop: 8,
    borderWidth: 2,
    borderColor: colors.accent,
    minHeight: 52,
    justifyContent: "center",
  },
  btnSecondary: {
    backgroundColor: colors.card,
    borderColor: colors.primary,
  },
  btnOutline: {
    backgroundColor: "transparent",
    borderColor: colors.primary,
  },
  btnOff: { opacity: 0.55 },
  txt: { color: colors.accent, fontSize: 16, fontWeight: "bold" },
  txtSecondary: { color: colors.primary },
  txtOutline: { color: colors.primary },
});
