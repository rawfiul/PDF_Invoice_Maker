from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import sqlite3
import tkinter as tk
from tkinter import ttk
import sys
from weasyprint import HTML


# If .db file is missing, close the program, if not create a global db object
try:
    con = sqlite3.connect("company.db",)
    db = con.cursor()
    db.row_factory = sqlite3.Row
except FileNotFoundError:
    sys.exit(1)
    

# Global variables so that they can be accessed anywhere
supplier_logo_path = ""
invoice_no = 0
invoice_date = ""
supplier_name = ""
supplier_address1 = ""
supplier_address2 = ""
supplier_contact = ""
supplier_gst = ""
buyer_name = ""
buyer_address1 = ""
buyer_address2 = ""
buyer_contact = ""
buyer_gst = ""
items = []
currency = ""
total = 0
update_invoice_no = False
again = True


# This is done to conditionally loop the whole process if user wants
def main():
    global again
    while again:
        again = False
        invoicer()


# This is more like main
def invoicer():
    global supplier_logo_path
    global invoice_no
    global invoice_date
    global supplier_name
    global supplier_address1
    global supplier_address2
    global supplier_contact
    global supplier_gst
    global buyer_name
    global buyer_address1
    global buyer_address2
    global buyer_contact
    global buyer_gst
    global items
    global currency
    global total
    global again

    # Checks if the program is launched for the 1st time
    first_time = True
    db.execute("SELECT id FROM suppliers;")
    if len(db.fetchall()):
        first_time = False


    # Launch the supplier window if its first time since user will need supplier details to move forward
    if first_time:
        suppliers_window()
    else:
        buyer_window()

    # After all user inputs are over, fetch all relating data from db
    if total:
        db.execute("SELECT * FROM suppliers WHERE name = ?;", (supplier_name,))
        supplier_line = db.fetchone()
        supplier_logo_path = supplier_line["logo_path"]
        supplier_address1 = supplier_line["address1"]
        supplier_address2 = supplier_line["address2"]
        supplier_contact = supplier_line["contact"]
        supplier_gst = supplier_line["gst"]
        currency = supplier_line["currency"]

    # Arranging all userinput to feed to html using jinja
    data = {
        "supplier_logo_path": supplier_logo_path,
        "invoice_no": invoice_no,
        "invoice_date": invoice_date,
        "supplier_name": supplier_name,
        "supplier_address1": supplier_address1,
        "supplier_address2": supplier_address2,
        "supplier_contact": supplier_contact,
        "supplier_gst": supplier_gst,
        "buyer_name": buyer_name,
        "buyer_address1": buyer_address1,
        "buyer_address2": buyer_address2,
        "buyer_contact": buyer_contact,
        "buyer_gst": buyer_gst,
        "items": items,
        "currency": currency,
        "total": total,
    }

    # Update template HTML based on userinput data
    rendered_html = render_html(data)

    # Convert the html 2 pdf and clear all data from memory to process next invoice request(if any)
    if total:
        convert_html2pdf(
            rendered_html, f"PDFs/{supplier_name}_invoice_{invoice_no}.pdf"
        )
        supplier_logo_path = ""
        invoice_no = 0
        invoice_date = ""
        supplier_name = ""
        supplier_address1 = ""
        supplier_address2 = ""
        supplier_contact = ""
        supplier_gst = ""
        buyer_name = ""
        buyer_address1 = ""
        buyer_address2 = ""
        buyer_contact = ""
        buyer_gst = ""
        items = []
        currency = ""
        total = 0


# This function launches the GUI window asking for supplier details
def suppliers_window():
    # Create the supplier window
    s_window = tk.Tk()
    s_window.title("Your Company Details")

    # Create and set the title label
    title_label = ttk.Label(
        s_window, text="Your Company Details", font=("Helvetica", 16)
    )
    title_label.grid(row=0, column=0, columnspan=2, pady=10)

    # Create and set the labels and entry widgets for each field
    fields = [
        "Company logo File Name:",
        "Company Name (unique):",
        "Company Address Line 1:",
        "Company Address Line 2:",
        "Company Contact:",
        "Company Registration/GST:",
        "Currency for Invoice:",
    ]

    # Assigning each field a position in the grid of GUI
    for i, field in enumerate(fields):
        label = ttk.Label(s_window, text=field)
        label.grid(row=i + 1, column=0, sticky=tk.E, pady=5, padx=10)

    # Entry widgets
    logo_entry = ttk.Entry(s_window, width=30)
    name_entry = ttk.Entry(s_window, width=30)
    address1_entry = ttk.Entry(s_window, width=30)
    address2_entry = ttk.Entry(s_window, width=30)
    contact_entry = ttk.Entry(s_window, width=30)
    gst_entry = ttk.Entry(s_window, width=30)
    currency_entry = ttk.Entry(s_window, width=30)

    entries = [
        logo_entry,
        name_entry,
        address1_entry,
        address2_entry,
        contact_entry,
        gst_entry,
        currency_entry,
    ]

    # Place entry widgets on the window
    for i, entry in enumerate(entries):
        entry.grid(row=i + 1, column=1, pady=5, padx=10)
        entry.bind("<Return>", on_enter)

    def save_details():
        # Retrieve data from the entry widgets and save it in db, or throw appropriate errors
        if name_entry.get():
            db.execute("SELECT name FROM suppliers")
            sList = db.fetchall()
            sList = [s["name"] for s in sList]
            if name_entry.get() not in sList:
                db.execute(
                    "INSERT INTO suppliers (logo_path, name, address1, address2, contact, gst, currency) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (logo_entry.get(), name_entry.get(), address1_entry.get(), address2_entry.get(), contact_entry.get(), gst_entry.get(), currency_entry.get())
                )
                con.commit()
            else:
                error_label.configure(text="Company Name already exists")
                return

        else:
            error_label.configure(text="Please enter your Company Name")
            return

        # Close this window and open buyers window where buyers details are prompted
        s_window.destroy()
        buyer_window()

    # Create a button to save the details
    save_button = ttk.Button(s_window, text="Save Details", command=save_details)
    save_button.grid(row=8, column=0, columnspan=2, pady=10)

    # Error label to display a message if any
    error_label = ttk.Label(s_window, text="", foreground="red")
    error_label.grid(row=9, column=0, columnspan=2, pady=5, padx=10)

    # Run the application
    s_window.mainloop()


# This function launches the GUI window asking for client details
def buyer_window():
    buyer_list = []
    new_buyer = True

    # Create the client window
    b_window = tk.Tk()
    b_window.title("Client details")

    # Create and set the title label
    title_label = ttk.Label(b_window, text="Client Details", font=("Helvetica", 16))
    title_label.grid(row=0, column=0, columnspan=4, pady=10)

    # Row 1 - Supplier Name
    label_company = ttk.Label(b_window, text="Your company:")
    label_company.grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
    # Creating and Populating a dropbox with data from db
    db.execute("SELECT name FROM suppliers;")
    supplier_names = db.fetchall()
    company_options = [name["name"] for name in supplier_names]
    company_dropdown = ttk.Combobox(b_window, values=company_options)
    company_dropdown.set(company_options[0])
    company_dropdown.grid(row=1, column=1, padx=10, pady=5)

    # Whhen clicked it stores selection in memory and fetches additional data from db based on selection
    def nameconfirm_button():
        global supplier_name
        nonlocal buyer_list
        supplier_name = company_dropdown.get()
        db.execute("SELECT name FROM suppliers")
        exisitng_supplier_list = db.fetchall()
        exisitng_supplier_list = [s["name"] for s in exisitng_supplier_list]
        if supplier_name not in exisitng_supplier_list:
            error_label.configure(
                text="Please select a company from dropdown list or add new"
            )
            return
        company_dropdown.configure(state="disabled")
        add_another_button.configure(state="disabled")
        name_confirm_button.configure(state="disabled")
        # row2
        entry_invoice_number.configure(state="normal")
        auto_checkbox_invoice.configure(state="normal")
        auto_checkbox_invoice.state(["!alternate"])
        # row3
        entry_date.configure(state="normal")
        auto_checkbox_date.configure(state="normal")
        auto_checkbox_date.state(["!alternate"])
        # row4
        buyer_dropdown.configure(state="normal")
        db.execute("SELECT name FROM buyers WHERE supplier_name = ?;", (supplier_name,))
        buyers_list = db.fetchall()
        buyer_list = [name["name"] for name in buyers_list]
        if buyer_list:
            buyer_dropdown["values"] = buyer_list
            buyer_dropdown.set(buyer_list[0])
            buyer_confirm_button.configure(state="normal")
        add_new_button.configure(state="normal")

    # Button to confirm the suppliers name which enables future functions and blocks the past ones
    name_confirm_button = ttk.Button(
        b_window, text="Confirm", command=nameconfirm_button
    )
    name_confirm_button.grid(row=1, column=2, padx=10, pady=5)

    def addanother_button():
        b_window.destroy()
        suppliers_window()

    # A button to add a new supplier if not found in the populated list
    add_another_button = ttk.Button(
        b_window, text="Add another", command=addanother_button
    )
    add_another_button.grid(row=1, column=3, padx=10, pady=5)

    # Row 2 - Invoice number
    label_invoice_number = ttk.Label(b_window, text="Invoice Number:")
    label_invoice_number.grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)

    entry_invoice_number = ttk.Entry(b_window, state="disabled")
    entry_invoice_number.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)

    # If auto invoice enabled then fetch data from db
    def auto_invoice_no():
        global supplier_name
        if auto_checkbox_invoice.instate(["selected"]):
            db.execute("SELECT last_invoice_no FROM suppliers WHERE name = ?;",(supplier_name,))
            display_no = db.fetchone()["last_invoice_no"] + 1
            
            entry_invoice_number.delete(0, tk.END)
            entry_invoice_number.insert(0, display_no)
            entry_invoice_number.configure(state="disabled")
        else:
            entry_invoice_number.configure(state="normal")
            entry_invoice_number.delete(0, tk.END)

    auto_checkbox_invoice = ttk.Checkbutton(
        b_window, text="Auto", state="disabled", command=auto_invoice_no
    )
    auto_checkbox_invoice.grid(row=2, column=2, padx=10, pady=5)

    # Row 3 - Invoice Date
    label_date = ttk.Label(b_window, text="Date:")
    label_date.grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)

    entry_date = ttk.Entry(b_window, state="disabled")
    entry_date.grid(row=3, column=1, padx=10, pady=5, sticky=tk.W)

    # If auto date enabled then use datetime module to fetch current date
    def auto_date():
        if auto_checkbox_date.instate(["selected"]):
            display_date = datetime.now().strftime("%d %b %Y")
            entry_date.delete(0, tk.END)
            entry_date.insert(0, display_date)
            entry_date.configure(state="disabled")
        else:
            entry_date.configure(state="normal")
            entry_date.delete(0, tk.END)

    auto_checkbox_date = ttk.Checkbutton(
        b_window, text="Auto", state="disabled", command=auto_date
    )
    auto_checkbox_date.grid(row=3, column=2, padx=10, pady=5)

    # Row 4 - List of Exisitng clients specific to the supplier
    label_client = ttk.Label(b_window, text="Existing Clients:")
    label_client.grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)

    buyer_dropdown = ttk.Combobox(b_window, state="disabled")
    buyer_dropdown.grid(row=4, column=1, padx=10, pady=5)

    # Confirm button takes selection into memory, fetches data from db based on selection
    def buyerconfirm_button():
        global buyer_name
        nonlocal new_buyer
        nonlocal buyer_list
        buyer_name = buyer_dropdown.get()
        if buyer_name not in buyer_list:
            error_label.configure(
                text="Please select a client from dropdown list or add new"
            )
            return
        buyer_dropdown.configure(state="disabled")
        add_new_button.configure(state="disabled")
        entry_list = [
            entry_buyer_name,
            entry_buyer_add1,
            entry_buyer_add2,
            entry_buyer_contact,
            entry_buyer_gst,
        ]
        for each in entry_list:
            each.configure(state="normal")
            each.delete(0, tk.END)
        entry_buyer_name.insert(0, buyer_name)
        db.execute("SELECT address1 FROM buyers WHERE name = ?;", (buyer_name,))
        db_result = db.fetchone()["address1"]
        entry_buyer_add1.insert(0, db_result)
        db.execute("SELECT address2 FROM buyers WHERE name = ?;", (buyer_name,))
        db_result = db.fetchone()["address2"]
        entry_buyer_add2.insert(0, db_result)
        db.execute("SELECT contact FROM buyers WHERE name = ?;", (buyer_name,))
        db_result = db.fetchone()["contact"]
        entry_buyer_contact.insert(0, db_result)
        db.execute("SELECT gst FROM buyers WHERE name = ?;", (buyer_name,))
        db_result = db.fetchone()["gst"]
        entry_buyer_gst.insert(0, db_result)
        for each in entry_list:
            each.configure(state="disabled")
        buyer_confirm_button.configure(state="disabled")
        new_buyer = False
        final_submit_button.configure(state="normal")
        return

    buyer_confirm_button = ttk.Button(
        b_window, text="Confirm", command=buyerconfirm_button, state="disabled"
    )
    buyer_confirm_button.grid(row=4, column=2, padx=10, pady=5)

    # Blocks the dropdown and enables fields to enter new client details
    def addnew_button():
        buyer_dropdown.configure(state="disabled")
        buyer_confirm_button.configure(state="disabled")
        entry_list = [
            entry_buyer_name,
            entry_buyer_add1,
            entry_buyer_add2,
            entry_buyer_contact,
            entry_buyer_gst,
        ]
        for each in entry_list:
            each.configure(state="normal")
        add_new_button.configure(state="disabled")
        final_submit_button.configure(state="normal")
        return

    add_new_button = ttk.Button(
        b_window, text="Add New", command=addnew_button, state="disabled"
    )
    add_new_button.grid(row=4, column=3, padx=10, pady=5)

    # Row 5
    label_buyer_name = ttk.Label(b_window, text="Client Name:")
    label_buyer_name.grid(row=5, column=0, padx=10, pady=5, sticky=tk.W)

    entry_buyer_name = ttk.Entry(b_window, state="disabled")
    entry_buyer_name.grid(row=5, column=1, padx=10, pady=5, sticky=tk.W)
    entry_buyer_name.bind("<Return>", on_enter)

    # Row 6
    label_buyer_add1 = ttk.Label(b_window, text="Address Line 1:")
    label_buyer_add1.grid(row=6, column=0, padx=10, pady=5, sticky=tk.W)

    entry_buyer_add1 = ttk.Entry(b_window, state="disabled")
    entry_buyer_add1.grid(row=6, column=1, padx=10, pady=5, sticky=tk.W)
    entry_buyer_add1.bind("<Return>", on_enter)

    # Row 7
    label_buyer_add2 = ttk.Label(b_window, text="Address Line 2:")
    label_buyer_add2.grid(row=7, column=0, padx=10, pady=5, sticky=tk.W)

    entry_buyer_add2 = ttk.Entry(b_window, state="disabled")
    entry_buyer_add2.grid(row=7, column=1, padx=10, pady=5, sticky=tk.W)
    entry_buyer_add2.bind("<Return>", on_enter)

    # Row 8
    label_buyer_contact = ttk.Label(b_window, text="Client Contact:")
    label_buyer_contact.grid(row=8, column=0, padx=10, pady=5, sticky=tk.W)

    entry_buyer_contact = ttk.Entry(b_window, state="disabled")
    entry_buyer_contact.grid(row=8, column=1, padx=10, pady=5, sticky=tk.W)
    entry_buyer_contact.bind("<Return>", on_enter)

    # Row 9
    label_buyer_gst = ttk.Label(b_window, text="Client Registration/GST:")
    label_buyer_gst.grid(row=9, column=0, padx=10, pady=5, sticky=tk.W)

    entry_buyer_gst = ttk.Entry(b_window, state="disabled")
    entry_buyer_gst.grid(row=9, column=1, padx=10, pady=5, sticky=tk.W)
    entry_buyer_gst.bind("<Return>", on_enter)

    label_buyer_gstopt = ttk.Label(b_window, text="(Optional)")
    label_buyer_gstopt.grid(row=9, column=2, padx=10, pady=5, sticky=tk.W)

    # Stores all details from buyers window into memory
    def buyer_submit():
        global supplier_name
        global invoice_no
        global invoice_date
        global buyer_name
        global buyer_address1
        global buyer_address2
        global buyer_contact
        global buyer_gst
        global update_invoice_no
        # if invoice number was auto, update the db with the new invoice number
        invoice_no = entry_invoice_number.get()
        if auto_checkbox_invoice.instate(["selected"]):
            update_invoice_no = True
        if not invoice_no:
            error_label.configure(text="Invoice number missing")
            return
        # Checks for blank date field
        invoice_date = entry_date.get()
        if not invoice_date:
            error_label.configure(text="Invoice date missing")
            return

        buyer_name = entry_buyer_name.get()
        buyer_address1 = entry_buyer_add1.get()
        buyer_address2 = entry_buyer_add2.get()
        buyer_contact = entry_buyer_contact.get()
        buyer_gst = entry_buyer_gst.get()
        # If client was new, add it to db
        if new_buyer:
            if not buyer_name:
                error_label.configure(text="Client name missing")
                return
            db.execute("SELECT name FROM buyers")
            existing_buyers = db.fetchall()
            existing_buyers = [b["name"] for b in existing_buyers]
            if buyer_name not in existing_buyers:
                db.execute(
                    "INSERT INTO buyers(name, supplier_name, address1, address2, contact, gst) VALUES(?,?,?,?,?,?);",
                    (buyer_name,
                    supplier_name,
                    buyer_address1,
                    buyer_address2,
                    buyer_contact,
                    buyer_gst)
                )
                con.commit()
            else:
                error_label.configure(text="Client name already exists")
                return
        # Closes this window and opens items window
        b_window.destroy()
        items_window()

    # Submit Button
    final_submit_button = ttk.Button(
        b_window, text="Submit", command=buyer_submit, state="disabled"
    )
    final_submit_button.grid(row=10, column=0, columnspan=4, padx=10, pady=5)

    # Error label to display a message if any
    error_label = ttk.Label(b_window, text="", foreground="red")
    error_label.grid(row=11, column=0, columnspan=4, pady=5, padx=10)

    # Run this window
    b_window.mainloop()


# The items window
def items_window():
    # When enter/return key is pressed on keyboard, go highlight next field
    

    # This adds another row for userinput of item, quantity and price
    def add_row():
        nonlocal row_index
        nonlocal entry_items
        nonlocal entry_quantities
        nonlocal entry_prices

        row_index += 1
        # Create new entry fields
        entry_item = ttk.Entry(root)
        entry_quantity = ttk.Entry(root)
        entry_price = ttk.Entry(root)
        # Add newly created entry fields to the lists to easy data retrieval in future
        entry_items.append(entry_item)
        entry_quantities.append(entry_quantity)
        entry_prices.append(entry_price)
        # Creates new button to add more rows
        btn_add_more = ttk.Button(root, text="Add More", command=add_row)
        # When enter/return key is pressed, execute on_enter function
        entry_item.bind("<Return>", on_enter)
        entry_quantity.bind("<Return>", on_enter)
        # Place the components in the grid
        entry_item.grid(row=row_index, column=0, padx=5, pady=5)
        entry_quantity.grid(row=row_index, column=1, padx=5, pady=5)
        entry_price.grid(row=row_index, column=2, padx=5, pady=5)
        btn_add_more.grid(row=row_index, column=3, padx=5, pady=5)

    def save_data():
        global update_invoice_no
        global supplier_name
        global invoice_no
        nonlocal entry_items
        nonlocal entry_quantities
        nonlocal entry_prices
        nonlocal row_index
        global items
        global total


        # For each field row, get user input and store it in memory
        for i in range(row_index - 4):
            item_name = entry_items[i].get()
            quantity = entry_quantities[i].get()
            price = entry_prices[i].get()
            # Validating input and converting to float
            if quantity:
                try:
                    quantity1 = round(float(quantity), 2)
                except ValueError:
                    error_label.configure(text="Enter numeric quantity only")
                    return
            else:
                quantity1 = 1
            # Validating input and converting to float
            if price:
                try:
                    price1 = round(float(price), 2)
                    price1 = round(price1 * quantity1, 2)
                except ValueError:
                    error_label.configure(text="Enter numeric price only")
                    return
            else:
                price1 = 0
            # Updating total's value
            total = round(total + price1, 2)
            # Formatting price to look like a currency value
            price1 = "{:,.2f}".format(price1)
            # Adding all data to list
            if item_name and quantity and price:
                items.append(
                    {"name": item_name, "quantity": quantity1, "price": price1}
                )
            else:
                error_label.configure(text="Please fill all details")
                return

        # Formatting total to look like a currency value
        total = "{:,.2f}".format(total)

        # Update the invoice no in db
        if update_invoice_no:
            db.execute(
                "UPDATE suppliers SET last_invoice_no = ? WHERE name = ?",
                (invoice_no,
                supplier_name)
            )
            con.commit()
        # Disable the save button so that user cant press it twice before the window is closed
        btn_save.configure(state="disabled")
        # Close the window
        root.destroy()

    # Create the main window
    root = tk.Tk()
    root.title("ITEM DETAILS")

    # Create entry fields for item name, quantity, and price
    ttk.Label(root, text="Item Name").grid(row=4, column=0, padx=5, pady=5)
    ttk.Label(root, text="Quantity (Value only)").grid(row=4, column=1, padx=5, pady=5)
    ttk.Label(root, text="Price (each)").grid(row=4, column=2, padx=5, pady=5)

    # Initialize row index
    row_index = 4

    # Lists to store entry fields
    entry_items = []
    entry_quantities = []
    entry_prices = []

    # Add the first row of entry fields and button
    add_row()

    # Create and set the title label
    title_label = ttk.Label(root, text="Item Details", font=("Helvetica", 16))
    title_label.grid(row=0, column=0, columnspan=4, pady=10)

    # Add a "Save" button to collect and store data
    btn_save = ttk.Button(root, text="CREATE INVOICE PDF", command=save_data)
    btn_save.grid(row=1, column=0, columnspan=4, pady=10)

    def make_more():
        global again
        if btn_more.instate(["selected"]):
            again = True
        else:
            again = False

    # A button to rerun the program after creating current PDF
    btn_more = ttk.Checkbutton(
        root,
        text="After creating this PDF, run this program again for more invoices",
        command=make_more,
    )
    btn_more.grid(row=2, column=0, columnspan=4, pady=10)
    btn_more.state(["!alternate"])

    # Error placeholder
    error_label = ttk.Label(root, text="", foreground="red")
    error_label.grid(row=3, column=0, columnspan=4, pady=5, padx=10)

    # Start the window
    root.mainloop()


def on_enter(event):
        event.widget.tk_focusNext().focus()
        return "break"


def render_html(data):
    # Creating Jinja environment in templates directory
    env = Environment(loader=FileSystemLoader("templates"))
    # Loading the template html
    template = env.get_template("template.html")
    # Userinput data is rendered onto jinja html template
    return template.render(data)


def convert_html2pdf(htmlpath, pdfpath):
    # Instead of passing a .html file, we pass it as a string variable
    html = HTML(string=htmlpath, base_url="base_url")
    html.write_pdf(pdfpath)


if __name__ == "__main__":
    main()