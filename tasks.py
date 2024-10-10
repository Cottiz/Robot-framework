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
    open_robot_order_website()
    get_orders()
    archive_receipts()

def open_robot_order_website():
    #Open the webBrowser
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def download_orders_csv(url):
    http = HTTP()
    response = http.download(url, "orders.csv", overwrite=True)
    if response.status_code == 200:
        print(f"File downloaded successfully and saved to orders.csv")
    else:
        print(f"Failed to download file. Status code: {response.status_code}")

def read_csv_to_tables():
    library = Tables()
    orders = library.read_table_from_csv("orders.csv", columns=["Order number", "Head", "Body", "Legs", "Address"])

    numbers = library.group_table_by_column(orders, "Order number")
    for number in numbers:
        for order in number:
            close_annoying_modal()
            fill_the_form(order)
            order_robot(order)

def close_annoying_modal():
    page = browser.page()
    page.click("text=OK")

def order_robot(order):
    page = browser.page()
    while True:
        page.click("id=order")
        next_order = page.query_selector("id=order-another")
        if next_order:
            pdf_path = store_receipt_as_pdf(order["Order number"])
            ss_path = screenshot_robot(order["Order number"])
            embed_screenshot_to_pdf(pdf_path, ss_path)
            page.click("id=order-another")
            break
        else:
            print("Trying to order again")

def fill_the_form(order):
    page = browser.page()
    page.select_option("select[name='head']", order["Head"])
    page.click(f"input[name='body'][value='{order['Body']}']")
    page.fill("input[placeholder='Enter the part number for the legs']", order["Legs"])
    page.fill("input[name='address']", order["Address"])
    page.click("id=preview")

def store_receipt_as_pdf(order_number):
    page = browser.page()
    pdf = PDF()
    receipt_html = page.locator("#receipt").inner_html()
    system_path_to_pdf = "output/" + order_number + ".pdf"
    pdf.html_to_pdf(receipt_html, system_path_to_pdf)
    return system_path_to_pdf

def screenshot_robot(order_number):
    page = browser.page()
    element = page.locator("#robot-preview-image")
    system_path_to_screenshot = "output/" + order_number + ".png"
    element.screenshot(path=system_path_to_screenshot)
    return system_path_to_screenshot

def embed_screenshot_to_pdf(pdf_path, screenshot_path):
    pdf = PDF()
    pdf.add_files_to_pdf(files=[pdf_path, screenshot_path], target_document=pdf_path)

def archive_receipts():
    lib = Archive()
    lib.archive_folder_with_zip("output", "receipts.zip", include="*.pdf")

def get_orders():
    """Return the results"""
    orders_url = "https://robotsparebinindustries.com/orders.csv"
    download_orders_csv(orders_url)
    orders = read_csv_to_tables()

    return orders

