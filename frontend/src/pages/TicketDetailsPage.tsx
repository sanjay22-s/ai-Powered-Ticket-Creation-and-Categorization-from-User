/**
 * Ticket details: editable status/priority/category, assign to me, notes.
 */
import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { getTicket, updateTicket, addTicketNote, assignTicket } from '../services/api'
import { useAuth } from '../context/AuthContext'
import type { TicketDetail, TicketUpdatePayload } from '../types'
import { PriorityBadge } from '../components/PriorityBadge'
import { TicketForm } from '../components/TicketForm'
import { NotesSection } from '../components/NotesSection'

export function TicketDetailsPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { user } = useAuth()
  const [ticket, setTicket] = useState<TicketDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [addingNote, setAddingNote] = useState(false)

  const loadTicket = async () => {
    if (!id) return
    setLoading(true)
    try {
      const { data } = await getTicket(Number(id))
      setTicket(data)
    } catch {
      toast.error('Ticket not found')
      navigate('/')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadTicket()
  }, [id])

  const handleUpdate = async (payload: TicketUpdatePayload) => {
    if (!ticket) return
    setSaving(true)
    try {
      const { data } = await updateTicket(ticket.id, payload)
      setTicket(data)
      toast.success('Ticket updated')
    } catch {
      toast.error('Failed to update ticket')
    } finally {
      setSaving(false)
    }
  }

  const handleAddNote = async (note: string) => {
    if (!ticket) return
    setAddingNote(true)
    try {
      await addTicketNote(ticket.id, note)
      await loadTicket()
      toast.success('Note added')
    } catch {
      toast.error('Failed to add note')
    } finally {
      setAddingNote(false)
    }
  }

  const handleAssignToMe = async () => {
    if (!ticket || !user) return
    setSaving(true)
    try {
      const { data } = await assignTicket(ticket.id, user.id)
      setTicket(data)
      toast.success('Assigned to you')
    } catch {
      toast.error('Failed to assign')
    } finally {
      setSaving(false)
    }
  }

  if (loading || !ticket) {
    return (
      <div className="flex justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent" />
      </div>
    )
  }

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="flex items-center justify-between">
        <button
          type="button"
          onClick={() => navigate('/')}
          className="text-sm text-slate-600 hover:text-primary-600"
        >
          ← Back to dashboard
        </button>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
        <div className="p-6 border-b border-slate-200">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h1 className="text-xl font-bold text-slate-800">{ticket.title}</h1>
              <p className="text-sm text-slate-500 mt-1">ID: {ticket.id}</p>
            </div>
            <PriorityBadge priority={ticket.priority} />
          </div>
          {ticket.description && (
            <p className="mt-4 text-slate-600 text-sm whitespace-pre-wrap">{ticket.description}</p>
          )}
          <div className="mt-4 flex flex-wrap gap-4 text-sm text-slate-500">
            <span>Created: {new Date(ticket.created_at).toLocaleString()}</span>
            {ticket.creator_name && <span>By: {ticket.creator_name}</span>}
            {ticket.assignee_name && <span>Assigned: {ticket.assignee_name}</span>}
          </div>
        </div>

        <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-8">
          <div>
            <h2 className="font-semibold text-slate-800 mb-3">Details</h2>
            <TicketForm ticket={ticket} onUpdate={handleUpdate} saving={saving} />
            <div className="mt-4">
              <button
                type="button"
                onClick={handleAssignToMe}
                disabled={saving || ticket.assigned_to === user?.id}
                className="px-4 py-2 bg-primary-600 text-white text-sm font-medium rounded-lg hover:bg-primary-700 disabled:opacity-50"
              >
                {ticket.assigned_to === user?.id ? 'Assigned to you' : 'Assign to me'}
              </button>
            </div>
          </div>
          <div>
            <NotesSection
              notes={ticket.notes}
              onAddNote={handleAddNote}
              adding={addingNote}
            />
          </div>
        </div>
      </div>
    </div>
  )
}
