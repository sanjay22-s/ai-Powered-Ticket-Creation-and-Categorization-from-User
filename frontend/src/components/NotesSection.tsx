/**
 * Add note form and notes history for a ticket.
 */
import type { TicketNote } from '../types'

interface NotesSectionProps {
  notes: TicketNote[]
  onAddNote: (note: string) => void
  adding?: boolean
}

export function NotesSection({ notes, onAddNote, adding }: NotesSectionProps) {
  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const form = e.currentTarget
    const input = form.querySelector('textarea') as HTMLTextAreaElement
    const value = input?.value?.trim()
    if (value) {
      onAddNote(value)
      input.value = ''
    }
  }

  return (
    <div className="space-y-4">
      <h3 className="font-semibold text-slate-800">Internal notes</h3>
      <form onSubmit={handleSubmit}>
        <textarea
          name="note"
          rows={3}
          placeholder="Add an internal note..."
          disabled={adding}
          className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 resize-none"
        />
        <button
          type="submit"
          disabled={adding}
          className="mt-2 px-4 py-2 bg-primary-600 text-white text-sm font-medium rounded-lg hover:bg-primary-700 disabled:opacity-50"
        >
          {adding ? 'Adding...' : 'Add note'}
        </button>
      </form>
      <div className="space-y-3">
        {notes.length === 0 ? (
          <p className="text-sm text-slate-500">No notes yet.</p>
        ) : (
          notes.map((n) => (
            <div
              key={n.id}
              className="rounded-lg border border-slate-200 bg-slate-50 p-3 text-sm"
            >
              <p className="text-slate-700 whitespace-pre-wrap">{n.note}</p>
              <p className="text-xs text-slate-500 mt-2">
                {n.agent_name ?? 'Agent'} · {new Date(n.created_at).toLocaleString()}
              </p>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
