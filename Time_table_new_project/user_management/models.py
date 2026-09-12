from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group


class User(AbstractUser):
    ROLE_LABELS = {
        'admin': 'Administrator',
        'hoi': 'Head of Institution',
        'hod': 'Head of Department',
        'faculty': 'Faculty',
    }

    phone = models.BigIntegerField(null=True, blank=True)
    campus = models.CharField(max_length=100, null=True, blank=True)
    college_code = models.CharField(max_length=100, null=True, blank=True)
    dept_code = models.CharField(max_length=100, null=True, blank=True)
    designation_code = models.CharField(max_length=100, null=True, blank=True)
    dept_email = models.EmailField(null=True, blank=True)
    emp_id = models.CharField(max_length=100, null=True, blank=True)
    emp_type = models.CharField(max_length=100, null=True, blank=True)
    doj = models.DateField(null=True, blank=True)
    groups = models.ManyToManyField(
        Group,
        verbose_name=('groups'),
        blank=True,
        help_text=(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="user_set",
        related_query_name="user",
        through="UserGroups"
    )

    class Meta:
        db_table = "users"

    def __str__(self):
        return str(self.id)

    def get_active_membership(self):
        """The UserGroups row that decides which dashboard this user sees.

        A user can have several UserGroups rows (e.g. HOD of CSE + Faculty of
        IT), so 'active' is narrowed down in two steps:
        1. never consider a blocked membership (is_block=True)
        2. prefer the one marked is_default=True; if none is default, fall
           back to the first active one.
        """
        return (
            self.memberships.filter(is_active=True, is_block=False, is_default=True).first()
            or self.memberships.filter(is_active=True, is_block=False).first()
        )

    def get_role(self):
        membership = self.get_active_membership()
        return membership.role.lower() if membership else None

    @property
    def role(self):
        return self.get_role()

    def get_role_display(self):
        return self.ROLE_LABELS.get(self.role, 'User')


class UserGroups(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memberships')
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    role = models.CharField(max_length=50)
    is_active = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)
    is_block = models.BooleanField(default=False)

    class Meta:
        db_table = "user_groups"

    def __str__(self):
        return f"{self.user_id} - {self.role}"


class EmployeeMaster(models.Model):
    empid = models.CharField(db_column='EMPID', primary_key=True, max_length=25)  # Field name made lowercase.
    emp_name = models.CharField(db_column='EMP_NAME', max_length=500, blank=True,
                                null=True)  # Field name made lowercase.
    gender = models.CharField(db_column='GENDER', max_length=1, blank=True, null=True)  # Field name made lowercase.
    designation = models.CharField(db_column='DESIGNATION', max_length=500, blank=True,
                                   null=True)  # Field name made lowercase.
    job_description = models.CharField(db_column='JOB_DESCRIPTION', max_length=500, blank=True,
                                       null=True)  # Field name made lowercase.
    father_name = models.CharField(db_column='FATHER_NAME', max_length=500, blank=True,
                                   null=True)  # Field name made lowercase.
    category = models.CharField(db_column='CATEGORY', max_length=50, blank=True,
                                null=True)  # Field name made lowercase.
    doorno = models.CharField(db_column='DOORNO', max_length=500, blank=True, null=True)  # Field name made lowercase.
    location = models.CharField(db_column='LOCATION', max_length=500, blank=True,
                                null=True)  # Field name made lowercase.
    city = models.CharField(db_column='CITY', max_length=500, blank=True, null=True)  # Field name made lowercase.
    state = models.CharField(db_column='STATE', max_length=500, blank=True, null=True)  # Field name made lowercase.
    nation = models.CharField(db_column='NATION', max_length=500, blank=True, null=True)  # Field name made lowercase.
    pincode = models.CharField(db_column='PINCODE', max_length=50, blank=True, null=True)  # Field name made lowercase.
    phone1 = models.CharField(db_column='PHONE1', max_length=120, blank=True, null=True)  # Field name made lowercase.
    phone2 = models.CharField(db_column='PHONE2', max_length=120, blank=True, null=True)  # Field name made lowercase.
    mobile = models.CharField(db_column='MOBILE', max_length=120, blank=True, null=True)  # Field name made lowercase.
    emailid = models.CharField(db_column='EMAILID', max_length=500, blank=True, null=True)  # Field name made lowercase.
    dob = models.DateTimeField(db_column='DOB', blank=True, null=True)  # Field name made lowercase.
    doj = models.DateTimeField(db_column='DOJ', blank=True, null=True)  # Field name made lowercase.
    exp_details = models.CharField(db_column='EXP_DETAILS', max_length=5000, blank=True,
                                   null=True)  # Field name made lowercase.
    phd_description = models.CharField(db_column='PHD_DESCRIPTION', max_length=5000, blank=True,
                                       null=True)  # Field name made lowercase.
    achievements = models.CharField(db_column='ACHIEVEMENTS', max_length=5000, blank=True,
                                    null=True)  # Field name made lowercase.
    specialization = models.CharField(db_column='SPECIALIZATION', max_length=5000, blank=True,
                                      null=True)  # Field name made lowercase.
    emp_type = models.CharField(db_column='EMP_TYPE', max_length=3, blank=True, null=True)  # Field name made lowercase.
    panno = models.CharField(db_column='PANNO', max_length=500, blank=True, null=True)  # Field name made lowercase.
    pfno = models.CharField(db_column='PFNO', max_length=500, blank=True, null=True)  # Field name made lowercase.
    dept_name = models.CharField(db_column='DEPT_NAME', max_length=300, blank=True,
                                 null=True)  # Field name made lowercase.
    dept_code = models.CharField(db_column='DEPT_CODE', max_length=50, blank=True,
                                 null=True)  # Field name made lowercase.
    emp_status = models.CharField(db_column='EMP_STATUS', max_length=1, blank=True,
                                  null=True)  # Field name made lowercase.
    incharge_code = models.CharField(db_column='INCHARGE_CODE', max_length=50, blank=True,
                                     null=True)  # Field name made lowercase.
    ssc_year = models.CharField(db_column='SSC_YEAR', max_length=15, blank=True,
                                null=True)  # Field name made lowercase.
    ssc_marks = models.CharField(db_column='SSC_MARKS', max_length=15, blank=True,
                                 null=True)  # Field name made lowercase.
    ssc_percentage = models.CharField(db_column='SSC_PERCENTAGE', max_length=15, blank=True,
                                      null=True)  # Field name made lowercase.
    ssc_board = models.CharField(db_column='SSC_BOARD', max_length=1000, blank=True,
                                 null=True)  # Field name made lowercase.
    inter_year = models.CharField(db_column='INTER_YEAR', max_length=15, blank=True,
                                  null=True)  # Field name made lowercase.
    inter_marks = models.CharField(db_column='INTER_MARKS', max_length=15, blank=True,
                                   null=True)  # Field name made lowercase.
    inter_percentage = models.CharField(db_column='INTER_PERCENTAGE', max_length=15, blank=True,
                                        null=True)  # Field name made lowercase.
    inter_board = models.CharField(db_column='INTER_BOARD', max_length=1000, blank=True,
                                   null=True)  # Field name made lowercase.
    degree_year = models.CharField(db_column='DEGREE_YEAR', max_length=15, blank=True,
                                   null=True)  # Field name made lowercase.
    degree_marks = models.CharField(db_column='DEGREE_MARKS', max_length=15, blank=True,
                                    null=True)  # Field name made lowercase.
    degree_percentage = models.CharField(db_column='DEGREE_PERCENTAGE', max_length=15, blank=True,
                                         null=True)  # Field name made lowercase.
    degree_university = models.CharField(db_column='DEGREE_UNIVERSITY', max_length=1000, blank=True,
                                         null=True)  # Field name made lowercase.
    pg_year = models.CharField(db_column='PG_YEAR', max_length=15, blank=True, null=True)  # Field name made lowercase.
    pg_marks = models.CharField(db_column='PG_MARKS', max_length=15, blank=True,
                                null=True)  # Field name made lowercase.
    pg_percentage = models.CharField(db_column='PG_PERCENTAGE', max_length=15, blank=True,
                                     null=True)  # Field name made lowercase.
    pg_university = models.CharField(db_column='PG_UNIVERSITY', max_length=1000, blank=True,
                                     null=True)  # Field name made lowercase.
    college_code = models.CharField(db_column='COLLEGE_CODE', max_length=25, blank=True,
                                    null=True)  # Field name made lowercase.
    campus = models.CharField(db_column='CAMPUS', max_length=25, blank=True, null=True)  # Field name made lowercase.
    experience = models.CharField(max_length=5000, blank=True, null=True)
    bank_acno = models.CharField(db_column='BANK_ACNO', max_length=100, blank=True,
                                 null=True)  # Field name made lowercase.
    bank_name = models.CharField(db_column='BANK_NAME', max_length=500, blank=True,
                                 null=True)  # Field name made lowercase.
    job_status = models.CharField(db_column='JOB_STATUS', max_length=1, blank=True,
                                  null=True)  # Field name made lowercase.
    mgr_id = models.CharField(db_column='MGR_ID', max_length=250, blank=True, null=True)  # Field name made lowercase.
    retired_flag = models.CharField(db_column='RETIRED_FLAG', max_length=1, blank=True,
                                    null=True)  # Field name made lowercase.
    retired_date = models.DateTimeField(db_column='RETIRED_DATE', blank=True, null=True)  # Field name made lowercase.
    emp_age = models.CharField(db_column='EMP_AGE', max_length=25, blank=True, null=True)  # Field name made lowercase.
    gratuity_flag = models.CharField(db_column='GRATUITY_FLAG', max_length=1, blank=True,
                                     null=True)  # Field name made lowercase.
    gratuity_id = models.CharField(db_column='GRATUITY_ID', max_length=250, blank=True,
                                   null=True)  # Field name made lowercase.
    pfno_order = models.IntegerField(blank=True, null=True)
    marital_status = models.CharField(db_column='MARITAL_STATUS', max_length=500, blank=True,
                                      null=True)  # Field name made lowercase.
    father_occupation = models.CharField(db_column='FATHER_OCCUPATION', max_length=500, blank=True,
                                         null=True)  # Field name made lowercase.
    present_doorno = models.CharField(db_column='PRESENT_DOORNO', max_length=500, blank=True,
                                      null=True)  # Field name made lowercase.
    present_location = models.CharField(db_column='PRESENT_LOCATION', max_length=500, blank=True,
                                        null=True)  # Field name made lowercase.
    present_city = models.CharField(db_column='PRESENT_CITY', max_length=200, blank=True,
                                    null=True)  # Field name made lowercase.
    present_state = models.CharField(db_column='PRESENT_STATE', max_length=200, blank=True,
                                     null=True)  # Field name made lowercase.
    present_nation = models.CharField(db_column='PRESENT_NATION', max_length=200, blank=True,
                                      null=True)  # Field name made lowercase.
    present_pincode = models.CharField(db_column='PRESENT_PINCODE', max_length=150, blank=True,
                                       null=True)  # Field name made lowercase.
    phd_title = models.CharField(db_column='PHD_TITLE', max_length=550, blank=True,
                                 null=True)  # Field name made lowercase.
    phd_university = models.CharField(db_column='PHD_UNIVERSITY', max_length=150, blank=True,
                                      null=True)  # Field name made lowercase.
    phd_year = models.CharField(db_column='PHD_YEAR', max_length=150, blank=True,
                                null=True)  # Field name made lowercase.
    phd_percentage = models.CharField(db_column='PHD_PERCENTAGE', max_length=150, blank=True,
                                      null=True)  # Field name made lowercase.
    additional_qual_title = models.CharField(db_column='ADDITIONAL_QUAL_TITLE', max_length=150, blank=True,
                                             null=True)  # Field name made lowercase.
    additional_qual_university = models.CharField(db_column='ADDITIONAL_QUAL_UNIVERSITY', max_length=150, blank=True,
                                                  null=True)  # Field name made lowercase.
    additional_qual_year = models.CharField(db_column='ADDITIONAL_QUAL_YEAR', max_length=150, blank=True,
                                            null=True)  # Field name made lowercase.
    additional_qual_percentage = models.CharField(db_column='ADDITIONAL_QUAL_PERCENTAGE', max_length=150, blank=True,
                                                  null=True)  # Field name made lowercase.
    transport_vehicle = models.CharField(db_column='TRANSPORT_VEHICLE', max_length=150, blank=True,
                                         null=True)  # Field name made lowercase.
    transport_type = models.CharField(db_column='TRANSPORT_TYPE', max_length=150, blank=True,
                                      null=True)  # Field name made lowercase.
    transport_no = models.CharField(db_column='TRANSPORT_NO', max_length=150, blank=True,
                                    null=True)  # Field name made lowercase.
    service_in_gitam = models.CharField(db_column='SERVICE_IN_GITAM', max_length=150, blank=True,
                                        null=True)  # Field name made lowercase.
    outside_service = models.CharField(db_column='OUTSIDE_SERVICE', max_length=150, blank=True,
                                       null=True)  # Field name made lowercase.
    present_scale = models.CharField(db_column='PRESENT_SCALE', max_length=150, blank=True,
                                     null=True)  # Field name made lowercase.
    increment_date = models.DateTimeField(db_column='INCREMENT_DATE', blank=True,
                                          null=True)  # Field name made lowercase.
    promotion_date = models.DateTimeField(db_column='PROMOTION_DATE', blank=True,
                                          null=True)  # Field name made lowercase.
    desgn_before_promotion = models.CharField(db_column='DESGN_BEFORE_PROMOTION', max_length=150, blank=True,
                                              null=True)  # Field name made lowercase.
    desgn_after_promotion = models.CharField(db_column='DESGN_AFTER_PROMOTION', max_length=150, blank=True,
                                             null=True)  # Field name made lowercase.
    curr_post_totservice = models.CharField(db_column='CURR_POST_TOTSERVICE', max_length=150, blank=True,
                                            null=True)  # Field name made lowercase.
    transfer_date = models.DateTimeField(db_column='TRANSFER_DATE', blank=True, null=True)  # Field name made lowercase.
    from_establishment = models.CharField(db_column='FROM_ESTABLISHMENT', max_length=150, blank=True,
                                          null=True)  # Field name made lowercase.
    to_establishment = models.CharField(db_column='TO_ESTABLISHMENT', max_length=150, blank=True,
                                        null=True)  # Field name made lowercase.
    curr_establishment_totservice = models.CharField(db_column='CURR_ESTABLISHMENT_TOTSERVICE', max_length=150,
                                                     blank=True, null=True)  # Field name made lowercase.
    displinary_action_taken = models.CharField(db_column='DISPLINARY_ACTION_TAKEN', max_length=150, blank=True,
                                               null=True)  # Field name made lowercase.
    training_program1 = models.CharField(db_column='TRAINING_PROGRAM1', max_length=200, blank=True,
                                         null=True)  # Field name made lowercase.
    training_program2 = models.CharField(db_column='TRAINING_PROGRAM2', max_length=200, blank=True,
                                         null=True)  # Field name made lowercase.
    training_program3 = models.CharField(db_column='TRAINING_PROGRAM3', max_length=200, blank=True,
                                         null=True)  # Field name made lowercase.
    curriculam_activity1 = models.CharField(db_column='CURRICULAM_ACTIVITY1', max_length=200, blank=True,
                                            null=True)  # Field name made lowercase.
    curriculam_activity2 = models.CharField(db_column='CURRICULAM_ACTIVITY2', max_length=200, blank=True,
                                            null=True)  # Field name made lowercase.
    curriculam_activity3 = models.CharField(db_column='CURRICULAM_ACTIVITY3', max_length=200, blank=True,
                                            null=True)  # Field name made lowercase.
    health_problem = models.CharField(db_column='HEALTH_PROBLEM', max_length=300, blank=True,
                                      null=True)  # Field name made lowercase.
    strengths = models.CharField(db_column='STRENGTHS', max_length=300, blank=True,
                                 null=True)  # Field name made lowercase.
    weaknesses = models.CharField(db_column='WEAKNESSES', max_length=300, blank=True,
                                  null=True)  # Field name made lowercase.
    additional_info = models.TextField(db_column='ADDITIONAL_INFO', blank=True, null=True)  # Field name made lowercase.
    other_info = models.CharField(db_column='OTHER_INFO', max_length=500, blank=True,
                                  null=True)  # Field name made lowercase.
    subject = models.CharField(db_column='SUBJECT', max_length=500, blank=True, null=True)  # Field name made lowercase.
    incr_due_date = models.DateTimeField(db_column='INCR_DUE_DATE', blank=True, null=True)  # Field name made lowercase.
    service_ext_date = models.DateTimeField(db_column='SERVICE_EXT_DATE', blank=True,
                                            null=True)  # Field name made lowercase.
    desig_order = models.IntegerField(db_column='DESIG_ORDER', blank=True, null=True)  # Field name made lowercase.
    pf_flag = models.CharField(db_column='PF_FLAG', max_length=1, blank=True, null=True)  # Field name made lowercase.
    user_id = models.CharField(db_column='USER_ID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    dt_time = models.DateTimeField(db_column='DT_TIME', blank=True, null=True)  # Field name made lowercase.
    nominee = models.CharField(db_column='NOMINEE', max_length=300, blank=True, null=True)  # Field name made lowercase.
    nominee_relation = models.CharField(db_column='NOMINEE_RELATION', max_length=300, blank=True,
                                        null=True)  # Field name made lowercase.
    program_type = models.CharField(db_column='PROGRAM_TYPE', max_length=200, blank=True,
                                    null=True)  # Field name made lowercase.
    old_pfno = models.CharField(db_column='OLD_PFNO', max_length=50, blank=True,
                                null=True)  # Field name made lowercase.
    qualification = models.CharField(db_column='QUALIFICATION', max_length=500, blank=True,
                                     null=True)  # Field name made lowercase.
    research = models.CharField(db_column='RESEARCH', max_length=5000, blank=True,
                                null=True)  # Field name made lowercase.
    email1 = models.CharField(db_column='EMAIL1', max_length=350, blank=True, null=True)  # Field name made lowercase.
    email2 = models.CharField(db_column='EMAIL2', max_length=300, blank=True, null=True)  # Field name made lowercase.
    profile = models.CharField(db_column='PROFILE', max_length=500, blank=True, null=True)  # Field name made lowercase.
    web_order = models.IntegerField(db_column='WEB_ORDER', blank=True, null=True)  # Field name made lowercase.
    imp_phone_flag = models.CharField(db_column='IMP_PHONE_FLAG', max_length=1, blank=True,
                                      null=True)  # Field name made lowercase.
    top_mgmt_flag = models.CharField(db_column='TOP_MGMT_FLAG', max_length=5, blank=True,
                                     null=True)  # Field name made lowercase.
    bom_web_order = models.IntegerField(db_column='BOM_WEB_ORDER', blank=True, null=True)  # Field name made lowercase.
    director_web_order = models.IntegerField(db_column='DIRECTOR_WEB_ORDER', blank=True,
                                             null=True)  # Field name made lowercase.
    emp_photo_path = models.CharField(db_column='EMP_PHOTO_PATH', max_length=350, blank=True,
                                      null=True)  # Field name made lowercase.
    emp_job_role = models.CharField(db_column='EMP_JOB_ROLE', max_length=500, blank=True,
                                    null=True)  # Field name made lowercase.
    content_type = models.CharField(db_column='CONTENT_TYPE', max_length=50, blank=True,
                                    null=True)  # Field name made lowercase.
    subjects_taught = models.CharField(max_length=1000, blank=True, null=True)
    web_dept_code = models.CharField(max_length=150, blank=True, null=True)
    web_dept_name = models.CharField(max_length=150, blank=True, null=True)
    web_college_code = models.CharField(max_length=25, blank=True, null=True)
    web_campus = models.CharField(max_length=25, blank=True, null=True)
    area_of_interest = models.CharField(max_length=2000, blank=True, null=True)
    placement_role = models.CharField(max_length=1, blank=True, null=True)
    placement_web_order = models.IntegerField(blank=True, null=True)
    id = models.IntegerField(db_column='ID')  # Field name made lowercase.
    permanent_address = models.CharField(db_column='PERMANENT_ADDRESS', max_length=5000, blank=True,
                                         null=True)  # Field name made lowercase.
    present_address = models.CharField(db_column='PRESENT_ADDRESS', max_length=5000, blank=True,
                                       null=True)  # Field name made lowercase.
    religion = models.CharField(db_column='RELIGION', max_length=100, blank=True,
                                null=True)  # Field name made lowercase.
    web_designation1 = models.CharField(db_column='WEB_DESIGNATION1', max_length=100, blank=True,
                                        null=True)  # Field name made lowercase.
    web_status = models.CharField(db_column='WEB_STATUS', max_length=10, blank=True,
                                  null=True)  # Field name made lowercase.
    ug_degree = models.CharField(db_column='UG_DEGREE', max_length=150, blank=True,
                                 null=True)  # Field name made lowercase.
    pg_degree = models.CharField(db_column='PG_DEGREE', max_length=150, blank=True,
                                 null=True)  # Field name made lowercase.
    phd_degree = models.CharField(db_column='PHD_DEGREE', max_length=150, blank=True,
                                  null=True)  # Field name made lowercase.
    mphil_degree = models.CharField(max_length=150, blank=True, null=True)
    mphil_year = models.CharField(max_length=150, blank=True, null=True)
    mphil_equivalent_university = models.CharField(max_length=150, blank=True, null=True)
    web_designation2 = models.CharField(db_column='WEB_DESIGNATION2', max_length=100, blank=True,
                                        null=True)  # Field name made lowercase.
    courses_taught_curr_yr = models.CharField(db_column='COURSES_TAUGHT_CURR_YR', max_length=500, blank=True,
                                              null=True)  # Field name made lowercase.
    nature_work = models.CharField(max_length=500, blank=True, null=True)
    post_doctoral_exp = models.CharField(db_column='POST_DOCTORAL_EXP', max_length=500, blank=True,
                                         null=True)  # Field name made lowercase.
    previous_experience_industrial = models.CharField(db_column='PREVIOUS_EXPERIENCE_INDUSTRIAL', max_length=500,
                                                      blank=True, null=True)  # Field name made lowercase.
    previous_experience_research = models.CharField(db_column='PREVIOUS_EXPERIENCE_RESEARCH', max_length=500,
                                                    blank=True, null=True)  # Field name made lowercase.
    previous_exp_teaching = models.CharField(db_column='PREVIOUS_EXP_TEACHING', max_length=500, blank=True,
                                             null=True)  # Field name made lowercase.
    membership_professional_societies = models.CharField(db_column='MEMBERSHIP_PROFESSIONAL_SOCIETIES', max_length=500,
                                                         blank=True, null=True)  # Field name made lowercase.
    additional_job_role = models.CharField(db_column='ADDITIONAL_JOB_ROLE', max_length=500, blank=True,
                                           null=True)  # Field name made lowercase.
    gitam_expirence = models.CharField(db_column='GITAM_EXPIRENCE', max_length=50, blank=True,
                                       null=True)  # Field name made lowercase.
    total_expirence = models.CharField(db_column='TOTAL_EXPIRENCE', max_length=50, blank=True,
                                       null=True)  # Field name made lowercase.
    pdf = models.CharField(max_length=50, blank=True, null=True)
    pdf_field = models.CharField(max_length=100, blank=True, null=True)
    pdf_university = models.CharField(max_length=50, blank=True, null=True)
    weekoff = models.CharField(db_column='WEEKOFF', max_length=5, blank=True, null=True)  # Field name made lowercase.
    aadhar_no = models.CharField(db_column='AADHAR_NO', max_length=50, blank=True,
                                 null=True)  # Field name made lowercase.
    last_update = models.DateTimeField(db_column='LAST_UPDATE', blank=True, null=True)  # Field name made lowercase.
    hit_count = models.IntegerField(db_column='HIT_COUNT', blank=True, null=True)  # Field name made lowercase.
    uan = models.CharField(db_column='UAN', max_length=20, blank=True, null=True)  # Field name made lowercase.
    fpf_flag = models.CharField(db_column='FPF_FLAG', max_length=2, blank=True, null=True)  # Field name made lowercase.
    ifsc_code = models.CharField(db_column='IFSC_CODE', max_length=50, blank=True,
                                 null=True)  # Field name made lowercase.
    job_type = models.CharField(db_column='JOB_TYPE', max_length=5, blank=True, null=True)  # Field name made lowercase.
    aadhar_name = models.CharField(db_column='AADHAR_NAME', max_length=300, blank=True,
                                   null=True)  # Field name made lowercase.
    esi_no = models.CharField(db_column='ESI_NO', max_length=50, blank=True, null=True)  # Field name made lowercase.
    dor = models.DateTimeField(db_column='DOR', blank=True, null=True)  # Field name made lowercase.
    pwd = models.CharField(db_column='PWD', max_length=5, blank=True, null=True)  # Field name made lowercase.
    selection_mode = models.CharField(db_column='SELECTION_MODE', max_length=25, blank=True,
                                      null=True)  # Field name made lowercase.
    additional_qualification = models.CharField(db_column='ADDITIONAL_QUALIFICATION', max_length=25, blank=True,
                                                null=True)  # Field name made lowercase.
    highest_qualification = models.CharField(db_column='Highest_Qualification', max_length=25, blank=True,
                                             null=True)  # Field name made lowercase.
    nature_appointment = models.CharField(db_column='Nature_Appointment', max_length=25, blank=True,
                                          null=True)  # Field name made lowercase.
    dojtp = models.CharField(db_column='DOJTP', max_length=25, blank=True, null=True)  # Field name made lowercase.
    resignation_flag = models.CharField(db_column='RESIGNATION_FLAG', max_length=5, blank=True,
                                        null=True)  # Field name made lowercase.
    hod_flag = models.CharField(db_column='HOD_FLAG', max_length=2, blank=True, null=True)  # Field name made lowercase.
    web_job_description = models.CharField(db_column='WEB_JOB_DESCRIPTION', max_length=500, blank=True,
                                           null=True)  # Field name made lowercase.
    salutation = models.CharField(db_column='SALUTATION', max_length=10, blank=True,
                                  null=True)  # Field name made lowercase.
    first_name = models.CharField(db_column='FIRST_NAME', max_length=150, blank=True,
                                  null=True)  # Field name made lowercase.
    last_name = models.CharField(db_column='LAST_NAME', max_length=50, blank=True,
                                 null=True)  # Field name made lowercase.
    web_designation3 = models.CharField(db_column='WEB_DESIGNATION3', max_length=100, blank=True,
                                        null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'EMPLOYEE_MASTER'

    def __str__(self):
        return self.empid