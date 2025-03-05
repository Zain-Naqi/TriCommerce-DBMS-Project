import pyodbc
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableWidgetItem
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QSize
from PyQt6.uic import loadUi
from datetime import datetime



# Database Connection
def get_database_connection():
    """Establish and return a database connection."""
    try:
        connection = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=ZAIN_PC\\MYSQL1;"
            "DATABASE=StoreDatabase;"
            "Trusted_Connection=yes;"
            "TrustServerCertificate=yes;"
        )
        print("Connected to the database successfully.")
        return connection
    except pyodbc.Error as e:
        print(f"Database connection error: {e}")
        return None


class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi('login.ui', self)

        # Connect signals
        self.loginButton.clicked.connect(self.handle_login)
        self.newAccountButton.clicked.connect(self.create_account)
        self.resetPassword.clicked.connect(self.reset_password)
        

    def show_error_message(self, message):
        QMessageBox.critical(self, "Error", message)

    def handle_login(self):
        """Handle user login."""
        self.email = self.emailInput.text()
        password = self.passwordInput.text()

        if not self.email or not password:
            self.show_error_message("Please fill in both email and password.")
            return

        # Verify credentials in the database
        connection = get_database_connection()
        if not connection:
            self.show_error_message("Database connection error.")
            return

        try:
            query = "SELECT EmailID, Password FROM Customers WHERE EmailID = ? AND Password = ?"
            cursor = connection.cursor()
            cursor.execute(query, (self.email, password))
            result = cursor.fetchone()

            if result:
                QMessageBox.information(self, "Login Successful", "Welcome to the system!")
                self.open_dashboard()
            else:
                self.show_error_message("Invalid email or password.")
        except pyodbc.Error as e:
            self.show_error_message(f"Database query error: {e}")
        finally:
            connection.close()

    def create_account(self):
        self.hide()
        self.register_window = RegistrationWindow()
        self.register_window.show()

    def reset_password(self):
        QMessageBox.information(self, "Reset Password", "Password reset functionality is under development.")

    def open_dashboard(self):
        self.hide()
        self.dashboard = MainDashboard(self.email)
        self.dashboard.show()


class RegistrationWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("registration.ui", self)
        self.pushButton.clicked.connect(self.register_account)
        self.populate_city_combo_box()

    def populate_city_combo_box(self):
        connection = get_database_connection()
        if not connection:
            QMessageBox.critical(self, "Database Error", "Unable to connect to the database.")
            return

        try:
            cursor = connection.cursor()
            cursor.execute("SELECT CityName FROM Cities")
            self.comboBox.clear()
            self.comboBox.addItem("City")
            for row in cursor.fetchall():
                self.comboBox.addItem(row[0])
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to load cities: {e}")
        finally:
            connection.close()

    def register_account(self):
        first_name = self.lineEdit.text().strip()
        last_name = self.lineEdit_2.text().strip()
        email = self.lineEdit_3.text().strip()
        password = self.lineEdit_4.text().strip()
        contact_number = self.lineEdit_5.text().strip()
        city = self.comboBox.currentText()
        delivery_address = self.lineEdit_6.text().strip()

        if not first_name or not last_name:
            self.show_error_message("First Name and Last Name cannot be empty.")
            return

        if len(password) < 6:
            self.show_error_message("Password must be at least 6 characters long.")
            return

        if not contact_number.isdigit() or len(contact_number) != 11:
            self.show_error_message("Contact Number must be 11 digits long.")
            return

        if city == "City":
            self.show_error_message("Please select a valid city.")
            return

        connection = get_database_connection()
        if not connection:
            QMessageBox.critical(self, "Database Error", "Unable to connect to the database.")
            return

        try:
            query = """
            INSERT INTO Customers (FirstName, LastName, EmailID, Password, ContactNumber, City, DeliveryAddress)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            cursor = connection.cursor()
            cursor.execute(query, (first_name, last_name, email, password, contact_number, city, delivery_address))
            connection.commit()
            QMessageBox.information(self, "Success", "Account registered successfully!")
            self.loginWindow = LoginWindow()
            self.loginWindow.show()
            self.close()
        except pyodbc.Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to register account: {e}")
        finally:
            connection.close()

    def show_error_message(self, message):
        QMessageBox.critical(self, "Registration Error", message)


class AccountWindow(QMainWindow):
    def __init__(self, email):
        super().__init__()
        loadUi("account.ui", self)
        
        self.email = email
        
        self.pushButton_5.clicked.connect(self.update_account_info)
        self.populate_account_info()
        self.populate_city_combo_box()

    def populate_account_info(self):
        """Load customer account info."""
        connection = get_database_connection()
        if not connection:
            QMessageBox.critical(self, "Database Error", "Unable to connect to the database.")
            return

        try:
            query = "SELECT FirstName, LastName, EmailID, ContactNumber, Password, City, DeliveryAddress FROM Customers WHERE EmailID = ?"
            cursor = connection.cursor()
            cursor.execute(query, (self.email,))
            result = cursor.fetchone()

            if result:
                self.lineEdit_5.setText(str(result[0]))  # Name
                self.lastNameInput.setText(str(result[1]))
                self.lineEdit.setText(str(result[2]))  # Email
                self.lineEdit_2.setText(str(result[3]))  # Phone
                self.lineEdit_3.setText(str(result[4]))  # Password
                self.comboBox.setCurrentText(str(result[5]))  # City
                self.lineEdit_4.setText(str(result[6]))  # Address
            else:
                QMessageBox.warning(self, "Error", "Customer information not found.")
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to fetch account info: {e}")
        finally:
            connection.close()

    def populate_city_combo_box(self):
        connection = get_database_connection()
        if not connection:
            QMessageBox.critical(self, "Database Error", "Unable to connect to the database.")
            return

        try:
            cursor = connection.cursor()
            cursor.execute("SELECT CityName FROM Cities")
            self.comboBox.clear()
            self.comboBox.addItem("Select City")
            for row in cursor.fetchall():
                self.comboBox.addItem(row[0])
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to load cities: {e}")
        finally:
            connection.close()

    def update_account_info(self):
        name = self.lineEdit_5.text()
        lastName = self.lastNameInput.text()
        email = self.lineEdit.text()
        phone = self.lineEdit_2.text()
        password = self.lineEdit_3.text()
        city = self.comboBox.currentText()
        address = self.lineEdit_4.text()

        if not name or not lastName or not email or not phone or not password or city == "Select City" or not address:
            QMessageBox.warning(self, "Validation Error", "All fields must be filled in.")
            return

        connection = get_database_connection()
        if not connection:
            QMessageBox.critical(self, "Database Error", "Unable to connect to the database.")
            return

        try:
            query = """
            UPDATE Customers
            SET FirstName = ?, LastName = ?, ContactNumber = ?, Password = ?, City = ?, DeliveryAddress = ?
            WHERE EmailID = ?
            """
            cursor = connection.cursor()
            cursor.execute(query, (name, lastName, phone, password, city, address, email))
            connection.commit()
            QMessageBox.information(self, "Success", "Account information updated successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to update account info: {e}")
        finally:
            connection.close()


class MainDashboard(QMainWindow):
    def __init__(self, email):
        super().__init__()
        loadUi("maindashboard.ui", self)
        
        self.email = email

        # Connect signals
        self.pushButton.clicked.connect(self.open_search_products)
        self.pushButton_3.clicked.connect(self.open_cart)
        # self.pushButton_4.clicked.connect(self.open_checkout)
        self.pushButton_5.clicked.connect(self.open_account)

    def open_search_products(self):
        self.hide()
        self.search_product_window = SearchProduct(self.email)
        self.search_product_window.show()

    def open_cart(self):
        self.hide()
        self.cart_window = CartWindow(self.email)
        self.cart_window.show()

    # def open_checkout(self):
    #     self.hide()
    #     self.checkout_window = CheckoutWindow()
    #     self.checkout_window.show()

    def open_account(self):
        self.hide()
        self.account_window = AccountWindow(self.email)
        self.account_window.show()


class SearchProduct(QMainWindow):
    def __init__(self, email):
        super().__init__()
        loadUi("searchproduct.ui", self)
        self.comboBox.setEnabled(True)
        self.populate_categories()
        self.comboBox.currentIndexChanged.connect(self.show_details)
        self.homeButton.clicked.connect(self.openDashboard)
        self.email = email

        # Connect the details button to open the product page
        self.detailsButton.clicked.connect(self.open_product_page_from_button)

    def openDashboard(self):
        self.hide()
        self.addProductsWindow = MainDashboard(self.email)
        self.addProductsWindow.show()
    
    def populate_categories(self):
        connection = get_database_connection()
        if not connection:
            QMessageBox.critical(self, "Database Error", "Unable to connect to the database.")
            return

        try:
            cursor = connection.cursor()
            cursor.execute("SELECT CategoryName FROM Categories")
            self.comboBox.clear()
            self.comboBox.addItem("Select Category")
            for row in cursor.fetchall():
                self.comboBox.addItem(row[0])
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to load categories: {e}")
        finally:
            connection.close()

    def show_details(self):
        selected_category = self.comboBox.currentText()
        if selected_category == "Select Category":
            QMessageBox.warning(self, "Warning", "Please select a valid category.")
            return

        connection = get_database_connection()
        if not connection:
            QMessageBox.critical(self, "Database Error", "Unable to connect to the database.")
            return

        try:
            query = """
            SELECT ProductName, Price 
            FROM Products 
            WHERE CategoryID = (SELECT CategoryID FROM Categories WHERE CategoryName = ?)
            and status = 'Active'
            """
            cursor = connection.cursor()
            cursor.execute(query, (selected_category,))
            products = cursor.fetchall()

            if not products:
                QMessageBox.warning(self, "No Products", "No products found for the selected category.")
                return

            self.tableWidget.setRowCount(len(products))
            for row_number, product in enumerate(products):
                self.tableWidget.setItem(row_number, 0, QTableWidgetItem(product[0]))  # Product Name (Index 0)
                self.tableWidget.setItem(row_number, 1, QTableWidgetItem(str(product[1])))  # Price (Index 1)

        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Error fetching products: {e}")
        finally:
            connection.close()

    def open_product_page_from_button(self):
        # Get the selected row from the table
        selected_row = self.tableWidget.currentRow()

        if selected_row == -1:
            QMessageBox.warning(self, "No Product Selected", "Please select a product to view its details.")
            return

        # Get the product details from the selected row
        selected_product_name = self.tableWidget.item(selected_row, 0).text()
        selected_product_price = self.tableWidget.item(selected_row, 1).text()

        # Open the ProductPage with the selected product details
        self.product_page_window = ProductPage(selected_product_name, selected_product_price, self.email)
        self.product_page_window.show()


class ProductPage(QMainWindow):
    def __init__(self, product_name, product_price, customer_id):
        super().__init__()
        loadUi("ProductPage.ui", self)

        self.titleLabel.setText(product_name)
        self.priceLabel.setText(product_price)
        self.customer_id = customer_id  # Store the customer ID for cart operations
        self.populate_product_details(product_name)

        # Connect the cart button to the add_to_cart method
        self.cartButton.clicked.connect(self.add_to_cart)
    
    def populate_product_details(self, product_name):
        connection = get_database_connection()
        if not connection:
            QMessageBox.critical(self, "Database Error", "Unable to connect to the database.")
            return

        try:
            query = """
            SELECT ProductSKU, Description, StockQuantity, ProductImage 
            FROM Products 
            WHERE ProductName = ?
            """
            cursor = connection.cursor()
            cursor.execute(query, (product_name,))
            product_details = cursor.fetchone()

            if product_details:
                self.product_id = product_details[0]  
                self.descriptionLabel.setText(product_details[1])  
                self.load_product_image(product_details[3]) 
            else:
                QMessageBox.warning(self, "Error", "Product details not found.")
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to fetch product details: {e}")
        finally:
            connection.close()

    def load_product_image(self, image_path):
        if image_path:
            pixmap = QPixmap(image_path)
            self.imageLabel.setPixmap(
                pixmap.scaled(self.imageLabel.size(), Qt.AspectRatioMode.KeepAspectRatio)
            )

    def add_to_cart(self):
        connection = get_database_connection()
        if not connection:
            QMessageBox.critical(self, "Database Error", "Unable to connect to the database.")
            return

        try:
            query_customer_id = "SELECT CustomerID FROM Customers WHERE EmailID = ?"
            cursor = connection.cursor()
            cursor.execute(query_customer_id, (self.customer_id,))  # self.customer_id holds the email

            customer_id = cursor.fetchone()

            if not customer_id:
                QMessageBox.warning(self, "Error", "Customer not found.")
                return

            customer_id = customer_id[0]  

            query_insert = """
            INSERT INTO ShoppingCart (CustomerID, ProductID, Quantity)
            VALUES (?, ?, ?)
            """
            cursor.execute(query_insert, (customer_id, int(self.product_id), 1)) 
            connection.commit()

            QMessageBox.information(self, "Success", "Product added to cart successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to add product to cart: {e}")
        finally:
            connection.close()


class CartWindow(QMainWindow):
    def __init__(self, customer_email):
        super().__init__()
        loadUi("cart.ui", self)
        self.customer_email = customer_email

        self.addButton.clicked.connect(self.increase_quantity)
        self.subButton.clicked.connect(self.decrease_quantity)
        self.removeButton.clicked.connect(self.remove_product)
        self.checkOutButton.clicked.connect(self.open_checkout_window)
        self.homeButton.clicked.connect(self.openDashboard)

        self.load_cart_data()

    def openDashboard(self):
        self.hide()
        self.addProductsWindow = MainDashboard(self.customer_email)
        self.addProductsWindow.show()
    
    def load_cart_data(self):
        connection = get_database_connection()
        if not connection:
            QMessageBox.critical(self, "Database Error", "Unable to connect to the database.")
            return

        try:
            query = """
            SELECT p.ProductName, c.Quantity, p.Price 
            FROM ShoppingCart c
            JOIN Products p ON c.ProductID = p.ProductSKU
            JOIN Customers cu ON c.CustomerID = cu.CustomerID
            WHERE cu.EmailID = ?
            """
            cursor = connection.cursor()
            cursor.execute(query, (self.customer_email,))
            cart_items = cursor.fetchall()

            self.cartProducts.setRowCount(len(cart_items))
            total_amount = 0

            for row_number, (product_name, quantity, price) in enumerate(cart_items):
                total = quantity * price
                total_amount += total

                self.cartProducts.setItem(row_number, 0, QTableWidgetItem(product_name))
                self.cartProducts.setItem(row_number, 1, QTableWidgetItem(str(quantity)))
                self.cartProducts.setItem(row_number, 2, QTableWidgetItem(f"{price:.2f}"))
                self.cartProducts.setItem(row_number, 3, QTableWidgetItem(f"{total:.2f}"))

            self.totalAmount.setText(f"{total_amount:.2f}")

        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to load cart data: {e}")
        finally:
            connection.close()

    def update_cart_quantity(self, change):
        selected_row = self.cartProducts.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Selection Error", "Please select a product.")
            return

        product_name = self.cartProducts.item(selected_row, 0).text()
        current_quantity = int(self.cartProducts.item(selected_row, 1).text()) + change

        if current_quantity < 1:
            QMessageBox.warning(self, "Quantity Error", "Quantity cannot be less than 1.")
            return

        connection = get_database_connection()
        if not connection:
            QMessageBox.critical(self, "Database Error", "Unable to connect to the database.")
            return

        try:
            query = """
            UPDATE ShoppingCart
            SET Quantity = ?
            WHERE ProductID = (SELECT ProductSKU FROM Products WHERE ProductName = ?)
            AND CustomerID = (SELECT CustomerID FROM Customers WHERE EmailID = ?)
            """
            cursor = connection.cursor()
            cursor.execute(query, (current_quantity, product_name, self.customer_email))
            connection.commit()

            # Refresh the cart view
            self.load_cart_data()

        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to update quantity: {e}")
        finally:
            connection.close()

    def increase_quantity(self):
        self.update_cart_quantity(1)

    def decrease_quantity(self):
        self.update_cart_quantity(-1)

    def remove_product(self):
        selected_row = self.cartProducts.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Selection Error", "Please select a product.")
            return

        product_name = self.cartProducts.item(selected_row, 0).text()

        connection = get_database_connection()
        if not connection:
            QMessageBox.critical(self, "Database Error", "Unable to connect to the database.")
            return

        try:
            query = """
            DELETE FROM ShoppingCart
            WHERE ProductID = (SELECT ProductSKU FROM Products WHERE ProductName = ?)
            AND CustomerID = (SELECT CustomerID FROM Customers WHERE EmailID = ?)
            """
            cursor = connection.cursor()
            cursor.execute(query, (product_name, self.customer_email))
            connection.commit()

            # Refresh the cart view
            self.load_cart_data()

        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to remove product: {e}")
        finally:
            connection.close()
    
    def open_checkout_window(self):
        # Create and show the checkout window
        self.checkout_window = CheckOutWindow(self.customer_email)
        self.checkout_window.show()


class CheckOutWindow(QMainWindow):
    def __init__(self, customer_email):
        super().__init__()
        loadUi("checkout.ui", self)
        self.customer_email = customer_email

        self.load_checkout_data()
        self.homeButton.clicked.connect(self.openDashboard)
        self.confirmButton.clicked.connect(self.confirm_checkout)

    def openDashboard(self):
        self.hide()
        self.addProductsWindow = MainDashboard(self.customer_email)
        self.addProductsWindow.show()
        
    def load_checkout_data(self):
        connection = get_database_connection()
        if not connection:
            QMessageBox.critical(self, "Database Error", "Unable to connect to the database.")
            return

        try:
            query = """
            SELECT p.ProductName, c.Quantity, p.Price 
            FROM ShoppingCart c
            JOIN Products p ON c.ProductID = p.ProductSKU
            JOIN Customers cu ON c.CustomerID = cu.CustomerID
            WHERE cu.EmailID = ?
            """
            cursor = connection.cursor()
            cursor.execute(query, (self.customer_email))
            cart_items = cursor.fetchall()

            self.checkOutProducts.setRowCount(len(cart_items))
            total_amount = 0

            for row_number, (product_name, quantity, price) in enumerate(cart_items):
                total = quantity * price
                total_amount += total

                self.checkOutProducts.setItem(row_number, 0, QTableWidgetItem(product_name))
                self.checkOutProducts.setItem(row_number, 1, QTableWidgetItem(str(quantity)))
                self.checkOutProducts.setItem(row_number, 2, QTableWidgetItem(f"{price:.2f}"))
                self.checkOutProducts.setItem(row_number, 3, QTableWidgetItem(f"{total:.2f}"))

            self.totalAmount.setText(f"{total_amount:.2f}")

            query_address = """
            SELECT DeliveryAddress 
            FROM Customers 
            WHERE EmailID = ?
            """
            cursor.execute(query_address, (self.customer_email,))
            address = cursor.fetchone()

            if address:
                self.addressInput.setText(address[0])
            else:
                self.addressInput.setText("No address found.")

        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to load checkout data: {e}")
        finally:
            connection.close()

    def confirm_checkout(self):
        connection = get_database_connection()
        if not connection:
            QMessageBox.critical(self, "Database Error", "Unable to connect to the database.")
            return

        try:
            query_customer = """
            SELECT CustomerID, DeliveryAddress 
            FROM Customers 
            WHERE EmailID = ?
            """
            cursor = connection.cursor()
            cursor.execute(query_customer, (self.customer_email,))
            customer = cursor.fetchone()

            if not customer:
                QMessageBox.critical(self, "Customer Error", "Customer details not found.")
                return

            customer_id = customer[0]
            shipping_address = self.addressInput.text()

            order_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            query_insert_order = """
            INSERT INTO Orders (CustomerID, StatusID, ShippingAddress, OrderDate)
            VALUES (?, 1, ?, ?)
            """
            cursor.execute(query_insert_order, (customer_id, shipping_address, order_date))
            connection.commit()

            query_order_id = "SELECT @@IDENTITY"
            cursor.execute(query_order_id)
            order_id = cursor.fetchone()[0]

            self.insert_order_details(connection, order_id, customer_id)

            self.remove_cart_items(connection, customer_id)

            self.update_product_stock(connection, order_id)  

            QMessageBox.information(self, "Success", "Order placed successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to place the order: {e}")
        finally:
            connection.close()

    def insert_order_details(self, connection, order_id, customer_id):
        try:
            query_cart = """
            SELECT ProductID, Quantity 
            FROM ShoppingCart
            WHERE CustomerID = ?
            """
            cursor = connection.cursor()
            cursor.execute(query_cart, (customer_id))
            cart_items = cursor.fetchall()

            if cart_items:
                for product in cart_items:
                    product_id = product[0]
                    quantity = product[1]

                    query_insert_order_details = """
                    INSERT INTO OrderItems (OrderID, ProductSKU, Quantity)
                    VALUES (?, ?, ?)
                    """
                    cursor.execute(query_insert_order_details, (order_id, product_id, quantity))
                
                connection.commit()
            else:
                QMessageBox.warning(self, "Cart Empty", "Your cart is empty. Please add products before proceeding.")

        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to insert order details: {e}")

    def remove_cart_items(self, connection, customer_id):
        try:
            query_remove_cart_items = """
            DELETE FROM ShoppingCart
            WHERE CustomerID = ?
            """
            cursor = connection.cursor()
            cursor.execute(query_remove_cart_items, (customer_id,))
            connection.commit()

        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to remove items from cart: {e}")

    def update_product_stock(self, connection, order_id):
        try:
            query_update_stock = """
            UPDATE Products
            SET StockQuantity = StockQuantity - (SELECT Quantity FROM OrderItems WHERE ProductSKU = Products.ProductSKU AND OrderID = ?)
            WHERE ProductSKU IN (SELECT ProductSKU FROM Orders WHERE OrderID = ?)
            """
            cursor = connection.cursor()
            cursor.execute(query_update_stock, (order_id, order_id))  
            connection.commit()

        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to update product stock: {e}")
    

def main():
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
