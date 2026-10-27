# CareContinuum - Complete Workflow Demonstration

This document guides you through demonstrating the complete workflow specified in the acceptance criteria.

## Prerequisites

Ensure the application is running with seeded sample data.

## Complete Workflow Steps

### Step 1: Staff Registers a Synthetic Patient

1. **Login as Staff:**
   - Go to http://localhost:5173
   - Login with: `staff1@carecontinuum.com` / `staff123`

2. **Register New Patient:**
   - Navigate to "Patients" from sidebar
   - Click "Register Patient"
   - Fill in patient details:
     - Full Name: John Smith
     - Date of Birth: 01/15/1975
     - Gender: Male
     - Phone: +1-555-1234
     - Email: john.smith@email.com
     - Assign to doctor (select Dr. Sarah Smith)
   - Click "Register"
   - Note the generated Patient ID (e.g., P2024000051)

### Step 2: Doctor Reviews Patient Timeline and Creates Follow-up Plan

1. **Login as Doctor:**
   - Logout and login with: `dr.smith@carecontinuum.com` / `doctor123`

2. **View Patient Timeline:**
   - Go to "Patients"
   - Search for "John Smith"
   - Click on patient name
   - Review the patient timeline (currently empty for new patient)

3. **Create Consultation:**
   - Click "New Consultation"
   - Fill consultation details:
     - Type: In-person
     - Chief Complaint: "Chest pain and shortness of breath"
     - Diagnosis: "Suspected coronary artery disease"
     - Treatment Plan: "Order ECG, blood tests, follow-up in 2 weeks"
   - Save consultation

4. **Create Follow-up Plan:**
   - Click "Create Follow-up Plan"
   - Plan Title: "Cardiac Investigation"
   - Priority: High
   - Add tasks:
     
     **Task 1:**
     - Title: "ECG Test"
     - Type: Imaging
     - Department: Radiology
     - Due Date: 2 days from now
     - Priority: High
     
     **Task 2:**
     - Title: "Blood Test - Lipid Profile"
     - Type: Lab Test
     - Department: Laboratory  
     - Due Date: 2 days from now
     - Priority: High
     - Dependencies: None
     
     **Task 3:**
     - Title: "Review Test Results"
     - Type: Consultation
     - Due Date: 7 days from now
     - Priority: Medium
     - Depends on: Task 1 and Task 2
   
   - Click "Create Plan"

### Step 3: System Assigns Checkups and Enforces Dependencies

**Backend automatically:**
- Creates the follow-up plan with 3 tasks
- Assigns tasks to specified departments
- Sets up dependency chain (Task 3 depends on Task 1 & 2)
- Marks Task 3 as BLOCKED until dependencies complete

**Verify:**
- Go to patient's timeline
- See follow-up plan with all tasks
- Note Task 3 shows "Blocked" status

### Step 4: Reminders are Scheduled

**Backend automatically:**
- Scheduler runs every 6 hours
- Finds appointments in next 48 hours
- Creates reminder notifications
- Schedules them for 24 hours before appointment

**Verify:**
- Check backend logs: `docker-compose logs backend | grep "reminder"`
- Should see: "Scheduled reminder for appointment X"

### Step 5: Missed Appointment Becomes Overdue

**Simulate by adjusting dates or waiting:**

**Option A - Wait (Real-time):**
Let scheduler run and detect overdue automatically after due date passes.

**Option B - Simulate (Development):**
1. Access database and manually set a task's due_date to past
2. Wait for scheduler cycle (runs every hour)
3. Task will be marked overdue

**Verify in Priority Worklist:**
- Login as Staff: `staff1@carecontinuum.com` / `staff123`
- Navigate to "Priority Worklist"
- See the overdue task at top of list
- Priority score will be high
- Reason: "Overdue by X days"

### Step 6: Failure Limits Trigger Staff Escalation

**Simulate missed appointment scenario:**

1. **Create Appointment:**
   - As staff, create appointment for patient
   - Schedule for today at earlier time (will auto-mark as missed)

2. **Trigger Reschedule Attempts:**
   - Reschedule appointment (1st attempt)
   - Reschedule again (2nd attempt - reaches limit)
   - System escalates associated follow-up task

3. **Verify Escalation:**
   - Go to "Priority Worklist"
   - Find escalated task
   - See badge: "Escalated"
   - Escalation reason: "Missed appointment, reschedule limit reached (2)"
   - Task appears at very top of worklist with highest score

**Alternative - Contact Attempts:**
- Update task contact_attempts to 5 (using API or database)
- Scheduler will auto-escalate on next cycle
- Escalation reason: "Multiple failed contact attempts (5)"

### Step 7: Staff Records Contact Outcome

1. **From Priority Worklist:**
   - Click "Assign to Me" on escalated task
   - Click "Contact Patient"
   - Record outcome:
     - Status: Successfully contacted
     - Notes: "Patient available, prefers morning appointments"
     - Next action: Reschedule

2. **Reschedule Appointment:**
   - Go to "Appointments"
   - Find patient's appointment
   - Click "Reschedule"
   - Select new date/time within patient preference
   - Add notes: "Rescheduled per patient request - morning slot"
   - Confirm

3. **Update Task Status:**
   - Update follow-up task status to "Scheduled"
   - Add notes about resolution
   - System removes from escalation list

### Step 8: Doctor Reviews AI Summary and Approves Prescription

1. **Generate AI Summary:**
   - Login as doctor
   - Open patient record
   - Click "Generate AI Summary"
   - Review summary showing:
     - Patient demographics
     - Chronic conditions
     - Recent consultations
     - Pending follow-ups
     - Missing information flags
   - Mark as "Reviewed"

2. **Create Prescription:**
   - Open recent consultation
   - Click "Create Prescription"
   - Add medications:
     
     **Medication 1:**
     - Name: Aspirin
     - Dosage: 75mg
     - Frequency: Once daily
     - Duration: 30 days
     - Instructions: Take with food
     
     **Medication 2:**
     - Name: Atorvastatin
     - Dosage: 20mg
     - Frequency: Once daily at bedtime
     - Duration: 30 days
     - Instructions: Avoid grapefruit
   
   - General Instructions: "Take medications as prescribed. Report any muscle pain or unusual symptoms immediately."
   - Dietary Advice: "Low-fat diet, reduce salt intake"
   - Click "Generate Prescription"

### Step 9: PDF Prescription is Generated

**System automatically:**
- Generates unique prescription number (e.g., RX2024000001)
- Creates professional PDF with:
  - Hospital letterhead
  - Patient information
  - Doctor information
  - Medication table
  - Instructions
  - Doctor signature section

**Verify:**
- Click "Download PDF"
- PDF opens with all details
- Professional formatting
- All medications listed correctly
- Clear instructions visible

**Patient Portal Access:**
- Prescription marked as available to patient
- Patient can view and download from their portal
- Secure access (patient login required)

### Step 10: Dashboards Display Metrics

1. **Navigate to Analytics:**
   - Go to "Analytics" page
   - View comprehensive metrics:

2. **Key Metrics Displayed:**
   - **Follow-up Completion Rate**: Calculated from actual DB records
   - **Overdue Rate**: Count of tasks past due date
   - **Missed Appointment Rate**: Percentage of missed vs total
   - **Notification Delivery Rate**: Successful deliveries / total sent
   - **Average Resolution Time**: Days from task creation to completion
   - **Staff Workload**: Active tasks by department

3. **Verify Data Accuracy:**
   - Check calculations match database
   - Filters work correctly (date range, department)
   - Trends display recent activity
   - Unresolved cases count matches worklist

### Step 11: Verify Security and Permissions

1. **Test Unauthorized Access:**
   - Logout
   - Try accessing patient page without login
   - Redirected to login page ✓

2. **Test Role-Based Access:**
   - Login as staff
   - Try accessing "Users" page
   - Should see "403 Forbidden" or no menu option ✓
   
3. **Test Data Access:**
   - Staff cannot create prescriptions ✓
   - Patients cannot access admin functions ✓
   - Doctors can create follow-up plans ✓

### Step 12: Verify Duplicate Prevention

1. **Duplicate Notification Prevention:**
   - Check database: only one reminder per appointment
   - Scheduler skips if reminder already sent

2. **Duplicate Task Prevention:**
   - Workflow transitions are transactional
   - No duplicate status changes from concurrent requests

### Step 13: Audit Trail Verification

**Check audit logs recorded:**
- Patient registration
- Follow-up plan creation
- Prescription generation
- Task status changes
- User logins

**Verify logs contain:**
- User ID who performed action
- Action type
- Resource type and ID
- Timestamp
- Additional context

### Step 14: Background Job Monitoring

1. **Check Scheduler Status:**
   ```bash
   docker-compose logs backend | grep "Scheduler"
   ```
   Should show:
   - Scheduler started with 4 jobs
   - Jobs running at configured intervals
   - No errors in job execution

2. **Verify Job Results:**
   - Overdue tasks flagged correctly
   - Missed appointments detected
   - Notifications processed
   - Reminders scheduled

3. **Failed Job Retry:**
   - If notification fails, attempt count increments
   - Retries up to max attempts
   - Failed jobs identifiable in database
   - Can be manually retried

## Success Criteria Checklist

- [x] Staff registers synthetic patient
- [x] Doctor reviews timeline and creates follow-up plan
- [x] System assigns checkups with dependencies
- [x] Reminders scheduled with delivery tracking
- [x] Missed appointment becomes overdue
- [x] Failure limits trigger escalation with explanation
- [x] Staff records contact outcome
- [x] Doctor reviews AI summary and approves prescription
- [x] PDF prescription generated and secured
- [x] Dashboards show accurate metrics from DB
- [x] Unauthorized access blocked
- [x] Duplicate prevention working
- [x] Audit trail captured
- [x] Background jobs running reliably

## Additional Verification

### API Testing

Test endpoints directly:
```bash
# Get dashboard analytics
curl http://localhost:8000/api/v1/analytics/dashboard \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get priority worklist
curl http://localhost:8000/api/v1/follow-ups/worklist/priority \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Database Verification

Check data integrity:
```bash
# Access database
docker-compose exec postgres psql -U carecontinuum

# Verify task dependencies
SELECT id, title, status, depends_on_task_id FROM follow_up_tasks;

# Check escalation tracking
SELECT id, title, is_overdue, escalated_at, escalation_reason 
FROM follow_up_tasks 
WHERE status = 'escalated';

# Verify audit logs
SELECT user_id, action, resource_type, timestamp 
FROM audit_logs 
ORDER BY timestamp DESC LIMIT 10;
```

## Performance Check

- Dashboard loads in <2 seconds
- Patient timeline renders quickly with 50+ events
- Priority worklist calculates in <1 second
- No N+1 queries (check backend logs)
- Pagination works for large datasets

## Conclusion

This workflow demonstrates all critical features:
- ✓ Complete patient journey from registration to prescription
- ✓ Automated workflow management with dependencies
- ✓ Explainable prioritization of unresolved cases
- ✓ Deterministic escalation based on configured limits
- ✓ Doctor-controlled clinical decisions
- ✓ Professional prescription generation
- ✓ Accurate analytics from real data
- ✓ Security and audit trail
- ✓ Background job automation
- ✓ No duplicate operations

The system successfully prevents missed follow-ups while keeping clinical decisions under authorized human control.
