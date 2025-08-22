// ABOUTME: API client for WorkChat backend communication
// ABOUTME: Handles HTTP requests and response parsing with proper error handling

import { Channel, Message, Thread } from '../types'

const API_BASE = '/api'

class APIError extends Error {
  constructor(public status: number, message: string) {
    super(message)
    this.name = 'APIError'
  }
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE}${endpoint}`
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  })

  if (!response.ok) {
    throw new APIError(response.status, `API request failed: ${response.statusText}`)
  }

  return response.json()
}

export const api = {
  // Channel operations
  getChannels: (): Promise<Channel[]> => 
    request('/channels'),

  getChannel: (channelId: string): Promise<Channel> =>
    request(`/channels/${channelId}`),

  // Message operations
  getThreadMessages: (threadId: string): Promise<Thread> =>
    request(`/threads/${threadId}`),

  postMessage: (channelId: string, body: string, threadId?: string): Promise<Message> =>
    request('/messages', {
      method: 'POST',
      body: JSON.stringify({
        channel_id: channelId,
        body,
        thread_id: threadId || null,
      }),
    }),

  // Search operations
  searchMessages: (query: string, channelId?: string): Promise<{ messages: Message[] }> => {
    const params = new URLSearchParams({ q: query })
    if (channelId) {
      params.append('scope', `channel:${channelId}`)
    }
    return request(`/search?${params}`)
  },
}