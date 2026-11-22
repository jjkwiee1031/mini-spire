<template>
  <section class="reward">
    <h2>Victory! Choose a card to add to your deck</h2>
    <div class="options">
      <CardView
        v-for="card in options"
        :key="card.id"
        :card="card"
        @click="$emit('choose', card.id)"
      />
    </div>
    <button class="skip" @click="$emit('choose', null)">Skip reward</button>
  </section>
</template>

<script setup>
import CardView from './CardView.vue'

defineProps({ options: Array })
defineEmits(['choose'])
</script>

<style scoped>
.reward { text-align: center; padding: 32px 0; }
.options { display: flex; justify-content: center; gap: 16px; margin: 24px 0; }
.skip { background: #444; }
</style>
