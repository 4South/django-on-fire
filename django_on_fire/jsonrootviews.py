from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView
from rest_framework.response import Response
from django.utils.encoding import iri_to_uri

class JSONRootSingleModelView(RetrieveUpdateDestroyAPIView):
  '''
  allows GET, PUT, and DELETE
  GET returns a single instance of the view's model with the json data 
  nested inside the view's jsonroot
  '''
  #retrieve is called by self.get and returns json with self.jsonroot 
  def retrieve(self, request, *args, **kwargs):
    json_response = {}
    self.object = self.get_object()
    serial_data = self.get_serializer(self.object).data
    json_response[self.jsonroot] = serial_data 
    return Response(json_response) 

class JSONRootMultipleModelView(ListCreateAPIView):
  '''
  allows GET, POST
  GET returns a list of the view's model that may vary depending on queryset
  
  Overrides method inherited from django's MultipleObjectMixin
  this method allows for request.META.get('QUERY_STRING') to be evaluated 
  and converted to a query that is run against the database
  N.B. setting a queryset attribute on the view will raise an error
  '''
  def list(self, request, *args, **kwargs):
    json_plural_response = {}
    #TODO
    #this tester is here because of occasional issues w/ QUERY_STRING
    tester = iri_to_uri(request.META.get('QUERY_STRING', ''))
    queryset = self.get_queryset()
    self.object_list = self.filter_queryset(queryset)
    #code from DJRF List mixin that checks if empty querysets are allowed
    allow_empty = self.get_allow_empty()
    if not allow_empty and not self.object_list:
      class_name = self.__class__.__name__ 
      error_msg = self.empty_error % {'class_name': class_name} 
      raise Http404(error_msg)
    #CODE FOR PAGINATION HAS BEEN REMOVED FOR THE MOMENT
    #MAY ADD IT BACK AT A LATER TIME IF DESIRED
    serial_data = self.get_serializer(self.object_list).data
    json_plural_response[self.jsonroot] = serial_data
    return Response(json_plural_response)
