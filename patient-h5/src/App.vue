<template>
  <router-view />
</template>

<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  background: var(--color-bg);
  color: var(--color-text);
  min-height: 100vh;
}

#app {
  width: 100%;
  max-width: 480px;
  min-height: 100vh;
  margin: 0 auto;
  overflow-x: hidden;
  background: var(--color-bg);
}
</style>