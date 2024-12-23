'use client'
import { useState, useEffect } from 'react'
import { Sidebar } from './sidebar'
import { RightSidebar } from './right-sidebar'
import { ChatArea } from './chat-area'
import { InputArea } from './input-area'
import { PanelLeftOpen, PanelLeftClose, PanelRightOpen, PanelRightClose } from 'lucide-react'
import { Button } from "@/components/ui/button"
import useWebSocket, { ReadyState } from "react-use-websocket"

export interface Message {
  id: number
  content: string
  role: 'user' | 'assistant'
}

export interface Conversation {
  id: number
  title: string
  messages: Message[]
}

interface Document {
  id: number
  snippet: string
  content: string
}

enum QueryState {
  NONE,
  SEARCHING_LOCAL,
  SEARCHING_INTERNET,
  PENDING,
  SUCCESS,
  ERROR
}

export default function ChatInterface() {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null)
  const [leftSidebarOpen, setLeftSidebarOpen] = useState(true)
  const [isTyping, setIsTyping] = useState(false)
  const [rightSidebarOpen, setRightSidebarOpen] = useState(true)
  const [isInputAreaDisabled, setIsInputAreaDisabled] = useState(false)
  const { sendJsonMessage, lastJsonMessage, readyState } = useWebSocket("ws://localhost:4000/api/process-query", {
    share: true
  });

  // State to hold documents returned from the API
  const [documents, setDocuments] = useState<Document[]>([])
  // Control whether documents are shown in the right sidebar
  const [showDocuments, setShowDocuments] = useState(true);
  // State to hold the preprocessed query
  const [preprocessedQuery, setPreprocessedQuery] = useState<string | null>(null);

  useEffect(() => {
    if (readyState === ReadyState.OPEN) {
      console.log("WebSocket connection established");
    }
  }, [readyState]);
  
  useEffect(() => {
    if (lastJsonMessage && currentConversation) {
      const message = lastJsonMessage as any;
      switch (message.state) {
        case QueryState.SEARCHING_LOCAL:
          setIsTyping(true);
          break;
        case QueryState.SUCCESS:
          const assistantMessage: Message = {
            id: currentConversation.messages.length + 1,
            content: message.result.final_response,
            role: 'assistant'
          }
    
          const updatedConversation = {
            ...currentConversation,
            messages: [...currentConversation.messages, assistantMessage]
          }
    
          setCurrentConversation(updatedConversation)
          setConversations(conversations.map(conv =>
            conv.id === currentConversation.id ? updatedConversation : conv
          ))
    
          // Process documents returned by the API
          if (message.result.texts && message.result.texts.documents) {
            const newDocuments: Document[] = message.result.texts.documents.map((doc: string, index: number) => ({
              id: message.result.texts.fragment_ids[index],
              snippet: doc
            }))
            setDocuments(newDocuments)
          }
          setIsTyping(false)
          break;
        case QueryState.ERROR:
          const errorMessage: Message = {
            id: currentConversation.messages.length + 1,
            content: "I'm sorry, I encountered an error while processing your request.",
            role: 'assistant'
          }
          const finalConversation = {
            ...currentConversation,
            messages: [...currentConversation.messages, errorMessage]
          }
          setCurrentConversation(finalConversation)
          setConversations(conversations.map(conv =>
            conv.id === currentConversation.id ? finalConversation : conv
          ))
          setIsTyping(false)
          break;
      }
    }
  }, [lastJsonMessage]);

  useEffect(() => {
    const savedConversations = localStorage.getItem('conversations')
    if (savedConversations) {
      const parsedConversations = JSON.parse(savedConversations)
      setConversations(parsedConversations)
      if (parsedConversations.length > 0) {
        setCurrentConversation(parsedConversations[0])
      }
    } else {
      const initialConversation: Conversation = {
        id: 1,
        title: 'Welcome Chat',
        messages: [{ id: 1, content: "Hello! How can I assist you today?", role: 'assistant' }]
      }
      setConversations([initialConversation])
      setCurrentConversation(initialConversation)
    }
  }, [])

  useEffect(() => {
    if (conversations.length > 0) {
      localStorage.setItem('conversations', JSON.stringify(conversations))
      setIsInputAreaDisabled(false)
    } else {
      localStorage.removeItem('conversations')
      setIsInputAreaDisabled(true)
    }
  }, [conversations])

  const addMessage = async (content: string) => {
    if (!currentConversation) return

    setShowDocuments(true) // Show documents when a question is asked
    setDocuments([]) // Clear previous documents before fetching new ones

    const newMessage: Message = {
      id: currentConversation.messages.length + 1,
      content,
      role: 'user'
    }

    const updatedConversation = {
      ...currentConversation,
      messages: [...currentConversation.messages, newMessage]
    }

    setCurrentConversation(updatedConversation)
    setConversations(conversations.map(conv =>
      conv.id === currentConversation.id ? updatedConversation : conv
    ))

    sendJsonMessage({ query: content })
  }

  const startNewConversation = () => {
    const newConversation: Conversation = {
      id: conversations.length + 1,
      title: `New Chat ${conversations.length + 1}`,
      messages: []
    }
    setConversations([...conversations, newConversation])
    setCurrentConversation(newConversation)
    setShowDocuments(false)  // Reset showDocuments when starting a new conversation
    setDocuments([]) // Clear documents
  }

  const renameConversation = (id: number, newTitle: string) => {
    const updatedConversations = conversations.map(conv =>
      conv.id === id ? { ...conv, title: newTitle } : conv
    )
    setConversations(updatedConversations)
    if (currentConversation && currentConversation.id === id) {
      setCurrentConversation({ ...currentConversation, title: newTitle })
    }
  }

  const deleteConversation = (id: number) => {
    const updatedConversations = conversations.filter(conv => conv.id !== id)
    setConversations(updatedConversations)
    if (currentConversation && currentConversation.id === id) {
      setCurrentConversation(updatedConversations[0] || null)
    }
  }

  return (
    <div className="flex h-screen bg-gray-100 relative">
      <Sidebar
        conversations={conversations}
        currentConversation={currentConversation}
        setCurrentConversation={setCurrentConversation}
        startNewConversation={startNewConversation}
        renameConversation={renameConversation}
        deleteConversation={deleteConversation}
        isOpen={leftSidebarOpen}
        setShowDocuments={setShowDocuments}
        onPreprocessQuery={(query, action) => {
          if (action === 'append') {
            setPreprocessedQuery(preprocessedQuery ? `${preprocessedQuery} ${query}` : query)
          } else {
            setPreprocessedQuery(query)
          }
        }}
      />
      <Button
        variant="outline"
        size="icon"
        className={`fixed top-4 z-30 transition-all duration-300 ease-in-out ${
          leftSidebarOpen ? 'left-[260px]' : 'left-4'
        }`}
        onClick={() => setLeftSidebarOpen(!leftSidebarOpen)}
      >
        {leftSidebarOpen ? <PanelLeftClose className="h-4 w-4" /> : <PanelLeftOpen className="h-4 w-4" />}
        <span className="sr-only">{leftSidebarOpen ? 'Close left sidebar' : 'Open left sidebar'}</span>
      </Button>
      <div className={`flex flex-col flex-grow transition-all duration-300 ease-in-out ${
        leftSidebarOpen ? 'ml-64' : 'ml-0'
      } ${
        rightSidebarOpen ? 'mr-64' : 'mr-0'
      }`}>
        <ChatArea messages={currentConversation?.messages || []} isTyping={isTyping} />
        <InputArea onSendMessage={addMessage} preprocessedQuery={preprocessedQuery} disabled={isInputAreaDisabled}/>
      </div>
      <Button
        variant="outline"
        size="icon"
        className={`fixed top-4 right-4 z-30 transition-all duration-300 ease-in-out ${
          rightSidebarOpen ? 'right-[260px]' : 'right-4'
        }`}
        onClick={() => setRightSidebarOpen(!rightSidebarOpen)}
      >
        {rightSidebarOpen ? <PanelRightClose className="h-4 w-4" /> : <PanelRightOpen className="h-4 w-4" />}
        <span className="sr-only">{rightSidebarOpen ? 'Close right sidebar' : 'Open right sidebar'}</span>
      </Button>

      {/* Pass the dynamically fetched documents to the RightSidebar */}
      <RightSidebar documents={documents} isOpen={rightSidebarOpen} showDocuments={showDocuments}/>
    </div>
  )
}
