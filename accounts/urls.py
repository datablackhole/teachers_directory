from django.urls import path

from . import views

urlpatterns = [
    path('login', views.login,name='login'),
    path('logout', views.logout,name='logout'),
    path('', views.home,name='home'),
    path('import', views.import_,name='import'),
    path('search', views.search,name='search'),
    path('teacher/<int:id>', views.teacher,name='teacher'),
    path('register', views.register,name='register'),
    path('register/verify', views.register_verify,name='verify'),
    # path('import', views.import,name='import'),
]
