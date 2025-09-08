from connect import getdb
from sqlalchemy import text
import csv
import os

def select_fulldata():
    db = getdb()

    # query2 = text("""SELECT c.customerID, c.age, c.gender, c.income, c.location, 
    #              c.maritalStatus,c.policyHistory, c.claimsHistory,c.renewalStatus,
    #              p.policyID, p.policyType, p.premium,p.coverageDetails, p.issuanceDate, p.expiryDate,
    #              s.claimType, s.claimAmount, s.claimDate,
    #              b.interactionType, b.interactionDate, b.responseTime,
    #              r.renewalDate, r.renewalStatus,r.renewalPremium 

    #              FROM customer c
    #                 LEFT JOIN policy p ON c.CustomerID = p.AssociatedCustomerID
    #                 LEFT JOIN claims s ON c.CustomerID = s.CustomerID
    #                 LEFT JOIN behavioral_interaction b ON c.CustomerID = b.CustomerID
    #                 LEFT JOIN renewal r ON c.CustomerID = r.CustomerID AND p.PolicyID = r.PolicyID
                 
    #              """)
    
    query = text("""select age, gender, income,location, MaritalStatus, PolicyHistory, ClaimsHistory. claim amount,
            claimtype, claimdate, renewaldate, c.renewalstatus, RenewlPremium, PolicyType,premium,CoverageDetails,
            IssuanceDate,expirydate,interactionType, interactionDate, responsetime from customer c
            left join claims cl on c.cutomerID = cl.CustomerID
            join renewal r on r.customerID = c.customerID
            join policy p on p.policyID = r.PolicyID
            join behavioural_interaction b on b.CustomerID = c.CustomerID
            """)
   
    result = db.execute(query)
    fulldata = result.fetchall()
    headers = result.keys()

    save_path = r"C:\Users\Etteba\OneDrive\Documents\OptiSecureInsurance\database"
    file_path = os.path.join(save_path,"optiSecData_data.csv") 

    with open(file_path, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(fulldata)

    print(f"Data written to: {file_path}")


    

    return headers, fulldata

if __name__ == "__main__":
    select_fulldata()

#### # Example usage
"""
db = getdb()

query = text("select * from customer")

result = db.execute(query)

customers = result.fetchall()

print(customers)
"""