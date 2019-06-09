from pymongo import MongoClient


# Function to insert data into mongo db
def insert():
    try:
        employeeId = input('Enter Employee id :')
        employeeName = input('Enter Name :')
        employeeAge = input('Enter age :')
        employeeCountry = input('Enter Country :')

        db.Employees.insert_one(
            {
                "id": employeeId,
                "name": employeeName,
                "age": employeeAge,
                "country": employeeCountry
            })
        print('\nInserted data successfully\n')

    except Exception as e:
        print(str(e))


# function to read records from mongo db
def read():
    try:
        empCol = db.Employees.find()
        print('\n All data from EmployeeData Database \n')
        for emp in empCol:
            print(emp)

    except Exception as e:
        print(str(e))


# Function to update record to mongo db
def update():
    try:
        criteria = input('\nEnter id to update\n')
        name = input('\nEnter name to update\n')
        age = input('\nEnter age to update\n')
        country = input('\nEnter country to update\n')

        db.Employees.update_one(
            {"id": criteria},
            {
                "$set": {
                    "name": name,
                    "age": age,
                    "country": country
                }
            }
        )
        print("\nRecords updated successfully\n")

    except Exception as e:
        print(str(e))


# Function to delete record from mongo db
def delete():
    try:
        criteria = input('\nEnter employee id to delete\n')
        db.Employees.delete_many({"id":criteria})
        print('\nDeletion successful\n')

    except Exception as e:
        print(str(e))



client = MongoClient('localhost:27017')
db = client.EmployeeData

print("\nread:\n")
read()

# print("\ninsert:\n")
# insert()

# print("\nread:\n")
# read()
