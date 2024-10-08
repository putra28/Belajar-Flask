﻿# REST API for Retail Store Management

![Store Icon](https://brandeps.com/icon-download/S/Shop-icon-vector-02.svg) <!-- Replace with your desired store icon URL -->

## Overview

This REST API serves as the backend for a retail store management website. It provides endpoints for managing various functionalities, including user roles for administrators, managers, and cashiers (Point of Sale). 

## Features

- **User Management**: Admins can manage users, including adding, updating, and deleting user accounts.
- **Transaction Management**: Cashiers can process sales transactions, view transaction history, and manage customers.
- **Product Management**: Admins can manage products, including adding, updating, and deleting product information.
- **Reporting**: Managers can generate reports on sales and inventory status.

## API Endpoints

### Authentication

- `POST /api/login`: Authenticate users.

### Users

- `GET /api/users`: Retrieve a list of all users.
- `POST /api/users`: Create a new user.
- `PUT /api/users/{id}`: Update user information.
- `DELETE /api/users/{id}`: Delete a user.

### Products

- `GET /api/products`: Retrieve a list of products.
- `POST /api/products`: Add a new product.
- `PUT /api/products/{id}`: Update product information.
- `DELETE /api/products/{id}`: Delete a product.

### Transactions

- `GET /api/getdata/alldatatransaksi`: Retrieve all transactions.
- `POST /api/getdata/transaksibykasir`: Retrieve transactions by user ID.
