# PDF_Invoice_Maker
A simple python app to create simple invoices in PDF format.


### Screenshots:
**Sample Invoice**

![Sample Invoice](/assets_for_readme/screenshot_sample_invoice.png)

**Company Details GUI**

![Company Details GUI](/assets_for_readme/screenshot_company_details.png)

**Client Details GUI**

![Client Details GUI](/assets_for_readme/screenshot_client_details.png)

**Item Details GUI**

![Item Details GUI](/assets_for_readme/screenshot_items_details.png)


### Video Demo:  
[![Watch the video demo](https://img.youtube.com/vi/PssY15xIRgY/0.jpg)](https://www.youtube.com/watch?v=PssY15xIRgY)


### Description:
Enter details of your company, details of your clients and then details of the items transacted; and the program will export the PDF in the `/PDFs` folder. The program remembers your company and client details and last invoice number so its faster to create subsequent invoices, without entering recurring details twice.

**Points to Note for users:**
- Your company logo needs to be in .png format and inside the `/logos` folder. Then in the `Company Logo File Name` field of `Company Details` window, simply use the file name. For example, enter `my_logo.png` inside that field if the file name of your image is `my_logo.png`, without any `/` or `.`
- The names of your company and your client's company must be unique. Meaning if you created a company or client named `ABC Inc`, you can not create another company or client with the same name.
- You can skip entering other details of your company and client's, but name is mandatory. I recommend entering all details because the program asks for bare minimum anyways.
- The clients specific to your company will be stored. They will be visible to you under client list next time so that you can use same client for multiple invoices. They will not be visible to other invoice making companies.
- Auto-Invoice Number starts from 1 and is unique to each invoice making company. The next invoice your company makes will have invoice number as +1 from the last invoice number you created.
- Under `Item Details` window, there is only one row to enter details of one set of item. Click on `Add more` button and it will create another row asking for more item details. Add as many rows of items as desired, the pdf will continue to next page if all items dont fit in one.
- Under the `Price` column, enter price of 1 quantity of the item. In the invoice however, it will be shown at total price of the item i.e. Quantity X Price of each item.
- Your generated pdf will be found inside the `/PDFs` folder. The name of your pdf will include the name of your company and invoice number for easy identification and orginazing.
- In case you want to start fresh, deleting all data of all companies, simply delete the `company.db` file in main folder, copy the `clean.db` from `/templates` folder and paste it in main folder. In main folder rename the `clean.db` to `company.db`


### Technical:
The userinput part is handled using Tkinter library of python. I have not focused on making the graphical user interface pretty; but rather on making it robust. Each button and userinput field is carefully designed to catch and display errors in userinput(if any). Parts of the GUI also gets disabled or enabled dynamically based on the progress of userinput. This prevents unexpected behaviour of the program and makes the data fetching and updating robust.

The program uses SQL for data management. There is only one db file and has two tables. One of the tables records details of the company making the invoice, the other table records details of the company that the invoice is for. This is only being done to make the invoicing process faster for the user in a way that they dont have to enter the possibly recurring details repeatedly.

The program detects if the program is launched for the first time, based on readings from the database. If its detected its a first launch, a window will pop open asking details of the company making the invoice; if not, it launches a window asking for details of the client. The program has a feature of auto-invoice-number and auto-date. The auto-invoice numbering works by recording the last invoice number of the company producing invoices and incrementing it by 1 the next time an invoice is made by that company. This can be opted out using a checkbox which enables manual/custom input. The auto date works similarly but no data is fetched or recorded in the database for dates. The program also fetches a list of all previous clients specific to the current company, so that user need not to enter same details again. After own details(including image logo), client details, invoice date and invoice number, a new window pops up asking for item details. Name, quantity and price is asked with a button to add a new/more items if desired. An option to select "Make more invoices after this" will make the program run again after creating a PDF so that user need not to launch the program repeatedly if they they have more than 1 invoice to create.

After all data is collected from user, some data is stored in database and all data is loaded into memory. Using jinja, i update a template made in HTML with the user input details. I then pass the updated HTML, which consists of all updated data, to a function of weasyprint which converts the HTML to PDF and stores it into disk. I chose to create invoice templates in HTML beacause its much more easier and efficent to cook up templates in HTML using CSS than creating a raw pdf inside python. This enables me to create as many templates as i wish in future with same fields to fill data with. The original html template for the invoice is taken from here : [Link to original html](https://github.com/sparksuite/simple-html-invoice-template/blob/master/invoice.html). The modified version, the one used to create the pdf can be found inside the `/templates` folder. Be sure to properly install the [weasyprint module](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation), it requires GTK3 to be installed manually. Although, you do not need python or GTK3 installed on windows when running the program using the packaged .7z zip uploaded along with the raw .py file !


### Possible updates: 
- I might update the program to make the User input GUI prettier !
- I might upload more HTML invoice templates to choose from !
- Add additional functions if requested !