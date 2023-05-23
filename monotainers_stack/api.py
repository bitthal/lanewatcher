import logging
import os
import traceback
from django.http import JsonResponse
from rest_framework.decorators import api_view
import sqlite3
from django.conf import settings
from . import load_data
from .db2_setup import insert_initial_data
# from load_data import reset_files, delete_temp_file

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
def load_data_call2(request):
    payload = request.data
    try:
        message = load_data.process_data2(payload)
        # logger.info("Data processed successfully")
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


# @api_view(['POST'])
# def flush_stack_memory2(request):
#     db_path = os.path.join(settings.BASE_DIR, 'stack_memory2.db')
#     try:
#         if os.path.exists(db_path):
#             conn = sqlite3.connect(db_path)
#             cursor = conn.cursor()

#             # Delete all records from the lane_data table
#             cursor.execute("DELETE FROM lane_data")
#             conn.commit()
#             conn.close()

#             logger.info("All records deleted successfully from the database")
#             return JsonResponse({"Success": "All records deleted successfully from the database."})
#         else:
#             logger.warning("Database file not found")
#             return JsonResponse({"Error": "Database file not found."})
#     except Exception as e:
#         tb_str = traceback.format_exception(type(e), e, e.__traceback__)
#         tb_str = ''.join(tb_str)
#         logger.error("An error occurred while deleting records from the database: %s\n%s", str(e), tb_str)
#         return JsonResponse({"Error": "An error occurred while deleting records from the database: {}".format(e)})


# from django.http import JsonResponse
# from django.conf import settings
# from rest_framework.decorators import api_view
# import os
# import sqlite3
# import json
# import traceback
# import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
def flush_stack_memory2(request):
    load_data.reset_files()
    load_data.delete_temp_file()
    db_path = os.path.join(settings.BASE_DIR, 'stack_memory2.db')
    try:
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Delete all records from the lane_data table
            cursor.execute("DELETE FROM lane_data")
            conn.commit()

            # Insert initial data
            insert_initial_data(conn)

            conn.close()

            # logger.info("All records replaced successfully with initialized values in the database")
            return JsonResponse({"Success": "All records replaced successfully with initialized values in the database."})
        else:
            logger.warning("Database file not found")
            return JsonResponse({"Error": "Database file not found."})
    except Exception as e:
        tb_str = traceback.format_exception(type(e), e, e.__traceback__)
        tb_str = ''.join(tb_str)
        logger.error("An error occurred while replacing records with initialized values in the database: %s\n%s", str(e), tb_str)
        return JsonResponse({"Error": "An error occurred while replacing records with initialized values in the database: {}".format(e)})

# The insert_initial_data function remains the same as you provided
