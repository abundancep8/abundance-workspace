import React, { useState, useEffect } from 'react'
import axios from 'axios'

const Dashboard = ({ tasks }) => {
  const [budget, setBudget] = useState(null)
  const [costSummary, setCostSummary] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
    const interval = setInterval(fetchDashboardData, 5000) // Refresh every 5s
    return () => clearInterval(interval)
  }, [])

  const fetchDashboardData = async () => {
    try {
      const [budgetRes, dashRes] = await Promise.all([
        axios.get('/api/cost/budget'),
        axios.get('/api/dashboard')
      ])
      
      setBudget(budgetRes.data)
      setCostSummary(dashRes.data.cost_summary)
      setLoading(false)
    } catch (error) {
      console.error('Dashboard fetch error:', error)
    }
  }

  if (loading) {
    return <div className="dashboard">⏳ Loading dashboard...</div>
  }

  return (
    <div className="dashboard">
      <h3>📊 Real-Time Dashboard</h3>

      {/* Budget Status */}
      {budget && (
        <div className="dashboard-card budget-card">
          <h4>💰 Budget Status</h4>
          <div className="budget-bar">
            <div
              className="budget-used"
              style={{ width: `${budget.percent_used}%` }}
            ></div>
          </div>
          <div className="budget-stats">
            <span>${budget.spent.toFixed(2)} / ${budget.daily_budget}</span>
            <span className={`status-indicator ${budget.status.includes('healthy') ? 'green' : 'red'}`}>
              {budget.status}
            </span>
          </div>
          <p className="text-muted">Remaining: ${budget.remaining.toFixed(2)}</p>
        </div>
      )}

      {/* Cost Summary */}
      {costSummary && (
        <div className="dashboard-card cost-card">
          <h4>📈 Cost Summary</h4>
          <div className="cost-breakdown">
            {Object.entries(costSummary.by_model || {}).map(([model, data]) => (
              <div key={model} className="cost-item">
                <span className="model-label">{model.toUpperCase()}</span>
                <span className="cost-value">{data.count} tasks • ${data.cost.toFixed(2)}</span>
              </div>
            ))}
          </div>
          <p className="text-muted">
            Avg: ${costSummary.average_cost_per_task?.toFixed(4)}/task
          </p>
          {costSummary.estimated_savings && (
            <p className="savings">
              ✅ Savings: ${costSummary.estimated_savings.toFixed(2)}/day
            </p>
          )}
        </div>
      )}

      {/* Recent Tasks */}
      <div className="dashboard-card tasks-card">
        <h4>✨ Recent Tasks ({tasks.length})</h4>
        <div className="tasks-list">
          {tasks.slice(-5).map((task) => (
            <div key={task.task_id} className={`task-item ${task.status}`}>
              <div className="task-header">
                <span className="task-id">{task.task_id.substring(0, 12)}</span>
                <span className={`task-status ${task.status}`}>
                  {task.status === 'completed' ? '✅' : '❌'}
                </span>
              </div>
              <div className="task-details">
                <span>Model: {task.model_used}</span>
                <span>${task.cost.toFixed(4)}</span>
              </div>
            </div>
          ))}
          {tasks.length === 0 && (
            <p className="text-muted">No tasks yet</p>
          )}
        </div>
      </div>

      {/* System Status */}
      <div className="dashboard-card system-card">
        <h4>🤖 System Status</h4>
        <div className="system-status">
          <div className="status-item">
            <span>Chief of Staff</span>
            <span className="status-dot green">●</span>
          </div>
          <div className="status-item">
            <span>Neural Router</span>
            <span className="status-dot green">●</span>
          </div>
          <div className="status-item">
            <span>Voice Handler</span>
            <span className="status-dot green">●</span>
          </div>
          <div className="status-item">
            <span>Service Automation</span>
            <span className="status-dot green">●</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
