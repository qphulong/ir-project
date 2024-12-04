import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { PlusCircle } from 'lucide-react'
import { Conversation } from './chat-interface'

interface SidebarProps {
  conversations: Conversation[]
  currentConversation: Conversation
  setCurrentConversation: (conversation: Conversation) => void
  startNewConversation: () => void
  isOpen: boolean
}

export function Sidebar({ 
  conversations, 
  currentConversation, 
  setCurrentConversation, 
  startNewConversation,
  isOpen
}: SidebarProps) {
  return (
    <div 
      className={`w-64 bg-gray-900 text-white p-4 flex flex-col h-full fixed left-0 top-0 bottom-0 transition-transform duration-300 ease-in-out ${
        isOpen ? 'translate-x-0' : '-translate-x-full'
      } z-20`}
    >
      <Button onClick={startNewConversation} className="mb-4">
        <PlusCircle className="mr-2 h-4 w-4" /> New Chat
      </Button>
      <ScrollArea className="flex-grow">
        {conversations.map((conversation) => (
          <Button
            key={conversation.id}
            variant={conversation.id === currentConversation.id ? "secondary" : "ghost"}
            className="w-full justify-start mb-2"
            onClick={() => setCurrentConversation(conversation)}
          >
            {conversation.title}
          </Button>
        ))}
      </ScrollArea>
    </div>
  )
}

