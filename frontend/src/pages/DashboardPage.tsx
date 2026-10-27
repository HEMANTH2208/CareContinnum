import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { analyticsAPI, appointmentsAPI, followUpsAPI } from '../services/api';
import { Analytics, Appointment, PriorityWorklistItem } from '../types';
import { AlertCircle, Calendar, ClipboardList, TrendingUp, Users } from 'lucide-react';
import { format } from 'date-fns';

const DashboardPage = () => {
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [upcomingAppointments, setUpcomingAppointments] = useState<Appointment[]>([]);
  const [priorityTasks, setPriorityTasks] = useState<PriorityWorklistItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [analyticsRes, appointmentsRes, worklistRes] = await Promise.all([
        analyticsAPI.getDashboard(),
        appointmentsAPI.list({ limit: 5 }),
        followUpsAPI.getPriorityWorklist({ limit: 5 }),
      ]);

      setAnalytics(analyticsRes.data);
      setUpcomingAppointments(appointmentsRes.data);
      setPriorityTasks(worklistRes.data);
    } catch (error) {
      console.error('Failed to load dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center py-12">Loading dashboard...</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">Dashboard</h1>
        <p className="text-gray-600">Overview of follow-up management metrics</p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Patients</p>
              <p className="text-2xl font-semibold mt-1">
                {analytics?.patients.total || 0}
              </p>
            </div>
            <Users className="text-blue-600" size={32} />
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Overdue Tasks</p>
              <p className="text-2xl font-semibold mt-1 text-red-600">
                {analytics?.follow_ups.overdue || 0}
              </p>
            </div>
            <AlertCircle className="text-red-600" size={32} />
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Completion Rate</p>
              <p className="text-2xl font-semibold mt-1 text-green-600">
                {analytics?.follow_ups.completion_rate.toFixed(1) || 0}%
              </p>
            </div>
            <TrendingUp className="text-green-600" size={32} />
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Escalated Cases</p>
              <p className="text-2xl font-semibold mt-1 text-purple-600">
                {analytics?.follow_ups.escalated || 0}
              </p>
            </div>
            <ClipboardList className="text-purple-600" size={32} />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upcoming Appointments */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Upcoming Appointments</h2>
            <Link to="/appointments" className="text-sm text-blue-600 hover:underline">
              View all
            </Link>
          </div>

          {upcomingAppointments.length === 0 ? (
            <p className="text-gray-500 text-sm">No upcoming appointments</p>
          ) : (
            <div className="space-y-3">
              {upcomingAppointments.map((apt) => (
                <div key={apt.id} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-md">
                  <Calendar className="text-gray-400 mt-1" size={20} />
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-sm">
                      {format(new Date(apt.scheduled_date), 'MMM dd, yyyy HH:mm')}
                    </p>
                    <p className="text-sm text-gray-600 capitalize">
                      {apt.appointment_type.replace('_', ' ')}
                    </p>
                    <span
                      className={`badge ${
                        apt.status === 'confirmed'
                          ? 'badge-completed'
                          : apt.status === 'missed'
                          ? 'badge-overdue'
                          : 'badge-scheduled'
                      }`}
                    >
                      {apt.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Priority Worklist */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Priority Worklist</h2>
            <Link to="/worklist" className="text-sm text-blue-600 hover:underline">
              View all
            </Link>
          </div>

          {priorityTasks.length === 0 ? (
            <p className="text-gray-500 text-sm">No priority tasks</p>
          ) : (
            <div className="space-y-3">
              {priorityTasks.map((item) => (
                <div key={item.task.id} className="p-3 bg-gray-50 rounded-md">
                  <div className="flex items-start justify-between mb-2">
                    <p className="font-medium text-sm">{item.task.title}</p>
                    <span className="badge badge-overdue ml-2">
                      Score: {item.score}
                    </span>
                  </div>
                  <div className="text-xs text-gray-600 space-y-1">
                    {item.reasons.map((reason, idx) => (
                      <p key={idx}>• {reason}</p>
                    ))}
                  </div>
                  <p className="text-xs font-medium text-blue-600 mt-2">
                    → {item.next_action}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Staff Workload */}
      {analytics && analytics.staff_workload.length > 0 && (
        <div className="card">
          <h2 className="text-lg font-semibold mb-4">Staff Workload by Department</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {analytics.staff_workload.map((dept, idx) => (
              <div key={idx} className="p-4 bg-gray-50 rounded-md">
                <p className="text-sm font-medium text-gray-900">{dept.department}</p>
                <p className="text-2xl font-semibold text-blue-600 mt-1">
                  {dept.active_tasks}
                </p>
                <p className="text-xs text-gray-500">active tasks</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default DashboardPage;
