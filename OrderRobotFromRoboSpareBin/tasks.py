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
    browser.goto("https://robotsparebinindustries.com/#/robot-order")
    browser.page().click(".alert-buttons >button[class='btn btn-dark']")
    
def get_orders():
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)

def order_robot_from_csv():
    library = Tables()
    orders = library.read_table_from_csv("orders.csv",columns=["Order number","Head","Body","Legs","Address"])
    for row in orders:
        fill_the_form(row)
        screenshot_robot(row["Order number"])
        store_receipt_as_pdf(row["Order number"])
        browser.page().click("#order-another")
        browser.page().click(".alert-buttons >button[class='btn btn-dark']")
        
def fill_the_form(Order_Row=None):
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
    browser.page().screenshot(path=f"output/{orderNumber}.png")

def store_receipt_as_pdf(orderNumber):
    reciept_innerhtml = browser.page().locator("#receipt").inner_html()
    pdf = PDF()
    pdf.html_to_pdf(reciept_innerhtml,f"output/{orderNumber}.pdf")
    pdf.add_watermark_image_to_pdf(image_path=f"output/{orderNumber}.png",source_path=f"output/{orderNumber}.pdf",output_path=f"output/{orderNumber}.pdf")
    
def archive_receipts():
    lib =  Archive()
    lib.archive_folder_with_zip(folder="output",archive_name="output/orders.zip",include="*.pdf")