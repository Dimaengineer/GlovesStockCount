from flask import Flask, render_template, request, redirect
from datetime import datetime
import mysql.connector
import pytz

app = Flask(__name__)

UsersFlows = {6: {'Stage': "В'язання", 'Worker': 'Вʼячислав', '': {'Worker': 'Вʼячислав', 'Stage': "В'язання", 'ShiftStart': '23.06.2024 19:02', 'GlovesCount': {8: {'FirstSort': 168, 'SecondSort': 0, 'DefectSort': 4}, 4: {'FirstSort': 168, 'SecondSort': 0, 'DefectSort': 0}, 2: {'FirstSort': 168, 'SecondSort': 0, 'DefectSort': 1}, 15: {'FirstSort': 144, 'SecondSort': 0, 'DefectSort': 0}, 13: {'FirstSort': 120, 'SecondSort': 0, 'DefectSort': 0}, 1: {'FirstSort': 168, 'SecondSort': 0, 'DefectSort': 0}, 12: {'FirstSort': 168, 'SecondSort': 0, 'DefectSort': 0}, 5: {'FirstSort': 144, 'SecondSort': 0, 'DefectSort': 0}, 11: {'FirstSort': 120, 'SecondSort': 0, 'DefectSort': 0}, 6: {'FirstSort': 168, 'SecondSort': 0, 'DefectSort': 0}}, 'ShiftId': 80}}, 4: {'Stage': 'ПВХ', 'Worker': 'Полякова Наталія', '': {'Worker': 'Полякова Наталія', 'Stage': 'ПВХ', 'ShiftStart': '25.06.2024 08:14', 'GlovesCount': {(7, 21): {'FirstSort': 0, 'SecondSort': 0, 'DefectSort': 250}, (4, 19): {'FirstSort': 910, 'SecondSort': 0, 'DefectSort': 0}}, 'ShiftId': 85, 'AddedComingProduct': '10кл 20гр Біла', 'ComingProductId': 4}}, 2: {'Stage': "В'язання", 'Worker': 'Карловська Вікторія', '': {'Worker': 'Карловська Вікторія', 'Stage': "В'язання", 'ShiftStart': '24.06.2024 18:49', 'GlovesCount': {8: {'FirstSort': 144, 'SecondSort': 0, 'DefectSort': 0}, 5: {'FirstSort': 120, 'SecondSort': 0, 'DefectSort': 0}, 11: {'FirstSort': 120, 'SecondSort': 0, 'DefectSort': 0}, 2: {'FirstSort': 144, 'SecondSort': 0, 'DefectSort': 0}, 1: {'FirstSort': 120, 'SecondSort': 0, 'DefectSort': 0}, 4: {'FirstSort': 120, 'SecondSort': 0, 'DefectSort': 0}, 12: {'FirstSort': 120, 'SecondSort': 0, 'DefectSort': 0}, 6: {'FirstSort': 144, 'SecondSort': 0, 'DefectSort': 0}, 3: {'FirstSort': 120, 'SecondSort': 0, 'DefectSort': 0}, 13: {'FirstSort': 72, 'SecondSort': 0, 'DefectSort': 0}, 15: {'FirstSort': 96, 'SecondSort': 0, 'DefectSort': 0}, 14: {'FirstSort': 96, 'SecondSort': 0, 'DefectSort': 0}}, 'ShiftId': 83}}, 7: {'Worker': 'Ілона', 'Stage': 'Оверлок', 'ShiftStart': '12.06.2024 08:53', 'GlovesCount': {}, 'ShiftId': 48}, 1: {'Stage': 'Оверлок', 'Worker': 'Карловська Вікторія', '': {'Worker': 'Карловська Вікторія', 'Stage': 'Оверлок', 'ShiftStart': '22.06.2024 17:46', 'GlovesCount': {(0, 36): {'FirstSort': 0, 'SecondSort': 0, 'DefectSort': 0}}, 'ShiftId': 77, 'StartPauseTime': '25.06.2024 19:33'}, 'ShiftStart': '25.06.2024 20:18', 'GlovesCount': {(13, 32): {'FirstSort': 0, 'SecondSort': 12, 'DefectSort': 0}}, 'ShiftId': 87}, 0: {'Worker': 'Стадник Андрій', 'Stage': "В'язання", 'ShiftStart': '25.06.2024 18:57', 'GlovesCount': {}, 'ShiftId': 86}, 5: {'Stage': "В'язання", 'Worker': 'Маріна', '': {'Worker': 'Маріна', 'Stage': "В'язання", 'ShiftStart': '25.06.2024 06:57', 'GlovesCount': {15: {'FirstSort': 120, 'SecondSort': 0, 'DefectSort': 0}, 2: {'FirstSort': 120, 'SecondSort': 0, 'DefectSort': 0}, 3: {'FirstSort': 96, 'SecondSort': 0, 'DefectSort': 0}, 12: {'FirstSort': 96, 'SecondSort': 0, 'DefectSort': 3}, 4: {'FirstSort': 120, 'SecondSort': 2, 'DefectSort': 0}, 13: {'FirstSort': 96, 'SecondSort': 0, 'DefectSort': 0}, 1: {'FirstSort': 72, 'SecondSort': 0, 'DefectSort': 1}, 14: {'FirstSort': 72, 'SecondSort': 2, 'DefectSort': 1}, 11: {'FirstSort': 96, 'SecondSort': 0, 'DefectSort': 0}, 5: {'FirstSort': 72, 'SecondSort': 1, 'DefectSort': 1}, 6: {'FirstSort': 120, 'SecondSort': 0, 'DefectSort': 0}, 8: {'FirstSort': 96, 'SecondSort': 0, 'DefectSort': 0}}, 'ShiftId': 84}}, 8: {'Stage': 'Оверлок', 'Worker': 'Анна', '': {'Worker': 'Анна', 'Stage': 'Оверлок', 'ShiftStart': '14.06.2024 16:02', 'GlovesCount': {}, 'ShiftId': 55}}}

def OpenDB():
    global DBConnector, DBCursor
    DBConnector = mysql.connector.connect(user='gloves_stock', password='5954Semestr', host='ckhns327.mysql.network', port=10313, database='gloves_stock')
    DBCursor = DBConnector.cursor(buffered=True)

def CloseDB():
    DBCursor.close()
    DBConnector.close()

def SaveInfoToDBMachine(WorkerId, Sort, GloveCount, Machine, Product):
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


def SaveInfoToDBProduct(WorkerId, Sort, GloveCount, ComingProductId, ProductId):
    global UsersFlows
    OpenDB()
    if '1' in Sort:
        UsersFlows[WorkerId]['GlovesCount'][(ComingProductId, ProductId)]['FirstSort']+=int(GloveCount)
    elif '2' in Sort:
        UsersFlows[WorkerId]['GlovesCount'][(ComingProductId, ProductId)]['SecondSort']+=int(GloveCount)
    elif '3' in Sort:
        UsersFlows[WorkerId]['GlovesCount'][(ComingProductId, ProductId)]['DefectSort']+=int(GloveCount)


    DBCursor.execute(f"SELECT FullName FROM products WHERE Id='{ProductId}'")
    ProductFullName=DBCursor.fetchone()[0]

    DBCursor.execute(f"SELECT MAX(Id) FROM workers_gloves_quantity")
    Id=DBCursor.fetchone()[0]
    Id=Id+1 if Id != None else 0
    DBCursor.execute(f"""INSERT INTO workers_gloves_quantity VALUES ({Id}, {WorkerId}, '1', '{UsersFlows[WorkerId]['Stage'].replace("'", "''")}', '{ProductFullName}', {Sort}, {int(GloveCount)}, '{str(datetime.now(pytz.timezone('Europe/Kiev')).strftime("%d.%m.%Y %H:%M"))}')""")

    DBCursor.execute(f"SELECT MAX(Id) FROM products_gloves_quantity")
    Id=DBCursor.fetchone()[0]
    Id=Id+1 if Id != None else 0
    DBCursor.execute(f"""INSERT INTO products_gloves_quantity VALUES ({Id}, {ProductId}, '{UsersFlows[WorkerId]['Stage'].replace("'", "''")}', '1', {Sort}, {int(GloveCount)}, '{str(datetime.now(pytz.timezone('Europe/Kiev')).strftime("%d.%m.%Y %H:%M"))}')""")


    # DBCursor.execute(f"SELECT ShortName FROM products WHERE Id='{ComingProductId}'")
    # ComeProductName=DBCursor.fetchone()[0]
    # DBCursor.execute(f"""SELECT Id FROM comings WHERE Product='{ComeProductName}' AND Stage='{UsersFlows[WorkerId]['Stage'].replace("'", "''")}'""")
    # ComeId=DBCursor.fetchone()[0]
    # DBCursor.execute(f"""SELECT Pair FROM comings WHERE Id={ComeId}""")
    # ComePair=DBCursor.fetchone()[0]-int(GloveCount)
    # DBCursor.execute(f"""UPDATE comings SET Pair={ComePair} WHERE Id={ComeId}""")

    # DBCursor.execute(f"SELECT MAX(Id) FROM comings_info")
    # Id=DBCursor.fetchone()[0]
    # Id=Id+1 if Id != None else 0
    # DBCursor.execute(f"""INSERT INTO comings_info VALUES ({Id}, {ComeId}, '{UsersFlows[WorkerId]['Stage'].replace("'", "''")}', '{UsersFlows[WorkerId]['Worker']}', '{ProductFullName}', {int(GloveCount)}, {Sort}, '{str(datetime.now(pytz.timezone('Europe/Kiev')).strftime("%d.%m.%Y %H:%M"))}')""")

    # if ComePair==0:
    #     DBCursor.execute(f"""UPDATE comings SET TimeEnd='{str(datetime.now(pytz.timezone('Europe/Kiev')).strftime("%d.%m.%Y %H:%M"))}' WHERE Id={ComeId}""")
    DBConnector.commit()
    CloseDB()


@app.route('/admin', methods=['GET', 'POST'])
def Admin():
    return str(UsersFlows)


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
        Workers = sorted(list(set([row[0] for row in DBCursor.fetchall()])))
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
            elif UsersFlows[WorkerId]['Stage']=="В'язання": return redirect(f'/{WorkerId}/machine_select')
            else: return redirect(f'/{WorkerId}/coming_product_select')
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

            OpenDB()
            DBCursor.execute(f"SELECT MAX(Id) FROM workers_shifts")
            Id=DBCursor.fetchone()[0]
            Id=Id+1 if Id != None else 0
            UsersFlows[WorkerId]['ShiftId']=Id
            DBCursor.execute(f"""INSERT INTO workers_shifts VALUES ({Id}, {WorkerId}, '{UsersFlows[WorkerId]['ShiftStart']}', '?', '?', '?', '', '0 годин 0 хвилин')""")
            DBConnector.commit()
            CloseDB()

        if UsersFlows[WorkerId]['Stage']=="В'язання":
            return redirect(f'/{WorkerId}/machine_select')
        else:
            return redirect(f'/{WorkerId}/coming_product_select')
    else:
        if WorkerId not in UsersFlows:
            return redirect(f'/')
        
        return render_template('Shift.html', AddGlovesUrl=f'/{WorkerId}/machine_select', ShiftName=f"{UsersFlows[WorkerId]['Worker']}, {UsersFlows[WorkerId]['Stage']}")


@app.route('/<int:WorkerId>/machine_select/', methods=['GET', 'POST'])
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
            DBCursor.execute(f"""SELECT PausesTime FROM workers_shifts WHERE Id = {UsersFlows[WorkerId]['ShiftId']}""")
            PausesTime = DBCursor.fetchone()[0]

            HoursPauses, MinutesPauses = map(int, ShiftsTime.split()[0::2])
            HoursPause, MinutesPause = map(int, PausesTime.split()[0::2])
            
            MinutesPause = MinutesPauses - MinutesPause
            HoursPause = HoursPauses - HoursPause
            if MinutesPause < 0:
                MinutesPause += 60
                HoursPause -= 1

            ActiveShiftTime = f"{HoursPause} годин{'а' if HoursPause == 1 else ''} {MinutesPause} хвилин{'а' if MinutesPause == 1 else ''}"


            DBCursor.execute(f"""UPDATE workers_shifts SET ShiftEnd='{str(datetime.now(pytz.timezone('Europe/Kiev')).strftime("%d.%m.%Y %H:%M"))}', ShiftTime='{ShiftsTime}', ActiveShiftTime='{ActiveShiftTime}' WHERE Id = {UsersFlows[WorkerId]['ShiftId']}""")
            DBConnector.commit()
            CloseDB()
            UsersFlows[WorkerId]={'Stage':UsersFlows[WorkerId]['Stage'], 'Worker':UsersFlows[WorkerId]['Worker'], '':UsersFlows[WorkerId]}
            return redirect(f'/{WorkerId}/shift')
        else:
            return redirect(f'/')
        
    else:
        if WorkerId not in UsersFlows:
            return redirect(f'/')
        
        OpenDB()
        DBCursor.execute(f"""SELECT Machine FROM products_for_machines WHERE Exist=1""")

        Machines=list(map(str, sorted(set(map(lambda Machine: int(Machine[0]), DBCursor.fetchall())))))

        CloseDB()

        return render_template('MachineSelect.html', Machines=Machines, WorkerId=f'/{WorkerId}/', ShiftName=f"{UsersFlows[WorkerId]['Worker']}, {UsersFlows[WorkerId]['Stage']}", ShiftStart=UsersFlows[WorkerId]['ShiftStart'])


@app.route('/<int:WorkerId>/add_gloves/<int:Machine>', methods=['GET', 'POST'])
def AddGloves(WorkerId, Machine):
    global UsersFlows
    if request.method == 'POST':
        Sort=request.form['Sort']
        GloveCount=request.form['CountInput']
        if WorkerId in UsersFlows and Machine in UsersFlows[WorkerId]['GlovesCount']:
            OpenDB()
            DBCursor.execute(f"""SELECT Product FROM products_for_machines WHERE Machine='{Machine}' AND Exist=1""")
            Product = DBCursor.fetchone()[0]
            CloseDB()
            SaveInfoToDBMachine(WorkerId, Sort, GloveCount, Machine, Product)
            return redirect(f'/{WorkerId}/machine_select')
        elif WorkerId in UsersFlows and Machine not in UsersFlows[WorkerId]['GlovesCount']:
            return redirect(f'/{WorkerId}/machine_select')
        else:
            return redirect(f'/')

    else:
        if WorkerId not in UsersFlows:
            return redirect(f'/')
        
        if Machine not in UsersFlows[WorkerId]['GlovesCount']:
            UsersFlows[WorkerId]['GlovesCount'][Machine] = {'FirstSort': 0, 'SecondSort':0, 'DefectSort':0}

        OpenDB()
        DBCursor.execute(f"""SELECT Product FROM products_for_machines WHERE Machine='{Machine}' AND Exist=1""")
        Product = DBCursor.fetchone()
        if Product == None: 
            return redirect(f'/{WorkerId}/machine_select')
        else: 
            Product = Product[0]
            DBCursor.execute(f"""SELECT ShortName FROM products WHERE FullName='{Product}'""")
            Product = DBCursor.fetchone()[0]
        CloseDB()
        ShiftName=f"Зміна ({UsersFlows[WorkerId]['Worker']}, {UsersFlows[WorkerId]['Stage']}, {Machine} машина, {Product})"

        return render_template('AddGlovesByMachine.html', BackUrl=f'/{WorkerId}/machine_select', ShiftName=ShiftName, FirstSortGloveCount=UsersFlows[WorkerId]['GlovesCount'][Machine]['FirstSort'], SecondSortGloveCount=UsersFlows[WorkerId]['GlovesCount'][Machine]['SecondSort'], DefectSortGloveCount=UsersFlows[WorkerId]['GlovesCount'][Machine]['DefectSort'])



@app.route('/<int:WorkerId>/show_products_machine/', methods=['GET', 'POST'])
def ShowProductsMachine(WorkerId):
    global UsersFlows

    if WorkerId not in UsersFlows:
        return redirect(f'/')
    
    CountdownInfo=[]
    for Machine, ProductCount in UsersFlows[WorkerId]['GlovesCount'].items():
        OpenDB()
        DBCursor.execute(f"""SELECT Product FROM products_for_machines WHERE Machine='{Machine}' AND Exist=1""")
        ProductName = DBCursor.fetchone()[0]
        CloseDB()
        for Sort, Count in ProductCount.items():
            if Count != 0:
                CountdownInfo.append((Machine, ProductName, Sort.replace("FirstSort", "1").replace("SecondSort", "2").replace("DefectSort", "3"), Count/2))

    ShiftName=f"Звіт зміни {UsersFlows[WorkerId]['Worker']}, {UsersFlows[WorkerId]['Stage']}"

    return render_template('ShowProductsMachine.html', BackUrl=f'/{WorkerId}/machine_select/', ShiftName=ShiftName, CountdownInfo=CountdownInfo)





@app.route('/<int:WorkerId>/coming_product_select/', methods=['GET', 'POST'])
def ComingProductSelect(WorkerId):
    global UsersFlows
    if request.method == 'POST' and request.form['StopShift']=='0':
        Product=request.form['Product']
        OpenDB()
        DBCursor.execute(f"""SELECT Id FROM products WHERE ShortName = '{Product}'""")
        ProductId = DBCursor.fetchone()[0]

        DBCursor.execute(f"""SELECT Come FROM products WHERE Id = {ProductId}""")
        ComingProductName = DBCursor.fetchone()[0]
        DBCursor.execute(f"""SELECT Id FROM products WHERE FullName = '{ComingProductName}'""")
        ComingProductId = DBCursor.fetchone()[0]

        CloseDB()
        if WorkerId in UsersFlows:
            return redirect(f'/{WorkerId}/add_gloves/{ComingProductId}/{ProductId}/')
        else:
            return redirect(f'/')
    elif request.method == 'POST' and request.form['StopShift']=='1':
        if WorkerId in UsersFlows:
            OpenDB()
            Minutes = (datetime.now(pytz.timezone('Europe/Kiev')) - pytz.timezone('Europe/Kiev').localize(datetime.strptime(UsersFlows[WorkerId]['ShiftStart'], "%d.%m.%Y %H:%M"))).total_seconds() / 60
            Hours = int(Minutes // 60)
            Minutes = int(Minutes % 60)
            ShiftsTime = f"{Hours} {'годин' if Hours != 1 else 'година'} {Minutes} {'хвилин' if Minutes != 1 else 'хвилина'}"
            DBCursor.execute(f"""SELECT PausesTime FROM workers_shifts WHERE Id = {UsersFlows[WorkerId]['ShiftId']}""")
            PausesTime = DBCursor.fetchone()[0]

            HoursPauses, MinutesPauses = map(int, ShiftsTime.split()[0::2])
            HoursPause, MinutesPause = map(int, PausesTime.split()[0::2])
            
            MinutesPause = MinutesPauses - MinutesPause
            HoursPause = HoursPauses - HoursPause
            if MinutesPause < 0:
                MinutesPause += 60
                HoursPause -= 1

            ActiveShiftTime = f"{HoursPause} годин{'а' if HoursPause == 1 else ''} {MinutesPause} хвилин{'а' if MinutesPause == 1 else ''}"


            DBCursor.execute(f"""UPDATE workers_shifts SET ShiftEnd='{str(datetime.now(pytz.timezone('Europe/Kiev')).strftime("%d.%m.%Y %H:%M"))}', ShiftTime='{ShiftsTime}', ActiveShiftTime='{ActiveShiftTime}' WHERE Id = {UsersFlows[WorkerId]['ShiftId']}""")
            DBConnector.commit()
            CloseDB()
            UsersFlows[WorkerId]={'Stage':UsersFlows[WorkerId]['Stage'], 'Worker':UsersFlows[WorkerId]['Worker'], '':UsersFlows[WorkerId]}
            return redirect(f'/{WorkerId}/shift')
        else:
            return redirect(f'/')
        
    else:
        if WorkerId not in UsersFlows:
            return redirect(f'/')
        
        OpenDB()
        # DBCursor.execute(f"""SELECT Product, Pair FROM comings WHERE Stage='{UsersFlows[WorkerId]['Stage'].replace("'", "''")}' AND TimeEnd='?'""")
        # Products=sorted(map(lambda Element: f"{Element[0]} ({int(Element[1])} пар)", DBCursor.fetchall()))

        DBCursor.execute(f"""SELECT ShortName FROM products WHERE Stage='{UsersFlows[WorkerId]['Stage'].replace("'", "''")}'""")
        Products=list(map(lambda Element: f"{Element[0]}", DBCursor.fetchall()))

        CloseDB()

        # return render_template('ComingProductSelect.html', Products=Products, WorkerId=f'/{WorkerId}/', ShiftName=f"{UsersFlows[WorkerId]['Worker']}, {UsersFlows[WorkerId]['Stage']}", ShiftStart=UsersFlows[WorkerId]['ShiftStart'])
        return render_template('ProductSelectTemporametly.html', Products=Products, WorkerId=f'/{WorkerId}/', ShiftName=f"{UsersFlows[WorkerId]['Worker']}, {UsersFlows[WorkerId]['Stage']}", ShiftStart=UsersFlows[WorkerId]['ShiftStart'])



# @app.route('/<int:WorkerId>/product_select/<int:ComingProductId>/', methods=['GET', 'POST'])
# def ProductSelect(WorkerId, ComingProductId):
#     global UsersFlows
#     if request.method == 'POST':
#         Product=request.form['Product']
#         OpenDB()
#         DBCursor.execute(f"""SELECT Id FROM products WHERE ShortName = '{Product}'""")
#         ProductId = DBCursor.fetchone()[0]
#         CloseDB()
#         if WorkerId in UsersFlows:
#             return redirect(f'/{WorkerId}/add_gloves/{ComingProductId}/{ProductId}/')
#         else:
#             return redirect(f'/')
        
#     else:
#         if WorkerId not in UsersFlows:
#             return redirect(f'/')
        
#         OpenDB()
#         DBCursor.execute(f"""SELECT FullName, ShortName FROM products WHERE Id='{ComingProductId}'""")
#         ComingProductFullName, ComingProductShortName = DBCursor.fetchone()

#         DBCursor.execute(f"""SELECT ShortName FROM products WHERE Come='{ComingProductFullName}' AND Stage='{UsersFlows[WorkerId]['Stage'].replace("'", "''")}'""")

#         Products=sorted(map(lambda Element: Element[0], DBCursor.fetchall()))

#         CloseDB()

#         return render_template('ProductSelect.html', Products=Products, BackUrl=f'/{WorkerId}/coming_product_select/', ShiftName=f"{UsersFlows[WorkerId]['Worker']}, {UsersFlows[WorkerId]['Stage']}, {ComingProductShortName}")



@app.route('/<int:WorkerId>/add_gloves/<int:ComingProductId>/<int:ProductId>/', methods=['GET', 'POST'])
def AddGlovesInProduct(WorkerId, ComingProductId, ProductId):
    global UsersFlows
    if request.method == 'POST':
        Sort=request.form['Sort']
        GloveCount=request.form['CountInput']
        if WorkerId in UsersFlows and (ComingProductId, ProductId) in UsersFlows[WorkerId]['GlovesCount']:
            SaveInfoToDBProduct(WorkerId, Sort, GloveCount, ComingProductId, ProductId)
            return redirect(f'/{WorkerId}/coming_product_select')
        elif WorkerId in UsersFlows and (ComingProductId, ProductId) not in UsersFlows[WorkerId]['GlovesCount']:
            return redirect(f'/{WorkerId}/coming_product_select')
        else:
            return redirect(f'/')

    else:
        if WorkerId not in UsersFlows:
            return redirect(f'/')
        
        if (ComingProductId, ProductId) not in UsersFlows[WorkerId]['GlovesCount']:
            UsersFlows[WorkerId]['GlovesCount'][(ComingProductId, ProductId)] = {'FirstSort': 0, 'SecondSort':0, 'DefectSort':0}

        OpenDB()
        DBCursor.execute(f"""SELECT ShortName FROM products WHERE Id={ComingProductId}""")
        ComingProductName = DBCursor.fetchone()[0]
        DBCursor.execute(f"""SELECT ShortName FROM products WHERE Id={ProductId}""")
        ProductName = DBCursor.fetchone()[0]

        # DBCursor.execute(f"""SELECT Pair FROM comings WHERE Product='{ComingProductName}' AND Stage='{UsersFlows[WorkerId]['Stage'].replace("'", "''")}'""")
        # ComingProductCounts = DBCursor.fetchone()[0]
        CloseDB()
        ShiftName=f"Зміна ({UsersFlows[WorkerId]['Worker']}, {UsersFlows[WorkerId]['Stage']}, Прихід {ComingProductName}, {ProductName})"

        # return render_template('AddGlovesByProduct.html', BackUrl=f'/{WorkerId}/product_select/{ComingProductId}/', ShiftName=ShiftName, FirstSortGloveCount=UsersFlows[WorkerId]['GlovesCount'][(ComingProductId, ProductId)]['FirstSort'], SecondSortGloveCount=UsersFlows[WorkerId]['GlovesCount'][(ComingProductId, ProductId)]['SecondSort'], DefectSortGloveCount=UsersFlows[WorkerId]['GlovesCount'][(ComingProductId, ProductId)]['DefectSort'], ComingProductCounts=ComingProductCounts)
        return render_template('AddGlovesByProduct.html', BackUrl=f'/{WorkerId}/coming_product_select/', ShiftName=ShiftName, FirstSortGloveCount=UsersFlows[WorkerId]['GlovesCount'][(ComingProductId, ProductId)]['FirstSort'], SecondSortGloveCount=UsersFlows[WorkerId]['GlovesCount'][(ComingProductId, ProductId)]['SecondSort'], DefectSortGloveCount=UsersFlows[WorkerId]['GlovesCount'][(ComingProductId, ProductId)]['DefectSort'], ComingProductCounts=1000000)


@app.route('/<int:WorkerId>/show_products_product/', methods=['GET', 'POST'])
def ShowProductsProduct(WorkerId):
    global UsersFlows

    if WorkerId not in UsersFlows:
        return redirect(f'/')
    
    CountdownInfo=[]
    for ProductsId, ProductCount in UsersFlows[WorkerId]['GlovesCount'].items():
        OpenDB()
        DBCursor.execute(f"""SELECT ShortName FROM products WHERE Id={ProductsId[0]}""")
        ComingProductName = DBCursor.fetchone()[0]
        DBCursor.execute(f"""SELECT ShortName FROM products WHERE Id={ProductsId[1]}""")
        ProductName = DBCursor.fetchone()[0]
        CloseDB()
        for Sort, Count in ProductCount.items():
            if Count != 0:
                CountdownInfo.append((ComingProductName, ProductName, Sort.replace("FirstSort", "1").replace("SecondSort", "2").replace("DefectSort", "3"), Count))

    ShiftName=f"Звіт зміни {UsersFlows[WorkerId]['Worker']}, {UsersFlows[WorkerId]['Stage']}"

    return render_template('ShowProductsProduct.html', BackUrl=f'/{WorkerId}/coming_product_select/', ShiftName=ShiftName, CountdownInfo=CountdownInfo)



# @app.route('/<int:WorkerId>/add_coming_product/', methods=['GET', 'POST'])
# def ComingProductSet(WorkerId):
#     global UsersFlows
#     if request.method == 'POST':
#         if WorkerId not in UsersFlows:
#             return redirect(f'/')
        
#         UsersFlows[WorkerId]["AddedComingProduct"]=request.form['Product'].replace(" (В'язання)", "").replace(" (ПВХ)", "").replace(" (Оверлок)", "").replace(" (Упаковка)", "")
#         return redirect(f'/{WorkerId}/add_coming_product_count')
#     else:
#         if WorkerId not in UsersFlows:
#             return redirect(f'/')
        
#         OpenDB()
#         DBCursor.execute(f"""SELECT ShortName, Stage FROM products""")
#         Products = list(map(lambda Element: f"{Element[0]} ({Element[1]})", DBCursor.fetchall()))
#         CloseDB()

#         return render_template('ComingProductSet.html', Products=Products, BackUrl=f'/{WorkerId}/coming_product_select', ShiftName=f"{UsersFlows[WorkerId]['Stage']}")


# @app.route('/<int:WorkerId>/add_coming_product_count/', methods=['GET', 'POST'])
# def ComingProductCountSet(WorkerId):
#     global UsersFlows
#     if request.method == 'POST':
#         if WorkerId not in UsersFlows:
#             return redirect(f'/')
        
#         ComingProductCount=int(request.form['products_count_input'])
#         OpenDB()

#         DBCursor.execute(f"""SELECT Product, Stage FROM comings WHERE TimeEnd='?'""")
#         Comings=list(map(lambda Element: (Element[0], Element[1]), DBCursor.fetchall()))

#         if (UsersFlows[WorkerId]["AddedComingProduct"], UsersFlows[WorkerId]['Stage'].replace("'", "''")) not in Comings:
#             DBCursor.execute(f"SELECT MAX(Id) FROM comings")
#             Id=DBCursor.fetchone()[0]
#             Id=Id+1 if Id != None else 0
#             DBCursor.execute(f"""INSERT INTO comings VALUES ({Id}, '{UsersFlows[WorkerId]['Stage'].replace("'", "''")}', '{UsersFlows[WorkerId]["AddedComingProduct"]}', {ComingProductCount}, '{str(datetime.now(pytz.timezone('Europe/Kiev')).strftime("%d.%m.%Y %H:%M"))}', '?')""")
        
#             if ComingProductCount==0:
#                 DBCursor.execute(f"""UPDATE comings SET TimeEnd='{str(datetime.now(pytz.timezone('Europe/Kiev')).strftime("%d.%m.%Y %H:%M"))}' WHERE Id={Id}""")
#         else:
#             DBCursor.execute(f"""SELECT Id FROM comings WHERE Product='{UsersFlows[WorkerId]["AddedComingProduct"]}' AND Stage='{UsersFlows[WorkerId]['Stage'].replace("'", "''")}'""")
#             ComeId=DBCursor.fetchone()[0]
#             DBCursor.execute(f"""SELECT Pair FROM comings WHERE Id={ComeId}""")
#             ComePair=DBCursor.fetchone()[0]+ComingProductCount
#             DBCursor.execute(f"""UPDATE comings SET Pair={ComePair} TimeEnd='?' WHERE Id={ComeId}""")
        
#             if ComePair==0:
#                 DBCursor.execute(f"""UPDATE comings SET TimeEnd='{str(datetime.now(pytz.timezone('Europe/Kiev')).strftime("%d.%m.%Y %H:%M"))}' WHERE Id={ComeId}""")

#         DBConnector.commit()
#         CloseDB()

#         return redirect(f'/{WorkerId}/coming_product_select')
#     else:
#         if WorkerId not in UsersFlows:
#             return redirect(f'/')
        
#         OpenDB()
#         DBCursor.execute(f"""SELECT Id FROM products WHERE ShortName = '{UsersFlows[WorkerId]["AddedComingProduct"]}'""")
#         UsersFlows[WorkerId]["ComingProductId"] = DBCursor.fetchone()[0]
#         CloseDB()

#         return render_template('ComingProductCountSet.html', Product=UsersFlows[WorkerId]["AddedComingProduct"], BackUrl=f'/{WorkerId}/add_coming_product', ShiftName=f"""{UsersFlows[WorkerId]['Stage']}\n{UsersFlows[WorkerId]["AddedComingProduct"]}""")




@app.route('/<int:WorkerId>/pause_shift/', methods=['GET', 'POST'])
def PauseShift(WorkerId):
    global UsersFlows
    if request.method == 'POST':
        if WorkerId in UsersFlows:
            OpenDB()
            DBCursor.execute(f"""SELECT Pauses, PausesTime FROM workers_shifts WHERE Id = {UsersFlows[WorkerId]['ShiftId']}""")
            Pauses, PausesTime = DBCursor.fetchone()
            EndPauseTime=str(datetime.now(pytz.timezone('Europe/Kiev')).strftime("%d.%m.%Y %H:%M"))
            if Pauses=="":
                Pauses=f"{UsersFlows[WorkerId]['StartPauseTime']}-{EndPauseTime}"
            else:
                Pauses+=f", {UsersFlows[WorkerId]['StartPauseTime']}-{EndPauseTime}"

            Minutes = (datetime.strptime(EndPauseTime, "%d.%m.%Y %H:%M") - datetime.strptime(UsersFlows[WorkerId]['StartPauseTime'], "%d.%m.%Y %H:%M")).total_seconds() / 60
            Hours = int(Minutes // 60)
            Minutes = int(Minutes % 60)
            ShiftPauseTime = f"{Hours} {'годин' if Hours != 1 else 'година'} {Minutes} {'хвилин' if Minutes != 1 else 'хвилина'}"
            if PausesTime=="": 
                PausesTime=ShiftPauseTime
            else:
                HoursPauses, MinutesPauses = map(int, PausesTime.split()[0::2])
                HoursPause, MinutesPause = map(int, ShiftPauseTime.split()[0::2])
                
                MinutesPause = MinutesPause + MinutesPauses
                HoursPause = HoursPauses + HoursPause + (MinutesPause // 60)
                MinutesPause %= 60
    
                PausesTime = f"{HoursPause} годин{'а' if HoursPause == 1 else ''} {MinutesPause} хвилин{'а' if MinutesPause == 1 else ''}"

            DBCursor.execute(f"""UPDATE workers_shifts SET Pauses='{Pauses}', PausesTime='{PausesTime}' WHERE Id = {UsersFlows[WorkerId]['ShiftId']}""")
            DBConnector.commit()
            CloseDB()
            if UsersFlows[WorkerId]['Stage']=="В'язання":
                return redirect(f'/{WorkerId}/machine_select/')
            else:
                return redirect(f'/{WorkerId}/coming_product_select/')
        else:
            return redirect(f'/')
    else:
        if WorkerId not in UsersFlows:
            return redirect(f'/')
        UsersFlows[WorkerId]["StartPauseTime"]=str(datetime.now(pytz.timezone('Europe/Kiev')).strftime("%d.%m.%Y %H:%M"))
        return render_template('PauseShift.html', WorkerId=f'/{WorkerId}/', ShiftName=f"{UsersFlows[WorkerId]['Worker']}, {UsersFlows[WorkerId]['Stage']}", ShiftStart=UsersFlows[WorkerId]['ShiftStart'], ShiftStartPause=UsersFlows[WorkerId]['StartPauseTime'])


if __name__ == '__main__':
    app.run(debug=True)
