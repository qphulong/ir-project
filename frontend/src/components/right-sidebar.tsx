import { useEffect, useState } from 'react'
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { api } from '@/api'
import { Spinner } from '@/components/ui/spinner'
import { DialogDescription } from '@radix-ui/react-dialog'

interface Document {
  id: number
  snippet: string
}

interface RightSidebarProps {
  documents: Document[]
  isOpen: boolean
  showDocuments: boolean
}

const NO_TEXT_AVAILABLE = "No text available";

export function RightSidebar({ documents, isOpen, showDocuments }: RightSidebarProps) {
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [text, setText] = useState<string | null>(null);

  async function getText() {
    try {
      const response = await api.get(`/api/texts/${selectedDocument?.id}`);
      setText(response.data.text);
    } catch (error) {
      console.error(error);
      setText(NO_TEXT_AVAILABLE);
    }
  }

  useEffect(() => {
    setText(null);
    if (selectedDocument) {
      getText();
    }
  }, [selectedDocument]);

  if (!isOpen) return null

  return (
    <div className="w-64 bg-gray-100 text-gray-800 flex flex-col h-full transition-all duration-300 ease-in-out fixed right-0 top-0 bottom-0 z-20">
      <div className="p-4 flex-grow overflow-hidden flex flex-col">
        <h2 className="text-lg font-semibold mb-4">Documents</h2>
        {showDocuments && documents.length > 0 ? (
          <ScrollArea className="flex-grow">
            {documents.map((doc) => (
              <Dialog key={doc.id}>
                <DialogTrigger asChild>
                  <Button
                    variant="ghost"
                    className="w-full justify-start h-full text-left hover:bg-gray-200"
                    onClick={() => setSelectedDocument(doc)}
                  >
                    <div className='line-clamp-3 text-wrap'>{doc.snippet}</div>
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-h-[80vh] w-full sm:max-w-lg">
                  <DialogHeader>
                    <DialogTitle>Document Details</DialogTitle>
                    <DialogDescription></DialogDescription>
                  </DialogHeader>
                  {/* Make the dialog content scrollable */}
                  {text ?
                  <ScrollArea className="mt-4 max-h-[60vh]">
                    <p className="whitespace-pre-line	text-justify">{text}</p>
                  </ScrollArea> : 
                  <div className="flex items-center justify-center">
                    <Spinner />
                  </div>}
                </DialogContent>
              </Dialog>
            ))}
          </ScrollArea>
        ) : (
          <p className="text-center text-gray-500">Ask a question to see relevant documents.</p>
        )}
      </div>
    </div>
  )
}
