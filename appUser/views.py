from django.shortcuts import render,redirect
from django.contrib.auth import login,logout,authenticate
from django.contrib import messages
from django.contrib.auth.models import User
from django.urls import reverse
from .models import *
from appMy.models import *
from django.http import HttpResponse



def loginPage(request):
    context={}
    if request.method == "POST":
        submit = request.POST.get("submit")
        if submit == "login":
            username = request.POST.get("username")
            password = request.POST.get("password")
            user = authenticate(username=username,password=password)
            if user is not None:
                login(request,user)
                profile = Profile.objects.get_or_create(user=user)[0]
                profile.loginUser = True
                profile.save()
                return redirect ("dashboardPage")
            else:
                messages.warning(request,"kullanıcı adı veya şifre yanlış")
                return redirect ("loginPage")
        
        if submit == "register":
            fname = request.POST.get("fname")
            username_register = request.POST.get("username_register")
            email = request.POST.get("email")
            password1 = request.POST.get("password1")
            password2 = request.POST.get("password2")
            
            password_bool = email_bool = username_register_bool = True

            if password1 != password2:
                password_bool = False
                messages.warning(request,"Şifreler aynı değil")
            if User.objects.filter(email = email).exists():
                email = False
                messages.warning(request,"Bu email zaten kullanılmakta")
            if User.objects.filter(username = username_register).exists():
                username_register_bool = False

            if password_bool and email_bool and username_register_bool:
                user = User.objects.create_user(first_name = fname,email = email,username=username_register,password=password1)
                user.save()
                
                image = Profileimage(image='profile/owl.png')
                image.save()
                Profile.objects.create(user=user,loginUser=False,image=image)

                return redirect("dashboardPage")
    return render(request, 'login-register.html', context)


def logoutUser(request):
    user = Profile.objects.filter(user=request.user,loginUser=True).first()
    print(user)
    user.loginUser = False
    user.save()
    logout(request)
    return redirect("dashboardPage")


# comment
def postDetail(request, category, pk):
    games = GameCard.objects.filter(slug=category).first()
    print(category)
    subject = Subject.objects.filter(slug=pk).first()
    print(subject)
    comments = Comment.objects.filter(subject_brand__subjectBrand =subject)
    subject_author = comments.first()
    
 
    if request.user.is_authenticated:
        user = Profile.objects.filter(user = request.user).first()
    else:
        user = Profile.objects.all()
        
    if request.method == 'POST':
        
        text = request.POST.get("text")
        comment = Comment(text=text,subject_brand=subject,author=request.user, image= user.image)
        comment.save()
        subject.comment_number += 1
        subject.save()
        user.comment_user +=1
        user.save()
        
        return redirect('/blog/'+category+'/'+ pk )
    
    context = {
        "comments":comments,
        "subject":subject,
        "games":games,
        'subject_author':subject_author,
        "user":user
        }
    
    return render(request,'postDetail.html',context)
    

def messagePost(request, game_slug):
    comment_number = 0
    comment_user = 0

    # game_slug a göre messagepostu getirme
    try:
        game = GameCard.objects.get(slug=game_slug) 
        user = Profile.objects.filter(user = request.user).first()
    except GameCard.DoesNotExist:
        return HttpResponse("Oyun bulunamadı.")
    
    # game_slug a göre konu başlığı oluşturup yorumu kaydetme
    if request.method == 'POST':
        subject_slug = request.POST.get("subject")  
        print(subject_slug)
        text = request.POST.get("text")
        comment_number += 1
        subject_title=Subject(subjectBrand=subject_slug,game_cate=game,comment_number = comment_number)
        subject_title.save()
        subject_url = Subject.objects.filter().last()
        
        print("son konu:", subject_url)
      
        comment = Comment(text=text, subject_brand=subject_title, author=request.user, game_cate=game,image= user.image)
        comment.save()
        user.comment_user += 1
        user.save()
        return redirect('/blog/'+game_slug+'/'+str((subject_url.slug)))    
    context = {
        'game': game,
    }
    return render(request, 'messagePost.html', context)




def accountUser(request):
    context = {}
    
    return render(request, 'accountUser.html', context)

