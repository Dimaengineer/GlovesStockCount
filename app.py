from flask import Flask, render_template, request, redirect
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


    DBCursor.execute(f"SELECT ShortName FROM products WHERE Id='{ComingProductId}'")
    ComeProductName=DBCursor.fetchone()[0]
    DBCursor.execute(f"""SELECT Id FROM comings WHERE Product='{ComeProductName}' AND Stage='{UsersFlows[WorkerId]['Stage'].replace("'", "''")}'""")
    ComeId=DBCursor.fetchone()[0]
    DBCursor.execute(f"""SELECT Pair FROM comings WHERE Id={ComeId}""")
    ComePair=DBCursor.fetchone()[0]-int(GloveCount)
    DBCursor.execute(f"""UPDATE comings SET Pair={ComePair} WHERE Id={ComeId}""")

    DBCursor.execute(f"SELECT MAX(Id) FROM comings_info")
    Id=DBCursor.fetchone()[0]
    Id=Id+1 if Id != None else 0
    DBCursor.execute(f"""INSERT INTO comings_info VALUES ({Id}, {ComeId}, '{UsersFlows[WorkerId]['Stage'].replace("'", "''")}', '{UsersFlows[WorkerId]['Worker']}', '{ProductFullName}', {int(GloveCount)}, {Sort}, '{str(datetime.now(pytz.timezone('Europe/Kiev')).strftime("%d.%m.%Y %H:%M"))}')""")

    if ComePair==0:
        DBCursor.execute(f"""UPDATE comings SET TimeEnd='{str(datetime.now(pytz.timezone('Europe/Kiev')).strftime("%d.%m.%Y %H:%M"))}' WHERE Id={ComeId}""")
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
            DBCursor.execute(f"""INSERT INTO workers_shifts VALUES ({Id}, {WorkerId}, '{UsersFlows[WorkerId]['ShiftStart']}', '?', '?' )""")
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

            DBCursor.execute(f"""UPDATE workers_shifts SET ShiftEnd='{str(datetime.now(pytz.timezone('Europe/Kiev')).strftime("%d.%m.%Y %H:%M"))}', ShiftTime='{ShiftsTime}' WHERE Id = {UsersFlows[WorkerId]['ShiftId']}""")
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
        Product=(Product[:Product.find(' (')] + Product[Product.find(')')+1:]).strip()
        OpenDB()
        DBCursor.execute(f"""SELECT Id FROM products WHERE ShortName = '{Product}'""")
        ProductId = DBCursor.fetchone()[0]
        CloseDB()
        if WorkerId in UsersFlows:
            return redirect(f'/{WorkerId}/product_select/{ProductId}')
        else:
            return redirect(f'/')
    elif request.method == 'POST' and request.form['StopShift']=='1':
        if WorkerId in UsersFlows:
            OpenDB()
            Minutes = (datetime.now(pytz.timezone('Europe/Kiev')) - pytz.timezone('Europe/Kiev').localize(datetime.strptime(UsersFlows[WorkerId]['ShiftStart'], "%d.%m.%Y %H:%M"))).total_seconds() / 60
            Hours = int(Minutes // 60)
            Minutes = int(Minutes % 60)
            ShiftsTime = f"{Hours} {'годин' if Hours != 1 else 'година'} {Minutes} {'хвилин' if Minutes != 1 else 'хвилина'}"

            DBCursor.execute(f"""UPDATE workers_shifts SET ShiftEnd='{str(datetime.now(pytz.timezone('Europe/Kiev')).strftime("%d.%m.%Y %H:%M"))}', ShiftTime='{ShiftsTime}' WHERE Id = {UsersFlows[WorkerId]['ShiftId']}""")
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
        DBCursor.execute(f"""SELECT Product, Pair FROM comings WHERE Stage='{UsersFlows[WorkerId]['Stage'].replace("'", "''")}' AND TimeEnd='?'""")

        Products=sorted(map(lambda Element: f"{Element[0]} ({int(Element[1])} пар)", DBCursor.fetchall()))

        CloseDB()

        return render_template('ComingProductSelect.html', Products=Products, WorkerId=f'/{WorkerId}/', ShiftName=f"{UsersFlows[WorkerId]['Worker']}, {UsersFlows[WorkerId]['Stage']}", ShiftStart=UsersFlows[WorkerId]['ShiftStart'])



@app.route('/<int:WorkerId>/product_select/<int:ComingProductId>/', methods=['GET', 'POST'])
def ProductSelect(WorkerId, ComingProductId):
    global UsersFlows
    if request.method == 'POST':
        Product=request.form['Product']
        OpenDB()
        DBCursor.execute(f"""SELECT Id FROM products WHERE ShortName = '{Product}'""")
        ProductId = DBCursor.fetchone()[0]
        CloseDB()
        if WorkerId in UsersFlows:
            return redirect(f'/{WorkerId}/add_gloves/{ComingProductId}/{ProductId}/')
        else:
            return redirect(f'/')
        
    else:
        if WorkerId not in UsersFlows:
            return redirect(f'/')
        
        OpenDB()
        DBCursor.execute(f"""SELECT FullName, ShortName FROM products WHERE Id='{ComingProductId}'""")
        ComingProductFullName, ComingProductShortName = DBCursor.fetchone()

        DBCursor.execute(f"""SELECT ShortName FROM products WHERE Come='{ComingProductFullName}' AND Stage='{UsersFlows[WorkerId]['Stage'].replace("'", "''")}'""")

        Products=sorted(map(lambda Element: Element[0], DBCursor.fetchall()))

        CloseDB()

        return render_template('ProductSelect.html', Products=Products, BackUrl=f'/{WorkerId}/coming_product_select/', ShiftName=f"{UsersFlows[WorkerId]['Worker']}, {UsersFlows[WorkerId]['Stage']}, {ComingProductShortName}")



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
        if (ComingProductId, ProductId) not in UsersFlows[WorkerId]['GlovesCount']:
            UsersFlows[WorkerId]['GlovesCount'][(ComingProductId, ProductId)] = {'FirstSort': 0, 'SecondSort':0, 'DefectSort':0}

        OpenDB()
        DBCursor.execute(f"""SELECT ShortName FROM products WHERE Id={ComingProductId}""")
        ComingProductName = DBCursor.fetchone()[0]
        DBCursor.execute(f"""SELECT ShortName FROM products WHERE Id={ProductId}""")
        ProductName = DBCursor.fetchone()[0]

        DBCursor.execute(f"""SELECT Pair FROM comings WHERE Product='{ComingProductName}' AND Stage='{UsersFlows[WorkerId]['Stage'].replace("'", "''")}'""")
        ComingProductCounts = DBCursor.fetchone()[0]
        CloseDB()
        ShiftName=f"Зміна ({UsersFlows[WorkerId]['Worker']}, {UsersFlows[WorkerId]['Stage']}, Прихід {ComingProductName}, {ProductName})"

        return render_template('AddGlovesByProduct.html', BackUrl=f'/{WorkerId}/product_select/{ComingProductId}/', ShiftName=ShiftName, FirstSortGloveCount=UsersFlows[WorkerId]['GlovesCount'][(ComingProductId, ProductId)]['FirstSort'], SecondSortGloveCount=UsersFlows[WorkerId]['GlovesCount'][(ComingProductId, ProductId)]['SecondSort'], DefectSortGloveCount=UsersFlows[WorkerId]['GlovesCount'][(ComingProductId, ProductId)]['DefectSort'], ComingProductCounts=ComingProductCounts)


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



@app.route('/<int:WorkerId>/add_coming_product/', methods=['GET', 'POST'])
def ComingProductSet(WorkerId):
    global UsersFlows
    if request.method == 'POST':
        if WorkerId not in UsersFlows:
            return redirect(f'/')
        
        UsersFlows[WorkerId]["AddedComingProduct"]=request.form['Product'].replace(" (В'язання)", "").replace(" (ПВХ)", "").replace(" (Оверлок)", "").replace(" (Упаковка)", "")
        return redirect(f'/{WorkerId}/add_coming_product_count')
    else:
        if WorkerId not in UsersFlows:
            return redirect(f'/')
        
        OpenDB()
        DBCursor.execute(f"""SELECT ShortName, Stage FROM products""")
        Products = list(map(lambda Element: f"{Element[0]} ({Element[1]})", DBCursor.fetchall()))
        CloseDB()

        return render_template('ComingProductSet.html', Products=Products, BackUrl=f'/{WorkerId}/coming_product_select', ShiftName=f"{UsersFlows[WorkerId]['Stage']}")


@app.route('/<int:WorkerId>/add_coming_product_count/', methods=['GET', 'POST'])
def ComingProductCountSet(WorkerId):
    global UsersFlows
    if request.method == 'POST':
        if WorkerId not in UsersFlows:
            return redirect(f'/')
        
        ComingProductCount=int(request.form['products_count_input'])
        OpenDB()

        DBCursor.execute(f"""SELECT Product, Stage FROM comings""")
        Comings=list(map(lambda Element: (Element[0], Element[1]), DBCursor.fetchall()))

        if (UsersFlows[WorkerId]["AddedComingProduct"], UsersFlows[WorkerId]['Stage'].replace("'", "''")) not in Comings:
            DBCursor.execute(f"SELECT MAX(Id) FROM comings")
            Id=DBCursor.fetchone()[0]
            Id=Id+1 if Id != None else 0
            DBCursor.execute(f"""INSERT INTO comings VALUES ({Id}, '{UsersFlows[WorkerId]['Stage'].replace("'", "''")}', '{UsersFlows[WorkerId]["AddedComingProduct"]}', {ComingProductCount}, '{str(datetime.now(pytz.timezone('Europe/Kiev')).strftime("%d.%m.%Y %H:%M"))}', '?')""")
        
            if ComingProductCount==0:
                DBCursor.execute(f"""UPDATE comings SET TimeEnd='{str(datetime.now(pytz.timezone('Europe/Kiev')).strftime("%d.%m.%Y %H:%M"))}' WHERE Id={Id}""")
        else:
            DBCursor.execute(f"""SELECT Id FROM comings WHERE Product='{UsersFlows[WorkerId]["AddedComingProduct"]}' AND Stage='{UsersFlows[WorkerId]['Stage'].replace("'", "''")}'""")
            ComeId=DBCursor.fetchone()[0]
            DBCursor.execute(f"""SELECT Pair FROM comings WHERE Id={ComeId}""")
            ComePair=DBCursor.fetchone()[0]+ComingProductCount
            DBCursor.execute(f"""UPDATE comings SET Pair={ComePair} WHERE Id={ComeId}""")
        
            if ComePair==0:
                DBCursor.execute(f"""UPDATE comings SET TimeEnd='{str(datetime.now(pytz.timezone('Europe/Kiev')).strftime("%d.%m.%Y %H:%M"))}' WHERE Id={ComeId}""")

        DBConnector.commit()
        CloseDB()

        return redirect(f'/{WorkerId}/coming_product_select')
    else:
        if WorkerId not in UsersFlows:
            return redirect(f'/')
        
        OpenDB()
        DBCursor.execute(f"""SELECT Id FROM products WHERE ShortName = '{UsersFlows[WorkerId]["AddedComingProduct"]}'""")
        UsersFlows[WorkerId]["ComingProductId"] = DBCursor.fetchone()[0]
        CloseDB()

        return render_template('ComingProductCountSet.html', Product=UsersFlows[WorkerId]["AddedComingProduct"], BackUrl=f'/{WorkerId}/add_coming_product', ShiftName=f"""{UsersFlows[WorkerId]['Stage']}\n{UsersFlows[WorkerId]["AddedComingProduct"]}""")



if __name__ == '__main__':
    app.run(debug=True)
