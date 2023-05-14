import logging
import os
import traceback
from django.http import JsonResponse
from rest_framework.decorators import api_view
import sqlite3
from django.conf import settings
from . import load_data

# Set up logging
log_directory = 'logs'
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

log_filename = os.path.join(log_directory, 'api.log')
logging.basicConfig(filename=log_filename, level=logging.DEBUG, format='%(asctime)s [%(levelname)s]: %(message)s')

logger = logging.getLogger(__name__)

@api_view(['POST'])
def load_data_call(request):
    payload = request.data
    try:
        message = load_data.process_data(payload)
        logger.info("Data processed successfully")
        return JsonResponse({"Message": message})
    except Exception as e:
        tb_str = traceback.format_exception(type(e), e, e.__traceback__)
        tb_str = ''.join(tb_str)
        logger.error("Error occurred while processing the data: %s\n%s", str(e), tb_str)
        return JsonResponse({"Error": "An error occurred while processing the data: {}".format(e)})

@api_view(['POST'])
def flush_stack_memory(request):
    db_path = os.path.join(settings.BASE_DIR, 'stack_memory.db')
    try:
        if os.path.exists(db_path):
            os.remove(db_path)
            logger.info("Database deleted successfully")
            return JsonResponse({"Success": "Database deleted successfully."})
        else:
            logger.warning("Database file not found")
            return JsonResponse({"Error": "Database file not found."})
    except Exception as e:
        tb_str = traceback.format_exception(type(e), e, e.__traceback__)
        tb_str = ''.join(tb_str)
        logger.error("An error occurred while deleting the database: %s\n%s", str(e), tb_str)
        return JsonResponse({"Error": "An error occurred while deleting the database: {}".format(e)})
