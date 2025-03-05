CREATE DATABASE StoreDatabase

USE StoreDatabase

CREATE TABLE Status (
    StatusID BIGINT IDENTITY(1,1) PRIMARY KEY,
    StatusTitle VARCHAR(50) NOT NULL
);

CREATE TABLE Categories (
    CategoryID BIGINT IDENTITY(1,1) PRIMARY KEY,
    CategoryName VARCHAR(100) NOT NULL,
    PlatformCommission DECIMAL(5, 2) NOT NULL
);

CREATE TABLE Sellers (
    SellerID BIGINT IDENTITY(1,1) PRIMARY KEY,
    StoreName VARCHAR(100),
    EmailID VARCHAR(100),
    CNIC BIGINT,
    BankName VARCHAR(100),
    BankAccount BIGINT,
    City VARCHAR(100),
    BusinessAddress TEXT,
    ContactNumber BIGINT,
    Password VARCHAR(100),
    AccountStatus VARCHAR(50)
);

CREATE TABLE Products (
    ProductSKU BIGINT IDENTITY(1,1) PRIMARY KEY,
    SellerID BIGINT,
    ProductName VARCHAR(100),
    Description TEXT,
    Price DECIMAL(10, 2),
    StockQuantity INT,
    CategoryID BIGINT,
    ProductImage VARCHAR(100),
    Status VARCHAR(50),
    PublishDate DATE,
    NumberOfClicks INT,
    FOREIGN KEY (SellerID) REFERENCES Sellers(SellerID),
    FOREIGN KEY (CategoryID) REFERENCES Categories(CategoryID)
);

CREATE TABLE Customers (
    CustomerID BIGINT IDENTITY(1,1) PRIMARY KEY,
    FirstName VARCHAR(50),
    LastName VARCHAR(50),
    EmailID VARCHAR(100),
    City VARCHAR(100),
    DeliveryAddress TEXT,
    ContactNumber BIGINT,
    Password VARCHAR(100)
);

CREATE TABLE Orders (
    OrderID BIGINT IDENTITY(1,1) PRIMARY KEY,
    CustomerID BIGINT,
    StatusID BIGINT,
    ShippingAddress TEXT,
    OrderDate DATE,
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID),
    FOREIGN KEY (StatusID) REFERENCES Status(StatusID)
);

CREATE TABLE OrderItems (
    OrderID BIGINT,
    ProductSKU BIGINT,
    Quantity INT,
    UnitPrice DECIMAL(10, 2),
    PRIMARY KEY (OrderID, ProductSKU),
    FOREIGN KEY (OrderID) REFERENCES Orders(OrderID),
    FOREIGN KEY (ProductSKU) REFERENCES Products(ProductSKU)
);

CREATE TABLE ShoppingCart (
    CustomerID BIGINT,
    ProductID BIGINT,
    Quantity INT,
    PRIMARY KEY (CustomerID, ProductID),
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID),
    FOREIGN KEY (ProductID) REFERENCES Products(ProductSKU)
);

CREATE TABLE Reviews (
    OrderID BIGINT,
    ProductSKU BIGINT,
    Rating INT,
    ReviewDate DATE,
    PRIMARY KEY (OrderID, ProductSKU),
    FOREIGN KEY (OrderID) REFERENCES Orders(OrderID),
    FOREIGN KEY (ProductSKU) REFERENCES Products(ProductSKU)
);


CREATE TABLE Finances (
    TransactionID BIGINT IDENTITY(1,1) PRIMARY KEY,
    MonthOfPayment VARCHAR(20),
    SellerID BIGINT,
    PaymentDate DATE,
    Status VARCHAR(50),
    Amount DECIMAL(10, 2),  -- Assuming Amount is a decimal with two decimal places
    FOREIGN KEY (SellerID) REFERENCES Sellers(SellerID)
);


CREATE TABLE SaleCampaigns (
    CampaignID BIGINT IDENTITY(1,1) PRIMARY KEY,
    CampaignName VARCHAR(100),
    StartDate DATETIME,
    EndDate DATETIME,
    MinimumDiscount DECIMAL(5, 2)
);

CREATE TABLE CampaignProducts (
    CampaignID BIGINT,
    ProductSKU BIGINT,
    DiscountPercentage DECIMAL(5, 2),
    PRIMARY KEY (CampaignID, ProductSKU),
    FOREIGN KEY (CampaignID) REFERENCES SaleCampaigns(CampaignID),
    FOREIGN KEY (ProductSKU) REFERENCES Products(ProductSKU)
);

CREATE TABLE Banks (
    BankID INT IDENTITY(1,1) PRIMARY KEY,     
    BankName VARCHAR(255) NOT NULL 
);

CREATE TABLE Cities (
    CityID INT IDENTITY(1,1) PRIMARY KEY,     
    CityName VARCHAR(255) NOT NULL 
);

select * from sellers

select * from Products


INSERT INTO Categories (CategoryName, PlatformCommission)
VALUES 
    ('Electronics', 15.00),
    ('Fashion', 12.00),
    ('Home Appliances', 18.50),
    ('Books', 8.00),
    ('Beauty Products', 10.00),
    ('Toys', 14.50),
    ('Furniture', 17.50),
    ('Sports Equipment', 11.50),
    ('Groceries', 9.00),
    ('Stationery', 5.50),
    ('Automotive', 13.50),
    ('Jewelry', 19.00),
    ('Health Products', 7.50),
    ('Pet Supplies', 6.00),
    ('Garden Supplies', 16.00);


INSERT INTO Banks (BankName) VALUES 
('National Bank of Pakistan'),
('Habib Bank Limited'),
('United Bank Limited'),
('Allied Bank Limited'),
('MCB Bank Limited'),
('Meezan Bank Limited'),
('Bank Alfalah Limited'),
('Faysal Bank Limited'),
('Askari Bank Limited'),
('Bank of Punjab'),
('Sindh Bank Limited'),
('Bank Islami Pakistan Limited'),
('JS Bank Limited'),
('Summit Bank Limited'),
('Soneri Bank Limited'),
('Standard Chartered Bank (Pakistan)'),
('Habib Metropolitan Bank'),
('First Women Bank Limited'),
('Al Baraka Bank (Pakistan) Limited'),
('UBL Omni'),
('Silk Bank Limited'),
('Dubai Islamic Bank Pakistan Limited'),
('Citi Bank Pakistan'),
('Punjab Provincial Cooperative Bank'),
('KASB Bank Limited'),
('Pak Oman Microfinance Bank'),
('FINCA Microfinance Bank'),
('U Microfinance Bank Limited'),
('Khushhali Microfinance Bank Limited'),
('Mobilink Microfinance Bank'),
('NRSP Microfinance Bank'),
('Apna Microfinance Bank'),
('First Microfinance Bank Limited');


INSERT INTO Cities (CityName) VALUES 
('Karachi'),
('Lahore'),
('Islamabad'),
('Rawalpindi'),
('Peshawar'),
('Quetta'),
('Faisalabad'),
('Multan'),
('Hyderabad'),
('Sialkot'),
('Gujranwala'),
('Bahawalpur'),
('Sargodha'),
('Sukkur'),
('Larkana'),
('Mardan'),
('Abbottabad'),
('Mingora'),
('Dera Ghazi Khan'),
('Nawabshah'),
('Khuzdar'),
('Muzaffarabad'),
('Gilgit'),
('Skardu'),
('Chitral'),
('Mirpur'),
('Rahim Yar Khan'),
('Gujrat'),
('Kasur'),
('Sheikhupura'),
('Jhelum'),
('Okara'),
('Sahiwal'),
('Vehari'),
('Mansehra'),
('Attock'),
('Bannu'),
('Chakwal'),
('Dera Ismail Khan'),
('Turbat'),
('Zhob'),
('Jhang'),
('Swat'),
('Hafizabad'),
('Chaman'),
('Kotli'),
('Shikarpur'),
('Jacobabad'),
('Khanewal'),
('Nowshera');

INSERT INTO Status (StatusTitle) VALUES 
('Pending'),
('Active'),
('Inactive'),
('Shipped'),
('Delivered');

SELECT ProductName, Price 
            FROM Products 
            WHERE CategoryID = (SELECT CategoryID FROM Categories WHERE CategoryName = 'Fashion')

select * from Sellers


select * from Products

