from collections import defaultdict
from src.models import (
    OrderExtractionResult,
    ProcessedOrderReport,
    AggregatedOrderLine
)

def aggregate_orders(extraction: OrderExtractionResult) -> ProcessedOrderReport:
    # Key: (item_name, unit) -> dict with total_quantity and list of studios
    grouped = defaultdict(lambda: {"total_quantity": 0, "studios": []})
    pending_clarifications = []

    for item in extraction.items:
        # Only aggregate items that are complete and have both quantity and unit specified 
        if item.is_complete and item.quantity is not None and item.unit is not None:
            key = (item.item_name.strip(), item.unit.strip())
            grouped[key]["total_quantity"] += item.quantity
            if item.studio not in grouped[key]["studios"]:
                grouped[key]["studios"].append(item.studio + " " + "(" + str(item.quantity) + " " + item.unit + ")")
        else:
            pending_clarifications.append(item)

    aggregated_lines = [
        AggregatedOrderLine(
            item_name=item_name,
            unit=unit,
            total_quantity=data["total_quantity"],
            studios=data["studios"]
        )
        for (item_name, unit), data in grouped.items()
    ]

    return ProcessedOrderReport(
        valid_aggregated_orders=aggregated_lines,
        pending_clarifications=pending_clarifications
    )