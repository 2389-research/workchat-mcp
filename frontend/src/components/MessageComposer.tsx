// ABOUTME: Message composer component for sending new messages
// ABOUTME: Handles textarea input, form submission, and loading states

import { useState, KeyboardEvent } from 'react'

interface MessageComposerProps {
  onSendMessage: (body: string) => void
  isLoading?: boolean
}

export default function MessageComposer({ onSendMessage, isLoading }: MessageComposerProps) {
  const [message, setMessage] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!message.trim() || isLoading) return

    onSendMessage(message)
    setMessage('')
  }

  const handleKeyPress = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <div className="message-composer">
      <form onSubmit={handleSubmit} className="composer-form">
        <textarea
          className="composer-input"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyPress}
          placeholder="Type your message here... (Enter to send, Shift+Enter for new line)"
          disabled={isLoading}
          rows={3}
        />
        <button
          type="submit"
          className="composer-button"
          disabled={!message.trim() || isLoading}
        >
          {isLoading ? 'Sending...' : 'Send'}
        </button>
      </form>
    </div>
  )
}