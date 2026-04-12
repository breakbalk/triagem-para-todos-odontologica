/**
 * Campo de texto reutilizável (Sprint 1 — telas de login/cadastro).
 */
import React from "react";
import { Text, TextInput, View, StyleSheet } from "react-native";

export default function Input({ label, value, onChangeText, secureTextEntry, keyboardType, autoCapitalize }) {
  return (
    <View style={styles.wrap}>
      {label ? <Text style={styles.label}>{label}</Text> : null}
      <TextInput
        style={styles.input}
        value={value}
        onChangeText={onChangeText}
        secureTextEntry={secureTextEntry}
        keyboardType={keyboardType || "default"}
        autoCapitalize={autoCapitalize || "none"}
      />
    </View>
  );
}

var styles = StyleSheet.create({
  wrap: { marginBottom: 14 },
  label: { color: "#353375", fontWeight: "700", marginBottom: 6, fontSize: 14 },
  input: {
    borderWidth: 1,
    borderColor: "#ccc",
    borderRadius: 12,
    paddingHorizontal: 14,
    paddingVertical: 12,
    fontSize: 16,
    backgroundColor: "#fff",
  },
});
