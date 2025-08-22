import { useState } from 'react'
import ChannelSidebar from './components/ChannelSidebar'
import ThreadView from './components/ThreadView'
import { useSSE } from './hooks/useSSE'

function App() {
  const [selectedChannelId, setSelectedChannelId] = useState<string | null>(null)
  const { connectionStatus } = useSSE()

  return (
    <div className="app">
      <div className={`connection-status ${connectionStatus}`}>
        {connectionStatus === 'connected' ? '🟢 Connected' : '🔴 Disconnected'}
      </div>
      
      <ChannelSidebar 
        selectedChannelId={selectedChannelId}
        onChannelSelect={setSelectedChannelId}
      />
      
      <main className="main-content">
        {selectedChannelId ? (
          <ThreadView channelId={selectedChannelId} />
        ) : (
          <div className="empty-state">
            <h2>Welcome to WorkChat</h2>
            <p>Select a channel from the sidebar to start chatting</p>
          </div>
        )}
      </main>
    </div>
  )
}

export default App