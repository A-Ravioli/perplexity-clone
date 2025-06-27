'use client'

import { useState, useRef, useEffect } from 'react'
import { Search, Send, Globe, Clock, ArrowRight } from 'lucide-react'
import axios from 'axios'

interface SearchResult {
  title: string
  url: string
  snippet: string
  domain: string
}

interface SearchResponse {
  query: string
  results: SearchResult[]
  ai_summary: string
  sources: string[]
  conversation_id: string
  timestamp: string
}

interface Message {
  type: 'user' | 'assistant'
  content: string
  results?: SearchResult[]
  sources?: string[]
  timestamp: Date
}

export default function Home() {
  const [query, setQuery] = useState('')
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [conversationId, setConversationId] = useState<string>('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const exampleQueries = [
    "What are the latest developments in AI?",
    "How does quantum computing work?",
    "What's happening in renewable energy?",
    "Explain the metaverse concept"
  ]

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`
    }
  }, [query])

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim() || isLoading) return

    const userMessage: Message = {
      type: 'user',
      content: query,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setQuery('')
    setIsLoading(true)

    try {
      const response = await axios.post<SearchResponse>('http://localhost:8000/search', {
        query: query,
        conversation_id: conversationId || undefined
      })

      const assistantMessage: Message = {
        type: 'assistant',
        content: response.data.ai_summary,
        results: response.data.results,
        sources: response.data.sources,
        timestamp: new Date()
      }

      setMessages(prev => [...prev, assistantMessage])
      setConversationId(response.data.conversation_id)
    } catch (error) {
      console.error('Search error:', error)
      const errorMessage: Message = {
        type: 'assistant',
        content: 'Sorry, I encountered an error while searching. Please make sure the backend server is running on port 8000.',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleExampleClick = (example: string) => {
    setQuery(example)
  }

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Header */}
      <header className="border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <Search className="w-4 h-4 text-white" />
            </div>
            <h1 className="text-xl font-semibold">Perplexity Clone</h1>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-8">
        {messages.length === 0 ? (
          /* Welcome Screen */
          <div className="text-center space-y-8">
            <div className="space-y-4">
              <h2 className="text-4xl font-bold">What can I help you discover?</h2>
              <p className="text-muted-foreground text-lg">
                                 Ask me anything and I&apos;ll search the web and provide you with comprehensive answers.
              </p>
            </div>

            {/* Example Queries */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-2xl mx-auto">
              {exampleQueries.map((example, index) => (
                <button
                  key={index}
                  onClick={() => handleExampleClick(example)}
                  className="p-4 text-left bg-card border border-border rounded-lg hover:bg-accent hover:text-accent-foreground transition-colors group"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-sm">{example}</span>
                    <ArrowRight className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" />
                  </div>
                </button>
              ))}
            </div>
          </div>
        ) : (
          /* Chat Interface */
          <div className="space-y-6">
            {messages.map((message, index) => (
              <div key={index} className={`space-y-4 ${message.type === 'user' ? 'ml-12' : ''}`}>
                <div className={`flex gap-4 ${message.type === 'user' ? 'justify-end' : ''}`}>
                  {message.type === 'assistant' && (
                    <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center flex-shrink-0">
                      <Search className="w-4 h-4 text-white" />
                    </div>
                  )}
                  
                  <div className={`space-y-3 flex-1 ${message.type === 'user' ? 'max-w-lg' : ''}`}>
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <Clock className="w-3 h-3" />
                      <span>{message.timestamp.toLocaleTimeString()}</span>
                    </div>
                    
                    <div className={`prose prose-gray dark:prose-invert max-w-none ${
                      message.type === 'user' 
                        ? 'bg-primary text-primary-foreground p-4 rounded-lg ml-auto' 
                        : 'bg-card p-4 rounded-lg border border-border'
                    }`}>
                      <p className="m-0 whitespace-pre-wrap">{message.content}</p>
                    </div>

                    {message.results && message.results.length > 0 && (
                      <div className="space-y-3">
                        <h4 className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                          <Globe className="w-4 h-4" />
                          Sources
                        </h4>
                        <div className="grid gap-3">
                          {message.results.map((result, resultIndex) => (
                            <div key={resultIndex} className="bg-card border border-border rounded-lg p-4 hover:bg-accent/50 transition-colors">
                              <a 
                                href={result.url} 
                                target="_blank" 
                                rel="noopener noreferrer"
                                className="block space-y-2"
                              >
                                <div className="flex items-start justify-between gap-2">
                                  <h5 className="font-medium text-sm line-clamp-2 hover:text-primary">
                                    {result.title}
                                  </h5>
                                  <span className="text-xs text-muted-foreground bg-muted px-2 py-1 rounded flex-shrink-0">
                                    {result.domain}
                                  </span>
                                </div>
                                <p className="text-sm text-muted-foreground line-clamp-3">
                                  {result.snippet}
                                </p>
                              </a>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="flex gap-4">
                <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                  <Search className="w-4 h-4 text-white animate-pulse" />
                </div>
                <div className="bg-card border border-border rounded-lg p-4 flex-1">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" />
                    <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                    <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                    <span className="text-sm text-muted-foreground ml-2">Searching...</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Search Input */}
        <div className={`${messages.length === 0 ? 'mt-8' : 'mt-6 sticky bottom-4'}`}>
          <form onSubmit={handleSearch} className="relative">
            <div className="relative bg-card border border-border rounded-2xl shadow-lg">
              <textarea
                ref={textareaRef}
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask anything..."
                className="w-full resize-none bg-transparent px-4 py-4 pr-12 text-sm focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 rounded-2xl"
                rows={1}
                style={{ minHeight: '56px' }}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault()
                    handleSearch(e)
                  }
                }}
              />
              <button
                type="submit"
                disabled={!query.trim() || isLoading}
                className="absolute right-3 top-1/2 -translate-y-1/2 w-8 h-8 bg-primary text-primary-foreground rounded-lg flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed hover:bg-primary/90 transition-colors"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </form>
        </div>
      </main>
    </div>
  )
}
