import json
from src.extractor import extract_orders_from_messages
from src.processor import aggregate_orders

from src.sample_order_messages import SAMPLE_MESSAGES

def main():
    print("Extracting structured order items via Groq API (qwen/qwen3.8-27b)...")
    extracted_data = extract_orders_from_messages(SAMPLE_MESSAGES)

    print("Extracted Order Data: "+str(extracted_data.model_dump_json(indent=2)))

    print("Aggregating valid orders and filtering incomplete items...\n")
    report = aggregate_orders(extracted_data)

    print("=" * 60)
    print("STRUKTURIERTE BESTELLÜBERSICHT (GESAMTSUMME)")
    print("=" * 60)
    print(f"{'Artikel':<25} | {'Einheit':<10} | {'Menge':<6} | {'Studios'}")
    print("-" * 60)
    for line in report.valid_aggregated_orders:
        studios_str = ", ".join(line.studios)
        print(f"{line.item_name:<25} | {line.unit:<10} | {line.total_quantity:<6} | {studios_str}")

    print("\n" + "=" * 60)
    print("OFFENE RÜCKFRAGEN (NICHT IN GESAMTSUMME ENTHALTEN)")
    print("=" * 60)
    for item in report.pending_clarifications:
        print(f"Studio:  {item.studio}")
        print(f"Artikel: {item.item_name} (Unvollständige Angabe)")
        print(f"Entwurf: \"{item.clarification_question}\"")
        print("-" * 60)

    print("\nJSON-Ausgabe:")
    print(report.model_dump_json(indent=2))

if __name__ == "__main__":
    main()