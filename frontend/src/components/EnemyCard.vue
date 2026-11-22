<template>
  <div class="enemy" :class="{ dead: enemy.hp === 0 }">
    <div class="sprite">👹</div>
    <div class="name">{{ enemy.name }}</div>
    <div class="intent" v-if="enemy.intent">
      {{ enemy.intent.kind === 'attack' ? '⚔️' : '🛡️' }}
      {{ enemy.intent.value }}
    </div>
    <div class="hpbar"><div class="fill" :style="{ width: hpPct + '%' }"></div></div>
    <div class="hp">{{ enemy.hp }} / {{ enemy.max_hp }} <span v-if="enemy.block" class="block">🛡️{{ enemy.block }}</span></div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({ enemy: Object })
const hpPct = computed(() => (props.enemy.hp / props.enemy.max_hp) * 100)
</script>

<style scoped>
.enemy { text-align: center; width: 150px; }
.enemy.dead { opacity: 0.2; filter: grayscale(1); }
.sprite { font-size: 3.5rem; }
.name { color: #ffaaaa; font-weight: bold; }
.intent { margin: 4px 0; color: #ffb74d; }
.hpbar { height: 8px; background: #333; border-radius: 4px; overflow: hidden; }
.fill { height: 100%; background: #e53935; transition: width 0.3s; }
.block { color: #90caf9; }
</style>
