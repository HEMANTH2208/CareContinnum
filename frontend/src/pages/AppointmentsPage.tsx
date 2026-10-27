import { useEffect, useState } from 'react';
import { appointmentsAPI } from '../services/api';
import { Appointment } from '../types';
import { Calendar, Filter } from 'lucide-react';
import { format } from 'date-fns';

const AppointmentsPage = () => {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');

  useEffect(() => {
    loadAppointments();
  }, [statusFilter]);

  const loadAppointments = async () => {
    try {
      const params = statusFilter ? { status: statusFilter } : {};
      const response = await appointmentsAPI.list(params);
      setAppointments(response.data);
    } catch (error) {
      console.error('Failed to load appointments:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const badges: Record<string, string> = {
      scheduled: 'badge-scheduled',
      confirmed: 'badge-completed',
      completed: 'badge-completed',
      missed: 'badge-overdue',
      cancelled: 'badge-pending',
    };
    return badges[status] || 'badge-pending';
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Appointments</h1>
          <p className="text-gray-600">Manage patient appointments and scheduling</p>
        </div>
        <button className="btn btn-primary">Schedule Appointment</button>
      </div>

      {/* Filters */}
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-2">
          <Filter size={20} className="text-gray-400" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="input w-48"
          >
            <option value="">All Statuses</option>
            <option value="scheduled">Scheduled</option>
            <option value="confirmed">Confirmed</option>
            <option value="completed">Completed</option>
            <option value="missed">Missed</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </div>
      </div>

      {/* Appointments List */}
      <div className="card">
        {loading ? (
          <p className="text-center py-8 text-gray-500">Loading appointments...</p>
        ) : appointments.length === 0 ? (
          <p className="text-center py-8 text-gray-500">No appointments found</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">
                    Date & Time
                  </th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">
                    Patient
                  </th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">
                    Type
                  </th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">
                    Department
                  </th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">
                    Status
                  </th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">
                    Reschedules
                  </th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {appointments.map((apt) => (
                  <tr key={apt.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3">
                      <div className="flex items-center space-x-2">
                        <Calendar size={16} className="text-gray-400" />
                        <span className="text-sm">
                          {format(new Date(apt.scheduled_date), 'MMM dd, yyyy HH:mm')}
                        </span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-sm">Patient #{apt.patient_id}</td>
                    <td className="px-4 py-3 text-sm capitalize">
                      {apt.appointment_type.replace('_', ' ')}
                    </td>
                    <td className="px-4 py-3 text-sm">{apt.department || '-'}</td>
                    <td className="px-4 py-3">
                      <span className={`badge ${getStatusBadge(apt.status)}`}>
                        {apt.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-center">
                      {apt.reschedule_count > 0 && (
                        <span className="text-orange-600">{apt.reschedule_count}x</span>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      <button className="text-sm text-blue-600 hover:underline">
                        View
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default AppointmentsPage;
