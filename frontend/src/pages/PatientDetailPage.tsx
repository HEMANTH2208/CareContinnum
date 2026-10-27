import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { patientsAPI } from '../services/api';
import { Patient } from '../types';
import { ArrowLeft, Calendar, FileText, Pill, Activity } from 'lucide-react';
import { format } from 'date-fns';

const PatientDetailPage = () => {
  const { id } = useParams<{ id: string }>();
  const [patient, setPatient] = useState<Patient | null>(null);
  const [timeline, setTimeline] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('timeline');

  useEffect(() => {
    if (id) {
      loadPatientData();
    }
  }, [id]);

  const loadPatientData = async () => {
    try {
      const [patientRes, timelineRes] = await Promise.all([
        patientsAPI.get(Number(id)),
        patientsAPI.getTimeline(Number(id)),
      ]);

      setPatient(patientRes.data);
      setTimeline(timelineRes.data.events);
    } catch (error) {
      console.error('Failed to load patient:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center py-12">Loading patient data...</div>;
  }

  if (!patient) {
    return <div className="text-center py-12">Patient not found</div>;
  }

  const age = Math.floor(
    (Date.now() - new Date(patient.date_of_birth).getTime()) / (365.25 * 24 * 60 * 60 * 1000)
  );

  const getEventIcon = (type: string) => {
    switch (type) {
      case 'consultation':
        return <FileText size={20} className="text-blue-600" />;
      case 'appointment':
        return <Calendar size={20} className="text-green-600" />;
      case 'prescription':
        return <Pill size={20} className="text-purple-600" />;
      case 'follow_up_plan':
        return <Activity size={20} className="text-orange-600" />;
      default:
        return <FileText size={20} className="text-gray-600" />;
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <Link to="/patients" className="inline-flex items-center text-blue-600 hover:underline mb-4">
          <ArrowLeft size={20} className="mr-1" />
          Back to Patients
        </Link>
        <h1 className="text-2xl font-semibold text-gray-900">{patient.full_name}</h1>
        <p className="text-gray-600">Patient ID: {patient.patient_id}</p>
      </div>

      {/* Patient Info Card */}
      <div className="card">
        <h2 className="text-lg font-semibold mb-4">Patient Information</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div>
            <p className="text-sm text-gray-600">Age / Gender</p>
            <p className="font-medium">{age} years / {patient.gender}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Phone</p>
            <p className="font-medium">{patient.phone}</p>
          </div>
          {patient.email && (
            <div>
              <p className="text-sm text-gray-600">Email</p>
              <p className="font-medium">{patient.email}</p>
            </div>
          )}
          {patient.last_visit_date && (
            <div>
              <p className="text-sm text-gray-600">Last Visit</p>
              <p className="font-medium">
                {format(new Date(patient.last_visit_date), 'MMM dd, yyyy')}
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <div className="flex space-x-6">
          <button
            onClick={() => setActiveTab('timeline')}
            className={`pb-3 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'timeline'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            Timeline
          </button>
          <button
            onClick={() => setActiveTab('follow-ups')}
            className={`pb-3 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'follow-ups'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            Follow-ups
          </button>
        </div>
      </div>

      {/* Timeline */}
      {activeTab === 'timeline' && (
        <div className="card">
          <h2 className="text-lg font-semibold mb-4">Patient Timeline</h2>
          {timeline.length === 0 ? (
            <p className="text-gray-500 text-sm">No events recorded yet</p>
          ) : (
            <div className="space-y-4">
              {timeline.map((event, idx) => (
                <div key={idx} className="flex space-x-4">
                  <div className="flex flex-col items-center">
                    <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center">
                      {getEventIcon(event.event_type)}
                    </div>
                    {idx < timeline.length - 1 && (
                      <div className="w-0.5 h-full bg-gray-200 mt-2" />
                    )}
                  </div>
                  <div className="flex-1 pb-6">
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="font-medium text-gray-900">{event.title}</p>
                        <p className="text-sm text-gray-600 mt-1">{event.description}</p>
                      </div>
                      <span className="text-sm text-gray-500 whitespace-nowrap ml-4">
                        {format(new Date(event.event_date), 'MMM dd, yyyy')}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Follow-ups Tab */}
      {activeTab === 'follow-ups' && (
        <div className="card">
          <h2 className="text-lg font-semibold mb-4">Active Follow-up Plans</h2>
          <p className="text-gray-500 text-sm">Follow-up plans will be displayed here</p>
        </div>
      )}
    </div>
  );
};

export default PatientDetailPage;
