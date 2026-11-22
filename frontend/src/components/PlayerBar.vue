<template>
  <div class="playerbar">
    <div class="stat">❤️ {{ player.hp }} / {{ player.max_hp }}</div>
    <div class="stat" v-if="player.block">🛡️ {{ player.block }}</div>
    <div class="stat energy">⚡ {{ player.energy }} / {{ player.max_energy }}</div>
    <div class="stat piles">🂠 {{ piles.draw }} | {{ piles.discard }}</div>
    <button class="end" @click="$emit('end-turn')">End Turn</button>
  </div>
</template>

<script setup>
defineProps({ player: Object, piles: Object })
defineEmits(['end-turn'])
</script>

<style scoped>
.playerbar {
  display: flex; align-items: center; gap: 16px;
  background: #1c1c34; border: 1px solid #444; border-radius: 8px;
  padding: 10px 16px;
}
.stat { font-size: 1.1rem; }
.energy { color: #64b5f6; }
.piles { color: #888; font-size: 0.9rem; }
.end { margin-left: auto; background: #7b1fa2; border-color: #ce93d8; }
</style>
