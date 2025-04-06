from django.contrib.auth import authenticate,login as auth_login,logout as auth_logout
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.http import JsonResponse
import json

@csrf_exempt
def login(request):
    if request.method == "POST":
        import json
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")

        user = authenticate(request, username=username, password=password)
        if user:
            auth_login(request, user)
            return JsonResponse({"message": "Login successful"}, status=200)
        return JsonResponse({"error": "Invalid credentials"}, status=401)
    return JsonResponse({"error": "Only POST allowed"}, status=405)

@csrf_exempt
def logout(request):
    if request.method == 'POST':
        auth_logout(request)
        return JsonResponse({"message": "Logged out successfully"}, status=200)
    return JsonResponse({"error": "Only POST method allowed"}, status=405)

def signin(request):
    try:
        body=json.loads(request.body)
        print(body)
        try:
            User.objects.get(username=body["name"]) 
            return JsonResponse({"message":"Already exists"},status=205)
        except:
            user = User.objects.create_user(username= body["name"],email= body["email"],password= body["password"])
            names=body["name"].split(" ")
            if len(names)>0:
                user.first_name=names[0]
                try:
                    user.last_name=names[1]
                except Exception:
                    pass
            print(user)
            return JsonResponse({"message":"User Created"},status=200)
    except Exception as e:
        print(e)
        return JsonResponse({"error":"Failed to Create"},status=400)
