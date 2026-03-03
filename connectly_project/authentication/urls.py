from .views import GoogleLoginView

urlpatterns += [
    path('auth/google/login/', GoogleLoginView.as_view(), name='google-login'),
]
