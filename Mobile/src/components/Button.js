/**
 * Botão principal (mesma ideia do .btn-primary do site).
 */
import React from "react";
import { Text, TouchableOpacity, StyleSheet, ActivityIndicator } from "react-native";

export default function Button({ title, onPress, disabled, loading }) {
  return (
    <TouchableOpacity
      style={[styles.btn, disabled ? styles.btnOff : null]}
      onPress={onPress}
      disabled={disabled || loading}
      activeOpacity={0.8}
    >
      {loading ? (
        <ActivityIndicator color="#F4E7BB" />
      ) : (
        <Text style={styles.txt}>{title}</Text>
      )}
    </TouchableOpacity>
  );
}

var styles = StyleSheet.create({
  btn: {
    backgroundColor: "#353375",
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: "center",
    marginTop: 8,
    borderWidth: 2,
    borderColor: "#F4E7BB",
  },
  btnOff: { opacity: 0.6 },
  txt: { color: "#F4E7BB", fontSize: 16, fontWeight: "bold" },
});
