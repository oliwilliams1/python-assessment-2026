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
        self.quantity_labels: dict[MenuItem, ctk.CTkLabel] = {}
        self.summary_label: ctk.CTkLabel | None = None
        self.current_order: Order = Order()
    
    def place_order(self):
        self.orders.append(self.current_order)
        self.clear_current_order()
        self.update_past_order_summary()

    def modify_order(self, menu_item: MenuItem, delta: int):
        current_quantity = self.current_order.items[menu_item]
        new_quantity = max(0, current_quantity + delta)
        self.current_order.items[menu_item] = new_quantity
        self.update_order_summary()

    def clear_current_order(self):
        for item in self.current_order.items:
            self.current_order.items[item] = 0
        self.update_order_summary()

    def update_order_summary(self):
        summary = ""
        subtotal = 0.0

        for item, quantity in self.current_order.items.items():

            self.quantity_labels[item].configure(text=str(quantity))

            if quantity > 0:
                line_total = item.price * quantity
                subtotal += line_total

                summary += f"{item.name} x{quantity} - ${line_total:.2f}\n"

        is_order_empty: bool = True

        for item in self.current_order.items:
            if self.current_order.items[item] > 0:
                is_order_empty = False
                break

        gst_amount = subtotal * (GST - 1)
        total = subtotal * GST

        if is_order_empty:
            summary = "No items selected\n"
        else:
            summary += f"\nSubtotal: ${subtotal:.2f}\n"
            summary += f"GST: ${gst_amount:.2f}\n"
            summary += f"Total: ${total:.2f}"

        if self.summary_label != None:
            self.summary_label.configure(text=summary)

    def update_past_order_summary(self):
        summary = ""

        if self.past_order_label != None:
            self.past_order_label.configure(text=summary)

    def layout_menu_item(self, parent: ctk.CTkFrame, menu_item: MenuItem):
        parent.grid_rowconfigure(1, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        image_placeholder = ctk.CTkFrame(parent, height=120)
        image_placeholder.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        ctk.CTkLabel(image_placeholder, text="Image", font=ctk.CTkFont(size=18)).place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(parent, text=f"{menu_item.name}\n${menu_item.price:.2f}", font=ctk.CTkFont(size=18, weight="bold"), justify="center").grid(row=1, column=0, padx=10, pady=10)

        controls = ctk.CTkFrame(parent, fg_color="transparent")
        controls.grid(row=2, column=0, pady=(0, 10))

        ctk.CTkButton(controls, text="-", width=35, command=lambda: self.modify_order(menu_item, -1)).grid(row=0, column=0, padx=5)
        quantity_label = ctk.CTkLabel(controls, text="0", width=30)
        quantity_label.grid(row=0, column=1)
        self.quantity_labels[menu_item] = quantity_label

        ctk.CTkButton(controls, text="+", width=35, command=lambda: self.modify_order(menu_item, 1)).grid(row=0, column=2, padx=5)

    def layout_buttons(self, parent: ctk.CTkFrame):
        ctk.CTkButton(parent, text="Place Order", command=self.place_order).grid(row=0, column=0, padx=5, pady=5)
        ctk.CTkButton(parent, text="Clear", command=self.clear_current_order).grid(row=1, column=0, padx=5, pady=5)
        ctk.CTkButton(parent, text="Exit", command=app.destroy).grid(row=2, column=0, padx=5, pady=5)

    def layout_order_summary(self, parent: ctk.CTkScrollableFrame):
        ctk.CTkLabel(parent, text="Current Order", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)

        self.summary_label = ctk.CTkLabel(parent, text="No items selected", justify="left", anchor="w", font=ctk.CTkFont(size=16))
        self.summary_label.pack(padx=10, pady=10, fill="both", expand=True)

    def layout_past_orders(self, parent: ctk.CTkScrollableFrame):
        ctk.CTkLabel(parent, text="Past Orders", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)

        self.past_order_label = ctk.CTkLabel(parent, text="No past orders", justify="left", anchor="w", font=ctk.CTkFont(size=16))
        self.past_order_label.pack(padx=10, pady=10, fill="both", expand=True)

    def layout(self, app: ctk.CTk):
        ctk.CTkLabel(app, text=self.name, font=ctk.CTkFont(size=28, weight="bold")).pack(pady=20)

        rows = 2
        cols = 3

        top_frame = ctk.CTkFrame(app)
        top_frame.pack(padx=20, pady=20, fill="both", expand=True)

        for c in range(cols):
            top_frame.grid_columnconfigure(c, weight=1)

        for r in range(rows):
            top_frame.grid_rowconfigure(r, weight=1)

        items_index = 0
        for r in range(rows):
            for c in range(cols):
                if items_index >= len(items):
                    break

                cell_frame = ctk.CTkFrame(top_frame)
                cell_frame.grid(row=r, column=c, padx=10, pady=10, sticky="nsew")
                self.layout_menu_item(cell_frame, items[items_index])

                items_index += 1

        bottom_frame = ctk.CTkFrame(app)
        bottom_frame.pack(padx=20, pady=10, fill="both", expand=True)
        bottom_frame.grid_columnconfigure(0, weight=1)
        bottom_frame.grid_columnconfigure(1, weight=1)
        bottom_frame.grid_columnconfigure(2, weight=0)

        order_summary_frame = ctk.CTkScrollableFrame(bottom_frame)
        order_summary_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.layout_order_summary(order_summary_frame)

        past_orders_frame = ctk.CTkScrollableFrame(bottom_frame)
        past_orders_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.layout_past_orders(past_orders_frame)

        button_grid_frame = ctk.CTkFrame(bottom_frame)
        button_grid_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        self.layout_buttons(button_grid_frame)

    order: Order = Order()

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    app = ctk.CTk()
    app.geometry("1080x900")

    restaurant = Restaurant("My Restaurant")
    restaurant.layout(app)

    app.mainloop()