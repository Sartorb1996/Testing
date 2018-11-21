from sqlalchemy import create_engine,sql,select,MetaData,Table,or_, and_,text

from BarBeerDrinker import config

engine = create_engine(config.database_uri)

def get_bars():
    with engine.connect() as con:
        rs = con.execute("SELECT barname, lic, city, state, phone, address FROM bars;")
        return [dict(row) for row in rs]

def find_bar(name):
    with engine.connect() as con:
        query = sql.text(
            "SELECT barname, lic, city, state, phone, address FROM bars WHERE barname = :name;"
        )
        rs = con.execute(query, name=name)
        result = rs.first()
        if result is None:
            return None
        return dict(result)

def filter_beers(max_price):
    with engine.connect() as con:
        query = sql.text(
            "SELECT * FROM sells WHERE item in (select name from beers) and price < 10;"
        )

        rs = con.execute(query, max_price=max_price)
        results = [dict(row) for row in rs]
        for r in results:
            r['price'] = float(r['price'])
        return results


def get_bar_menu(bar_name):
    with engine.connect() as con:
        query = sql.text(
            'SELECT a.item, a.price, a.manufacturer \
            FROM sells as a \
            WHERE a.barname = :bar\
            ORDER BY manufacturer desc;\
            ')
        rs = con.execute(query, bar=bar_name)
        results = [dict(row) for row in rs]
        for i, _ in enumerate(results):
            results[i]['price'] = float(results[i]['price'])
        return results


def get_bars_selling(beer):
    with engine.connect() as con:
        query = sql.text("""
            SELECT barname,item, price, b.customers
            FROM sells
            JOIN (
                SELECT lic, COUNT(*) AS customers FROM frequents GROUP BY Bar
                  ) as b
            ON lice = b.lic 
            WHERE item = :beer
            ORDER BY price ASC
        
        """)
        rs = con.execute(query, beer=beer)
        results = [dict(row) for row in rs]
        for i, _ in enumerate(results):
            results[i]['price'] = float(results[i]['price'])
        return results


def get_bar_frequent_counts():
    with engine.connect() as con:
        query = sql.text('SELECT Bar, count(*) AS frequentCount \
                FROM frequents \
                GROUP BY Bar; \
            ')
        rs = con.execute(query)
        results = [dict(row) for row in rs]
        return results

def get_frequent_bar(drinker):
    with engine.connect() as con:
        query = sql.text('SELECT DISTINCT Bar FROM Frequents where Drinker = :drinker;')
        rs = con.execute(query, drinker=drinker)
        results = [dict(row) for row in rs]
        return results

def get_bar_cities():
    with engine.connect() as con:
        rs = con.execute('SELECT DISTINCT city FROM bars;')
        return [row['city'] for row in rs]


def get_beers():
    """gets a list of beer names from the beers table."""

    with engine.connect() as con:
        rs = con.execute('SELECT name, manufacturer FROM beers;')
        return [dict(row) for row in rs]


def get_beer_manufacturers(beer):
    with engine.connect() as con:
        if beer is None:
            rs = con.execute('SELECT DISTINCT manufacturer as manf FROM beers;')
            return [row['manf'] for row in rs]

        query = sql.text('SELECT manufacturer as manf FROM beers WHERE name = :beer;')
        rs = con.execute(query, beer=beer)
        result = rs.first()
        if result is None:
            return None
        return result['manf']


def get_drinkers():
    with engine.connect() as con:
        rs = con.execute('SELECT Dname as dname, city, phone, address, state, User_ID as userid FROM Drinkers;')
        return [dict(row) for row in rs]


def get_likes(drinker_name):
    """gets a list of beers liked by the drinker provided."""

    with engine.connect() as con:
        query = sql.text('SELECT beer FROM likes WHERE drinker = :name;')
        rs = con.execute(query, name=drinker_name)
        return [dict(row) for row in rs]


def get_drinker_info(drinker_name):
    with engine.connect() as con:
        query = sql.text('SELECT * FROM Drinkers WHERE DName = :name;')
        rs = con.execute(query, name=drinker_name)
        result = rs.first()
        if result is None:
            return None
        return dict(result)


# for  top drinkers who are largest spenders,

def get_top_spenders(bar_name):
    with engine.connect() as con: 
        query = sql.text(
            'SELECT DName AS drinker, SUM(Gross) AS spent\
             FROM bills \
             WHERE bills.barname = :bar \
             GROUP BY Uid \
             ORDER BY spent DESC \
             Limit 10 \
             ')
        rs = con.execute(query, bar = bar_name)
        results = [dict(row) for row in rs]
        for i, _ in enumerate(results):
            results[i]['spent'] = float(results[i]['spent'])

        return results

# Get Most Popular Beers from a bar

def beers_by_popularity(bar_name):
    with engine.connect() as con:
        query = sql.text("""
            SELECT item, COUNT(item) AS sold

            FROM(
                SELECT item, tid, barname
                FROM (
                SELECT *
                FROM TRANSACTIONS
                WHERE item IN(SELECT name AS item FROM beers)
                 )as beersales
                 JOIN bars ON beersales.license = bars.lic
                 ) AS beerswnames

            WHERE barname = :bar
            GROUP BY item
            ORDER BY sold
        
       ''' )
        rs = con.execute(query, bar=bar_name)
        return [dict(row) for row in rs]

#Get Most Popular Manufacturers

def manufacturers_by_popularity(bar_name):
    with engine.connect() as con:

        query = sql.text("""
        SELECT manufacturer, COUNT(manufacturer) AS sold
        FROM (
            SELECT  name, manufacturer, License,Tid
            FROM(
                SELECT *
                FROM TRANSACTIONS
                WHERE item IN(SELECT name AS item FROM beers)
                ) as beersales
            JOIN beers ON beersales.item = beers.name
            ) AS saleswman
        JOIN bars ON bars.lic = saleswman.License
        WHERE barname = :bar
        GROUP BY manufacturer
        """

                         )
        rs = con.execute(query, bar=bar_name)
        return [dict(row) for row in rs]


# 4 Demonstrate time distribution of sales, show what are the busiest periods of the day
def sales_by_time(bar_name):
    with engine.connect() as con:
        query = sql.expression.text("""
        Select SoldEarly, SoldMid, SoldLate
            From bills
            Join (Select barname, Sum(Gross) as SoldEarly
            From bills
            Where barname = :bar And tim <= 1600
            ) as early on bills.barname = early.barname
        
            Join (Select barname, Sum(Gross) as SoldMid
            From bills
            Where barname = :bard And tim > 1600 And tim <= 2000
            ) as midday on bills.barname = midday.barname
        
            Join (Select barname, Sum(Gross) as SoldLate
            From bills
            Where barname = :bare And tim > 2000
            ) as late on bills.barname = late.barname
        """)

        rs = con.execute(query, bar=bar_name, bare=bar_name, bard=bar_name)
        results = [dict(row) for row in rs]
        for i, _ in enumerate(results):
            results[i]['SoldEarly'] = float(results[i]['SoldEarly'])
            results[i]['SoldMid'] = float(results[i]['SoldMid'])
            results[i]['SoldLate'] = float(results[i]['SoldLate'])
        return results

#Show Busiest Day of the week


def busiest_day_of_the_week(bar_name):
    with engine.connect() as con:
        query = sql.expression.text("""
        SELECT aday, sum(Gross) AS DailyTotal
        FROM bills
        WHERE barname = :bar
        GROUP BY aday
        ORDER BY dat
        """)

        rs = con.execute(query, bar=bar_name)
        results = [dict(row) for row in rs]
        for i, _ in enumerate(results):
            results[i]['DailyTotal'] = float(results[i]['DailyTotal'])



# 1.Given a drinker, show all his/her transactions ordered by time and grouped by different bars

def drinker_transactions(name):
    with engine.connect() as con:
        query = sql.expression.text("""
            SELECT barname, `bills`.`E﻿name` as ename, Gross as gross, Tip as tip, tim, dat
            FROM bills
            WHERE dname = :name
            GROUP BY barname
            ORDER BY tim
        """)

        rs = con.execute(query, name=name)
        results = [dict(row) for row in rs]
        for i, _ in enumerate(results):
            results[i]['gross'] = float(results[i]['gross'])
            results[i]['tip'] = float(results[i]['tip'])
        return results

# Show bar graphs of beers s/he orders the most.
def most_ordered_beers(name):
    with engine.connect() as con:
        query = sql.expression.text("""
            SELECT Item, COUNT(item) AS ordered
            FROM (
                SELECT *
                FROM TRANSACTIONS
                WHERE item IN(SELECT name AS item FROM beers)) AS tab
            WHERE tab.Tid IN (SELECT `bills`.`﻿Trid` FROM bills  WHERE bills.DName = :name)
            GROUP BY item
        """)

        rs = con.execute(query, name=name)
        return [dict(row) for row in rs]


# 3.Drinkers spending in different bars, on different dates/weeks/months

def spending_by_bar(name):
    with engine.connect() as con:
        query = sql.expression.text("""
            SELECT  barname, dat, SUM(Gross) as spent
            FROM bills
            WHERE bills.Dname = :name
            GROUP BY barname,dat
        """)

        rs = con.execute(query, name=name)
        results = [dict(row) for row in rs]
        for i, _ in enumerate(results):
            results[i]['spent'] = float(results[i]['spent'])
        return results

# Show top 10 places where beer sells the most

def top_bars_by_beer(beer):
    with engine.connect() as con:
        query = sql.expression.text("""
            SELECT barname, COUNT(item) AS sold
            FROM(
                SELECT item, tid, barname
                FROM (
                    SELECT *
                    FROM TRANSACTIONS
                    WHERE item IN(SELECT name AS item FROM beers)
                    )as beersales
                JOIN bars ON beersales.license = bars.lic
                    ) AS beerswnames
            WHERE item = :beer
            GROUP BY barname
            
        """)

        rs = con.execute(query, beer=beer)
        return [dict(row) for row in rs]

# 2.show also drinkers who are the biggest consumers of this beer

def biggest_consumers(beer):
    with engine.connect() as con:
        query = sql.expression.text("""
            SELECT Dname , COUNT(Uid) AS bought
            FROM (
                SELECT *
                FROM TRANSACTIONS
                WHERE item IN(SELECT NAME AS item FROM beers)
                 )as beersales
            LEFT JOIN bills ON beersales.Tid = `bills`.`﻿Trid`
            WHERE Item = :beer
            GROUP BY Uid
            ORDER BY bought DESC
            LIMIT 10
        """)

        rs = con.execute(query, beer=beer)
        return [dict(row) for row in rs]

#Time Distribution of Beers Sold

def beer_sales_by_time(beer):
    with engine.connect() as con:
        query = sql.expression.text("""
            Select SoldEarly, SoldMid, SoldLate
            From bills
            Join(
            SELECT tim, COUNT(item) AS soldEarly
             FROM (
             SELECT *
             FROM TRANSACTIONS
             WHERE item IN(SELECT NAME AS item FROM beers)
             )AS beersales
             JOIN bills ON beersales.Tid = `bills`.`﻿Trid`
             WHERE tim <= 1600 AND Item = :beer) as early
             
             Join(
            SELECT tim, COUNT(item) AS soldMid
             FROM (
             SELECT *
             FROM TRANSACTIONS
             WHERE item IN(SELECT NAME AS item FROM beers)
             )AS beersales
             JOIN bills ON beersales.Tid = `bills`.`﻿Trid`
             WHERE tim > 1600 And tim <= 2000 AND Item = :beers) as mid
             
              Join(
            SELECT tim, COUNT(item) AS soldlate
             FROM (
             SELECT *
             FROM TRANSACTIONS
             WHERE item IN(SELECT NAME AS item FROM beers)
             )AS beersales
             JOIN bills ON beersales.Tid = `bills`.`﻿Trid`
             WHERE tim > 2000 AND Item = :beerd) as late
            
            limit 5;
        """)


        rs = con.execute(query, beer=beer, beers=beer, beerd=beer)
        results = [dict(row) for row in rs]

        for i, _ in enumerate(results):
            results[i]['SoldEarly'] = float(results[i]['SoldEarly'])
            results[i]['SoldMid'] = float(results[i]['SoldMid'])
            results[i]['SoldLate'] = float(results[i]['SoldLate'])
        return results













