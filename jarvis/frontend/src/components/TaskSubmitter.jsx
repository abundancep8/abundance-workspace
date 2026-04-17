import React, { useState } from 'react'

const TaskSubmitter = ({ onSubmit }) => {
  const [selectedTask, setSelectedTask] = useState('lead_gen')
  const [content, setContent] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const tasks = [
    { type: 'lead_gen', label: '🎯 Generate Leads', description: 'Find qualified prospects' },
    { type: 'sales', label: '📈 Sales Pipeline', description: 'Manage deals and forecasts' },
    { type: 'research', label: '📚 Research', description: 'Deep analysis and insights' },
    { type: 'remember', label: '💾 Remember', description: 'Store knowledge and decisions' },
    { type: 'schedule', label: '📅 Schedule Meeting', description: 'Book appointments' }
  ]

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!content.trim()) return

    setSubmitting(true)
    try {
      await onSubmit(selectedTask, content, {
        timestamp: new Date().toISOString(),
        user_initiated: true
      })
      setContent('')
    } catch (error) {
      console.error('Submit error:', error)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="task-submitter">
      <h3>✨ Task Submitter</h3>
      
      <form onSubmit={handleSubmit}>
        {/* Task Type Selection */}
        <div className="task-selector">
          {tasks.map((task) => (
            <button
              key={task.type}
              type="button"
              className={`task-btn ${selectedTask === task.type ? 'active' : ''}`}
              onClick={() => setSelectedTask(task.type)}
              title={task.description}
            >
              {task.label}
            </button>
          ))}
        </div>

        {/* Content Input */}
        <div className="input-group">
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder={`Describe your ${tasks.find(t => t.type === selectedTask)?.label.toLowerCase() || 'task'}...`}
            rows={4}
            disabled={submitting}
          />
        </div>

        {/* Submit Button */}
        <div className="submit-group">
          <button
            type="submit"
            className="submit-btn"
            disabled={!content.trim() || submitting}
          >
            {submitting ? '⏳ Processing...' : '🚀 Submit'}
          </button>
        </div>
      </form>

      {/* Task Hints */}
      <div className="task-hints">
        <p><strong>💡 Tips:</strong></p>
        <ul>
          <li>Be specific about what you want</li>
          <li>Add context for better results</li>
          <li>Tasks route to cost-optimal AI model</li>
        </ul>
      </div>
    </div>
  )
}

export default TaskSubmitter
