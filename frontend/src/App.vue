<template>
  <div v-if="!run">Loading…</div>
  <template v-else>
  <div v-if="error" class="error-banner">{{ error }}</div>
  <header class="topbar">
    <h1>⚔️ Mini Spire</h1>
    <div class="progress">
      Encounter {{ run.encounters_won + 1 }} / 4
      <span v-if="run.is_boss_fight" class="boss-badge">BOSS</span>
    </div>
  </header>

  <CombatView
    v-if="run.phase === 'combat'"
    :run="run"
    :selected-card="selectedCard"
    @select-card="selectCard"
    @play-card="playCard"
    @end-turn="endTurn"
  />

  <RewardView
    v-else-if="run.phase === 'card_reward'"
    :options="run.reward.options"
    @choose="chooseReward"
  />

  <EndScreen v-else :victory="run.phase === 'victory'" @restart="restart" />

  <LogPanel :log="run.log" />
  </template>
</template>

<script setup>
import { ref } from 'vue'
import { api } from './api.js'
import CombatView from './components/CombatView.vue'
import RewardView from './components/RewardView.vue'
import EndScreen from './components/EndScreen.vue'
import LogPanel from './components/LogPanel.vue'

const run = ref(null)
const selectedCard = ref(null)
const error = ref(null)

async function start() {
  run.value = await api.createRun()
  selectedCard.value = null
}

function selectCard(card) {
  selectedCard.value = selectedCard.value === card ? null : card
}

async function act(fn) {
  try {
    run.value = await fn()
    selectedCard.value = null
    error.value = null
  } catch (e) {
    selectedCard.value = null
    error.value = e.message
    setTimeout(() => (error.value = null), 2500)
  }
}

const playCard = (i) => act(() => api.playCard(run.value.run_id, i, 0))
const endTurn = () => act(() => api.endTurn(run.value.run_id))
const chooseReward = (cardId) => act(() => api.chooseReward(run.value.run_id, cardId))
const restart = () => act(() => api.createRun())

start()
</script>

<style scoped>
.topbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.progress { color: #aaa; }
.error-banner {
  background: #5a1a1a; color: #ffb0b0; padding: 8px 12px;
  border-radius: 6px; margin-bottom: 8px; text-align: center;
}
.boss-badge { color: #ff4444; font-weight: bold; margin-left: 6px; }
</style>
