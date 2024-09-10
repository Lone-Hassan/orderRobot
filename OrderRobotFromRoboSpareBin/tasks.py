from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    
    browser.configure()
    open_robot_order_site()
    get_orders()
    order_robot_from_csv()
    archive_receipts()
    
def open_robot_order_site():
    """_summary_
        navigate to site and click on alert message
    """
    browser.goto("https://robotsparebinindustries.com/#/robot-order")
    browser.page().click(".alert-buttons >button[class='btn btn-dark']")
    
def get_orders():
    """_summary_
    Downloads orders.csv to current directory
    """
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)

def order_robot_from_csv():
    """_summary_
    Reads orders.csv returns as a table 
    fills the form for oreders in csv
    
    """
    library = Tables()
    orders = library.read_table_from_csv("orders.csv",columns=["Order number","Head","Body","Legs","Address"])
    for row in orders:
        fill_the_form(row)
        screenshot_robot(row["Order number"])
        store_receipt_as_pdf(row["Order number"])
        browser.page().click("#order-another")
        browser.page().click(".alert-buttons >button[class='btn btn-dark']")
        
def fill_the_form(Order_Row=None):
    """_summary_
    Interacts with page to fill the form
    Args:
        Order_Row (_type_, optional): _description_. Defaults to None.
    
    """
    order_number = Order_Row["Order number"]
    head = Order_Row["Head"]
    body = Order_Row["Body"]
    legs = Order_Row["Legs"]
    address = Order_Row["Address"]
    page = browser.page()
    page.select_option("#head",index=int(head))
    page.click(f"#id-body-{body}")
    page.fill("input[type='number']",legs)
    page.fill("#address",address)
    page.click("#order")
    while page.is_visible('.alert.alert-danger'):
        page.click('#order')

def screenshot_robot(orderNumber):
    """_summary_
    Take screen shot of Reciept generated
    Args:
        orderNumber (_type_): _description_
    """
    browser.page().screenshot(path=f"output/{orderNumber}.png")

def store_receipt_as_pdf(orderNumber):
    """_summary_
    Make PDF file of order reciept and attach screenshot of crossponding order
    Args:
        orderNumber (_type_): _description_
    """
    reciept_innerhtml = browser.page().locator("#receipt").inner_html()
    pdf = PDF()
    pdf.html_to_pdf(reciept_innerhtml,f"output/{orderNumber}.pdf")
    pdf.add_watermark_image_to_pdf(image_path=f"output/{orderNumber}.png",source_path=f"output/{orderNumber}.pdf",output_path=f"output/{orderNumber}.pdf")
    
def archive_receipts():
    """_summary_
    Generate orders.zip folder of *.pdf in output directory
    """
    lib =  Archive()
    lib.archive_folder_with_zip(folder="output",archive_name="output/orders.zip",include="*.pdf")