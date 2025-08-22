// ABOUTME: Channel list sidebar component for navigation
// ABOUTME: Displays available channels and handles channel selection

import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'
import { Channel } from '../types'

interface ChannelSidebarProps {
  selectedChannelId: string | null
  onChannelSelect: (channelId: string) => void
}

export default function ChannelSidebar({ selectedChannelId, onChannelSelect }: ChannelSidebarProps) {
  const { data: channels, isLoading, error } = useQuery({
    queryKey: ['channels'],
    queryFn: api.getChannels,
  })

  if (isLoading) {
    return (
      <div className="sidebar">
        <h2>Channels</h2>
        <div className="loading">Loading channels...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="sidebar">
        <h2>Channels</h2>
        <div className="error">Failed to load channels</div>
      </div>
    )
  }

  return (
    <div className="sidebar">
      <h2>Channels</h2>
      <ul className="channel-list">
        {channels?.map((channel: Channel) => (
          <li
            key={channel.id}
            className={`channel-item ${selectedChannelId === channel.id ? 'active' : ''}`}
            onClick={() => onChannelSelect(channel.id)}
          >
            <div className="channel-name">
              # {channel.name}
            </div>
            {channel.description && (
              <div className="channel-description">
                {channel.description}
              </div>
            )}
          </li>
        ))}
      </ul>
      
      {channels?.length === 0 && (
        <div className="empty-state">
          <p>No channels available</p>
        </div>
      )}
    </div>
  )
}