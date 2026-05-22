/**
 * Entrada do app Expo — Sprint 4: navegação e boot com tema unificado.
 */
import React, { useState, useEffect } from "react";
import { View, Text, ActivityIndicator, StyleSheet } from "react-native";
import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { SafeAreaProvider } from "react-native-safe-area-context";
import { StatusBar } from "expo-status-bar";

import LoginScreen from "./src/screens/LoginScreen";
import RegisterScreen from "./src/screens/RegisterScreen";
import RecoverPasswordScreen from "./src/screens/RecoverPasswordScreen";
import HomeScreen from "./src/screens/HomeScreen";
import TriageScreen from "./src/screens/TriageScreen";
import SuccessScreen from "./src/screens/SuccessScreen";

import * as api from "./src/services/api";
import { colors, stackScreenOptions } from "./src/theme";

var Stack = createNativeStackNavigator();

export default function App() {
  var [carregando, setCarregando] = useState(true);
  var [inicio, setInicio] = useState("Login");

  useEffect(function () {
    function comTimeout(promise, ms) {
      return new Promise(function (resolve, reject) {
        var id = setTimeout(function () {
          reject(new Error("timeout"));
        }, ms);
        promise.then(
          function (v) {
            clearTimeout(id);
            resolve(v);
          },
          function (e) {
            clearTimeout(id);
            reject(e);
          }
        );
      });
    }

    async function verificarTokenSalvo() {
      try {
        var r = await comTimeout(api.quemSou(), 8000);
        if (r.dados.ok && r.dados.user) {
          setInicio("Home");
        } else {
          await api.apagarToken();
          setInicio("Login");
        }
      } catch (e) {
        await api.apagarToken();
        setInicio("Login");
      } finally {
        setCarregando(false);
      }
    }
    verificarTokenSalvo();
  }, []);

  if (carregando) {
    return (
      <View style={styles.boot}>
        <Text style={styles.bootLogo}>COE</Text>
        <ActivityIndicator size="large" color={colors.primary} style={{ marginTop: 16 }} />
        <Text style={styles.bootTxt}>Carregando aplicativo...</Text>
        <StatusBar style="dark" />
      </View>
    );
  }

  return (
    <SafeAreaProvider>
      <NavigationContainer>
        <StatusBar style="light" />
        <Stack.Navigator initialRouteName={inicio} screenOptions={stackScreenOptions}>
          <Stack.Screen name="Login" component={LoginScreen} options={{ title: "Entrar", headerShown: false }} />
          <Stack.Screen name="Cadastro" component={RegisterScreen} options={{ title: "Nova conta" }} />
          <Stack.Screen name="Recuperar" component={RecoverPasswordScreen} options={{ title: "Recuperar senha" }} />
          <Stack.Screen name="Home" component={HomeScreen} options={{ title: "Início", headerBackVisible: false }} />
          <Stack.Screen name="Triage" component={TriageScreen} options={{ title: "Nova triagem" }} />
          <Stack.Screen
            name="Success"
            component={SuccessScreen}
            options={{ title: "Confirmação", gestureEnabled: false, headerBackVisible: false }}
          />
        </Stack.Navigator>
      </NavigationContainer>
    </SafeAreaProvider>
  );
}

var styles = StyleSheet.create({
  boot: { flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: colors.bg },
  bootLogo: { fontSize: 42, fontWeight: "800", color: colors.primary },
  bootTxt: { marginTop: 12, color: colors.textMuted },
});
