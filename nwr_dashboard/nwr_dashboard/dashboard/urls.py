from django.urls import path
from . import views


# ...existing code...

urlpatterns = [
    # ...existing url patterns...
     
    path('upload_master_excel/', views.upload_master_excel, name='upload_master_excel'),
    path('upload_nwr_zone/', views.upload_nwr_zone, name='upload_nwr_zone'),
    path('upload_debit_zone/', views.debit_scroll, name='debit_scroll'),
    path('get_rule/', views.get_rule, name='get_rule'),
    path('dash/', views.dashboard, name='dashboard'),
    path('upload-mismatch/', views.upload_mismatch, name='upload_mismatch'),
    path('mismatch/', views.load_mismatch_page, name='mismatch_page'),
    path('chat_completion/', views.chat_completion, name='chat_completion'),
]
