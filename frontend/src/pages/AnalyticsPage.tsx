import { useEffect, useState } from 'react';
import { analyticsAPI } from '../services/api';
import { Analytics } from '../types';
import { TrendingUp, TrendingDown, Activity } from 'lucide-react';

const AnalyticsPage = () => {
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      const response = await analyticsAPI.getDashboard();
      setAnalytics(response.data);
    } catch (error) {
      console.error('Failed to load analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center py-12">Loading analytics...</div>;
  }

  if (!analytics) {
    return <div className="text-center py-12">Failed to load analytics</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">Analytics</h1>
        <p className="text-gray-600">
          Performance metrics and insights for follow-up management
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-600">Follow-up Completion Rate</h3>
            <Activity className="text-green-600" size={20} />
          </div>
          <p className="text-3xl font-bold text-gray-900">
            {analytics.follow_ups.completion_rate.toFixed(1)}%
          </p>
          <p className="text-sm text-gray-600 mt-2">
            {analytics.follow_ups.completed} of {analytics.follow_ups.total} tasks completed
          </p>
        </div>

        <div className="card">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-600">Missed Appointment Rate</h3>
            <TrendingDown className="text-red-600" size={20} />
          </div>
          <p className="text-3xl font-bold text-gray-900">
            {analytics.appointments.missed_rate.toFixed(1)}%
          </p>
          <p className="text-sm text-gray-600 mt-2">
            {analytics.appointments.missed} of {analytics.appointments.total} appointments
          </p>
        </div>

        <div className="card">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-600">Notification Delivery Rate</h3>
            <TrendingUp className="text-blue-600" size={20} />
          </div>
          <p className="text-3xl font-bold text-gray-900">
            {analytics.notifications.delivery_rate.toFixed(1)}%
          </p>
          <p className="text-sm text-gray-600 mt-2">
            {analytics.notifications.delivered} of {analytics.notifications.total} delivered
          </p>
        </div>
      </div>

      {/* Detailed Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Follow-up Metrics</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Total Tasks</span>
              <span className="font-semibold">{analytics.follow_ups.total}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Completed</span>
              <span className="font-semibold text-green-600">
                {analytics.follow_ups.completed}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Overdue</span>
              <span className="font-semibold text-red-600">
                {analytics.follow_ups.overdue}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Escalated</span>
              <span className="font-semibold text-purple-600">
                {analytics.follow_ups.escalated}
              </span>
            </div>
            <div className="flex justify-between pt-3 border-t">
              <span className="text-gray-600">Avg Resolution Time</span>
              <span className="font-semibold">
                {analytics.follow_ups.avg_resolution_days} days
              </span>
            </div>
          </div>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Appointment Metrics</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Total Appointments</span>
              <span className="font-semibold">{analytics.appointments.total}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Completed</span>
              <span className="font-semibold text-green-600">
                {analytics.appointments.completed}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Missed</span>
              <span className="font-semibold text-red-600">
                {analytics.appointments.missed}
              </span>
            </div>
            <div className="flex justify-between pt-3 border-t">
              <span className="text-gray-600">Completion Rate</span>
              <span className="font-semibold">
                {analytics.appointments.completion_rate.toFixed(1)}%
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Staff Workload */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Staff Workload by Department</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {analytics.staff_workload.map((dept, idx) => (
            <div key={idx} className="p-4 bg-gray-50 rounded-lg">
              <p className="text-sm font-medium text-gray-700">{dept.department}</p>
              <p className="text-2xl font-bold text-blue-600 mt-2">{dept.active_tasks}</p>
              <p className="text-xs text-gray-500 mt-1">active tasks</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default AnalyticsPage;
