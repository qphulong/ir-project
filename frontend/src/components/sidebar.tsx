import { Conversation } from './chat-interface'

import { useState, useRef, useEffect } from 'react'
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { PlusCircle, Pencil, Trash2, Search } from 'lucide-react'
// import { Conversation } from './chatgpt-like-interface'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Input } from "@/components/ui/input"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogClose,
} from "@/components/ui/dialog"

interface SidebarProps {
  conversations: Conversation[]
  currentConversation: Conversation | null
  setCurrentConversation: (conversation: Conversation) => void
  startNewConversation: () => void
  renameConversation: (id: number, newTitle: string) => void
  deleteConversation: (id: number) => void
  isOpen: boolean
}

export function Sidebar({ 
  conversations, 
  currentConversation, 
  setCurrentConversation, 
  startNewConversation,
  renameConversation,
  deleteConversation,
  isOpen
}: SidebarProps) {
  const [editingId, setEditingId] = useState<number | null>(null)
  const [newTitle, setNewTitle] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<string[]>([])
  const searchResultsRef = useRef<HTMLUListElement>(null)

  useEffect(() => {
    if (searchResultsRef.current) {
      searchResultsRef.current.scrollTop = 0
    }
  }, [searchResults])

  if (!isOpen) return null

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (searchQuery.trim() === '') {
      setSearchResults([])
      return
    }
    
    // Simulated search results
    const results = [
      `What is the best way to learn ${searchQuery}?`,
      `What are the most effective methods to learn ${searchQuery}?`,
      `How can I learn ${searchQuery} effectively?`,
      `Top resources for learning ${searchQuery}`,
      `${searchQuery} for beginners: where to start?`,
      `Advanced techniques in ${searchQuery}`,
      `${searchQuery} vs other similar topics`,
      `Career opportunities with ${searchQuery} skills`,
      `Common mistakes when learning ${searchQuery}`,
      `How long does it take to master ${searchQuery}?`
    ]
    setSearchResults(results)
  }

  return (
    <div className="w-64 bg-gray-900 text-white flex flex-col h-full transition-all duration-300 ease-in-out fixed left-0 top-0 bottom-0 z-20">
      <div className="p-4 flex-grow overflow-hidden flex flex-col">
        <Button onClick={startNewConversation} className="mb-4">
          <PlusCircle className="mr-2 h-4 w-4" /> New Chat
        </Button>
        <ScrollArea className="flex-grow mb-4">
          {conversations.map((conversation) => (
            <div key={conversation.id} className="mb-2 flex items-center">
              <Button
                variant={conversation.id === currentConversation?.id ? "secondary" : "ghost"}
                className="w-full justify-start mr-2 text-left"
                onClick={() => setCurrentConversation(conversation)}
              >
                {conversation.title}
              </Button>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="icon" className="h-8 w-8">
                    <Pencil className="h-4 w-4" />
                    <span className="sr-only">Edit</span>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <Dialog>
                    <DialogTrigger asChild>
                      <DropdownMenuItem onSelect={(e) => e.preventDefault()}>
                        Rename
                      </DropdownMenuItem>
                    </DialogTrigger>
                    <DialogContent>
                      <DialogHeader>
                        <DialogTitle>Rename Conversation</DialogTitle>
                      </DialogHeader>
                      <Input
                        value={newTitle}
                        onChange={(e) => setNewTitle(e.target.value)}
                        placeholder="Enter new title"
                      />
                      <DialogClose asChild>
                        <Button onClick={() => {
                          if (newTitle.trim() !== '') {
                            renameConversation(conversation.id, newTitle)
                            setNewTitle('')
                          }
                        }}>
                          Save
                        </Button>
                      </DialogClose>
                    </DialogContent>
                  </Dialog>
                  <DropdownMenuItem onSelect={() => deleteConversation(conversation.id)}>
                    Delete
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          ))}
        </ScrollArea>
      </div>
      <div className="p-4 border-t border-gray-700">
        <form onSubmit={handleSearchSubmit} className="relative mb-2">
          <Input
            type="text"
            placeholder="Search..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-gray-800 text-white placeholder-gray-400 border-gray-700"
          />
          <Search className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
        </form>
        {searchResults.length > 0 && (
          <ScrollArea className="h-40 overflow-y-auto">
            <ul ref={searchResultsRef} className="space-y-1">
              {searchResults.map((result, index) => (
                <li key={index} className="text-sm text-gray-300 hover:bg-gray-800 p-1 rounded">
                  {result}
                </li>
              ))}
            </ul>
          </ScrollArea>
        )}
      </div>
    </div>
  )
}


