import customtkinter as ctk

GST = 1.15

class MenuItem:
    def __init__(self, name: str, price: float):
        self.name = name
        self.price = price

items: list[MenuItem] = [
    MenuItem("Burger", 5.99),
    MenuItem("Fries", 3.99),
    MenuItem("Soda", 3.49),
    MenuItem("Salad", 12.99),
    MenuItem("Pizza", 18.99)
]

class TrackedMenuItem:
    def __init__(self, menu_item: MenuItem):
        self.menu_item = menu_item
        self.times_ordered = 0

class Order:
    items: dict[MenuItem, int] = {item: 0 for item in items}

class Restaurant:
    def __init__(self, name: str):
        self.name = name
        self.orders: list[Order] = []
    
    def place_order(self, order: Order):
        self.orders.append(order)

    current_order: Order = Order()

    def layout_menu_item(self, parent: ctk.CTkFrame, menu_item: MenuItem):
        ctk.CTkButton(parent, text="+").grid(row=0, column=0, padx=5)
        ctk.CTkLabel(parent, text=menu_item.name + f" - ${menu_item.price:.2f}", font=ctk.CTkFont(size=16)).grid(row=0, column=1, padx=5)
        ctk.CTkButton(parent, text="-").grid(row=0, column=2, padx=5)

    def layout(self, app: ctk.CTk):
        ctk.CTkLabel(app, text=self.name, font=ctk.CTkFont(size=24, weight="bold")).pack(pady=10)
        
        rows: int = 2
        cols: int = 3
        items_index = 0

        grid_frame = ctk.CTkFrame(app)
        grid_frame.pack(padx=20, pady=20, fill="both", expand=True)

        for r in range(rows):
            for c in range(cols):
                if items_index < len(items):
                    cell_frame = ctk.CTkFrame(grid_frame)
                    cell_frame.grid(row=r, column=c, padx=10, pady=10, sticky="nsew")

                    self.layout_menu_item(cell_frame, items[items_index])
                    items_index += 1

        button_grid_frame = ctk.CTkFrame(app)
        button_grid_frame.pack(pady=10)
        ctk.CTkButton(button_grid_frame, text="Place Order").grid(row=0, column=0, padx=5, pady=5)
        ctk.CTkButton(button_grid_frame, text="View Orders").grid(row=0, column=1, padx=5, pady=5)
        ctk.CTkButton(button_grid_frame, text="Clear").grid(row=0, column=2, padx=5, pady=5)
        ctk.CTkButton(button_grid_frame, text="Exit", command=app.destroy).grid(row=0, column=3, padx=5, pady=5)

    order: Order = Order()

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    app = ctk.CTk()
    app.geometry("800x600")

    restaurant = Restaurant("My Restaurant")
    restaurant.layout(app)

    app.mainloop()