/**
 * URL base da API Flask (Web/backend).
 *
 * Celular físico na mesma rede Wi‑Fi: defina IP_DO_PC com o IP que aparece
 * ao rodar o Flask (ex.: "Running on http://192.168.0.232:5000").
 * Emulador Android: deixe IP_DO_PC vazio — o app usa 10.0.2.2 (host da máquina).
 */
import { Platform } from "react-native";
import Constants from "expo-constants";
import * as Device from "expo-device";

/**
 * IP da máquina na LAN (igual ao "Running on http://...:5000" do Flask).
 * Mantenha igual ao REACT_NATIVE_PACKAGER_HOSTNAME em package.json (script start:lan).
 */
const IP_DO_PC = "192.168.0.232";

function ipDoExpoSeForLocal() {
  var hostUri = Constants.expoConfig && Constants.expoConfig.hostUri;
  if (!hostUri || typeof hostUri !== "string") return null;
  var partes = hostUri.split(":");
  return partes.length >= 1 ? partes[0] : null;
}

function hostPadrao() {
  var envHost =
    typeof process !== "undefined" && process.env && process.env.EXPO_PUBLIC_COE_API_HOST
      ? String(process.env.EXPO_PUBLIC_COE_API_HOST).trim()
      : "";
  if (envHost) {
    return envHost;
  }
  if (Platform.OS === "android" && !Device.isDevice) {
    return "10.0.2.2";
  }
  if (IP_DO_PC) {
    return IP_DO_PC;
  }
  var doExpo = ipDoExpoSeForLocal();
  if (doExpo && doExpo !== "localhost" && doExpo !== "127.0.0.1") {
    return doExpo;
  }
  return Platform.OS === "android" ? "10.0.2.2" : "localhost";
}

var _host = hostPadrao();
var _porta = "5000";

export var API_BASE = "http://" + _host + ":" + _porta;

if (__DEV__) {
  console.log("[COE] API_BASE =", API_BASE, "| isDevice =", Device.isDevice);
}
