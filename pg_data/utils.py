# import pandas as pd
# from .models import Room
# from datetime import datetime

# def update_db_from_excel(file_path):
#     df = pd.read_excel(file_path, sheet_name=None)  # Read all sheets
#     for sheet, data in df.items():
#         for _, row in data.iterrows():
#             # Handle empty cells properly
#             date_of_joining = None if pd.isna(row.get('Date of Joining')) else datetime.strptime(str(row['Date of Joining']), "%d.%m.%Y")
#             name = None if pd.isna(row.get('Name')) else row['Name']
#             occupied = bool(row.get('Occupied', 0))
#             remarks = None if pd.isna(row.get('Remarks')) else row['Remarks']
            
#             Room.objects.update_or_create(
#                 floor=sheet,
#                 room_number=row['S. No.'], 
#                 bed_number=row['Particulars'],
#                 defaults={
#                     "date_of_joining": date_of_joining,
#                     "name": name,
#                     "occupied": occupied,
#                     "remarks": remarks
#                 }
#             )
