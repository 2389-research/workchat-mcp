// ABOUTME: Thread view component displaying messages and composition area
// ABOUTME: Shows message list and handles real-time message updates via SSE

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useEffect, useRef } from 'react'
import { api } from '../api/client'
import MessageList from './MessageList'
import MessageComposer from './MessageComposer'
import { useSSE } from '../hooks/useSSE'

interface ThreadViewProps {
  channelId: string
}

export default function ThreadView({ channelId }: ThreadViewProps) {
  const queryClient = useQueryClient()
  const messagesEndRef = useRef<HTMLDivElement>(null)
  
  // For simplicity, we'll use the channel as the root thread
  // In a real app, you might have multiple threads per channel
  const threadId = channelId

  const { data: thread, isLoading, error } = useQuery({
    queryKey: ['thread', threadId],
    queryFn: () => api.getThreadMessages(threadId),
  })

  const postMessageMutation = useMutation({
    mutationFn: ({ body }: { body: string }) => 
      api.postMessage(channelId, body, threadId),
    onSuccess: () => {
      // Refetch messages after successful post
      queryClient.invalidateQueries({ queryKey: ['thread', threadId] })
    },
  })

  // Handle SSE events for real-time updates
  const { lastMessage } = useSSE()
  
  useEffect(() => {
    if (lastMessage?.type === 'newMessage' && lastMessage.data?.channel_id === channelId) {
      // Invalidate and refetch messages when new message arrives
      queryClient.invalidateQueries({ queryKey: ['thread', threadId] })
    }
  }, [lastMessage, channelId, threadId, queryClient])

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [thread?.messages])

  const handleSendMessage = (body: string) => {
    postMessageMutation.mutate({ body })
  }

  if (isLoading) {
    return <div className="loading">Loading messages...</div>
  }

  if (error) {
    return <div className="error">Failed to load messages</div>
  }

  return (
    <div className="thread-view">
      {thread && (
        <>
          <div className="thread-header">
            <h1 className="thread-title"># {thread.channel.name}</h1>
            {thread.channel.description && (
              <p className="thread-description">{thread.channel.description}</p>
            )}
          </div>

          <MessageList 
            messages={thread.messages}
            isLoading={isLoading}
          />
          
          <div ref={messagesEndRef} />
        </>
      )}

      <MessageComposer 
        onSendMessage={handleSendMessage}
        isLoading={postMessageMutation.isPending}
      />
    </div>
  )
}