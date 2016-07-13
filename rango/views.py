from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect,HttpResponse
from django.shortcuts import render,get_object_or_404,redirect
from django.template import RequestContext
from rango.models import Category,Page,UserProfile
from rango.forms import CategoryForm,PageForm,UserForm, UserProfileForm
from django.contrib.auth.models import User
from django.contrib import auth
from django.conf import settings
from datetime import datetime
from django.db.models import Q
import operator
from rango.bing_search import run_query
import urllib
from dal import autocomplete
import json
from django.views.generic.edit import FormView
from django.utils import simplejson


def encode_url(url):
    a = urllib.urlencode(url)
    return a

def decode_url(url):
    b = urllib.unquote(url).decode('utf8')
    return b


def user_lookup(request):
    #default return list
    results = []
    if request.method == 'GET':
        if request.GET.has_key(u'query'):
            value = request.GET[u'query']
            #ignore queries shorter than length 3
            if len(value)>1:
                model_results = Category.objects.filter(name__icontains = value)
                results = [x.name for x in model_results]
    json = simplejson.dumps(results)
    return HttpResponse(json,mimetype = 'application/json')

#Autocomplete function

'''class CategoryAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        #Dont forget to filter out results depending on visitor
        if not self.request.user.is_authenticated():
            return Category.objects.none()

        qs = Category.objects.all()

        if self.q:
            qs = qs.filter(name__istartswith = self.q)

        return qs'''

#Autocomplete view using jquery
'''class AutoCompleteView(FormView):
    def get(self,request,*args,**kwargs):
        data = request.GET
        name = data.get("term")

        if name:
            cats = Category.objects.filter(name__icontains = name)
        else:
            cats = Category.objects.all()

        results = []

        for cat in cats:
            cat_json = {}
            #cat_json['id'] = cat.id
            #cat_json = cat.name
            cat_json = cat.name
            results.append(cat_json)
            data = json.dumps(results)
            mimetype = 'application/json'

            return HttpResponse(data,mimetype)'''

def get_cat(request):
    if request.is_ajax():
        q = request.Get.get('term','')
        cats = Category.objects.filter(name__icontains = q)
        results = []
        for cat in cats:
            #cat_json = {}
            #cat_json = cat.name

            results.append(cat.name)
        data = json.dumps(results)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)








#views.py

#VIEW HOME PAGE

def get_category_list(max_results=0 ,starts_with= ''):
    cat_list = []
    if starts_with:
        cat_list = Category.objects.filter(name__startswith = starts_with)
    else:
        cat_list = Category.objects.all()

    if max_results > 0:
        if len(cat_list) > max_results:
            cat_list = cat_list[:max_results]

    #cat_list = Category.objects.all(

    '''for cat in cat_list:
        cat.url = encode_url(cat.name)'''

    return cat_list

def suggest_category(request):
    cat_list =[]
    starts_with = ''
    if request.method == 'GET':
        starts_with = request.GET['suggestion']
    else:
        starts_with = request.POST['suggestion']

        cat_list = get_category_list(8, starts_with)

    return render(request,"category_list.html",{'cat_list':cat_list})

#@login_required
def index(request):
    #obtain context from the http request.
    #context = RequestContext(request)
    #request.session.set_test_cookie()
    cat_list = get_category_list()
    
    category_list = Category.objects.order_by('-likes') [:5]

    pages = Page.objects.order_by('-views')[:5]
    
    context_dict = {'categories' : category_list, 'pages': pages,'cat_list':cat_list}

    for category in category_list:
        category.url = category.name.replace(' ','_')
    
    response =  render(request,"index.html",context_dict)

    # Get the number of visits to the site.
    # We use the COOKIES.get() function to obtain the visits cookie.
    # If the cookie exists, the value returned is casted to an integer.
    # If the cookie doesn't exist, we default to zero and cast that.
    visits = int(request.COOKIES.get('visits','0'))

    #Does last_visit exist in cookie
    if request.COOKIES.has_key('last_visit'):
        #Yes it does,get the cookies value
        last_visit = request.COOKIES['last_visit']
        #cast the value to a python date/time object
        last_visit_time = datetime.strptime(last_visit[:-7],"%Y-%m-%d %H:%M:%S")
        #if its been more than a day
        if(datetime.now() - last_visit_time).days > 0:
            #..reassign the value of the cookie to +1 of what it was before...
            response.set_cookie('visits', visits+1)
            #..and update the last visit cookie,too
            response.set_cookie('last_visit',datetime.now())
    else:
        #Cookie last_visit doesnt exist then,create it to current time.
        response.set_cookie('last_visit', datetime.now())
        
    #return response back to the user,updating any cookies that need changed.
    return response
    ##END NEW CODE


#@login_required
def restricted(request):
    return render(request,"restricted.html")


#VIEW INDIVIDUAL CATEGORY AND ITS RESPECTIVE PAGES
#@login_required
def category(request, category_name_url):

    #replace spaces and underscores in url so that it can be handled by browsers
    categories = Category.objects.order_by('-likes') [:5]

    #pages = Page.objects.order_by('-views')[:5]
    
    #context_dict = {'categories' : category_list, 'pages':pages}

    '''for category in category_list:
        category.url = category.name.replace(' ','_')'''
    category_name = category_name_url.replace('_', ' ')

    #create context dictionary we can pass to the template
    context_dict = {'category_name': category_name,'category_name_url':category_name_url, 'categories':categories}
    
    #cat_list = get_category_list()
    
    #context_dict['cat_list'] = cat_list
    
    
    
    try:
        # Can we find a category with the given name?
        # If we can't, the .get() method raises a DoesNotExist exception.
        # So the .get() method returns one model instance or raises an exception.
        category = Category.objects.get(name = category_name)


        # Retrieve all of the associated pages.
        # Note that filter returns >= 1 model instance.
        pages = Page.objects.filter(category = category).order_by('-views')

        # Adds our results list to the template context under name pages
        context_dict['pages'] = pages

        # We also add the category object from the database to the context dictionary.
        # We'll use this in the template to verify that the category exists.
        context_dict['category'] = category
        
    except Category.DoesNotExist:
        #We get here if we didn't find the specified category.
        # Don't do anything - the template displays the "no category" message for us.
        pass

    return render(request,"category.html",context_dict)
        
        
def about(request):
    return render(request,"about.html")

#ADD A NEW CATEGORY
def add_category(request):
    #HTTP POST ?
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        #Have we been provided with a valid form ?
        if form.is_valid():
            #Save the new category to the database
            form.save(commit = True)

            #Now call index,user will be returned to homepage
            return index(request)
        else:
            #if form contains errors,print them to terminal
            print form.errors
    else:
        #If request was not POST,display form to enter details
        form = CategoryForm()

    #return render wih error messages if any

    return render(request,'add_category.html',{'form':form})

#ADD A NEW PAGE
def add_page(request, category_name_url):

    #category_name = category_name_url.replace('_', ' ')

    #context_dict  = {'category_name':category_name,'form':form}
    try:
        cat = Category.objects.get(name = category_name_url)
    except Category.DoesNotExist:
        cat = None

    #HTTP POST
    if request.method == 'POST':
        form = PageForm(request.POST)

        if form.is_valid():

        # This time we cannot commit straight away.
        # Not all fields are automatically populated!
            page = form.save(commit = False)

            #Retrieve the associated category of the page so that we can add it
            cat = Category.objects.get(name = category_name_url)
            page.category = cat

            #Also, create a default value of 0 for views
            page.views = 0

            #We can now save our new model instance
            page.save()

            #Now that the page is saved,display the category instead
            return category(request, category_name_url)
        else:
            print form.errors
    else:
        form = PageForm()
    context_dict = {'form': form, 'category':cat,'category_name_url':category_name_url}

    return render(request,"add_page.html",context_dict )

def register(request):
    '''if request.session.test_cookie_worked():
        print ">>>>TEST COOKIE WORKED !"
        request.session.delete_test_cookie()'''


    registered = False

    if request.method == 'POST':
        user_form = UserForm(data = request.POST)
        profile_form = UserProfileForm(data = request.POST)

        # if the two forms are valid
        if user_form.is_valid() and profile_form.is_valid():
            
            #save the users form to database
            user = user_form.save()

        #now we hash the password with the set_password method
        #once hashed,we can update the user object
            user.set_password(user.password)
            user.save()

        #now sort out the UserProfile instance
        #Since we need to set the user attribute ourselves,we set commit = False
        #this delays saving the model until we are ready to avoid integrity problems
            profile = profile_form.save(commit = False)
            profile.user = user

        #Did the user provide a profile picture ?
        #If so,we need to get it from the input form to the UserProfile Form.
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

        #save profile
            profile.save()
            registered = True
        
        #update  our variable to tell the template registration succesful
        else:
            print user_form.errors,profile_form.errors
    #NOT a HTTP POST,so we render our form using two modelForm instances
    #These forms will be blank,ready for user input.
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    #Render the template depending on the context
    #context_dict =  {'user_form':user_form,  'profile_form':profile_form, 'registered':registered}

    return render(request,"register.html", {'user_form':user_form, 'profile_form':profile_form, 'registered':registered } )


def user_login(request):
    # Like before, obtain the context for the user's request.
    context = RequestContext(request)

    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
        username = request.POST.get('username','')
        password = request.POST.get('password','')

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = auth.authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user is not None:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                auth.login(request, user)
                return HttpResponseRedirect('/rango/')
            else:
                return HttpResponse("your acc was disabled")
        else:
            # Bad login details were provided. So we can't log the user in.
            print "Invalid login details: {0}, {1}".format(username, password)
            return HttpResponse('Invalid login details')

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render(request,"login.html", {})


def user_logout(request):

    logout(request)

    return HttpResponseRedirect('/rango/')

def like_category(request):
    cat_id = None
    if request.method == 'GET':
        cat_id = request.GET['category_id']

    likes = 0
    if cat_id:
        category = Category.objects.get(id =int(cat_id))
        if category:
            likes = category.likes + 1
            category.likes = likes
            category.save()

    return HttpResponse(likes)




def searchh(request):
    if 'q' in request.GET and request.GET['q']:
        query = request.GET['q']
        categorys = Category.objects.filter(name__icontains = query)
        return render(request, 'search_category.html',
            {'categorys': categorys, 'query': query})
    else:
        return HttpResponse('Please submit a search term.')


'''def searchh(request):
    if 'q' in request.GET:
        #get the selected category id
        sel_category = request.GET.get('category',None)
        #If it exists,get the category object
        if sel_category:
            category = get_object_or_404(Category,pk = sel_category)
        query = request.GET['q']
        results = Page.objects.filter(title__icontains = query)
        #If category object exists filter the set based on that
        if category:
            results = results.filter(category__icontains = category.name)
            #print resuls query
    else:
        query = ""
        results  = None
        categories = Category.objects.all()
    return render(request,'search_category.html',{'query':query,'results':results,'categories':categories})'''
 

#function for displaying profile
def profile(request):
    #user = UserProfile.objects.all()
    u = User.objects.get(username = request.user)

    try:
        up = UserProfile.objects.get(user=u)
    except:
        up = None

    context_dict = {'user':u,'userprofile':up}

    return render(request,"profile.html",context_dict)

#u = User.objects.get(username = request.user)

'''try:
    up = UserProfile.objects.get(user = u)'''

#context_dict = {'user':u, 'userprofile':up}

def search(request):

    result_list =[]

    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            #Run our bing function to get the result list:
            result_list = run_query(query)

    return render(request,'search.html',{'result_list':result_list})

def track_url(request):
    page_id = None
    url = '/rango/'
    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']
            try:
                page = Page.objects.get(id = page_id)
                page.views = page.views+1
                page.save()
                url = page.url
            except:
                pass
    return redirect(url)








