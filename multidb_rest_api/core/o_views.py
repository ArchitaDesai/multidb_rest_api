"""
This is old views file.
Since one of the cases is not working with dynamic serializer, have create APIView & used Response.
Main view code is under core/views.py - this file is for further improvement to be used as serializer
"""

from django.apps import apps
from django.db.models import Avg, Count, Max, Min, Sum

from rest_framework import viewsets, serializers
from rest_framework.response import Response

from .serializers import CoreModelSerializer

AGGREGATE_FUNCTIONS = {
    'avg': Avg,
    'count': Count,
    'max': Max,
    'min': Min,
    'sum': Sum
}

"""
Works well for Showing all columns & specific columns/fields
However, serializer fields are not being defined dynamically for aggregation column 
"""
class CoreViewSet(viewsets.ModelViewSet):

    @property
    def database_name(self):
        return self.request.data['database_name']

    @property
    def request_table_data(self):
        table_data = self.request.data['data']
        return table_data 

    @property
    def model(self):
        table_data = self.request_table_data
        # Either 'table_name' or 'worksheet_id' is used to represent table's name
        table_name = table_data['table_name'] if 'table_name' in table_data else table_data['worksheet_id']
        Model = apps.get_model(app_label='core', model_name=table_name, require_ready=True)
        return Model

    @property
    def columns(self):
        table_data = self.request_table_data
        if 'select_list' in table_data:
            columns_select_list = table_data['select_list']
            column_list = [col['column'] for col in columns_select_list]
            columns_tuple = tuple(column_list)
        elif 'aggregate' in table_data or 'groupby' in table_data:
            column_list = []
            # Commenting aggregate for serializer
            if 'aggregate' in table_data:
                column_list = [*self.aggregate_dict.keys()] # Added aggregate names to column_list
            if 'groupby' in table_data:
                for groupby_column_name in self.groupby_column_names:
                    column_list.append(groupby_column_name)
            columns_tuple = tuple(column_list)
        else:
            columns_tuple = '__all__'
        return columns_tuple

    @property
    def groupby_column_names(self):
        table_data = self.request_table_data
        groupby_objects = table_data['groupby']
        column_names = []
        for groupby_object in groupby_objects:
            groupby_col_name = groupby_object['column']
            column_names.append(groupby_col_name)
        print("Group by column names:", column_names)
        return tuple(column_names)

    @property
    def aggregate_dict(self):
        aggregate_objects = self.request_table_data['aggregate']
        aggregates = {}
        for aggregate_object in aggregate_objects:
            aggregate_type = aggregate_object['type']
            aggregate_column = aggregate_object['column']
            aggregate_fn = AGGREGATE_FUNCTIONS[aggregate_type]
            # key = aggregate_type + '_of_' + aggregate_column # average_of_experience
            key = aggregate_column + '__' + aggregate_type # experience__avg
            value = aggregate_fn(aggregate_column) # Avg('experience') ; Avg is Django Aggregate object
            aggregates[key] = value # { 'average_of_experience': Avg('experience') }
        print("Aggregates names:", aggregates)        
        return aggregates

    def get_queryset(self):
        Model = self.model
        database_name = self.database_name
        table_data = self.request_table_data
        queryset = Model.objects.using(database_name).all()
        if 'groupby' in table_data:
            queryset = queryset.values(*self.groupby_column_names)
            print("Groupby queryset: ", queryset)
        if 'aggregate' in table_data:
            queryset = queryset.annotate(**self.aggregate_dict) # unpack aggregates
        print("FINAL Queryset: ", queryset)
        return queryset

    def get_serializer_class(self):
        print("Ser class")
        aggregate_columns = [*self.aggregate_dict]

        # serializerObject = CoreModelSerializer()
        # for aggregate_column in aggregate_columns:
        #     # serializerObject.aggregate_column = serializers.SerializerMethodField()
        #     setattr(CoreModelSerializer(), aggregate_column, serializers.SerializerMethodField())
        # print("CORE MODEL SRL ", CoreModelSerializer)

        CoreModelSerializer.Meta.model = self.model
        CoreModelSerializer.Meta.fields = self.columns
        

        field_name_objects = self.model._meta.get_fields()
        field_names = [field_name_object.name for field_name_object in field_name_objects]
        return CoreModelSerializer

    def transform(self, data):
        length = len(data)
        transformed_data = {"column": [], "data": [], "length": length}
        table_fields = list(data[0].keys())
        transformed_data['column'] = table_fields        
        for table_row in data:
            table_row_values = list(table_row.values())
            transformed_data['data'].append(table_row_values)    
        return transformed_data

    def list(self, request):
        serializer_response = super(CoreViewSet, self).list(request) # To override serializer response with custom response
        serializer_data = serializer_response.data

        data = self.transform(serializer_data)
        return Response(data)
