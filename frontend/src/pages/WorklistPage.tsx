import { useEffect, useState } from 'react';
import { followUpsAPI } from '../services/api';
import { PriorityWorklistItem } from '../types';
import { AlertCircle, Clock, Phone } from 'lucide-react';
import { format } from 'date-fns';

const WorklistPage = () => {
  const [worklist, setWorklist] = useState<PriorityWorklistItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedDepartment, setSelectedDepartment] = useState<string>('');

  useEffect(() => {
    loadWorklist();
  }, [selectedDepartment]);

  const loadWorklist = async () => {
    try {
      const params = selectedDepartment ? { department: selectedDepartment } : {};
      const response = await followUpsAPI.getPriorityWorklist(params);
      setWorklist(response.data);
    } catch (error) {
      console.error('Failed to load worklist:', error);
    } finally {
      setLoading(false);
    }
  };

  const getPriorityColor = (score: number) => {
    if (score >= 100) return 'bg-red-100 text-red-800 border-red-200';
    if (score >= 50) return 'bg-orange-100 text-orange-800 border-orange-200';
    if (score >= 20) return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    return 'bg-blue-100 text-blue-800 border-blue-200';
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Priority Worklist</h1>
          <p className="text-gray-600">
            Explainable prioritization of unresolved follow-up cases
          </p>
        </div>
        <select
          value={selectedDepartment}
          onChange={(e) => setSelectedDepartment(e.target.value)}
          className="input w-64"
        >
          <option value="">All Departments</option>
          <option value="Laboratory">Laboratory</option>
          <option value="Radiology">Radiology</option>
          <option value="Patient Coordination">Patient Coordination</option>
        </select>
      </div>

      {loading ? (
        <div className="text-center py-12">Loading worklist...</div>
      ) : worklist.length === 0 ? (
        <div className="card text-center py-12">
          <p className="text-gray-500">No priority tasks at this time</p>
        </div>
      ) : (
        <div className="space-y-4">
          {worklist.map((item, idx) => (
            <div
              key={item.task.id}
              className={`card border-l-4 ${getPriorityColor(item.score)}`}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <span className="text-2xl font-bold text-gray-400">#{idx + 1}</span>
                    <h3 className="text-lg font-semibold">{item.task.title}</h3>
                    <span className={`badge ${getPriorityColor(item.score)}`}>
                      Priority Score: {item.score}
                    </span>
                  </div>
                  {item.task.description && (
                    <p className="text-sm text-gray-600 mb-2">{item.task.description}</p>
                  )}
                </div>
              </div>

              {/* Task Details */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-3 text-sm">
                <div className="flex items-center space-x-2">
                  <Clock size={16} className="text-gray-400" />
                  <div>
                    <p className="text-gray-600">Due Date</p>
                    <p className="font-medium">
                      {format(new Date(item.task.due_date), 'MMM dd, yyyy')}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Phone size={16} className="text-gray-400" />
                  <div>
                    <p className="text-gray-600">Contact Attempts</p>
                    <p className="font-medium">{item.task.contact_attempts}</p>
                  </div>
                </div>
                <div>
                  <p className="text-gray-600">Status</p>
                  <span
                    className={`badge ${
                      item.task.status === 'escalated'
                        ? 'badge-escalated'
                        : item.task.is_overdue
                        ? 'badge-overdue'
                        : 'badge-pending'
                    }`}
                  >
                    {item.task.status}
                  </span>
                </div>
              </div>

              {/* Reasons */}
              <div className="mb-3">
                <p className="text-sm font-medium text-gray-700 mb-2">Priority Reasons:</p>
                <div className="space-y-1">
                  {item.reasons.map((reason, idx) => (
                    <div key={idx} className="flex items-start space-x-2 text-sm">
                      <AlertCircle size={16} className="text-orange-500 mt-0.5 flex-shrink-0" />
                      <p className="text-gray-700">{reason}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Next Action */}
              <div className="pt-3 border-t border-gray-200">
                <p className="text-sm font-medium text-gray-700 mb-1">Next Action:</p>
                <p className="text-sm text-blue-600 font-medium">→ {item.next_action}</p>
              </div>

              {/* Action Buttons */}
              <div className="flex space-x-2 mt-4">
                <button className="btn btn-primary text-sm">Assign to Me</button>
                <button className="btn btn-secondary text-sm">Contact Patient</button>
                <button className="btn btn-secondary text-sm">View Details</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default WorklistPage;
