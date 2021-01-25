from django.apps import apps
from django.db.models import Avg, Count, Max, Min, Sum

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound


AGGREGATE_FUNCTIONS = {
    'average': Avg,
    'count': Count,
    'max': Max,
    'min': Min,
    'sum': Sum
}

class CoreView(APIView):

    def get_model(self, request_data):
        table_data = request_data['data']
        # Either 'table_name' or 'worksheet_id' is used to represent table's name
        table_name = table_data['table_name'] if 'table_name' in table_data else table_data['worksheet_id']
        Model = apps.get_model(app_label='core', model_name=table_name, require_ready=True) # Fetch model dynamically
        return Model

    def get_groupby_column_names(self, request_data):
        table_data = request_data['data']
        groupby_objects = table_data['groupby']
        column_names = []
        for groupby_object in groupby_objects:
            groupby_col_name = groupby_object['column']
            column_names.append(groupby_col_name)
        return tuple(column_names)

    def get_aggregate_dict(self, request_data):
        aggregate_objects = request_data['data']['aggregate']
        aggregates = {}
        for aggregate_object in aggregate_objects:
            aggregate_type = aggregate_object['type']
            aggregate_column = aggregate_object['column']
            aggregate_fn = AGGREGATE_FUNCTIONS[aggregate_type]
            key = aggregate_type + '_of_' + aggregate_column # average_of_experience
            value = aggregate_fn(aggregate_column) # Avg('experience') ; Avg is Django Aggregate object
            aggregates[key] = value # { 'average_of_experience': Avg('experience') }
        return aggregates

    def get_queryset(self, request_data):
        database_name = request_data['database_name']
        table_data = request_data['data']
        Model = self.get_model(request_data)
        queryset = Model.objects.using(database_name).all()
        if 'groupby' in table_data:
            groupby_column_names = self.get_groupby_column_names(request_data)
            queryset = queryset.values(*groupby_column_names) # unpack groupby columns
        if 'aggregate' in table_data:
            aggregate_dict = self.get_aggregate_dict(request_data)
            queryset = queryset.annotate(**aggregate_dict) # unpack aggregates
        if 'select_list' in table_data:
            columns_select_list = table_data['select_list']
            column_list = [col['column'] for col in columns_select_list]
            queryset = queryset.values(*column_list)
        return queryset

    # To transform response data into desired API format
    def transform(self, response_data):
        length = len(response_data)
        transformed_data = {"column": [], "data": [], "length": length}
        if length>0:
            table_fields = list(response_data[0].keys())
            transformed_data['column'] = table_fields        
            for table_row in response_data:
                table_row_values = list(table_row.values())
                transformed_data['data'].append(table_row_values)    
        return transformed_data

    def post(self, request):
        table_data = request.data['data']
        try:
            queryset = self.get_queryset(request.data)
        except:
            error_message = "Error 404, Couldn't find the specified data. Please try changing parameters."
            raise NotFound(error_message)

        if not('select_list' in table_data or 'aggregate' in table_data or 'groupby' in table_data): 
            queryset = queryset.values() # To have list of dictionaries to be transformed later
        transformed_response = self.transform(queryset)
        return Response(transformed_response)
