from amfwx import Database
with Database() as db:
 db.execute('create table t (a text)'); db.execute('insert into t values (?)',('x',)); print(db.one('select * from t')['a'])
