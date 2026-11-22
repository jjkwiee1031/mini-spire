<template>
  <div class="card" :class="{ playable, selected, attack: card.type === 'attack' }">
    <div class="cost">{{ card.energy_cost }}</div>
    <div class="name">{{ card.name }}</div>
    <div class="desc">{{ card.description }}</div>
  </div>
</template>

<script setup>
defineProps({
  card: Object,
  playable: { type: Boolean, default: true },
  selected: { type: Boolean, default: false },
})
</script>

<style scoped>
.card {
  width: 120px; min-height: 160px;
  background: linear-gradient(170deg, #2e2e50, #232340);
  border: 2px solid #555; border-radius: 10px;
  padding: 10px; position: relative;
  cursor: pointer; transition: transform 0.1s;
  display: flex; flex-direction: column;
}
.card:hover { transform: translateY(-6px); }
.card.attack { border-color: #a33; }
.card.playable:hover { border-color: #ffd700; }
.card.selected { border-color: #ffd700; transform: translateY(-10px); }
.card:not(.playable) { opacity: 0.5; }
.cost {
  position: absolute; top: -8px; left: -8px;
  width: 28px; height: 28px; border-radius: 50%;
  background: #1e88e5; display: grid; place-items: center;
  font-weight: bold; border: 2px solid #90caf9;
}
.name { font-weight: bold; text-align: center; margin: 8px 0; color: #ffd700; }
.desc { font-size: 0.8rem; color: #ccc; text-align: center; margin-top: auto; }
</style>
