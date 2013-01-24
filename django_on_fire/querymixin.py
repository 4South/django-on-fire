from django.db.models.fields import FieldDoesNotExist
from django.db.models.fields import CharField, TextField, IntegerField, BigIntegerField, FloatField, DecimalField
from django.db.models.fields.related import ForeignKey
from django.db.models import Q
from django.http import Http404
import re

class QuerySetMixin(object):
  '''
  N.B. This view may be used with any view that returns multiple models
  provided that get_queryset is overridden
  It adds support for custom querysets based on url query_strings
  IE  http://url.com/model?attribute=value
      http://url.com/model?attr1=val1,val2&attr2=val3,val4 etc
  '''
  #values that may require special handling when forming queries
  special_query_values =  (  'null',
                             'Null',
                             'None',
                             'none',   )
  #this is a tuple of the Django FieldTypes currently supported
  supported_fields =      (  CharField,       
                             TextField,       
                             IntegerField,    
                             BigIntegerField, 
                             FloatField,      
                             DecimalField,   
                             ForeignKey,       ) 
  #these fields are a subset of supported_fields that expect string values
  #therefore special_query_values will be evaluated as normal strings
  #rather than as indicators that null values should be returned
  string_fields =         ( CharField,
                            TextField,  )

  def is_instance_of (self, field_type, field_list):
    '''
    checks if fieldtype is instance of any member of fieldlist
    '''
    if any([isinstance(field_type, field) for field in field_list]):
      return True
    else: return False 
  
  def build_dict_from_vals (self, values, field_type, is_null):
    '''
    helper method that coerces values to their python-type and constructs
    a dict of clean values and a boolean is_null flag for use in queryset filtering
    '''
    python_vals = [field_type.to_python(val) for val in values]
    return {'clean_vals': python_vals, 'is_null': is_null}

  def obtain_attr_dict (self, field_type, query_vals):
    '''
    separate query parameters into 'safe' and 'special' lists 
    safe values may be used as query parameters safely while special values will hold
    possible 'none' or 'null' variants that may be handled differently when querying 
    against numerical fields

    underlying field-type and pass appropriate values off to build_dict_from_vals to 
    construct a dictionary for use in building filtered queryset 
    '''
    special_case_values = [val for val in query_vals if val in self.special_query_values]
    normal_values = [val for val in query_vals if val not in self.special_query_values]

    if not special_case_values:
      return self.build_dict_from_vals(normal_values, field_type, False)
    else: 
      #if a string_field, add special case values back to list and return
      if self.is_instance_of(field_type, self.string_fields):
        return self.build_dict_from_vals(normal_values+special_case_values, field_type, False)
      else:
        #all special-case values are variations on 'null' or 'None' and are assumed to mean
        #include models with this field==None
        return self.build_dict_from_vals(normal_values, field_type, True)

  def filter_each_queryset (self, query_string, model, initial_queryset):
    '''
    coerce each query string into field name and query value(s)
    obtain the field_type for the field
    determine if the field_type is one of the supported queriable fields
    construct and return a filtered queryset 
    '''
    value_dict = {}
    null_dict = {}

    field_name, query_value_string = [el.strip() for el in query_string.split('=')]
    field_type = model._meta.get_field(field_name) 
    query_values = [value.strip() for value in query_value_string.split(',')]
    if not self.is_instance_of(field_type, self.supported_fields):
      raise FieldDoesNotExist("%s is not able to be queried against" % field_type)
    attr_dict = self.obtain_attr_dict(field_type, query_values)
    
    value_dict[field_name+"__in"] = attr_dict['clean_vals']
    #Q syntax on fieldname__isnull=False will return all objects that have non-null vals
    if attr_dict['is_null']:
      null_dict[field_name+"__isnull"] = True 
     
    filtered_queryset = initial_queryset.filter(  Q(**value_dict) | Q(**null_dict)  )
    return filtered_queryset

  def match_querystring (self, query_string):
    '''
    determine if querystring matches expected formats
    E.G ?att1=val1, val2&att2=val3, val5, ...
    '''
    key_value_pairs = re.compile(r'^([^=&]+=[^=&]+&?)+$')
    if key_value_pairs.match(query_string): return True
    else: return False 

  def obtain_queryset_from_kvpairs(self, query_string):
    '''
    split query string into key/values pairs based on position of &
    construct queryset by looping over all key/value pairs and building
    a queryset.filter using helper methods before returning final queryset
    '''
    queries = [query.strip() for query in query_string.split('&') if query]
    queryset = self.model._default_manager.all()
    for query in queries:
      queryset = self.filter_each_queryset(query, self.model, queryset) 
    return queryset

  def filter_by_querystring (self, query_string):
    '''
    initial method called by view that is used to obtain a queryset based on 
    URI query_string 
    if querystring is improperly formatted, will return empty queryset
    '''
    if self.match_querystring(query_string):
      return self.obtain_queryset_from_kvpairs(query_string)
    else:
      #TODO: Add error raising here to alert client of improper query format
      return model._default_manager.none() 
