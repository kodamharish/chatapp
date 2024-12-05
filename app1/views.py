from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request,'index.html')


from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User
from django.contrib.auth.hashers import make_password



from django.shortcuts import render, redirect, get_object_or_404
from django.db.models.functions import TruncDate
from itertools import groupby
from .models import Admin, User, Query, Response






def register_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        name = request.POST.get("name")
        email = request.POST.get("email")
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
        else:
            user = User(username=username, name=name, email=email)
            user.password = make_password(password)
            user.save()
            messages.success(request, "User registered successfully.")
            return redirect('login_user')
    
    return render(request, "register_user.html")


from .models import Admin

def register_admin(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        name = request.POST.get("name")
        email = request.POST.get("email")
        
        if Admin.objects.filter(username=username).exists():
            messages.error(request, "Admin username already exists.")
        elif Admin.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
        else:
            admin = Admin(username=username, name=name, email=email)
            admin.password = make_password(password)
            admin.save()
            messages.success(request, "Admin registered successfully.")
            return redirect('login_admin')
    
    return render(request, "register_admin.html")

from django.contrib.auth.hashers import check_password
from django.contrib.auth import login, logout
from django.shortcuts import render

def login_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        try:
            user = User.objects.get(username=username)
            if check_password(password, user.password):
                request.session['user_id'] = user.id  # Using sessions to track the logged-in user
                request.session['user_role'] = 'user'
                messages.success(request, "Login successful.")
                print('Login successful. user')
                return redirect('user_dashboard')  # Redirect to user-specific dashboard
            else:
                messages.error(request, "Invalid password.")
        except User.DoesNotExist:
            messages.error(request, "Username not found.")
    
    return render(request, "login_user.html")


def login_admin(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        try:
            admin = Admin.objects.get(username=username)
            if check_password(password, admin.password):
                request.session['admin_id'] = admin.id  # Using sessions to track the logged-in admin
                request.session['user_role'] = 'admin'
                messages.success(request, "Login successful.")
                return redirect('admin_dashboard')  # Redirect to admin-specific dashboard
            else:
                messages.error(request, "Invalid password.")
        except Admin.DoesNotExist:
            messages.error(request, "Admin username not found.")
    
    return render(request, "login_admin.html")


def logout_admin(request):
    logout(request)
    request.session.flush()  # Clear all session data
    #messages.success(request, "Logged out successfully.")
    return redirect('login_admin')  # Redirect to home or login page


def logout_user(request):
    logout(request)
    request.session.flush()  # Clear all session data
    #messages.success(request, "Logged out successfully.")
    return redirect('login_user')  # Redirect to home or login page









from django.shortcuts import render, redirect
from .models import User, Query, Response
from django.contrib.auth.decorators import login_required


def user_dashboard(request):
    # Check if the logged-in user is a `User` instance
    if request.session.get('user_role') == 'user':
        user_id = request.session.get('user_id')
        try:
            user = User.objects.get(id=user_id)  # Ensure it's a `User` instance
        except User.DoesNotExist:
            return redirect('login_user')  # Redirect if the user is not found

        if request.method == "POST":
            question = request.POST.get('question')
            Query.objects.create(user=user, question=question)
            return redirect('user_dashboard')

        # Fetch queries and responses for the logged-in user
        queries = Query.objects.filter(user=user).prefetch_related('responses').order_by('-created_at')

        return render(request, 'user_dashboard.html', {'queries': queries,'user':user})

    return redirect('login_user')  # Redirect if not logged in as a user




    




def admin_dashboard(request):
    if request.session.get('user_role') == 'admin':
        admin_id = request.session.get('admin_id')
        admin = get_object_or_404(Admin, id=admin_id)

        # Fetch all users
        users = User.objects.all()

        # Fetch users with open queries
        # users_with_open_queries = User.objects.filter(queries__status='open').distinct()
        # users_without_open_queries = User.objects.exclude(id__in=users_with_open_queries)

        # Fetch all users and categorize them based on query status
        users_with_open_queries = User.objects.filter(queries__status='open').distinct()
        users_without_open_queries = User.objects.exclude(id__in=users_with_open_queries)


        # Fetch selected user and their queries
        user_id = request.GET.get('user_id')
        if user_id:
            selected_user = get_object_or_404(User, id=user_id)


           

            # Fetch user's queries and annotate with date
            user_queries = Query.objects.filter(user=selected_user).order_by('created_at').annotate(date=TruncDate('created_at'))

             # Fetch all users and categorize them based on query status
            users_with_open_queries = User.objects.filter(queries__status='open').distinct()
            users_without_open_queries = User.objects.exclude(id__in=users_with_open_queries)

            # Group the queries by date
            grouped_queries = {}
            for date, queries in groupby(user_queries, key=lambda q: q.date):
                grouped_queries[date] = list(queries)

            if request.method == "POST":
                query_id = request.POST.get('query_id')

                answer = request.POST.get('answer')
                #print(query_id,answer)

                query = Query.objects.get(id=query_id)

                # Only respond to open queries
                if query.status == 'open':
                    Response.objects.create(query=query, admin=admin, answer=answer)
                    query.status = 'closed'  # Close the query after responding
                    query.save()
                    #print(query_id,answer,'open')


                return redirect('admin_dashboard')  # Avoid resubmission

            return render(request, 'admin_dashboard.html', {
                'users': users,
                'users_with_open_queries': users_with_open_queries,
                'users_without_open_queries': users_without_open_queries,

                'selected_user': selected_user,
                'grouped_queries': grouped_queries,
                'admin': admin,
                'user_queries': user_queries,

            })

        return render(request, 'admin_dashboard.html', {
            'users': users,
            'users_with_open_queries': users_with_open_queries,
            'users_without_open_queries': users_without_open_queries,

            'admin': admin,
        })

    return redirect('login_admin')







