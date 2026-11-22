<template>
  <section class="end" :class="{ win: victory }">
    <h2>{{ victory ? '🏆 You conquered the Spire!' : '💀 You died...' }}</h2>
    <button @click="$emit('restart')">New Run</button>
  </section>
</template>

<script setup>
defineProps({ victory: Boolean })
defineEmits(['restart'])
</script>

<style scoped>
.end { text-align: center; padding: 60px 0; }
.end h2 { color: #ffd700; margin-bottom: 24px; }
.end:not(.win) h2 { color: #ff6666; }
</style>
