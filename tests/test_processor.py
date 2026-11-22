from src.models import ExtractedItem, OrderExtractionResult
from src.models import ExtractedItem, OrderExtractionResult
from src.processor import aggregate_orders 

def test_aggregation_and_exclusion():
    mock_extraction = OrderExtractionResult(items=[
        ExtractedItem(studio="Innenstadt", item_name="Nitrilhandschuhe M", quantity=3, unit="Packung", is_complete=True),
        ExtractedItem(studio="Eimsbüttel", item_name="Nitrilhandschuhe M", quantity=2, unit="Packung", is_complete=True),
        ExtractedItem(studio="Eimsbüttel", item_name="Kochsalzlösung", quantity=None, unit="Flasche", is_complete=False, clarification_question="Wie viele Flaschen?"),
        ExtractedItem(studio="Wandsbek", item_name="Kochsalzlösung", quantity=2, unit="Flasche", is_complete=True),
    ])

    report = aggregate_orders(mock_extraction)

    # Verify Nitrilhandschuhe M summed to 5
    gloves = next(i for i in report.valid_aggregated_orders if i.item_name == "Nitrilhandschuhe M")
    assert gloves.total_quantity == 5
    assert gloves.studios == ["Innenstadt (3 Packung)", "Eimsbüttel (2 Packung)"]

    # Verify Kochsalzlösung only includes Wandsbek (2), excluding Eimsbüttel
    saline = next(i for i in report.valid_aggregated_orders if i.item_name == "Kochsalzlösung")
    assert saline.total_quantity == 2
    assert saline.studios == ["Wandsbek (2 Flasche)"]

    # Verify pending clarification contains Eimsbüttel
    assert len(report.pending_clarifications) == 1
    assert report.pending_clarifications[0].studio == "Eimsbüttel"