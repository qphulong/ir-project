import { useEffect, useState } from 'react'
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Send } from 'lucide-react'

interface InputAreaProps {
  onSendMessage: (content: string) => void
  preprocessedQuery: string | null
  disabled?: boolean
}

export function InputArea({ onSendMessage, preprocessedQuery, disabled }: InputAreaProps) {
  const [input, setInput] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (input.trim() === '') return
    onSendMessage(input)
    setInput('')
  }

  useEffect(() => {
    if (preprocessedQuery) {
      setInput(preprocessedQuery)
    }
  }, [preprocessedQuery]);

  return (
    <form onSubmit={handleSubmit} className="p-4 border-t bg-white">
      <div className="flex space-x-2">
        <Textarea
          placeholder="Type your message here..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="flex-grow"
          rows={1}
          disabled={disabled}
        />
        <Button type="submit" disabled={disabled}>
          <Send className="h-4 w-4" />
          <span className="sr-only">Send</span>
        </Button>
      </div>
    </form>
  )
}

