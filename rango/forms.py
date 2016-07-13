from django import forms
from rango.models import Page,Category,UserProfile
from django.contrib.auth.models import User
from dal import autocomplete

class CategoryForm(forms.ModelForm): #forms.FutureModelForm
    name = forms.CharField(max_length = 128,help_text = 'Please Enter category name')
    likes = forms.IntegerField(widget = forms.HiddenInput(), initial = 0)
    views = forms.IntegerField(widget = forms.HiddenInput(), initial = 0)

    #An inline cass to provide additional information on the form
    #Meta class links form to its model class

    class Meta:
        #Provide association between Modelform and model
        model = Category
        fields = ('name',)
        widgets = { 'name':autocomplete.ModelSelect2(url = '/rango/CategoryAutocomplete')}
        #ModelSelect2

class PageForm(forms.ModelForm):
    title = forms.CharField(max_length = 128, help_text ="Plese enter title of the page.")
    url = forms.URLField(max_length = 200,help_text = "Please enter the URL of the page.")
    views = forms.IntegerField(widget = forms.HiddenInput(),initial = 0)

    class Meta:
        #provide an association between Modelform and model
        model = Page

         #What fields do we want to include in our form?
        # This way we don't need every field in the model present.
        # Some fields may allow NULL values, so we may not want to include them...
        # Here, we are hiding the foreign key.

        fields = ('title', 'url', 'views')

    def clean(self):
        cleaned_data = self.cleaned_data
        url = cleaned_data.get('url')

        #if url is not empty and doesnt start with 'http://' prepend 'http://

        if url and not url.startswith('http://'):
            url = 'http://' + url
            cleaned_data['url'] = url

        return cleaned_data

class UserForm(forms.ModelForm):
    username = forms.CharField(help_text = "Please enter a username.")
    email = forms.CharField(help_text = "Please enter your email")
    password = forms.CharField(widget = forms.PasswordInput(),help_text = "Please enter a password")
        
    class Meta:
        model  = User
        fields = ('username','email','password')

class UserProfileForm(forms.ModelForm):
    website = forms.URLField(help_text = "Please enter your website.", required = False)
    picture = forms.ImageField(help_text = "Select a profile image to upload", required = False)

    class Meta:

        model = UserProfile
        fields = ('website', 'picture')

    
        

        

        
    
