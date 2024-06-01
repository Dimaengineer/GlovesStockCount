from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import mysql.connector
import pytz

app = Flask(__name__)

UsersFlows = {}

def OpenDB():
    global DBConnector, DBCursor
    DBConnector = mysql.connector.connect(user='gloves_stock', password='5954Semestr', host='ckhns327.mysql.network', port=10313, database='gloves_stock')
    DBCursor = DBConnector.cursor(buffered=True)

def CloseDB():
    DBCursor.close()
    DBConnector.close()

def SaveInfoToDB(WorkerId, Sort, GloveCount, Machine, Product):
    global UsersFlows
    OpenDB()
    if '1' in Sort:
        UsersFlows[WorkerId]['GlovesCount'][Machine]['FirstSort']+=int(GloveCount)
    elif '2' in Sort:
        UsersFlows[WorkerId]['GlovesCount'][Machine]['SecondSort']+=int(GloveCount)
    elif '3' in Sort:
        UsersFlows[WorkerId]['GlovesCount'][Machine]['DefectSort']+=int(GloveCount)


    DBCursor.execute(f"SELECT MAX(Id) FROM workers_gloves_quantity")
    Id=DBCursor.fetchone()[0]
    Id=Id+1 if Id != None else 0
    DBCursor.execute(f"""INSERT INTO workers_gloves_quantity VALUES ({Id}, {WorkerId}, '{Machine}', '{UsersFlows[WorkerId]['Stage'].replace("'", "''")}', '{Product}', {Sort}, {int(GloveCount)/2}, '{str(datetime.now(pytz.timezone('Europe/Kiev')).strftime("%d.%m.%Y %H:%M"))}')""")

    DBCursor.execute(f"SELECT MAX(Id) FROM products_gloves_quantity")
    Id=DBCursor.fetchone()[0]
    Id=Id+1 if Id != None else 0
    DBCursor.execute(f"SELECT Id FROM products WHERE FullName='{Product}'")
    ProductId=DBCursor.fetchone()[0]
    DBCursor.execute(f"""INSERT INTO products_gloves_quantity VALUES ({Id}, {ProductId}, '{UsersFlows[WorkerId]['Stage'].replace("'", "''")}', '{Machine}', {Sort}, {int(GloveCount)/2}, '{str(datetime.now(pytz.timezone('Europe/Kiev')).strftime("%d.%m.%Y %H:%M"))}')""")

    DBConnector.commit()
    CloseDB()


@app.route('/', methods=['GET', 'POST'])
def WorkerSelect():
    global UsersFlows, AvailableStages
    if request.method == "POST":
        Worker=request.form['Worker']
        OpenDB()
        DBCursor.execute(f"SELECT Stage FROM workers WHERE Name='{Worker}'")
        AvailableStages=[Stage[0] for Stage in DBCursor.fetchall()]
        CloseDB()
        if len(AvailableStages)>1:
            return redirect(f'/{Worker}/stage_select')
        else:
            OpenDB()
            DBCursor.execute(f"""SELECT Id FROM workers WHERE Name='{Worker}' AND Stage='{AvailableStages[0].replace("'", "''")}'""")
            WorkerId=DBCursor.fetchone()[0]
            CloseDB()
            
            if WorkerId not in UsersFlows or 'ShiftStart' not in UsersFlows[WorkerId]:
                UsersFlows[WorkerId]={'Worker':Worker}
                UsersFlows[WorkerId]['Stage'] = AvailableStages[0]

            return redirect(f'/{WorkerId}/worker_log_in')
            
    else:
        OpenDB()
        DBCursor.execute("SELECT Name FROM workers WHERE Exist=True ORDER BY Id DESC")
        Workers = list(set([row[0] for row in DBCursor.fetchall()]))
        CloseDB()
        return render_template('WorkerSelect.html', Workers=Workers)
    


@app.route('/<string:Worker>/stage_select', methods=['GET', 'POST'])
def StageSelect(Worker):
    global UsersFlows
    if request.method == 'POST':
        Stage=request.form['Stage']
        OpenDB()
        DBCursor.execute(f"""SELECT Id FROM workers WHERE Name='{Worker}' AND Stage='{Stage.replace("'", "''")}'""")
        WorkerId=DBCursor.fetchone()[0]
        CloseDB()
        if WorkerId not in UsersFlows or 'ShiftStart' not in UsersFlows[WorkerId]:
            UsersFlows[WorkerId]={'Worker':Worker}
            UsersFlows[WorkerId]['Stage'] = Stage
        return redirect(f'/{WorkerId}/worker_log_in')
    else:
        return render_template('StageSelect.html', AvailableStages=AvailableStages)
    

@app.route('/<int:WorkerId>/worker_log_in', methods=['GET', 'POST'])
def WorkerLogIn(WorkerId):
    global UsersFlows
    if request.method == 'POST':
        WorkerPassword=request.form['WorkerPassword']
        OpenDB()
        DBCursor.execute(f"""SELECT Password FROM workers WHERE Name='{UsersFlows[WorkerId]["Worker"]}' AND Stage='{UsersFlows[WorkerId]['Stage'].replace("'", "''")}'""")
        WorkerTruePassword=DBCursor.fetchone()[0]
        CloseDB()
        if WorkerPassword == WorkerTruePassword:
            if 'ShiftStart' not in UsersFlows[WorkerId]: return redirect(f'/{WorkerId}/shift')
            else: return redirect(f'/{WorkerId}/machine_select')
        else:
            return render_template('WorkerLogIn.html', Worker=UsersFlows[WorkerId]['Worker'], WrongPassword="true")
    else:
        return render_template('WorkerLogIn.html', Worker=UsersFlows[WorkerId]['Worker'], WrongPassword="false")


@app.route('/<int:WorkerId>/shift', methods=['GET', 'POST'])
def Shift(WorkerId):
    if request.method == 'POST':
        if WorkerId not in UsersFlows:
            return redirect(f'/')

        if 'ShiftStart' not in UsersFlows[WorkerId]:
            UsersFlows[WorkerId]['ShiftStart']=datetime.now(pytz.timezone('Europe/Kiev')).strftime("%d.%m.%Y %H:%M")
            UsersFlows[WorkerId]['GlovesCount'] = {}

        return redirect(f'/{WorkerId}/machine_select')
    else:
        return render_template('Shift.html', AddGlovesUrl=f'/{WorkerId}/machine_select', ShiftName=f"{UsersFlows[WorkerId]['Worker']}, {UsersFlows[WorkerId]['Stage']}")


@app.route('/<int:WorkerId>/machine_select', methods=['GET', 'POST'])
def MachineSelect(WorkerId):
    global UsersFlows
    if request.method == 'POST' and request.form['StopShift']=='0':
        Machine=request.form['Machine']
        if WorkerId in UsersFlows:
            return redirect(f'/{WorkerId}/add_gloves/{Machine}')
        else:
            return redirect(f'/')
    elif request.method == 'POST' and request.form['StopShift']=='1':
        if WorkerId in UsersFlows:
            OpenDB()
            Minutes = (datetime.now(pytz.timezone('Europe/Kiev')) - pytz.timezone('Europe/Kiev').localize(datetime.strptime(UsersFlows[WorkerId]['ShiftStart'], "%d.%m.%Y %H:%M"))).total_seconds() / 60
            Hours = int(Minutes // 60)
            Minutes = int(Minutes % 60)
            ShiftsTime = f"{Hours} {'годин' if Hours != 1 else 'година'} {Minutes} {'хвилин' if Minutes != 1 else 'хвилина'}"

            DBCursor.execute(f"SELECT MAX(Id) FROM workers_shifts")
            Id=DBCursor.fetchone()[0]
            Id=Id+1 if Id != None else 0
            DBCursor.execute(f"""INSERT INTO workers_shifts VALUES ({Id}, {WorkerId}, '{UsersFlows[WorkerId]['ShiftStart']}', '{str(datetime.now(pytz.timezone('Europe/Kiev')).strftime("%d.%m.%Y %H:%M"))}', '{ShiftsTime}' )""")
            DBConnector.commit()
            CloseDB()
            UsersFlows[WorkerId]={'Stage':UsersFlows[WorkerId]['Stage'], 'Worker':UsersFlows[WorkerId]['Worker'], '':UsersFlows[WorkerId]}
            return redirect(f'/{WorkerId}/shift')
        else:
            return redirect(f'/')
        
    else:
        OpenDB()
        DBCursor.execute(f"""SELECT Machine FROM plans WHERE Stage='{UsersFlows[WorkerId]['Stage'].replace("'", "''")}' AND Exist=1""")

        Machines=list(map(str, sorted(set(map(lambda Machine: int(Machine[0]), DBCursor.fetchall())))))
        CloseDB()

        return render_template('MachineSelect.html', Machines=Machines, BackUrl=f'/{WorkerId}/shift', ShiftName=f"{UsersFlows[WorkerId]['Worker']}, {UsersFlows[WorkerId]['Stage']}", ShiftStart=UsersFlows[WorkerId]['ShiftStart'])


@app.route('/<int:WorkerId>/add_gloves/<int:Machine>', methods=['GET', 'POST'])
def AddGloves(WorkerId, Machine):
    global UsersFlows
    if request.method == 'POST':
        Sort=request.form['Sort']
        GloveCount=request.form['CountInput']
        if WorkerId in UsersFlows and Machine in UsersFlows[WorkerId]['GlovesCount']:
            OpenDB()
            DBCursor.execute(f"""SELECT Product FROM plans WHERE Machine='{Machine}' AND Stage='{UsersFlows[WorkerId]['Stage'].replace("'", "''")}' AND Exist=True""")
            Product = DBCursor.fetchone()[0]
            CloseDB()
            SaveInfoToDB(WorkerId, Sort, GloveCount, Machine, Product)
            return redirect(f'/{WorkerId}/machine_select')
        elif WorkerId in UsersFlows and Machine not in UsersFlows[WorkerId]['GlovesCount']:
            return redirect(f'/{WorkerId}/machine_select')
        else:
            return redirect(f'/')

    else:
        if Machine not in UsersFlows[WorkerId]['GlovesCount']:
            UsersFlows[WorkerId]['GlovesCount'][Machine] = {'FirstSort': 0, 'SecondSort':0, 'DefectSort':0}

        OpenDB()
        DBCursor.execute(f"""SELECT Product FROM plans WHERE Machine='{Machine}' AND Stage='{UsersFlows[WorkerId]['Stage'].replace("'", "''")}' AND Exist=True""")
        Product = DBCursor.fetchone()
        if Product == None: 
            return redirect(f'/{WorkerId}/machine_select')
        else: 
            Product = Product[0]
            DBCursor.execute(f"""SELECT ShortName FROM products WHERE FullName='{Product}'""")
            Product = DBCursor.fetchone()[0]
        CloseDB()
        ShiftName=f"Зміна ({UsersFlows[WorkerId]['Worker']}, {UsersFlows[WorkerId]['Stage']}, {Machine} машина, {Product})"

        return render_template('AddGloves.html', BackUrl=f'/{WorkerId}/machine_select', ShiftName=ShiftName, FirstSortGloveCount=UsersFlows[WorkerId]['GlovesCount'][Machine]['FirstSort'], SecondSortGloveCount=UsersFlows[WorkerId]['GlovesCount'][Machine]['SecondSort'], DefectSortGloveCount=UsersFlows[WorkerId]['GlovesCount'][Machine]['DefectSort'])

if __name__ == '__main__':
    app.run(debug=True)
