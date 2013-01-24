from django.db.models import Q
from django.core.exceptions import ImproperlyConfigured
from django_on_fire.jsonrootviews import JSONRootMultipleModelView
from django_on_fire.querymixin import QuerySetMixin

class JSONRootQueryMultipleModelView (JSONRootMultipleModelView, QuerySetMixin):
  '''
  allows GET, POST
  GET returns a list of the view's model that may vary depending on queryset
  
  Overrides method inherited from django's MultipleObjectMixin
  this method allows for request.META.get('QUERY_STRING') to be evaluated 
  and converted to a query that is run against the database
  N.B. setting a queryset attribute on the view will raise an error
  '''
  def get_queryset(self):
    #check if this view is implementing custom URI-based queryset handling
    has_queryset_filter = hasattr(self, 'filter_by_querystring')
    query_string = self.request.META.get('QUERY_STRING')

    if self.queryset is not None:
      raise ImproperlyConfigured("View may NOT have queryset attribute defined") 
    if self.model is None:
      raise ImproperlyConfigured("View must declare a model attribute")
    if (has_queryset_filter and query_string): 
      queryset = self.filter_by_querystring(query_string)
    else:
      queryset = self.model._default_manager.all()
    return queryset
      
