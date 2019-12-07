import gspread
import serial
import syslog
import time
import datetime
from datetime import date
from oauth2client.service_account import ServiceAccountCredentials

scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("/home/pi/Downloads/rfid-attendance-261305-e0aabaccc7c0.json", scope)
 
client = gspread.authorize(creds)

today = str(date.today())
today = today[5:7] + "/" + today[8:10] + "/" + today[2:4]
now = datetime.datetime.now()
hourValue = int(time.strftime("%H"))
currentTime = (str((hourValue*60) + now.minute))

nameRefSheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1Eo7lmYTZy6hTixuwi1GJEZoH0Cvp-tCk3z0eguBEw08/edit#gid=0").sheet1
timeSchedule = client.open_by_url("https://docs.google.com/spreadsheets/d/1v8u4vsxb2HDqgvsYiqxXnwRaiQvEl9Y2H92VmT7HJdE/edit#gid=0").sheet1
attendSpreadsheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1OQJ36TorR42_jKj57jeh-MVUbXIqCUeUVTT45czdHdg/edit#gid=0")
assignSpreadsheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1bkzdfN-zWP6_Yrb003eBj8sdaSmGgGdNN3Y02GRh024/edit#gid=0")
assignSheet = assignSpreadsheet.get_worksheet(len(assignSpreadsheet.worksheets())-1)
    
try:
    ser=serial.Serial("/dev/ttyACM0",9600)
except:
    ser=serial.Serial("/dev/ttyACM1",9600)
    
def name():
    message = "System Engaged"
    print(message)
    ser.write(message.encode())
    preMsg = ""
    stay = True
    while stay:
        
        msg = ser.readline()
        msg = msg[0:(len(msg)-2)].decode('utf -8')
        print(msg)
        if preMsg != msg:
            
            try:
                cell = nameRefSheet.find(msg)
                name = nameRefSheet.cell(cell.row, cell.col-2).value
                print(name)
                ser.write(name.encode())
                stay = False
            except:
                print("Student not found")
                
        preMsg = msg
    return name
 
def attendance(name):

    sheet = attendSpreadsheet.sheet1
    time.sleep(.5)
    print("Attendance Start")
    
    sheetList = attendSpreadsheet.worksheets()
    skip = True
    for x in sheetList:
        if x.title==today:
            worksheet=x
            skip=False
            break
    if skip:
        worksheet = attendSpreadsheet.duplicate_sheet(sheet.id, len(sheetList), None, today)
        
    nameCell = worksheet.find(name)
    timeCol = 2
    
    for x in range(2,9):
        if (currentTime > (timeSchedule.cell(x,timeCol).value) or currentTime < (timeSchedule.cell(x,timeCol+1).value)):
            if (worksheet.cell(nameCell.row, nameCell.col+1) != ""):
                worksheet.update_cell(nameCell.row, nameCell.col+1,"T")
                break
            else:
                break
        else:
            worksheet.update_cell(nameCell.row, nameCell.col+1,"P")
    return nameCell.row

def assignments(studentY):
        
    sheetList = attendSpreadsheet.worksheets()
    print("Assignments Start")
    sheetLen = len(sheetList)
    lastDay = sheetList[1]
        
    for x in range((sheetLen-2),-1, -1):
        sheet = attendSpreadsheet.get_worksheet(x)
        if(sheet.cell(studentY, 2).value!=""):
            sheet = attendSpreadsheet.get_worksheet(x+1)
            lastDay = sheet.title
            ser.write((lastDay + ". " + today).encode())
            break
    print(lastDay)
    dateRow = assignSheet.find(lastDay).row
    while(assignSheet.cell(dateRow, 2).value != today):
        colVal = 3
        moreLeft = True 
        if (assignSheet.cell(dateRow, colVal).value != ""):
            while moreLeft:
                if (assignSheet.cell(dateRow, colVal).value != ""):
                    print(assignSheet.cell(dateRow, colVal).value)
                    ser.write(("|" + assignSheet.cell(dateRow, colVal).value).encode())
                    time.sleep(2)
                else:
                    moreLeft = False
                colVal = colVal + 1
        dateRow = dateRow + 1

while True:
    assignments(attendance(name()))