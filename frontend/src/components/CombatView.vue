<template>
  <section class="combat">
    <div class="arena">
      <EnemyCard
        v-for="(enemy, i) in run.combat.enemies"
        :key="enemy.id"
        :enemy="enemy"
      />
    </div>

    <PlayerBar :player="run.combat.player" :piles="run.combat.piles" @end-turn="$emit('end-turn')" />

    <div class="hand">
      <CardView
        v-for="(card, i) in run.combat.piles.hand"
        :key="i"
        :card="card"
        :playable="card.energy_cost <= run.combat.player.energy"
        :selected="selectedCard === card"
        @click="$emit('select-card', card)"
      />
    </div>
    <div class="hint" v-if="selectedCard">Click the enemy to attack... (single enemy: auto-targets)</div>

    <button class="play-selected" v-if="selectedCard" :disabled="!selectedPlayable" @click="$emit('play-card', handIndex)">
      Play {{ selectedCard.name }} ({{ selectedCard.energy_cost }} ⚡)
    </button>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import CardView from './CardView.vue'
import EnemyCard from './EnemyCard.vue'
import PlayerBar from './PlayerBar.vue'

const props = defineProps({
  run: Object,
  selectedCard: Object,
})
defineEmits(['select-card', 'play-card', 'end-turn'])

const handIndex = computed(() =>
  props.run.combat.piles.hand.findIndex((c) => c === props.selectedCard)
)
const selectedPlayable = computed(() =>
  handIndex.value >= 0 &&
  props.selectedCard.energy_cost <= props.run.combat.player.energy
)
</script>

<style scoped>
.combat { display: flex; flex-direction: column; gap: 12px; }
.arena { display: flex; justify-content: center; gap: 24px; min-height: 140px; }
.hand { display: flex; justify-content: center; gap: 10px; flex-wrap: wrap; }
.hint { text-align: center; color: #888; font-size: 0.85rem; }
.play-selected { align-self: center; background: #1b5e20; border-color: #4caf50; }
</style>
