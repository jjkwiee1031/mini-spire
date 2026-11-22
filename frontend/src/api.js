// API client: every call returns the full run state (backend is source of truth).

async function req(path, options) {
  const res = await fetch(path, options)
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.detail || `Request failed (${res.status})`)
  }
  return res.json()
}

const post = (path, body) =>
  req(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })

export const api = {
  createRun: () => post('/api/runs'),
  getRun: (id) => req(`/api/runs/${id}`),
  playCard: (id, handIndex, targetIndex) =>
    post(`/api/runs/${id}/play`, { hand_index: handIndex, target_index: targetIndex }),
  endTurn: (id) => post(`/api/runs/${id}/end-turn`),
  chooseReward: (id, cardId) => post(`/api/runs/${id}/reward`, { card_id: cardId }),
}
