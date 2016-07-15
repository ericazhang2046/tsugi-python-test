import pymysql
import random
from urllib.parse import urlparse
import urllib
import databaseconfig as CFG
import post as POST
import util as U

inp = input('Test Java, Node or PHP? ')
if inp.lower().startswith('j') :
    url = 'http://localhost:8080/tsugi-servlet/hello'
elif inp.lower().startswith('n') :
    url = 'http://localhost:3000/lti'
else :
    url = 'http://localhost:8888/tsugi/mod/map/index.php'

print('Test URL:',url)

user1 = 'unittest:user:'+str(random.random())
user2 = 'unittest:user:'+str(random.random())
context1 = 'unittest:context:'+str(random.random())
context2 = 'unittest:context:'+str(random.random())
link1 = 'unittest:link:'+str(random.random())
link2 = 'unittest:link:'+str(random.random())
link3 = 'unittest:link:'+str(random.random())

conn = pymysql.connect(host=CFG.host,
                             port=CFG.port,
                             user=CFG.user,
                             password=CFG.password,
                             db=CFG.db,
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

cursor = conn.cursor()

# Clean up old unit test users and contexts
U.cleanunit(conn, cursor)

post = {}
post.update(POST.core)
post.update(POST.inst)
post['resource_link_id'] = link1
post['context_id'] = context1
post['user_id'] = user1

print('Sending a launch with a bad secret... ',end='')
CFG.oauth_secret = 'bad_news'
r = U.launch(CFG,url,post, 302)

redirect = r.headers['Location']
up = urlparse(redirect)
qu = urllib.parse.parse_qs(up.query)
print (qu['lti_errormsg'][0])
# print (qu['detail'][0])


print('Loading secret for',CFG.oauth_consumer_key,'from the database')

sql = 'SELECT secret FROM lti_key WHERE key_key = %s'
cursor.execute(sql, (CFG.oauth_consumer_key, ))
result = cursor.fetchone()
if ( result == None ) :
    print('Unable to load secret for key',CFG.oauth_consumer_key)
    U.abort()
conn.commit()

CFG.oauth_secret = result['secret']

header = {'Content-Type' : 'application/x-www-form-urlencoded'}

print('Sending a launch with a good secret... ',end='')
r = U.launch(CFG,url,post)
U.verifyDb(conn,post)

print('Sending minimal launch to check DB persistence... ',end='')
post = {}
post.update(POST.core)
post['resource_link_id'] = link1
post['context_id'] = context1
post['user_id'] = user1

r = U.launch(CFG,url,post)
U.verifyDb(conn,post)

print('Changing context_title... ',end='')
post['context_title'] = 'Now for something completely dfferent';
r = U.launch(CFG,url,post)
U.verifyDb(conn,post)

print('Changing lis_person_contact_email_primary... ',end='')
post['lis_person_contact_email_primary'] = 'p@p.com';
r = U.launch(CFG,url,post)
U.verifyDb(conn,post)

