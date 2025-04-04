import React, { useState } from 'react';
import { Send, Filter, Clock, MessageSquare, Youtube, ChevronRight } from 'lucide-react';

interface Video {
  id: string;
  url: string;
  title: string;
}

interface ChatHistory {
  id: string;
  date: string;
  title: string;
}

function App() {
  const [url, setUrl] = useState('');
  const [videos, setVideos] = useState<Video[]>([]);
  const [activeTab, setActiveTab] = useState<'input' | 'summary'>('input');
  const [chatHistory] = useState<ChatHistory[]>([
    { id: '1', date: '2024-03-10', title: 'React Hooks Deep Dive' },
    { id: '2', date: '2024-03-09', title: 'TypeScript Best Practices' },
  ]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (url.trim()) {
      // In a real app, we'd validate the URL and fetch video details
      setVideos([...videos, {
        id: Date.now().toString(),
        url: url,
        title: 'Sample Video Title ' + (videos.length + 1),
      }]);
      setUrl('');
    }
  };

  return (
    <div className="flex min-h-screen bg-gray-900">
      {/* Sidebar */}
      <div className="w-64 bg-gray-800 p-4 flex flex-col border-r border-gray-700">
        <div className="flex items-center space-x-2 mb-8">
          <Youtube className="w-6 h-6 text-emerald-500" />
          <h1 className="text-xl font-bold text-white">VidProbeAi</h1>
        </div>

        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-semibold text-gray-400">History</h2>
          <button className="text-gray-400 hover:text-white">
            <Filter className="w-4 h-4" />
          </button>
        </div>

        <div className="space-y-2">
          {chatHistory.map((chat) => (
            <div
              key={chat.id}
              className="flex items-center space-x-3 p-2 rounded-lg hover:bg-gray-700 cursor-pointer text-gray-300 hover:text-white"
            >
              <Clock className="w-4 h-4" />
              <span className="text-sm truncate">{chat.title}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        <header className="bg-gray-800 p-6 border-b border-gray-700">
          <h1 className="text-2xl font-bold text-white">Welcome to VidProbeAi</h1>
        </header>

        <main className="flex-1 p-6">
          {activeTab === 'input' ? (
            <div className="max-w-3xl mx-auto">
              <form onSubmit={handleSubmit} className="mb-8">
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    placeholder="Paste YouTube URL here..."
                    className="flex-1 bg-gray-800 text-white rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                  />
                  <button
                    type="submit"
                    className="bg-emerald-500 text-white p-2 rounded-lg hover:bg-emerald-600 transition-colors"
                  >
                    <Send className="w-5 h-5" />
                  </button>
                </div>
              </form>

              {videos.length > 0 && (
                <div className="space-y-4 mb-8">
                  <h2 className="text-xl font-semibold text-white mb-4">Added Videos</h2>
                  {videos.map((video) => (
                    <div
                      key={video.id}
                      className="bg-gray-800 rounded-lg p-4 flex items-center justify-between"
                    >
                      <div className="flex items-center space-x-3">
                        <Youtube className="w-5 h-5 text-red-500" />
                        <span className="text-gray-300">{video.title}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {videos.length > 0 && (
                <button
                  onClick={() => setActiveTab('summary')}
                  className="w-full bg-emerald-500 text-white py-3 rounded-lg hover:bg-emerald-600 transition-colors flex items-center justify-center space-x-2"
                >
                  <span>Generate Summaries</span>
                  <ChevronRight className="w-5 h-5" />
                </button>
              )}
            </div>
          ) : (
            <div className="max-w-3xl mx-auto">
              <div className="bg-gray-800 rounded-lg p-6 mb-6">
                <h2 className="text-xl font-semibold text-white mb-4">Summary of Videos</h2>
                <div className="text-gray-300 space-y-4">
                  <p>This is where the AI-generated summary would appear...</p>
                </div>
              </div>

              <div className="bg-gray-800 rounded-lg p-6">
                <div className="flex items-center space-x-2 mb-4">
                  <MessageSquare className="w-5 h-5 text-emerald-500" />
                  <h2 className="text-xl font-semibold text-white">Ask Follow-up Questions</h2>
                </div>
                <div className="flex space-x-2">
                  <input
                    type="text"
                    placeholder="Type your question..."
                    className="flex-1 bg-gray-700 text-white rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                  />
                  <button className="bg-emerald-500 text-white p-2 rounded-lg hover:bg-emerald-600 transition-colors">
                    <Send className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default App;