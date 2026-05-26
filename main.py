# Import necessary libraries
# run `pip install customtkinter pillow` in cmd to install dependencies
import customtkinter as ctk
import copy
from PIL import Image

# Data classes for constants
class MenuItem:
	def __init__(self, name: str, price: float, image_path: str = ""):
		self.name = name
		self.price = price
		self.image_path = image_path

# Constants
GST: float = 1.15 # 15% GST
N_COLUMNS: int = 3
MIN_QUANTITY: int = 0
MAX_QUANTITY: int = 5

# Available menu items
ITEMS: list[MenuItem] = [
	MenuItem("Burger", 5.99, "burger.jpg"),
	MenuItem("Fries", 3.99, "fries.jpg"),
	MenuItem("Soda", 3.49, "soda.jpg"),
	MenuItem("Salad", 12.99, "salad.jpg"),
	MenuItem("Seitan", 9.99, "seitan.jpg")
]

# Class to track menu item orders
class TrackedMenuItem:
	def __init__(self, menu_item: MenuItem):
		self.menu_item = menu_item
		self.times_ordered: int = 0

# Class to represent an order, which contains multiple menu items and their respective quantities
class Order:
	def __init__(self):
		self.items: dict[MenuItem, int] = {item: 0 for item in ITEMS}

# Maintains the state of the restaurant, including current orders, past orders, and GUI
class Restaurant:
	# Initialise a collection of class variables
	def __init__(self, name: str):
		self.name = name
		self.past_orders: list[Order] = [] # List of past orders
		self.quantity_labels: dict[MenuItem, ctk.CTkLabel] = {} # Maps menu items to their quantity labels in the GUI
		self.decrement_buttons: dict[MenuItem, ctk.CTkButton] = {} # Maps menu items to their decrement buttons in the GUI
		self.increment_buttons: dict[MenuItem, ctk.CTkButton] = {} # Maps menu items to their increment buttons in the GUI
		self.place_order_button: ctk.CTkButton | None = None # Reference to the "Place Order" button in the GUI
		self.summary_label: ctk.CTkLabel | None = None # Reference to the current order summary label in the GUI
		self.email_entry: ctk.CTkEntry | None = None # Reference to the email entry field in the GUI
		self.email_error_label: ctk.CTkLabel | None = None # Reference to the email error label in the GUI
		self.current_order: Order = Order()
	
	# Helper function to validate email
	def is_email_valid(self) -> bool:
		if self.email_entry == None:
			return False

		email = self.email_entry.get().strip()

		# Basic validation
		return "@" in email and "." in email and len(email) > 5

	# Place the current order, add it to the list of past orders, and update the GUI
	def place_order(self):
		# Validate email before ordering
		if not self.is_email_valid():
			if self.email_error_label != None:
				self.email_error_label.configure(text="Please enter a valid email")
			return

		# Clear error message
		if self.email_error_label != None:
			self.email_error_label.configure(text="")

		# Copy the current order to past orders list
		self.past_orders.append(copy.deepcopy(self.current_order))

		# Clear the current order and update the GUI
		self.clear_current_order()
		self.update_past_order_summary()

	# Used for applying a delta to the quanity of a menu item in the current order & updating the GUI accordingly
	def modify_order(self, menu_item: MenuItem, delta: int):
		# Apply delta
		current_quantity = self.current_order.items[menu_item]
		new_quantity = current_quantity + delta

		# Clamp between MIN_QUANTITY and MAX_QUANTITY
		new_quantity = max(MIN_QUANTITY, min(MAX_QUANTITY, new_quantity))

		# Store updated quantity
		self.current_order.items[menu_item] = new_quantity

		# Update GUI
		self.update_order_summary()

	# Clear the current order and update the GUI
	def clear_current_order(self):
		# Set the quantity of all items in the current order to 0
		for item in self.current_order.items:
			self.current_order.items[item] = 0

		# Update the order summary in GUI
		self.update_order_summary()

	# Clear all past orders and update the GUI
	def clear_past_orders(self):
		self.past_orders.clear()
		self.update_past_order_summary()

	# Helper function to check if an order is empty
	def is_order_empty(self, order: Order) -> bool:
		for item in order.items:
			if order.items[item] > 0:
				return False
		return True
	
	# Updates the order summary section of the GUI
	def update_order_summary(self):
		# Declare variables
		summary: str = ""
		subtotal: float = 0.0

		# Iterate through all items to calc subtotal and build summary string
		for item, quantity in self.current_order.items.items():
			# Update the quantity label for the item in the GUI
			self.quantity_labels[item].configure(text=str(quantity))

			# Visual cues for limits
			decrement_button = self.decrement_buttons[item]
			increment_button = self.increment_buttons[item]

			# Disable decrement button at minimum
			if quantity <= MIN_QUANTITY:
				decrement_button.configure(state="disabled")
			else:
				decrement_button.configure(state="normal")

			# Disable increment button at maximum
			if quantity >= MAX_QUANTITY:
				increment_button.configure(state="disabled")
			else:
				increment_button.configure(state="normal")

			# Only have the item appear in summary if there is more than 0 of them
			if quantity > 0:
				line_total = item.price * quantity
				subtotal += line_total
				summary += f"{item.name} x {quantity} - ${line_total:.2f}\n"

		# Check if the order is empty
		is_order_empty: bool = self.is_order_empty(self.current_order)

		# Disable place order button if order is empty
		if self.place_order_button != None:
			if is_order_empty:
				self.place_order_button.configure(state="disabled")
			else:
				self.place_order_button.configure(state="normal")

		# Calculate the GST amount and total
		gst_amount = subtotal * (GST - 1)
		total = subtotal * GST

		# Build the summary string
		summary += f"\nSubtotal: ${subtotal:.2f}\n"
		summary += f"GST: ${gst_amount:.2f}\n"
		summary += f"Total: ${total:.2f}"

		# If the order is empty, set summary string to a message
		if is_order_empty:
			summary = "No items selected\n"

		# If the summary label exists, update its text to reflect the current state
		if self.summary_label != None:
			self.summary_label.configure(text=summary)

	# Updates the past order summary section of the GUI
	def update_past_order_summary(self):
		# Declare variables
		summary: str = ""
		is_past_orders_valid: bool = False

		# Iterate through all past orders to build summary string
		for i, order in enumerate(self.past_orders):
			# If this order isn't empty, then at least one order is valid
			if not self.is_order_empty(order):
				is_past_orders_valid = True

			# Add spacing between orders, but not the first one
			if (i > 0):
				summary += "\n\n"

			# Append order number to summary string as heading
			summary += f"Order {i + 1}:\n"

			# Calculate the subtotal & build the summary string for this order
			order_subtotal = 0.0

			# Iterate through all items to calc subtotal and build summary string
			for item, quantity in order.items.items():
				# Only have the item appear in sub-summary if there is more than 0 of them
				if quantity > 0:
					line_total = item.price * quantity
					order_subtotal += line_total
					summary += f"  {item.name} x {quantity} - ${line_total:.2f}\n"

			# Calculate the GST amount and total
			gst_amount = order_subtotal * (GST - 1)
			order_total = order_subtotal * GST

			# Build the summary string for this order
			summary += f"\n  Subtotal: ${order_subtotal:.2f}\n"
			summary += f"  GST: ${gst_amount:.2f}\n"
			summary += f"  Total: ${order_total:.2f}"

		# If there are no past orders, set summary string to a message
		if not is_past_orders_valid:
			summary = "No past orders\n"

		# If the summary label exists, update its text to reflect the current state
		if self.past_order_label != None:
			self.past_order_label.configure(text=summary)

	# Helper function to layout a menu item in the GUI
	def layout_menu_item(self, parent: ctk.CTkFrame, menu_item: MenuItem):
		# Make the the cell frame reacctive to parent size instead of child desired size
		parent.grid_rowconfigure(1, weight=1)
		parent.grid_columnconfigure(0, weight=1)

		# Create an image object using pillow
		image = Image.open(menu_item.image_path)

		# Turn it into a CTkImage and display in a label
		ctk_image = ctk.CTkImage(light_image=image, dark_image=image, size=(200, 120))
		ctk.CTkLabel(parent, text='', image=ctk_image).grid(row=0, column=0, padx=10, pady=10)

		# Display the item and its price in a label
		ctk.CTkLabel(parent, text=f"{menu_item.name}\n${menu_item.price:.2f}", font=ctk.CTkFont(size=18, weight="bold"), justify="center").grid(row=1, column=0, padx=10, pady=10)

		# Create a frame for the controls (+,quanitity,-))
		controls = ctk.CTkFrame(parent, fg_color="transparent")
		controls.grid(row=2, column=0, pady=(0, 10))

		# Decrement button
		decrement_button = ctk.CTkButton(controls, text="-", width=35, command=lambda: self.modify_order(menu_item, -1))
		decrement_button.grid(row=0, column=0, padx=5)

		# Quantity label
		quantity_label = ctk.CTkLabel(controls, text="0", width=30)
		quantity_label.grid(row=0, column=1)

		# Increment button
		increment_button = ctk.CTkButton(controls, text="+", width=35, command=lambda: self.modify_order(menu_item, 1))
		increment_button.grid(row=0, column=2, padx=5)

		ctk.CTkLabel(parent, text=f"Maximum Quantity: {MAX_QUANTITY}").grid(row=3, column=0)

		# Store references
		self.quantity_labels[menu_item] = quantity_label
		self.decrement_buttons[menu_item] = decrement_button
		self.increment_buttons[menu_item] = increment_button
		
		# Store a reference to the label to modify on updates
		self.quantity_labels[menu_item] = quantity_label

	# Helper function to layout the buttons in the GUI
	def layout_buttons(self, parent: ctk.CTkFrame):
		self.place_order_button = ctk.CTkButton(parent, text="Place Order", command=self.place_order)
		self.place_order_button.grid(row=0, column=0, padx=5, pady=5)

		ctk.CTkButton(parent, text="Clear Current Order", command=self.clear_current_order).grid(row=1, column=0, padx=5, pady=5)
		ctk.CTkButton(parent, text="Clear Past Orders", command=self.clear_past_orders).grid(row=2, column=0, padx=5, pady=5)
		ctk.CTkButton(parent, text="Exit", command=app.destroy).grid(row=3, column=0, padx=5, pady=5)

	# Helper function to layout the order summary section of the GUI
	def layout_order_summary(self, parent: ctk.CTkScrollableFrame):
		# Email heading
		ctk.CTkLabel(parent, text="Email", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(10, 5))

		# Email entry
		self.email_entry = ctk.CTkEntry(parent, placeholder_text="Enter your email")
		self.email_entry.pack(padx=10, pady=5, fill="x")

		# Validation error label
		self.email_error_label = ctk.CTkLabel(parent, text="", text_color="red")
		self.email_error_label.pack()

		# "Current Order" Label
		ctk.CTkLabel(parent, text="Current Order", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=5)

		# Dynamic current order summary label
		self.summary_label = ctk.CTkLabel(parent, text="No items selected\n", justify="left", anchor="w", font=ctk.CTkFont(size=16))
		self.summary_label.pack(padx=10, pady=10, fill="both", expand=True)

	# Helper function to layout the past orders section of the GUI
	def layout_past_orders(self, parent: ctk.CTkScrollableFrame):
		# "Past Orders" label
		ctk.CTkLabel(parent, text="Past Orders", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)

		# Dynamic past order summary label
		self.past_order_label = ctk.CTkLabel(parent, text="No past orders\n", justify="left", anchor="w", font=ctk.CTkFont(size=16))
		self.past_order_label.pack(padx=10, pady=10, fill="both", expand=True)

	# Layout the entire GUI
	def layout(self, app: ctk.CTk):
		# Restaurant name label
		ctk.CTkLabel(app, text=self.name, font=ctk.CTkFont(size=28, weight="bold")).pack(pady=20)

		# Calculate the number of rows needed for the menu items
		len_items = len(ITEMS)
		n_rows = (len_items + N_COLUMNS - 1) // N_COLUMNS

		# Top frame that is scrollable for menu items
		top_frame_scroll = ctk.CTkScrollableFrame(app, height=500)
		top_frame_scroll.pack(padx=20, pady=20, fill="both", expand=True)

		# Make all cells the same size
		for c in range(N_COLUMNS):
			top_frame_scroll.grid_columnconfigure(c, weight=1)

		for r in range(n_rows):
			top_frame_scroll.grid_rowconfigure(r, weight=1)

		# Track the index of the menu item to be placed in the grid
		items_index = 0

		# Iterate through all cells to place menu items
		for r in range(n_rows):
			for c in range(N_COLUMNS):
				if items_index >= len(ITEMS):
					break
				
				# Create a cell frame for each menu item
				cell_frame = ctk.CTkFrame(top_frame_scroll)
				cell_frame.grid(row=r, column=c, padx=10, pady=10, sticky="nsew")
				
				# Layout the menu item into the cell frame
				self.layout_menu_item(cell_frame, ITEMS[items_index])

				# Increment the menu item index
				items_index += 1

		# Create the bottom frame for the order summary, past orders, and buttons sections
		bottom_frame = ctk.CTkFrame(app)
		bottom_frame.pack(padx=20, pady=10, fill="both", expand=True)
		bottom_frame.grid_columnconfigure(0, weight=1) # Order summary FILL
		bottom_frame.grid_columnconfigure(1, weight=1) # Past orders FILL
		bottom_frame.grid_columnconfigure(2, weight=0) # Buttons FIT

		# Layout the order summary, past orders, and buttons sections in the bottom frame
		order_summary_frame = ctk.CTkScrollableFrame(bottom_frame)
		order_summary_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
		self.layout_order_summary(order_summary_frame)

		past_orders_frame = ctk.CTkScrollableFrame(bottom_frame)
		past_orders_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
		self.layout_past_orders(past_orders_frame)

		button_grid_frame = ctk.CTkFrame(bottom_frame)
		button_grid_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
		self.layout_buttons(button_grid_frame)

# Entry point
if __name__ == "__main__":
	# Set up the customtkinter app and start the main loop
	app = ctk.CTk()
	app.geometry("1080x900") # Set the window size

	# Create a restaurant instance and set up the initial GUI layout
	restaurant = Restaurant("Oli's Restaurant")
	restaurant.layout(app)
	restaurant.update_order_summary() # Reflect state in GUI

	# Start CTk's GUI event loop
	app.mainloop()
