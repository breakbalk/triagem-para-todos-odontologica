import React from "react";
import { Text, TextInput, View, StyleSheet } from "react-native";
import { colors } from "../theme";

export default function Input({
  label,
  value,
  onChangeText,
  secureTextEntry,
  keyboardType,
  autoCapitalize,
  placeholder,
  hint,
  error,
}) {
  return (
    <View style={styles.wrap}>
      {label ? <Text style={styles.label}>{label}</Text> : null}
      <TextInput
        style={[styles.input, error ? styles.inputError : null]}
        value={value}
        onChangeText={onChangeText}
        secureTextEntry={secureTextEntry}
        keyboardType={keyboardType || "default"}
        autoCapitalize={autoCapitalize || "none"}
        placeholder={placeholder}
        placeholderTextColor="#999"
      />
      {error ? <Text style={styles.error}>{error}</Text> : null}
      {!error && hint ? <Text style={styles.hint}>{hint}</Text> : null}
    </View>
  );
}

var styles = StyleSheet.create({
  wrap: { marginBottom: 14 },
  label: { color: colors.primary, fontWeight: "700", marginBottom: 6, fontSize: 14 },
  input: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 12,
    paddingHorizontal: 14,
    paddingVertical: 12,
    fontSize: 16,
    backgroundColor: colors.card,
    color: colors.text,
  },
  inputError: { borderColor: colors.error },
  hint: { marginTop: 4, fontSize: 12, color: colors.textMuted },
  error: { marginTop: 4, fontSize: 12, color: colors.error, fontWeight: "600" },
});
