import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { patientsAPI } from '../services/api';
import { Patient } from '../types';
import { Search, Plus, ChevronRight } from 'lucide-react';
import { format } from 'date-fns';

const PatientsPage = () => {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPatients();
  }, [search]);

  const loadPatients = async () => {
    try {
      const params = search ? { search } : {};
      const response = await patientsAPI.list(params);
      setPatients(response.data);
    } catch (error) {
      console.error('Failed to load patients:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Patients</h1>
          <p className="text-gray-600">Manage patient records and timelines</p>
        </div>
        <button className="btn btn-primary flex items-center space-x-2">
          <Plus size={20} />
          <span>Register Patient</span>
        </button>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
        <input
          type="text"
          placeholder="Search by name, ID, phone, or email..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="input pl-10"
        />
      </div>

      {/* Patients List */}
      <div className="card">
        {loading ? (
          <p className="text-center py-8 text-gray-500">Loading patients...</p>
        ) : patients.length === 0 ? (
          <p className="text-center py-8 text-gray-500">
            {search ? 'No patients found' : 'No patients registered yet'}
          </p>
        ) : (
          <div className="divide-y divide-gray-200">
            {patients.map((patient) => (
              <Link
                key={patient.id}
                to={`/patients/${patient.id}`}
                className="flex items-center justify-between p-4 hover:bg-gray-50 transition-colors"
              >
                <div className="flex-1">
                  <div className="flex items-center space-x-3">
                    <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                      <span className="text-blue-600 font-semibold text-lg">
                        {patient.full_name.charAt(0)}
                      </span>
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">{patient.full_name}</p>
                      <p className="text-sm text-gray-600">ID: {patient.patient_id}</p>
                    </div>
                  </div>
                  <div className="mt-2 flex items-center space-x-6 text-sm text-gray-600">
                    <span>{patient.gender}</span>
                    <span>{patient.phone}</span>
                    {patient.email && <span>{patient.email}</span>}
                    {patient.last_visit_date && (
                      <span>
                        Last visit: {format(new Date(patient.last_visit_date), 'MMM dd, yyyy')}
                      </span>
                    )}
                  </div>
                </div>
                <ChevronRight className="text-gray-400" size={20} />
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default PatientsPage;
