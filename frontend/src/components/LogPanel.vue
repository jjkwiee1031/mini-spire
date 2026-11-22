<template>
  <section class="log">
    <h3>Combat Log</h3>
    <div class="lines">
      <div v-for="(line, i) in log" :key="i" class="line">{{ line }}</div>
    </div>
  </section>
</template>

<script setup>
defineProps({ log: Array })
</script>

<style scoped>
.log {
  margin-top: 16px; background: #12121f; border: 1px solid #333;
  border-radius: 8px; padding: 10px;
}
.log h3 { font-size: 0.9rem; color: #888; margin-bottom: 6px; }
.lines { max-height: 140px; overflow-y: auto; font-size: 0.85rem; }
.line { padding: 2px 0; color: #bbb; }
.line:last-child { color: #fff; }
</style>
