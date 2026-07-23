import pandas as pd
import numpy as np
import random

random.seed(42)
np.random.seed(42)

roles = ["Employee", "Manager", "Admin"]

data = []

for _ in range(1000):

    login_hour = random.randint(0, 23)
    failed_logins = random.randint(0, 10)
    usb_usage = random.randint(0, 1)
    files_accessed = random.randint(1, 200)
    emails_sent = random.randint(0, 80)
    downloads = random.randint(0, 40)
    after_hours = random.randint(0, 1)
    role = random.choice(roles)

    risk = 0

    if (
        failed_logins > 5 or
        usb_usage == 1 or
        downloads > 20 or
        after_hours == 1
    ):
        risk = 1

    data.append([
        login_hour,
        failed_logins,
        usb_usage,
        files_accessed,
        emails_sent,
        downloads,
        after_hours,
        role,
        risk
    ])

columns = [
    "login_hour",
    "failed_logins",
    "usb_usage",
    "files_accessed",
    "emails_sent",
    "downloads",
    "after_hours",
    "role",
    "risk"
]

df = pd.DataFrame(data, columns=columns)

df.to_csv("data/insider_logs.csv", index=False)

print(df.head())

print("\nDataset created successfully!")