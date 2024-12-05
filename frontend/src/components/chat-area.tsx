import React from 'react';
import { ScrollArea } from "@/components/ui/scroll-area"
import { Message } from './chat-interface'


interface ChatAreaProps {
  messages: Message[]
  isTyping: boolean
}

export function ChatArea({ messages, isTyping }: ChatAreaProps) {
  return (
    <ScrollArea className="flex-grow p-4 space-y-4">
      {messages.map((message) => (
        <div
          key={message.id}
          className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
        >
          <div
            className={`max-w-[70%] rounded-lg p-3 ${
              message.role === 'user'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-200 text-gray-800'
            }`}
          >
            {message.content}
          </div>
        </div>
      ))}
      {isTyping && (
        <div className="flex justify-start">
          <div className="max-w-[70%] rounded-lg p-3 bg-gray-200 text-gray-800">
            <div className="typing-animation">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      )}
    </ScrollArea>
  )
}