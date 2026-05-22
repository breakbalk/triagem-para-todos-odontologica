/**
 * Identidade visual COE — cores e espaçamentos compartilhados (Sprint 4).
 */
export var colors = {
  bg: "#f4f4fb",
  primary: "#353375",
  accent: "#F4E7BB",
  text: "#222222",
  textMuted: "#555555",
  border: "#dddddd",
  card: "#ffffff",
  success: "#2e7d4a",
  successBg: "#e8f5e9",
  warning: "#8a5a00",
  warningBg: "#fff8e1",
  info: "#1a5f8a",
  infoBg: "#e3f2fd",
  error: "#b3261e",
  errorBg: "#fdecea",
};

export var spacing = {
  screen: 24,
  section: 16,
  card: 12,
};

export var screenContentStyle = {
  backgroundColor: colors.bg,
};

export var stackScreenOptions = {
  headerStyle: { backgroundColor: colors.primary },
  headerTintColor: colors.accent,
  headerTitleStyle: { fontWeight: "700" },
  contentStyle: screenContentStyle,
};
