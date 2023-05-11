from django.http import JsonResponse
from rest_framework.decorators import api_view
import sqlite3
import os
from django.conf import settings

# Add this import statement
from . import load_data

@api_view(['POST'])
def load_data_call(request):
    payload = request.data
    
    try:
        result, num_values = load_data.process_data(payload)
        return JsonResponse({"Success": result})
    except Exception as e:
        print("Error occured : {}".format(e))
        
        
@api_view(['POST'])
def flush_stack_memory(request):
    db_path = os.path.join(settings.BASE_DIR, 'stack_memory.db')
    try:
        if os.path.exists(db_path):
            os.remove(db_path)
            return JsonResponse({"Success": "Database deleted successfully."})
        else:
            return JsonResponse({"Error": "Database file not found."})
    except Exception as e:
        return JsonResponse({"Error": "An error occurred while deleting the database: {}".format(e)})