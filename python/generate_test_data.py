from database import guardar_pedido
import uuid
import random

def generate_orders():
    products = [
        ("Pizza Margarita", "Sin albahaca"),
        ("Hamburguesa Completa", "Poco hecha"),
        ("Tacos al Pastor", "Sin cilantro"),
        ("Sushi Variado", "Con extra de wasabi"),
        ("Pasta Carbonara", "")
    ]

    print("Generating test orders...")
    
    # Generate 3 tickets
    for _ in range(3):
        ticket_id = str(uuid.uuid4())[:8].upper()
        # 1 to 3 items per ticket
        num_items = random.randint(1, 3)
        
        for _ in range(num_items):
            prod, note = random.choice(products)
            qty = random.randint(1, 2)
            success = guardar_pedido(ticket_id, prod, qty, note)
            if success:
                print(f"Added: {qty}x {prod} (Ticket: {ticket_id})")
            else:
                print(f"Failed to add order for ticket {ticket_id}")

if __name__ == "__main__":
    generate_orders()
