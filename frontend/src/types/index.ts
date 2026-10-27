export type UserRole = 'admin' | 'doctor' | 'staff' | 'patient';

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: UserRole;
  department?: string;
  is_active: boolean;
}

export interface Patient {
  id: number;
  patient_id: string;
  full_name: string;
  date_of_birth: string;
  gender: string;
  phone: string;
  email?: string;
  assigned_doctor_id?: number;
  last_visit_date?: string;
}

export interface Appointment {
  id: number;
  patient_id: number;
  doctor_id: number;
  appointment_type: string;
  scheduled_date: string;
  status: 'scheduled' | 'confirmed' | 'completed' | 'missed' | 'cancelled';
  department?: string;
  reschedule_count: number;
}

export interface FollowUpTask {
  id: number;
  plan_id: number;
  title: string;
  description?: string;
  task_type: string;
  status: 'pending' | 'scheduled' | 'in_progress' | 'completed' | 'blocked' | 'escalated';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  due_date: string;
  is_overdue: boolean;
  contact_attempts: number;
  escalation_reason?: string;
}

export interface FollowUpPlan {
  id: number;
  patient_id: number;
  doctor_id: number;
  title: string;
  description?: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  is_active: boolean;
  tasks: FollowUpTask[];
}

export interface Consultation {
  id: number;
  patient_id: number;
  doctor_id: number;
  consultation_type: string;
  consultation_date: string;
  chief_complaint?: string;
  diagnosis?: string;
  treatment_plan?: string;
}

export interface Prescription {
  id: number;
  prescription_number: string;
  patient_id: number;
  doctor_id: number;
  medications: string;
  status: string;
  issued_date: string;
  pdf_generated: boolean;
}

export interface Analytics {
  period: {
    from: string;
    to: string;
  };
  patients: {
    total: number;
  };
  appointments: {
    total: number;
    completed: number;
    missed: number;
    completion_rate: number;
    missed_rate: number;
  };
  follow_ups: {
    total: number;
    completed: number;
    overdue: number;
    escalated: number;
    completion_rate: number;
    avg_resolution_days: number;
  };
  notifications: {
    total: number;
    delivered: number;
    failed: number;
    delivery_rate: number;
  };
  staff_workload: Array<{
    department: string;
    active_tasks: number;
  }>;
}

export interface PriorityWorklistItem {
  task: FollowUpTask;
  score: number;
  reasons: string[];
  next_action: string;
}
