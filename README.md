# 🚀 Serverless Attendance System with Face Recognition

## 📌 Overview

This project is a **serverless, contactless attendance system** that uses facial recognition to mark employee attendance in real time. The system eliminates manual attendance tracking by leveraging AWS cloud services.

---

## ✨ Features

* 📸 Face recognition-based attendance (clock-in / clock-out)
* ⚡ Real-time processing using AWS Lambda
* 🗄️ Attendance storage using DynamoDB
* 🧑‍💼 Admin dashboard for employee management
* 📊 Automated attendance tracking and status updates
* 🔐 Secure and scalable serverless architecture

---

## 🏗️ Architecture

![Architecture](docs/architecture.png)

---

## 🧠 How It Works

1. User captures image via frontend (webcam)
2. Image is uploaded to S3 using pre-signed URL
3. S3 triggers AWS Lambda
4. Lambda calls AWS Rekognition to identify employee
5. Employee attendance is recorded in DynamoDB
6. Admin dashboard fetches and displays attendance data

---

## 🛠️ Tech Stack

* AWS Lambda
* Amazon S3
* Amazon Rekognition
* Amazon DynamoDB
* API Gateway
* HTML, CSS, JavaScript

---

## 📸 Screenshots

### 👨‍💻 Employee Interface

![Employee_attendance_system](https://github.com/user-attachments/assets/8c15342b-179f-4f50-b380-0b14f57856a5)


### 🧑‍💼 Admin Dashboard

![Admin_dashboard](https://github.com/user-attachments/assets/3d9b6e93-7736-450a-b7f6-4d7c6eed7b1d)


---

## 🔗 API Endpoints

| Method | Endpoint           | Description            |
| ------ | ------------------ | ---------------------- |
| POST   | /createEmployee    | Register employee      |
| GET    | /employees         | Fetch employee list    |
| POST   | /approveEmployee   | Update employee status |
| GET    | /get-presigned-url | Generate upload URL    |

---

## ⚙️ Setup Instructions

### 1. Create S3 Bucket

* Upload bucket for images
* Enable lifecycle rule to delete images

### 2. Setup Rekognition

* Create face collection
* Index employee faces

### 3. Create DynamoDB Table

* Table: attendance
* Partition Key: employee_id
* Sort Key: date

### 4. Deploy Lambda Functions

* Face recognition handler
* Pre-signed URL generator

### 5. Configure API Gateway

* Connect endpoints to Lambda

### 6. Deploy Frontend

* Upload frontend files to S3
* Enable static website hosting

---

## 🔐 Security Features

* IAM roles with least privilege
* S3 lifecycle rules for image deletion
* Encrypted DynamoDB storage
* Secure API communication

---

## 💰 Cost Optimization

* Pay-per-use serverless architecture
* Minimal storage due to auto-deletion
* Efficient Rekognition usage

---

## 🚀 Future Enhancements

* Real-time notifications (SNS)
* Multi-factor authentication
* Mobile app integration
* Advanced analytics dashboard

---



