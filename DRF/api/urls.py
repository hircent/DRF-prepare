from accounts.views import (
    RoleBasesUserListView,RoleBasedUserCreateView,RoleBasedUserDeleteView,
    RoleBasedUserUpdateView,RoleBasedUserDetailsView,
    ParentListView,ParentDetailsView,TeachingUserListView,
    SearchParentListView
)

from api.views import (
    ChangePasswordView
)

from branches.views import (
    BranchListView ,BranchCreateView,BranchRetrieveView,BranchUpdateView,BranchDeleteView,
    CombinedPrincipalsAndBranchGradesView,BranchSelectorListView
)
from calendars.views import (
    CalendarListView,CalendarRetrieveView,CalendarDestroyView,CalendarCreateView,CalendarUpdateView,
    CalendarThemeLessonListView,GenerateCalendarThemeLessonView
)

from category.views import (
    CategoryListView, ThemeListView, CategoryRetrieveView,
    CategoryCreateView, ThemeRetrieveView, CategoryDestroyView,
    ThemeDestroyView, CategoryUpdateView, ThemeUpdateView, ThemeCreateView,
    CategorySelectionListView
)

from classes.views import (
    ClassListView, StudentEnrolmentListView, ClassCreateView, ClassUpdateView,
    ClassDetailsView, ClassDestroyView, ClassLessonListByDateView,SearchTimeSlotListView,
    StudentEnrolmentDetailView, StudentEnrolmentUpdateView, StudentEnrolmentDeleteView,
    EnrolmentLessonListView, EnrolmentExtendView, VideoAssignmentListView, VideoAssignmentDetailsView,
    VideoAssignmentUpdateView, MarkAttendanceView, EnrolmentRescheduleClassView,EnrolmentAdvanceView,
    TestLearnView
)

from country.views import (
    CountryListView
)

from feeStructure.views import (
    GradeListView, GradeRetrieveView, GradeCreateView, GradeUpdateView, GradeDestroyView
)

from students.views import (
    StudentListView ,StudentDetailsView ,StudentCreateView,StudentUpdateView,StudentDeleteView,
    ExportStudentsCSV
)

from payments.views import (
    PaymentListView, InvoiceListView
)

from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView
)

from .views import CustomTokenObtainPairView


urlpatterns = [
    # Users for Superadmin, Principals, Managers, Teachers, Parents
    path("users/<str:role>/list",RoleBasesUserListView.as_view(),name="user-role-based-list"), 
    path("users/details/<int:pk>",RoleBasedUserDetailsView.as_view(),name="user-details"), 
    path("users/create/<str:role>",RoleBasedUserCreateView.as_view(),name="create-user"), 
    path("users/update/<str:role>/<int:pk>",RoleBasedUserUpdateView.as_view(),name="update-user"), 
    path("users/delete/<str:role>/<int:pk>",RoleBasedUserDeleteView.as_view(),name="delete-user"), 

    #Country
    path("country/list",CountryListView.as_view(),name="country-list"),
    
    #Branch
    path("branch/list",BranchListView.as_view(),name="branch-list"),
    path("branch/details/<int:branch_id>",BranchRetrieveView.as_view(),name="branch-details"),
    path("branch/create",BranchCreateView.as_view(),name="create-branch"),
    path("branch/update/<int:branch_id>",BranchUpdateView.as_view(),name="update-branch"),
    path("branch/delete/<int:branch_id>",BranchDeleteView.as_view(),name="delete-branch"),

    #Students
    path("student/list",StudentListView.as_view(),name="student-list"),
    path("student/details/<int:student_id>",StudentDetailsView.as_view(),name="student-details"),
    path("student/create",StudentCreateView.as_view(),name="create-student"),
    path("student/update/<int:student_id>",StudentUpdateView.as_view(),name="update-student"),
    path("student/delete/<int:student_id>",StudentDeleteView.as_view(),name="delete-student"),
    path('students/export-csv', ExportStudentsCSV.as_view(), name='export-students-csv'),

    #Parents
    path("parent/list",ParentListView.as_view(),name="parent-list"),
    path("parent/details/<int:parent_id>",ParentDetailsView.as_view(),name="parent-details"),
    # path("parent/create",parentCreateView.as_view(),name="create-parent"),
    # path("parent/update/<int:parent_id>",parentUpdateView.as_view(),name="update-parent"),
    # path("parent/delete/<int:parent_id>",parentDeleteView.as_view(),name="delete-parent"),

    #Calendars
    path('calendars/list', CalendarListView.as_view(), name='calendar-list'),
    path('calendars/details/<int:calendar_id>', CalendarRetrieveView.as_view(), name='calendar-details'),
    path('calendars/delete/<int:calendar_id>', CalendarDestroyView.as_view(), name='delete-calendar'),
    path('calendars/update/<int:calendar_id>', CalendarUpdateView.as_view(), name='update-calendar'),
    path('calendars/create', CalendarCreateView.as_view(), name='create-calendar'),

    #Calendar Theme Lesson
    path('calendars/theme-lesson/list', CalendarThemeLessonListView.as_view(), name='calendar-theme-lesson-list'),
    path('generate_theme_lesson/<int:year>', GenerateCalendarThemeLessonView.as_view(), name='generate_theme_lesson'),

    #Category
    path('category/list', CategoryListView.as_view(), name='category-list'),
    path('category/selection-list', CategorySelectionListView.as_view(), name='category-selection-list'),
    path('category/details/<int:category_id>', CategoryRetrieveView.as_view(), name='category-details'),
    path('category/create', CategoryCreateView.as_view(), name='create-category'),
    path('category/update/<int:category_id>', CategoryUpdateView.as_view(), name='update-category'),
    path('category/delete/<int:category_id>', CategoryDestroyView.as_view(), name='delete-category'),

    path('theme/list', ThemeListView.as_view(), name='theme-list'),
    path('theme/details/<int:theme_id>', ThemeRetrieveView.as_view(), name='theme-details'),
    path('theme/create', ThemeCreateView.as_view(), name='create-theme'),
    path('theme/delete/<int:theme_id>', ThemeDestroyView.as_view(), name='delete-theme'),
    path('theme/update/<int:theme_id>', ThemeUpdateView.as_view(), name='update-theme'),

    path('grade/list', GradeListView.as_view(), name='grade-list'),
    path('grade/details/<int:grade_id>', GradeRetrieveView.as_view(), name='grade-details'),
    path('grade/create', GradeCreateView.as_view(), name='create-grade'),
    path('grade/update/<int:grade_id>', GradeUpdateView.as_view(), name='update-grade'),
    path('grade/delete/<int:grade_id>', GradeDestroyView.as_view(), name='delete-grade'),

    #Classes
    path('class/list', ClassListView.as_view(), name='class-list'),
    path('class/create', ClassCreateView.as_view(), name='create-class'),
    path('class/details/<int:class_id>', ClassDetailsView.as_view(), name='class-details'),
    path('class/update/<int:class_id>', ClassUpdateView.as_view(), name='update-class'),
    path('class/delete/<int:class_id>', ClassDestroyView.as_view(), name='delete-class'),

    #Student Enrolment
    path('student/enrolment/list', StudentEnrolmentListView.as_view(), name='student-enrolment-list'),
    path('student/enrolment/details/<int:enrolment_id>', StudentEnrolmentDetailView.as_view(), name='student-enrolment-details'),
    path('student/enrolment/update/<int:enrolment_id>', StudentEnrolmentUpdateView.as_view(), name='update-student-enrolment'),
    path('student/enrolment/delete/<int:enrolment_id>', StudentEnrolmentDeleteView.as_view(), name='delete-student-enrolment'),
    path('student/enrolment/<int:enrolment_id>/lessons/list', EnrolmentLessonListView.as_view(), name='student-enrolment-lesson-list'),
    path('student/enrolment/<int:enrolment_id>/extend', EnrolmentExtendView.as_view(), name='enrolment-extend'),
    path('student/enrolment/<int:enrolment_id>/reschedule-class', EnrolmentRescheduleClassView.as_view(), name='enrolment-reschedule-class'),
    path('student/enrolment/<int:enrolment_id>/advance', EnrolmentAdvanceView.as_view(), name='enrolment-advancement'),

    #Video Assignment
    path('student/enrolment/<int:enrolment_id>/video/list', VideoAssignmentListView.as_view(), name='video-assignment-list'),
    path('student/enrolment/video/details/<int:video_id>', VideoAssignmentDetailsView.as_view(), name='video-assignment-details'),
    path('student/enrolment/video/update/<int:video_id>', VideoAssignmentUpdateView.as_view(), name='update-video-assignment'),

    #Attendance
    path('class/attendance/list', ClassLessonListByDateView.as_view(), name='class-lesson-list-by-date'),
    path('class/mark-attendance', MarkAttendanceView.as_view(), name='mark-attendance'),

    #Payment
    path('payment/list', PaymentListView.as_view(), name='payment-list'),
    path('invoice/list', InvoiceListView.as_view(), name='invoice-list'),

    #Others
    path("branch/principals/branch_grade",CombinedPrincipalsAndBranchGradesView.as_view(),name="principal-branch_grade-for-branch"),
    path("branch/selector",BranchSelectorListView.as_view(),name="branch-selector"),
    path("timeslot/list",SearchTimeSlotListView.as_view(),name="available-timeslot-list"),
    path("teaching-user/list",TeachingUserListView.as_view(),name="teaching-user-list"),
    path("search/parent/list",SearchParentListView.as_view(),name="search-parent-list"),
    path("test-learn/<int:enrolment_id>",TestLearnView.as_view(),name="test-learn"),

    #Token
    path('login', CustomTokenObtainPairView.as_view(), name='login_token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('change-password', ChangePasswordView.as_view(), name='change-password'),

    
]