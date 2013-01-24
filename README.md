# Django-On-Fire
## v 0.1

# OVERVIEW
On-Fire is a project initiated by [steve-twitter] and [pete-twitter]
of 4-south Studios to solve integration problems between Ember.js and Django 
(with Django-Rest-Framework).  The apps this package aims to help a user build 
are apps that live primarily in javascript on the client-side but need a robust 
back-end to handle validation, serving json, performing queries etc.

# DEPENDENCIES:

* Django 1.4-1.5 [django]
* Django-Rest-Framework (2.X the more current the better) [django-rest-framework]
* Ember.js [ember] 
* Ember-Data.js [ember-data]
** and its associated dependencies are not technically required to use 
** this package though some of the results of its use will remain hidden until 
** both Ember.js and Ember-data.js are engaged.


# FEATURES:
## Django-on-Fire currently has two major features and plans for more: 

1. JSON output available under a "root" that is definable by the user but should 
   be the model's singular or plural name depending on how many objects ember expects 
   to recieve.
    
   We are looking to add sideloading support to this paradigm as Ember already 
   supports it and has certain expectations for formatting.

2. URI-based query support allowing your Ember App to construct queries of the 
   following format:

   /appname/api/modelname?attr1=val1,val2&attr2=val3,val4

   Where the query results from attr1, attr2 will be OR'ed together to form a queryset.

   More notes on the details of this system are found below and in comments in the code.

# GETTING STARTED:

1. Add Django-on-Fire and its dependencies to INSTALLED_APPS in settings.py.

2. Create your views by extending the views found in jsonrootviews.py.  These are both 
   direct extensions of Django-Rest-Framework's standard API views.

3. If you desire URI-based query support then you must use the mixin provided in 
   query-mixins.py with the views that you wish to support this feature.
   IMPORTANT: You must also override the view's get_queryset method to call 
   filter_by_querystring (a method from the mixin).
   An example of such an overridden method may be found in the views.py file as part of 
   the included "JSONRootQueryMultipleModelsView". 

4. Finally, you could also elect to use the query support mixin without the jsonroot view
   or even without django-rest-framework views altogether.  Just mix it in with any view
   that returns models and be sure that filter_by_querystring is called as explained above.

# EMBER CONVENTIONS:
In order to fit seamlessly into Ember-Data's (admittedly often-changing) adapter/store 
classes, several conventions must be followed in your Django project.  Ember does also 
feature customizable adapters that can be molded to fit any backend api (in theory).

Toran Billups has an excellent [ember-data-django-rest-adapter] written that molds 
ember to fit around Django.  Because Ember is changing so much, I have chosen to modify 
Django and let Ember's API evolve while allowing them to stick to relatively immutable 
conventions.

Be sure to take these steps to make your django-on-fire project integrate with Ember.

1. If you use the jsonroot views, your views must declare a jsonroot attribute and this
   attribute should be the model's name/plural name.  Ember requires you to handle 
   special case plurals (like "people" for "person" models) on the front-end.  If you 
   intend to use these plural forms, be sure your view's jsonroot is set appropriately.

2. You MUST override your related field's to return by this naming convention:
    
   If model has attribute that is a foreignkey to another model (other_model)
   Then your serializer field must look as follows:
   other_model_id = serializers.PrimaryKeyRelatedField(source='other_model')

   This should be done automatically in a future version but for now this manual step is
   critical for allowing Ember to find your relational models in the serialized JSON.

    
[django]: https://github.com/django/django "Django on github"
[django-rest-framework]: https://github.com/tomchristie/django-rest-framework "Django-Rest-Framework"
[ember-data-django-rest-adapter]: https://github.com/toranb/ember-data-django-rest-adapter "Django-Rest-Ember-Adapter" 
[ember]: https://github.com/emberjs/ember "Ember on Github"
[ember-data]: https://github.com/emberjs/data "Ember-data on Github" 
[steve-twitter]: http://twitter.com/stv_kn "Steve Kane"
[pete-twitter]: http://twitter.com/chen_pete "Pete Chen"
