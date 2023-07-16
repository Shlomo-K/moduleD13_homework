from django_filters import FilterSet
from .models import Comments, Notice
 
class PostFilter(FilterSet):
   
    class Meta:
        model = Comments
        fields = {
            'Notice': ['exact']
            }
