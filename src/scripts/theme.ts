const THEME_KEY = "theme";
const SYSTEM = "system";
const LIGHT = "light";
const DARK = "dark";
const THEME_MODES = [SYSTEM, LIGHT, DARK] as const;

type ThemeMode = (typeof THEME_MODES)[number];
type ResolvedTheme = typeof LIGHT | typeof DARK;

type InitialTheme = {
  mode?: ThemeMode;
  value?: ResolvedTheme;
};

function isThemeMode(value: string | null | undefined): value is ThemeMode {
  return THEME_MODES.includes(value as ThemeMode);
}

function getStoredMode(): ThemeMode {
  const stored = localStorage.getItem(THEME_KEY);
  return isThemeMode(stored) ? stored : SYSTEM;
}

function prefersDark(): boolean {
  return window.matchMedia("(prefers-color-scheme: dark)").matches;
}

function resolveTheme(mode: ThemeMode): ResolvedTheme {
  if (mode === SYSTEM) return prefersDark() ? DARK : LIGHT;
  return mode;
}

const initialTheme = (window as unknown as { __theme?: InitialTheme }).__theme;

// Reuse the mode/value already set by the inline FOUC-prevention script when available.
let themeMode: ThemeMode = initialTheme?.mode ?? getStoredMode();
let themeValue: ResolvedTheme = initialTheme?.value ?? resolveTheme(themeMode);

function persist(): void {
  localStorage.setItem(THEME_KEY, themeMode);
  reflect();
}

function reflect(): void {
  themeValue = resolveTheme(themeMode);

  const root = document.firstElementChild;
  root?.setAttribute("data-theme", themeValue);
  root?.setAttribute("data-theme-mode", themeMode);
  root?.classList.toggle("dark", themeValue === DARK);

  const label = themeMode === SYSTEM ? `system (${themeValue})` : themeMode;
  document.querySelector("#theme-btn")?.setAttribute("aria-label", label);
  document.querySelector("#theme-btn")?.setAttribute("title", label);

  // Fill <meta name="theme-color"> with the computed background colour so
  // Android's browser chrome matches the page background.
  const bg = window.getComputedStyle(document.body).backgroundColor;
  document
    .querySelector("meta[name='theme-color']")
    ?.setAttribute("content", bg);
}

function nextMode(mode: ThemeMode): ThemeMode {
  if (mode === SYSTEM) return LIGHT;
  if (mode === LIGHT) return DARK;
  return SYSTEM;
}

function setup(): void {
  reflect();
  document.querySelector("#theme-btn")?.addEventListener("click", () => {
    themeMode = nextMode(themeMode);
    persist();
  });
}

setup();

// Re-run after View Transitions navigation.
document.addEventListener("astro:after-swap", setup);

// Carry the theme-color value across View Transitions to prevent the
// Android navigation bar from flashing during page transitions.
document.addEventListener("astro:before-swap", event => {
  const color = document
    .querySelector("meta[name='theme-color']")
    ?.getAttribute("content");
  if (color) {
    (event as { newDocument: Document }).newDocument
      .querySelector("meta[name='theme-color']")
      ?.setAttribute("content", color);
  }
});

// Sync with OS-level dark/light preference changes only while in system mode.
window
  .matchMedia("(prefers-color-scheme: dark)")
  .addEventListener("change", () => {
    if (themeMode === SYSTEM) reflect();
  });
