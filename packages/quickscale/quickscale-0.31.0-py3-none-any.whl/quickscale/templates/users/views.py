"""User authentication and account management views."""
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from .forms import ProfileForm
from credits.models import APIKey

User = get_user_model()

@require_http_methods(["GET", "POST"])
def login_view(request: HttpRequest) -> HttpResponse:
    """Handle user login."""
    is_htmx = request.headers.get('HX-Request') == 'true'
    
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        # For django-allauth email authentication
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Successfully logged in!')
            
            if is_htmx:
                response = HttpResponse()
                response['HX-Redirect'] = '/'
                return response
            return redirect('public:index')
            
        messages.error(request, 'Invalid email or password.')
        if is_htmx:
            # For HTMX requests, return the entire form container with error message
            return render(request, 'users/login_form.html', {'form': {'errors': True}, 'is_htmx': is_htmx})
        # For non-HTMX requests, render the entire login page with error
        return render(request, 'users/login.html', {'form': {'errors': True}, 'is_htmx': is_htmx})
    
    return render(request, 'users/login.html', {'is_htmx': is_htmx})

@require_http_methods(["GET", "POST"])
def logout_view(request: HttpRequest) -> HttpResponse:
    """Handle user logout."""
    is_htmx = request.headers.get('HX-Request') == 'true'
    
    logout(request)
    messages.success(request, 'Successfully logged out!')
    
    if is_htmx:
        response = HttpResponse()
        response['HX-Redirect'] = '/'
        return response
    
    return redirect('public:index')

class CustomSignupForm(UserCreationForm):
    """Custom signup form with email field."""
    email = forms.EmailField(
        max_length=254,
        required=True,
        help_text="Required. Enter a valid email address.",
        widget=forms.EmailInput(attrs={'class': 'input', 'placeholder': 'Email'})
    )
    username = forms.CharField(
        max_length=150,
        required=True,
        help_text="Required. 150 characters or fewer.",
        widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Username'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

@require_http_methods(["GET", "POST"])
def signup_view(request: HttpRequest) -> HttpResponse:
    """Handle user registration."""
    is_htmx = request.headers.get('HX-Request') == 'true'
    
    if request.method == "POST":
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            # Save the user
            user = form.save()
            messages.success(request, 'Account created successfully! Please check your email to confirm your account.')
            
            # For HTMX requests, send a redirect header instead of rendering the template
            if is_htmx:
                response = HttpResponse()
                # Redirect to login page
                response['HX-Redirect'] = '/users/login/'
                return response
            return redirect('users:login')
    else:
        form = CustomSignupForm()
    
    # For HTMX requests that aren't POST or have invalid forms, just return the form part
    if is_htmx and request.method == "POST":
        # If we're here with an HTMX request, the form is invalid
        return render(request, 'users/signup_form.html', {
            'form': form,
            'is_htmx': is_htmx
        })
    
    # For non-HTMX requests or GET requests, return the full page
    return render(request, 'users/signup.html', {
        'form': form,
        'is_htmx': is_htmx
    })

@login_required
@require_http_methods(["GET", "POST"])
def profile_view(request: HttpRequest) -> HttpResponse:
    """Display and update user profile."""
    is_htmx = request.headers.get('HX-Request') == 'true'
    
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            
            if is_htmx:
                # Return the updated profile form for HTMX
                return render(request, 'users/profile_form.html', {
                    'form': form,
                    'is_htmx': is_htmx
                })
            return redirect('users:profile')
    else:
        form = ProfileForm(instance=request.user)
    
    return render(request, 'users/profile.html', {
        'form': form,
        'is_htmx': is_htmx
    })


@login_required
@require_http_methods(["GET"])
def api_keys_view(request: HttpRequest) -> HttpResponse:
    """Display user's API keys."""
    is_htmx = request.headers.get('HX-Request') == 'true'
    
    api_keys = APIKey.objects.filter(user=request.user).order_by('-created_at')
    
    return render(request, 'users/api_keys.html', {
        'api_keys': api_keys,
        'is_htmx': is_htmx
    })


@login_required
@csrf_protect
@require_http_methods(["POST"])
def generate_api_key_view(request: HttpRequest) -> HttpResponse:
    """Generate a new API key for the user."""
    is_htmx = request.headers.get('HX-Request') == 'true'
    
    try:
        # Get the optional name for the API key
        name = request.POST.get('name', '').strip()
        
        # Generate the API key
        full_key, prefix, secret_key = APIKey.generate_key()
        
        # Create the API key record
        api_key = APIKey.objects.create(
            user=request.user,
            prefix=prefix,
            hashed_key=APIKey.get_hashed_key(secret_key),
            name=name
        )
        
        messages.success(request, 'API key generated successfully!')
        
        # Return the generated key template (shows raw key once)
        return render(request, 'users/api_key_generated.html', {
            'api_key': api_key,
            'full_key': full_key,
            'is_htmx': is_htmx
        })
        
    except Exception as e:
        messages.error(request, f'Error generating API key: {str(e)}')
        
        if is_htmx:
            return render(request, 'users/api_keys.html', {
                'api_keys': APIKey.objects.filter(user=request.user).order_by('-created_at'),
                'is_htmx': is_htmx
            })
        
        return redirect('users:api_keys')


@login_required
@csrf_protect
@require_http_methods(["POST"])
def revoke_api_key_view(request: HttpRequest) -> HttpResponse:
    """Revoke/deactivate an API key."""
    is_htmx = request.headers.get('HX-Request') == 'true'
    
    try:
        api_key_id = request.POST.get('api_key_id')
        if not api_key_id:
            raise ValidationError('API key ID is required')
        
        api_key = get_object_or_404(APIKey, id=api_key_id, user=request.user)
        api_key.is_active = False
        api_key.save(update_fields=['is_active'])
        
        messages.success(request, f'API key "{api_key.name or api_key.prefix}" has been revoked.')
        
    except ValidationError as e:
        messages.error(request, str(e))
    except Exception as e:
        messages.error(request, f'Error revoking API key: {str(e)}')
    
    if is_htmx:
        return render(request, 'users/api_keys.html', {
            'api_keys': APIKey.objects.filter(user=request.user).order_by('-created_at'),
            'is_htmx': is_htmx
        })
    
    return redirect('users:api_keys')


@login_required
@csrf_protect
@require_http_methods(["POST"])
def regenerate_api_key_view(request: HttpRequest) -> HttpResponse:
    """Regenerate an API key (deactivate old, create new)."""
    is_htmx = request.headers.get('HX-Request') == 'true'
    
    try:
        api_key_id = request.POST.get('api_key_id')
        if not api_key_id:
            raise ValidationError('API key ID is required')
        
        old_api_key = get_object_or_404(APIKey, id=api_key_id, user=request.user)
        
        # Deactivate the old key
        old_api_key.is_active = False
        old_api_key.save(update_fields=['is_active'])
        
        # Generate new API key
        full_key, prefix, secret_key = APIKey.generate_key()
        
        # Create new API key with same name
        new_api_key = APIKey.objects.create(
            user=request.user,
            prefix=prefix,
            hashed_key=APIKey.get_hashed_key(secret_key),
            name=old_api_key.name
        )
        
        messages.success(request, f'API key "{old_api_key.name or old_api_key.prefix}" has been regenerated.')
        
        # Return the generated key template (shows raw key once)
        return render(request, 'users/api_key_generated.html', {
            'api_key': new_api_key,
            'full_key': full_key,
            'is_htmx': is_htmx,
            'is_regeneration': True
        })
        
    except ValidationError as e:
        messages.error(request, str(e))
    except Exception as e:
        messages.error(request, f'Error regenerating API key: {str(e)}')
    
    if is_htmx:
        return render(request, 'users/api_keys.html', {
            'api_keys': APIKey.objects.filter(user=request.user).order_by('-created_at'),
            'is_htmx': is_htmx
        })
    
    return redirect('users:api_keys')