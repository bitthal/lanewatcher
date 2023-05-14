from django.http import JsonResponse
from django.shortcuts import render
from .models import LaneData, Planogram, Pending, Processed
from django.core import serializers
import logging, os, traceback

# Set up logging
log_directory = 'logs'
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

log_filename = os.path.join(log_directory, 'views.log')
logging.basicConfig(filename=log_filename, level=logging.DEBUG, format='%(asctime)s [%(levelname)s]: %(message)s')

logger = logging.getLogger(__name__)

def table(request):
    try:
        logger.info("Rendering table view")
        lane_data = LaneData.objects.all()
        data = {}
        for position in range(8, 0, -1):
            data[position] = {"lane1": {"upper": "", "lower": ""}, "lane2": {"upper": "", "lower": ""}}

        for entry in lane_data:
            lane = "lane1" if entry.lane == 1 else "lane2"
            data[entry.position][lane]['upper'] = entry.upper
            data[entry.position][lane]['lower'] = entry.lower

        return render(request, 'monotainers_stack/table.html', {'data': data})
    except Exception as e:
        tb_str = traceback.format_exception(type(e), e, e.__traceback__)
        tb_str = ''.join(tb_str)
        logger.error("Error while rendering table view: %s\n%s", str(e), tb_str)
        # You can return an appropriate error response here if needed

def fetch_data(request):
    try:
        logger.info("Fetching lane data")
        data = list(LaneData.objects.values())
        return JsonResponse(data, safe=False)
    except Exception as e:
        tb_str = traceback.format_exception(type(e), e, e.__traceback__)
        tb_str = ''.join(tb_str)
        logger.error("Error while fetching lane data: %s\n%s", str(e), tb_str)
        # You can return an appropriate error response here if needed

def get_all_data(request):
    try:
        logger.info("Getting all data")
        planogram_data = Planogram.objects.all()
        data = []

        for planogram in planogram_data:
            lane_data = list(LaneData.objects.filter(lane=planogram.lane_number).values())
            pending_queryset = Pending.objects.filter(lane=planogram)
            processed_queryset = Processed.objects.filter(lane=planogram)

            pending_data = {
                "monotainers": [{"monotainer_id": p.monotainer_id} for p in pending_queryset],
                "total_monotainers": pending_queryset.count(),
            }

            real_time_positions = []
            for entry in lane_data:
                position_data = {
                    "position": entry["position"],
                    "upper": {
                        "monotainer_id": entry["upper"],
                        "misplaced": 0  # Dummy value
                    },
                    "lower": {
                        "monotainer_id": entry["lower"],
                        "misplaced": 0  # Dummy value
                    },
                }
                real_time_positions.append(position_data)

            processed_data = {
                "monotainers": [{"monotainer_id": p.monotainer_id} for p in processed_queryset],
                "total_monotainers": processed_queryset.count(),
                "trucks_required": planogram.trucks_required,
                                "trucks_ordered": planogram.trucks_ordered,
            }

            data.append({
                'lane_number': planogram.lane_number,
                'lane_name': planogram.lane_name,
                'planogram': {
                    'in_stage': planogram.in_staged,
                    'mapped': planogram.mapped,
                    'missing': planogram.missing,
                    'total': planogram.total,
                },
                'pending': pending_data,
                'real_time_positions': real_time_positions,
                'processed': processed_data,
            })

        return JsonResponse({'lanes': data})
    except Exception as e:
        tb_str = traceback.format_exception(type(e), e, e.__traceback__)
        tb_str = ''.join(tb_str)
        logger.error("Error while getting all data: %s\n%s", str(e), tb_str)
        # You can return an appropriate error response here if needed

