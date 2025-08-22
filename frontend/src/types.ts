// ABOUTME: TypeScript type definitions for WorkChat API responses
// ABOUTME: Matches the backend SQLModel schemas for type safety

export interface Channel {
  id: string
  name: string
  description?: string
  org_id: string
  created_at: string
}

export interface Message {
  id: string
  channel_id: string
  thread_id: string
  user_id: string
  body: string
  version: number
  edited_at?: string
  created_at: string
  user?: User
}

export interface User {
  id: string
  email: string
  display_name: string
  role: 'ADMIN' | 'MEMBER'
  org_id: string
  created_at: string
}

export interface Thread {
  messages: Message[]
  channel: Channel
  total: number
}

export interface SSEEvent {
  type: 'newMessage' | 'presenceUpdate'
  data: any
}