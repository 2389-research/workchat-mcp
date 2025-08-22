// ABOUTME: SSE hook for real-time event stream from WorkChat backend
// ABOUTME: Maintains EventSource connection and provides connection status

import { useState, useEffect, useRef } from 'react'
import { SSEEvent } from '../types'

interface UseSSEReturn {
  lastMessage: SSEEvent | null
  connectionStatus: 'connected' | 'disconnected'
}

export function useSSE(): UseSSEReturn {
  const [lastMessage, setLastMessage] = useState<SSEEvent | null>(null)
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected'>('disconnected')
  const eventSourceRef = useRef<EventSource | null>(null)

  useEffect(() => {
    const connectEventSource = () => {
      try {
        const eventSource = new EventSource('/events')
        eventSourceRef.current = eventSource

        eventSource.onopen = () => {
          setConnectionStatus('connected')
          console.log('SSE connection established')
        }

        eventSource.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data)
            setLastMessage(data)
          } catch (error) {
            console.error('Failed to parse SSE message:', error)
          }
        }

        eventSource.onerror = (error) => {
          console.error('SSE connection error:', error)
          setConnectionStatus('disconnected')
          
          // Reconnect after a delay
          setTimeout(() => {
            if (eventSource.readyState === EventSource.CLOSED) {
              connectEventSource()
            }
          }, 5000)
        }

        eventSource.addEventListener('newMessage', (event) => {
          try {
            const data = JSON.parse(event.data)
            setLastMessage({ type: 'newMessage', data })
          } catch (error) {
            console.error('Failed to parse newMessage event:', error)
          }
        })

        eventSource.addEventListener('presenceUpdate', (event) => {
          try {
            const data = JSON.parse(event.data)
            setLastMessage({ type: 'presenceUpdate', data })
          } catch (error) {
            console.error('Failed to parse presenceUpdate event:', error)
          }
        })

      } catch (error) {
        console.error('Failed to create EventSource:', error)
        setConnectionStatus('disconnected')
      }
    }

    connectEventSource()

    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close()
        eventSourceRef.current = null
      }
    }
  }, [])

  return { lastMessage, connectionStatus }
}