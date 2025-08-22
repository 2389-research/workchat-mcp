// ABOUTME: Message list component for displaying thread messages
// ABOUTME: Renders individual messages with user info and timestamps

import { Message } from '../types'

interface MessageListProps {
  messages: Message[]
  isLoading?: boolean
}

export default function MessageList({ messages, isLoading }: MessageListProps) {
  if (isLoading) {
    return <div className="loading">Loading messages...</div>
  }

  if (messages.length === 0) {
    return (
      <div className="empty-state">
        <p>No messages yet. Be the first to say something!</p>
      </div>
    )
  }

  return (
    <div className="message-list-container">
      <ul className="message-list">
        {messages.map((message) => (
          <li key={message.id} className="message">
            <div className="message-header">
              <span className="message-author">
                {message.user?.display_name || 'Unknown User'}
              </span>
              <span className="message-time">
                {formatMessageTime(message.created_at)}
              </span>
              {message.edited_at && (
                <span className="message-edited">
                  (edited {formatMessageTime(message.edited_at)})
                </span>
              )}
            </div>
            <div className="message-body">
              {message.body}
            </div>
          </li>
        ))}
      </ul>
    </div>
  )
}

function formatMessageTime(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60)

  if (diffInHours < 24) {
    // Show time for messages from today
    return date.toLocaleTimeString(undefined, { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  } else {
    // Show date and time for older messages
    return date.toLocaleString(undefined, {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }
}