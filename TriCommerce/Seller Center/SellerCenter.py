import pyodbc
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableWidgetItem, QFileDialog
from PyQt6.QtGui import QIntValidator
from PyQt6.uic import loadUi
from datetime import date

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        loadUi('Login.ui', self)  
        
        self.loginButton.clicked.connect(self.onLogin)
        self.newAccountButton.clicked.connect(self.onNewAccount)


    def showErrorMessage(self, s):
        error_message = QMessageBox(self)
        error_message.setIcon(QMessageBox.Icon.Critical) 
        error_message.setWindowTitle("Error")
        error_message.setText(s)
        error_message.setInformativeText("Please try again!")
        error_message.setStandardButtons(QMessageBox.StandardButton.Ok)
        error_message.exec()
    

    def onLogin(self):
        email = self.emailInput.text()
        password = self.passwordInput.text()
        
        query = "select SellerID, EmailID, Password from Sellers where EmailId = ? and Password = ?"
        connection = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=ZAIN_PC\MYSQL1;"
            "DATABASE=StoreDatabase;"
            "Trusted_Connection=yes;"
            "TrustServerCertificate=yes;"
        )
        cursor = connection.cursor()
        cursor.execute(query, (email, password))
        result = cursor.fetchone()
        if not result:
            self.showErrorMessage("Email or Password are incorrect.")
        else:
            self.sellerID = result[0]
            self.hide()
            self.dashboard = DashboardWindow(self.sellerID)
            self.dashboard.show()
        connection.close()
        
                
    def onNewAccount(self):
        self.hide()
        self.register = RegisterWindow()
        self.register.show()


class RegisterWindow(QMainWindow):
    def __init__(self):
        super().__init__()
    
        loadUi('Register.ui', self)  
        
        self.populateBanks()
        self.populateCities()
        self.registerButton.clicked.connect(self.onRegister)
        
        
    
    def populateBanks(self):
        connection = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=ZAIN_PC\MYSQL1;"
            "DATABASE=StoreDatabase;"
            "Trusted_Connection=yes;"
            "TrustServerCertificate=yes;"
        )
        cursor = connection.cursor()
        cursor.execute("select BankName from Banks")
        self.bankNameInput.clear() 
        for row in cursor.fetchall():
            self.bankNameInput.addItem(row[0])
        connection.close()
        
    
    def populateCities(self):
        connection = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=ZAIN_PC\MYSQL1;"
            "DATABASE=StoreDatabase;"
            "Trusted_Connection=yes;"
            "TrustServerCertificate=yes;"
        )

        cursor = connection.cursor()
        cursor.execute("select CityName from Cities")
        self.cityInput.clear() 
        for row in cursor.fetchall():
            self.cityInput.addItem(row[0])
        connection.close()
        
    
    def showErrorMessage(self, s):
        error_message = QMessageBox(self)
        error_message.setIcon(QMessageBox.Icon.Critical)  
        error_message.setWindowTitle("Error")
        error_message.setText(s)
        error_message.setInformativeText("Please try again!")
        error_message.setStandardButtons(QMessageBox.StandardButton.Ok)
        error_message.exec()
    
    def onRegister(self):
        storeName = self.storeNameInput.text()
        cnicNumber = self.cnicInput.text()
        bankName = self.bankNameInput.currentText()
        accountNumber = self.accountNumberInput.text()
        name = self.nameInput.text()
        contactNumber = self.contactNumberInput.text()
        emailAddress = self.emailInput.text()
        password = self.passwordInput.text()
        city = self.cityInput.currentText()
        address = self.addressInput.text() 
        
        if len(storeName) > 20 or len(storeName) < 3:
            self.showErrorMessage("Store Name should be in between 4 to 20 characters.")
        elif not cnicNumber.isdigit() or len(cnicNumber) != 13:
            self.showErrorMessage("CNIC should be of 13 digits and only contain numeric characters.")
        elif not contactNumber.isdigit() or len(contactNumber) != 11:
            self.showErrorMessage("Contact number should be of 11 digits and only contain numeric characters.")
        else:
            
            searchQuery = "SELECT StoreName, EmailID FROM Sellers WHERE StoreName = ? OR EmailID = ?"
            connection = pyodbc.connect(
                "DRIVER={ODBC Driver 17 for SQL Server};"
                "SERVER=ZAIN_PC\MYSQL1;"
                "DATABASE=StoreDatabase;"
                "Trusted_Connection=yes;"
                "TrustServerCertificate=yes;"
            )
            cursor = connection.cursor()
            # Assuming emailAddress corresponds to the email and storeName corresponds to the store
            cursor.execute(searchQuery, (storeName, emailAddress))
            result = cursor.fetchone()
            if result:
                self.showErrorMessage("Email or Store Name already exists!")
                connection.close()
            else:
                query = """INSERT INTO Sellers (StoreName, EmailID, CNIC, BankName, BankAccount, City, BusinessAddress, ContactNumber, Password, AccountStatus) 
                            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""         
                connection = pyodbc.connect(
                    "DRIVER={ODBC Driver 17 for SQL Server};"
                    "SERVER=ZAIN_PC\MYSQL1;"
                    "DATABASE=StoreDatabase;"
                    "Trusted_Connection=yes;"
                    "TrustServerCertificate=yes;"
                )
                cursor = connection.cursor()
                cursor.execute(query, (storeName, emailAddress, cnicNumber, bankName, accountNumber, city, address, contactNumber, password, "PendingApproval"))
                connection.commit()
                connection.close()
                self.hide()
                self.loginWindow = LoginWindow()
                self.loginWindow.show()
                           
    
class DashboardWindow(QMainWindow):
    def __init__(self, sellerID):
        super().__init__()
        self.sellerID = sellerID
        loadUi('SellerDashboard.ui', self)  
    
        self.manageOrdersButton.clicked.connect(self.onManageOrders)
        self.manageProductsButton.clicked.connect(self.onManageProducts)
        self.numOrdersControl()
        
    def numOrdersControl(self):
        
        query = """SELECT COUNT(o.OrderID) AS PendingOrders 
                        FROM Products p INNER JOIN OrderItems oi ON p.ProductSKU = oi.ProductSKU
                        INNER JOIN Orders o ON oi.OrderID = o.OrderID
                        INNER JOIN Status st ON o.StatusID = st.StatusID
                        WHERE p.SellerID = ? AND st.StatusTitle = 'Pending';"""
                        
        connection = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=ZAIN_PC\MYSQL1;"
            "DATABASE=StoreDatabase;"
            "Trusted_Connection=yes;"
            "TrustServerCertificate=yes;"
        )
        cursor = connection.cursor()
        cursor.execute(query, (self.sellerID))
        result = cursor.fetchone()
        self.numOrders.display(result[0])
        connection.close()
    
    def onManageOrders(self):
        self.hide()
        self.manageOrders = ManageOrdersWindow(self.sellerID)
        self.manageOrders.show()
    
    def onManageProducts(self):
        self.hide()
        self.manageProducts = ManageProductsWindow(self.sellerID)
        self.manageProducts.show()


class ManageProductsWindow(QMainWindow):
    def __init__(self, sellerID):
        super().__init__()
        self.sellerID = sellerID

        loadUi('Manage Products.ui', self)

        self.addProductButton.clicked.connect(self.onAddProduct)
        self.activeButton.clicked.connect(self.show_active_products)
        self.pendingButton.clicked.connect(self.show_pending_products)
        self.inactiveButton.clicked.connect(self.show_inactive_products)
        self.activateButton.clicked.connect(self.toggle_product_status)
        self.homeButton.clicked.connect(self.openDashboard)
        
        self.connection = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=ZAIN_PC\\MYSQL1;"
            "DATABASE=StoreDatabase;"
            "Trusted_Connection=yes;"
            "TrustServerCertificate=yes;"
        )
        self.cursor = self.connection.cursor()

        self.load_products("Active")  
    
    def openDashboard(self):
        self.hide()
        self.addProductsWindow = DashboardWindow(self.sellerID)
        self.addProductsWindow.show()
    
    def onAddProduct(self):
        self.hide()
        self.addProductsWindow = AddProductsWindow(self.sellerID)
        self.addProductsWindow.show()
        

    def load_products(self, status):
        # Clear the current table contents
        self.productsTable.setRowCount(0)
        
        query = f"SELECT ProductSKU, ProductName, StockQuantity, Price, Status FROM Products WHERE Status = ? and sellerID = ?"
        self.cursor.execute(query, (status, self.sellerID))
        rows = self.cursor.fetchall()

        # Populate the table with products from the query result
        for row in rows:
            row_position = self.productsTable.rowCount()
            self.productsTable.insertRow(row_position)
            for column, value in enumerate(row):
                self.productsTable.setItem(row_position, column, QTableWidgetItem(str(value)))

    def show_active_products(self):
        self.load_products("Active")

    def show_pending_products(self):
        self.load_products("Pending")

    def show_inactive_products(self):
        self.load_products("Inactive")

    def toggle_product_status(self):
        # Get selected rows
        selected_items = self.productsTable.selectedItems()
        if not selected_items:
            return  # No row is selected

        # Get the SKU of the selected product
        product_sku = selected_items[0].text()

        # Get the current status of the selected product
        self.cursor.execute("SELECT Status FROM Products WHERE ProductSKU = ?", (product_sku,))
        current_status = self.cursor.fetchone()[0]

        # Toggle the product status
        new_status = "Pending" if current_status == "Inactive" else "Inactive"

        # Update the product's status in the database
        self.cursor.execute("UPDATE Products SET Status = ? WHERE ProductSKU = ?", (new_status, product_sku))
        self.connection.commit()

        # Reload products (based on current active/inactive status)
        if current_status == "Inactive":
            self.load_products("Inactive")
        else:
            self.load_products("Active")

        # Update the button text
        self.activateButton.setText("Deactivate" if new_status == "Active" else "Activate")

    def closeEvent(self, event):
        # Close the database connection when the window is closed
        self.connection.close()
        event.accept()  


class ManageOrdersWindow(QMainWindow):
    def __init__(self, sellerID):
        super().__init__()
    
        loadUi('Manage Orders.ui', self)
        
        self.sellerID = sellerID

        self.pendingButton.clicked.connect(self.showPendingOrders)
        self.shippedButton.clicked.connect(self.showShippedOrders)
        self.deliveredButton.clicked.connect(self.showDeliveredOrders)
        self.homeButton.clicked.connect(self.openDashboard)

        self.showPendingOrders()
    
    def openDashboard(self):
        self.hide()
        self.addProductsWindow = DashboardWindow(self.sellerID)
        self.addProductsWindow.show()

    def fetchOrders(self, status):
        """
        Fetch orders for the given seller and status from the database.
        """
        query = """
        SELECT 
            o.OrderID, 
            oi.ProductSKU, 
            oi.Quantity, 
            (oi.Quantity * oi.UnitPrice) AS TotalAmount, 
            o.CustomerID, 
            CONCAT(c.FirstName, ' ', c.LastName) AS CustomerName, 
            o.OrderDate
        FROM Orders o
        INNER JOIN OrderItems oi ON o.OrderID = oi.OrderID
        INNER JOIN Products p ON oi.ProductSKU = p.ProductSKU
        INNER JOIN Customers c ON o.CustomerID = c.CustomerID
        INNER JOIN Status st ON o.StatusID = st.StatusID
        WHERE p.SellerID = ? AND st.StatusTitle = ?;
        """
        
        connection = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=ZAIN_PC\MYSQL1;"
            "DATABASE=StoreDatabase;"
            "Trusted_Connection=yes;"
            "TrustServerCertificate=yes;"
        )
        
        cursor = connection.cursor()
        cursor.execute(query, (self.sellerID, status))
        orders = cursor.fetchall()
        connection.close()
        return orders

    def populateTable(self, orders):
        """
        Populate the table widget with the given orders.
        """
        self.ordersTable.setRowCount(0)  
        self.ordersTable.setColumnCount(7) 

        for row_number, order in enumerate(orders):
            self.ordersTable.insertRow(row_number)
            for column_number, data in enumerate(order):
                self.ordersTable.setItem(row_number, column_number, QTableWidgetItem(str(data)))

    def showPendingOrders(self):
        """
        Show pending orders in the table.
        """
        orders = self.fetchOrders('Pending')
        self.populateTable(orders)

    def showShippedOrders(self):
        """
        Show shipped orders in the table.
        """
        orders = self.fetchOrders('Shipped')
        self.populateTable(orders)

    def showDeliveredOrders(self):
        """
        Show delivered orders in the table.
        """
        orders = self.fetchOrders('Delivered')
        self.populateTable(orders)


class AddProductsWindow(QMainWindow):
    def __init__(self, sellerID):
        super().__init__()
        self.sellerID = sellerID
        loadUi('Add Product.ui', self)
    
        self.titleInput.setMaxLength(255)
        
        int_validator = QIntValidator(0, 10**9, self)
        self.priceInput.setValidator(int_validator)
        self.stockInput.setValidator(int_validator)
        
        self.populate_categories()
        
        # Connect buttons to their respective functions
        self.imageButton.clicked.connect(self.add_image)
        self.submitButton.clicked.connect(self.submit_to_database)
        
        self.homeButton.clicked.connect(self.openDashboard)
        
        # Initialize image path variable
        self.image_path = None
    
    def add_image(self):
        # Open a file dialog to select an image
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            self.image_path = file_path
            QMessageBox.information(self, "Image Selected", "Image added successfully!")
    
    def validate_inputs(self):
        # Validate title input
        if not self.titleInput.text():
            return "Title cannot be empty."
        
        # Validate category input
        if self.categoryInput.currentText() == "":
            return "Please select a category."
        
        # Validate description input
        if not self.descriptionInput.toPlainText():
            return "Description cannot be empty."
        
        # Validate price input
        if not self.priceInput.text().isdigit():
            return "Price must be a numeric value."
        
        # Validate stock input
        if not self.stockInput.text().isdigit():
            return "Stock quantity must be a numeric value."
        
        # Validate image
        if not self.image_path:
            return "Please add an image."
        
        # If all validations pass
        return None
    
    def submit_to_database(self):
        # Validate inputs
        error_message = self.validate_inputs()
        if error_message:
            QMessageBox.critical(self, "Validation Error", error_message)
            return
        
        # Gather inputs
        title = self.titleInput.text()
        category = self.categoryInput.currentText()
        description = self.descriptionInput.toPlainText()
        price = float(self.priceInput.text())
        stock = int(self.stockInput.text())
        image_path = self.image_path
        
        # Insert into the database
        try:
            connection = pyodbc.connect(
                "DRIVER={ODBC Driver 17 for SQL Server};"
                "SERVER=ZAIN_PC\MYSQL1;"
                "DATABASE=StoreDatabase;"
                "Trusted_Connection=yes;"
                "TrustServerCertificate=yes;"
            )
            cursor = connection.cursor()
            query = """
                INSERT INTO Products (SellerID, ProductName, CategoryID, Description, Price, StockQuantity, ProductImage, Status, PublishDate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            category_id = self.get_category_id(cursor, category)
            cursor.execute(query, (self.sellerID, title, category_id, description, price, stock, image_path, "Pending", date.today()))
            connection.commit()
            QMessageBox.information(self, "Success", "Product added successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))
        finally:
            connection.close()
    
    def get_category_id(self, cursor, category_name):
        # Fetch the category ID based on category name
        query = "SELECT CategoryID FROM Categories WHERE CategoryName = ?"
        cursor.execute(query, (category_name,))
        result = cursor.fetchone()
        return result[0] if result else None

    def populate_categories(self):
        try:
            connection = pyodbc.connect(
                "DRIVER={ODBC Driver 17 for SQL Server};"
                "SERVER=ZAIN_PC\MYSQL1;"
                "DATABASE=StoreDatabase;"
                "Trusted_Connection=yes;"
                "TrustServerCertificate=yes;"
            )
            cursor = connection.cursor()
            query = "SELECT CategoryName FROM Categories"
            cursor.execute(query)
            categories = cursor.fetchall()
            
            # Clear existing items in the combo box
            self.categoryInput.clear()
            
            # Add categories to the combo box
            for category in categories:
                self.categoryInput.addItem(category[0])  # category[0] contains the CategoryName
            
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to load categories: {str(e)}")
        finally:
            connection.close()
    
    def openDashboard(self):
        self.hide()
        self.addProductsWindow = DashboardWindow(self.sellerID)
        self.addProductsWindow.show()

       
def main():
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

