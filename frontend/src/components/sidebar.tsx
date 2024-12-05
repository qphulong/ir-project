import { useState } from 'react'
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { PlusCircle, Pencil, Trash2 } from 'lucide-react'
import { Conversation } from './chat-interface'
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

  if (!isOpen) return null

  return (
    <div className={`w-64 bg-gray-900 text-white p-4 flex flex-col h-full transition-all duration-300 ease-in-out fixed left-0 top-0 bottom-0 z-20`}>
      <Button onClick={startNewConversation} className="mb-4">
        <PlusCircle className="mr-2 h-4 w-4" /> New Chat
      </Button>
      <ScrollArea className="flex-grow">
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
  )
}
