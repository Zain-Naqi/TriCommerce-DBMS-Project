import pyodbc
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableWidgetItem
from PyQt6.uic import loadUi


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


class AdminDashboardWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi('AdminDashboard.ui', self)  

        self.productsButton = self.pushButton 
        self.sellersButton = self.pushButton_2 
        self.financesButton = self.pushButton_3  

        self.productsButton.clicked.connect(self.manageProducts)
        self.sellersButton.clicked.connect(self.manageSellers)
        self.financesButton.clicked.connect(self.manageFinances)
        self.manageOrdersButton.clicked.connect(self.manageOrders)  

    def manageProducts(self):
        self.hide()
        self.productsWindow = ManageProductsWindow()
        self.productsWindow.show()

    def manageSellers(self):
        self.hide()
        self.sellersWindow = ManageSellersWindow()
        self.sellersWindow.show()
    
    def manageOrders(self):
        self.hide()
        self.sellersWindow = ManageOrdersWindow()
        self.sellersWindow.show()

    def manageFinances(self):
        QMessageBox.information(self, "Manage Finances", "Finance management functionality is under development.")


class ManageProductsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi('Products.ui', self)  

        self.statusCombo.currentIndexChanged.connect(self.filterProducts)
        self.activeButton.clicked.connect(self.toggleProductStatus)
        self.approveButton.clicked.connect(self.approveProduct)
        self.approveAllButton.clicked.connect(self.approveAllProducts)
        self.homeButton.clicked.connect(self.openDashboard)

        self.connection = get_database_connection()
        if self.connection:
            self.loadProducts("Active")  

    def openDashboard(self):
        self.hide()
        self.addProductsWindow = AdminDashboardWindow()
        self.addProductsWindow.show()
    
    def loadProducts(self, status):
        self.productsTable.clearContents()
        self.productsTable.setRowCount(0)

        if not self.connection:
            QMessageBox.critical(self, "Database Error", "Unable to connect to the database.")
            return

        cursor = self.connection.cursor()
        query = "SELECT ProductSKU, SellerID, ProductName, StockQuantity, Price FROM Products WHERE Status = ?"
        cursor.execute(query, (status,))
        rows = cursor.fetchall()

        for row in rows:
            row_position = self.productsTable.rowCount()
            self.productsTable.insertRow(row_position)
            for col, value in enumerate(row):
                self.productsTable.setItem(row_position, col, QTableWidgetItem(str(value)))

        self.updateActiveButtonText(status)

    def filterProducts(self):
        status = self.statusCombo.currentText()
        self.loadProducts(status)

    def updateActiveButtonText(self, status):
        if status == "Inactive":
            self.activeButton.setText("Activate")
        else:
            self.activeButton.setText("Deactivate")

    def toggleProductStatus(self):
        selected_items = self.productsTable.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a product to toggle status.")
            return

        product_sku = selected_items[0].text()
        cursor = self.connection.cursor()
        cursor.execute("SELECT Status FROM Products WHERE ProductSKU = ?", (product_sku,))
        current_status = cursor.fetchone()[0]

        if current_status == "Inactive":
            new_status = "Active"
        else:
            new_status = "Inactive"

        cursor.execute("UPDATE Products SET Status = ? WHERE ProductSKU = ?", (new_status, product_sku))
        self.connection.commit()
        QMessageBox.information(self, "Status Updated", f"Product {product_sku} status updated to {new_status}.")

        self.filterProducts()

    def approveProduct(self):
        selected_items = self.productsTable.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a product to approve.")
            return

        product_sku = selected_items[0].text()
        cursor = self.connection.cursor()
        cursor.execute("UPDATE Products SET Status = 'Active' WHERE ProductSKU = ?", (product_sku,))
        self.connection.commit()
        QMessageBox.information(self, "Approval", f"Product {product_sku} approved!")
        self.filterProducts()

    def approveAllProducts(self):
        cursor = self.connection.cursor()
        cursor.execute("UPDATE Products SET Status = 'Active' WHERE Status = 'Pending'")
        self.connection.commit()
        QMessageBox.information(self, "Approval", "All pending products approved!")
        self.filterProducts()

    def closeEvent(self, event):
        if self.connection:
            self.connection.close()
        event.accept()


class ManageSellersWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi('SellerApproval.ui', self)  

        self.activateButton = self.pushButton
        self.deactivateButton = self.pushButton_2

        self.activateButton.clicked.connect(self.activateSeller)
        self.deactivateButton.clicked.connect(self.deactivateSeller)
        self.homeButton.clicked.connect(self.openDashboard)

        self.connection = get_database_connection()
        if self.connection:
            self.loadSellers()
        
    def openDashboard(self):
        self.hide()
        self.addProductsWindow = AdminDashboardWindow()
        self.addProductsWindow.show()

    def loadSellers(self):
        if not self.connection:
            QMessageBox.critical(self, "Database Error", "Unable to connect to the database.")
            return

        cursor = self.connection.cursor()
        query = "SELECT StoreName, CNIC, EmailID, BusinessAddress, AccountStatus FROM Sellers"
        cursor.execute(query)

        self.tableWidget.setRowCount(0)
        for row in cursor.fetchall():
            row_position = self.tableWidget.rowCount()
            self.tableWidget.insertRow(row_position)
            for col, value in enumerate(row):
                self.tableWidget.setItem(row_position, col, QTableWidgetItem(str(value)))

    def activateSeller(self):
        selected_items = self.tableWidget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a seller to activate.")
            return

        seller_name = selected_items[0].text()
        cursor = self.connection.cursor()
        cursor.execute("UPDATE Sellers SET AccountStatus = 'Active' WHERE StoreName = ?", (seller_name,))
        self.connection.commit()
        QMessageBox.information(self, "Activation", f"Seller {seller_name} activated!")
        self.loadSellers()

    def deactivateSeller(self):
        selected_items = self.tableWidget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a seller to deactivate.")
            return

        seller_name = selected_items[0].text()
        cursor = self.connection.cursor()
        cursor.execute("UPDATE Sellers SET AccountStatus = 'Deactivated' WHERE StoreName = ?", (seller_name,))
        self.connection.commit()
        QMessageBox.information(self, "Deactivation", f"Seller {seller_name} deactivated!")
        self.loadSellers()


class ManageOrdersWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        loadUi('Manage Orders.ui', self)


        self.pendingButton.clicked.connect(self.showPendingOrders)
        self.shippedButton.clicked.connect(self.showShippedOrders)
        self.deliveredButton.clicked.connect(self.showDeliveredOrders)
        self.homeButton.clicked.connect(self.openDashboard)

        self.cancelButton.clicked.connect(self.cancelOrder)  
        self.processButton.clicked.connect(self.processOrder)  

        self.showPendingOrders()
    
    def openDashboard(self):
        self.hide()
        self.addProductsWindow = AdminDashboardWindow()
        self.addProductsWindow.show()

    def openDashboard(self):
        self.hide()
        self.addProductsWindow = AdminDashboardWindow()
        self.addProductsWindow.show()

    def fetchOrders(self, status):
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
        WHERE st.StatusTitle = ?;
        """

        connection = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=ZAIN_PC\MYSQL1;"
            "DATABASE=StoreDatabase;"
            "Trusted_Connection=yes;"
            "TrustServerCertificate=yes;"
        )

        cursor = connection.cursor()
        cursor.execute(query, (status))
        orders = cursor.fetchall()
        connection.close()
        return orders

    def populateTable(self, orders):
        self.ordersTable.setRowCount(0)
        self.ordersTable.setColumnCount(7)

        for row_number, order in enumerate(orders):
            self.ordersTable.insertRow(row_number)
            for column_number, data in enumerate(order):
                self.ordersTable.setItem(row_number, column_number, QTableWidgetItem(str(data)))

    def showPendingOrders(self):
        orders = self.fetchOrders('Pending')
        self.populateTable(orders)

    def showShippedOrders(self):
        orders = self.fetchOrders('Shipped')
        self.populateTable(orders)

    def showDeliveredOrders(self):
        orders = self.fetchOrders('Delivered')
        self.populateTable(orders)

    def cancelOrder(self):
        selected_row = self.ordersTable.currentRow()

        if selected_row != -1:  
            order_id = self.ordersTable.item(selected_row, 0).text()  

            status = self.ordersTable.item(selected_row, 6).text() 
            if status != "Pending":
                QMessageBox.warning(self, "Invalid Status", "Only pending orders can be canceled.")
                return

            try:
                
                connection = pyodbc.connect(
                    "DRIVER={ODBC Driver 17 for SQL Server};"
                    "SERVER=ZAIN_PC\MYSQL1;"
                    "DATABASE=StoreDatabase;"
                    "Trusted_Connection=yes;"
                    "TrustServerCertificate=yes;"
                )

                cursor = connection.cursor()
                delete_query = "DELETE FROM Orders WHERE OrderID = ?"
                cursor.execute(delete_query, (order_id,))
                connection.commit()
                connection.close()

                # Remove the order from the table widget
                self.ordersTable.removeRow(selected_row)

                QMessageBox.information(self, "Success", "Order canceled successfully.")

            except Exception as e:
                QMessageBox.critical(self, "Database Error", f"Failed to cancel the order: {e}")

    def processOrder(self):

        selected_row = self.ordersTable.currentRow()

        if selected_row != -1:  
            order_id = self.ordersTable.item(selected_row, 0).text()  

            try:
                connection = pyodbc.connect(
                    "DRIVER={ODBC Driver 17 for SQL Server};"
                    "SERVER=ZAIN_PC\MYSQL1;"
                    "DATABASE=StoreDatabase;"
                    "Trusted_Connection=yes;"
                    "TrustServerCertificate=yes;"
                )
                cursor = connection.cursor()

                cursor.execute("""
                    SELECT st.StatusTitle 
                    FROM Orders o
                    INNER JOIN Status st ON o.StatusID = st.StatusID
                    WHERE o.OrderID = ?
                """, (order_id,))
                current_status = cursor.fetchone()

                connection.close()

                if current_status is None:
                    QMessageBox.warning(self, "Invalid Order", "The selected order does not exist.")
                    return

                status_title = current_status[0]

                if status_title != "Pending":
                    QMessageBox.warning(self, "Invalid Status", "Only pending orders can be processed.")
                    return

                connection = pyodbc.connect(
                    "DRIVER={ODBC Driver 17 for SQL Server};"
                    "SERVER=ZAIN_PC\MYSQL1;"
                    "DATABASE=StoreDatabase;"
                    "Trusted_Connection=yes;"
                    "TrustServerCertificate=yes;"
                )
                cursor = connection.cursor()

                update_query = """
                UPDATE Orders 
                SET StatusID = (SELECT StatusID FROM Status WHERE StatusTitle = 'Shipped') 
                WHERE OrderID = ?
                """
                cursor.execute(update_query, (order_id,))
                connection.commit()
                connection.close()

                self.showPendingOrders()

                QMessageBox.information(self, "Success", "Order processed and marked as Shipped.")

            except Exception as e:
                QMessageBox.critical(self, "Database Error", f"Failed to process the order: {e}")


        
def main():
    app = QApplication(sys.argv)
    dashboard_window = AdminDashboardWindow()
    dashboard_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
