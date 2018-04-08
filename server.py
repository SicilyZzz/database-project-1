#!/usr/bin/env python2.7

"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver

To run locally:

    python server.py

Go to http://localhost:8111 in your browser.

A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

# other library:
import datetime
# import hashlib
from flask import session, flash, url_for

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
# YELP_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'photos')
# YELP_FOLDER = os.path.join('static', '')

app = Flask(__name__, template_folder=tmpl_dir)
# app.config['UPLOAD_FOLDER'] = YELP_FOLDER

#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@35.227.79.146/proj1part2
#
# For example, if you had username gravano and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://gravano:foobar@35.227.79.146/proj1part2"
#
DATABASEURI = "postgresql://mz2655:3940@35.227.79.146/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
# engine.execute("""CREATE TABLE IF NOT EXISTS test (
#   id serial,
#   name text
# );""")
# engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")


@app.before_request
def before_request():
    """
    This function is run at the beginning of every web request 
    (every time you enter an address in the web browser).
    We use it to setup a database connection that can be used throughout the request.

    The variable g is globally accessible.
    """
    try:
        g.conn = engine.connect()
    except:
        print ("uh oh, problem connecting to database")
        import traceback; traceback.print_exc()
        g.conn = None

@app.teardown_request
def teardown_request(exception):
    """
    At the end of the web request, this makes sure to close the database connection.
    If you don't, the database could run out of memory!
    """
    try:
        g.conn.close()
    except Exception as e:
        pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
    """
    request is a special object that Flask provides to access web request information:

    request.method:   "GET" or "POST"
    request.form:     if the browser submitted a form, this contains the data in the form
    request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

    See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
    """

    # DEBUG: this is debugging code to see what request looks like
    print(request.args)


    #
    # example of a database query
    #
    cursor = g.conn.execute("SELECT r_name FROM restaurants LIMIT 10")
    names = []
    for result in cursor:
      names.append(result['r_name'])  # can also be accessed using result[0]
    cursor.close()

    #
    # Flask uses Jinja templates, which is an extension to HTML where you can
    # pass data to a template and dynamically generate HTML based on the data
    # (you can think of it as simple PHP)
    # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
    #
    # You can see an example template in templates/index.html
    #
    # context are the variables that are passed to the template.
    # for example, "data" key in the context variable defined below will be 
    # accessible as a variable in index.html:
    #
    #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
    #     <div>{{data}}</div>
    #     
    #     # creates a <div> tag for each element in data
    #     # will print: 
    #     #
    #     #   <div>grace hopper</div>
    #     #   <div>alan turing</div>
    #     #   <div>ada lovelace</div>
    #     #
    #     {% for n in data %}
    #     <div>{{n}}</div>
    #     {% endfor %}
    #
    username="guest"
    if session.get('logged_in'):
        username=session['u_name']
    
    context = dict(data = names, username=username)


    #
    # render_template looks in the templates/ folder for files.
    # for example, the below file reads template/index.html
    #
    return render_template("index.html", **context)

#
# This is an example of a different path.  You can see it at:
# 
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#
@app.route('/another')
def another():
    return render_template("another.html")


# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
    name = request.form['name']
    #g.conn.execute('INSERT INTO test(name) VALUES (%s)', name)
    return redirect('/')

# Login
@app.route('/login_act', methods=['POST'])
def login_act():
    # abort(401)
    # this_is_never_executed()
    user={}
    user['account'] = request.form['account']
    user['password'] = request.form['password'] 
    cursor = g.conn.execute("SELECT * FROM users WHERE account=\'%(account)s\' AND password=\'%(password)s\'" % user)
    for result in cursor:
        
        session['logged_in']=True
        session['account']=result['account']
        session['uid']=result['uid']
        session['u_name']=result['u_name']
    cursor.close()
    if not session.get('logged_in'):
        flash('wrong username or password')
        return render_template("login.html")
    return redirect('/')
@app.route('/login_page')
def login_page():
    return render_template("login.html")
# Logout
@app.route('/logout_act')
def logout_act():
    # abort(401)
    # this_is_never_executed()
    if session.get('logged_in'):
        session['logged_in']=False
        session['account']=None
        session['uid']=None
        session['u_name']=None
    
    return redirect('/')

# Register
@app.route('/register_act', methods=['POST'])
def register_act():
    user={}
    user['u_name'] = request.form['u_name']
    user['account'] = request.form['account']
    user['password'] = request.form['password']
    conf_pw = request.form['conf_pw']
    user['since']=datetime.datetime.now().strftime("%Y-%m-%d")
    
    # m=hashlib.blake2s()
    # m.update(u_name.encode('utf-8')+str(datetime.datetime.now().isoformat()).encode('utf-8'))
    # uid=m.hexdigest()
    
    uid=user['u_name']
    cursor = g.conn.execute("SELECT COUNT(uid) FROM users")
    for result in cursor:
        uid=int(result[0])+1
    cursor.close()
    user['uid']=str(uid)
    if user['password']!=conf_pw:
        flash('Passwords not match.')
        return render_template("register.html")
        
    else: 
        try:
            g.conn.execute('INSERT INTO users(uid, u_name, account, password, since) VALUES (%(uid)s, %(u_name)s, %(account)s, %(password)s, %(since)s)', user)
        except:
            flash('account exist')
            return render_template("register.html")
    # context = dict(data = [u_name, acc, pw, conf_pw, since, uid]) # show on page
    # return render_template("register.html", **context)
    return redirect('/')
@app.route('/register_page')
def register_page():
    # abort(401)
    # this_is_never_executed()
    return render_template("register.html")
# search restaurnats
@app.route('/search_restaurants_act', methods=['POST'])
def search_restaurants_act():
    
    print(request.args)

    restaurants={}
    # restaurants['r_name'] = request.form['r_name']

    # restaurants['password'] = request.form['password'] 
    
    # print(request.form['noiselevel'])
    results = []
    sql="SELECT * FROM restaurants "
    flag=False
    colnames=['r_name', 'noiselevel']#, 'smoking', 'dogsallowed', 'hastv', 'accepts_credit_cards', 'goodforkids', 'alcohol', 'wifi', 'stars'] # maybe show others in detail page
    
    for col in colnames:
        if col in request.form:
            restaurants[col]=str(request.form[col])
    for col in colnames:
        print(sql)
        if col in restaurants and restaurants[col]!="Not Specified":
            sp=""
            
            if type(restaurants[col])==type(""):
                sp="\'"
            if not flag:
                sql=sql+" WHERE "
                flag=True
                sql=sql+col+"="+sp+restaurants[col]+sp
            else:
                sql=sql+"AND "+col+"="+sp+restaurants[col]+sp
            
    print(restaurants)
    try:
        cursor = g.conn.execute(sql)
        for result in cursor:
            results.append(dict(result))
            # names.append(result['r_name'])  # can also be accessed using result[0]
        cursor.close()
    except:
        flash('error')
        
    # return redirect('/search_restaurants')
    return search_restaurants(results)
    # return render_template("search_restaurants.html", **context)
@app.route('/search_restaurants')
def search_restaurants(results=None):

    username="guest"
    if session.get('logged_in'):
        username=session['u_name']
    
    # context = dict(username=username)
    context = dict(data = results, username=username)

    return render_template("search_restaurants.html", **context)
# show restaurant details
@app.route('/show_restaurant_details')
def show_restaurant_details():
    restaurant={}
    restaurant['rid']=request.args.get('rid')

    username="guest"
    if session.get('logged_in'):
        username=session['u_name']
    
    ###############
    # restaurants #
    ###############

    try:
        cursor = g.conn.execute('SELECT * FROM restaurants WHERE rid=%(rid)s', restaurant)
        for result in cursor:
            restaurant=dict(result)
            # names.append(result['r_name'])  # can also be accessed using result[0]
        cursor.close()
    except:
        flash('error in restaurants')

    ############################
    # restaurants (categories) #
    ############################
    try:
        cursor = g.conn.execute('SELECT style FROM categories WHERE rid=%(rid)s', restaurant)
        restaurant['categories']=[]
        for result in cursor:
            restaurant['categories'].append(result['style'])
            # names.append(result['r_name'])  # can also be accessed using result[0]
        cursor.close()
    except:
        flash('error in restaurants (categories)')
    #########
    # photo #
    #########
    restaurant['has_photo']=[]
    try:
        cursor = g.conn.execute('SELECT pid, caption, label FROM has_photo WHERE rid=%(rid)s', restaurant)
        for result in cursor:
            print(result)
            restaurant['has_photo'].append(dict(result))
            restaurant['has_photo'][-1]['path']="/static/photos/"+str(result['pid'])+".jpg"
            # restaurant['has_photo'][-1]['path']=str(os.path.join(app.config['UPLOAD_FOLDER'], result['pid']+".jpg"))
        cursor.close()
    except:
        flash('error in restaurants (photo)')
    print(restaurant['has_photo'])
    # if len(restaurant['has_photo'])==0:
    #     restaurant['has_photo']=None

    ############################
    # restaurants (location)   #
    ############################
    try:
        cursor = g.conn.execute('SELECT * FROM open_location WHERE rid=%(rid)s', restaurant)
        restaurant['address']=None
        restaurant['postal_code']=None
        for result in cursor:
            restaurant['address']=result['address']
            restaurant['postal_code']=result['postal_code']
        cursor.close()
    except:
        flash('error in restaurants (open_location)')

    try:
        cursor = g.conn.execute('SELECT * FROM location WHERE address=%(address)s AND postal_code=%(postal_code)s', restaurant)
        restaurant['latitude'], restaurant['longitude'], restaurant['city'], restaurant['state']=None, None, None, None
        
        for result in cursor:
            restaurant['latitude'], restaurant['longitude'], restaurant['city'], restaurant['state']=result['latitude'], result['longitude'], result['city'], result['state']
        cursor.close()
    except:
        flash('error in restaurants (location)')
    ############################
    # restaurants (open hours) #
    ############################
    try:
        cursor = g.conn.execute('SELECT * FROM open_hours WHERE rid=%(rid)s', restaurant)
        restaurant['open_hours']={}
        for result in cursor:
            # print(result)
            restaurant['open_hours'][result['day']]={}
            restaurant['open_hours'][result['day']]['open']=result['open'].strftime('%H:%M')
            restaurant['open_hours'][result['day']]['close']=result['close'].strftime('%H:%M')
        cursor.close()
    except:
        flash('error in restaurants (open_hours)')
    for weekday in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
        if weekday not in restaurant['open_hours']:
            restaurant['open_hours'][weekday]={}
            restaurant['open_hours'][weekday]['open']="x"
            restaurant['open_hours'][weekday]['close']="x"
    
    ############################################
    # restaurants (check in/ show peak hours)  #
    ############################################
    try:
        cursor = g.conn.execute('SELECT * FROM checkin WHERE rid=%(rid)s', restaurant)
        restaurant['checkin']={}
        for result in cursor:
            # print(result)
            restaurant['checkin'][result['weekday']]={}
            restaurant['checkin'][result['weekday']][str(result['hour'].strftime('%H'))]=result['counts']
            # print(type(result['hour'].strftime('%H:%M')))
            # print(result['hour'].strftime('%H:%M'))
        cursor.close()
    except:
        flash('error in restaurants (checkin)')

    for weekday in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
        if weekday not in restaurant['checkin']:
            restaurant['checkin'][weekday]={}
            for h in range(24):
                
                h_s=str('{:02d}'.format(int(h)))
                if h_s not in restaurant['checkin'][weekday]:
                    restaurant['checkin'][weekday][h_s]=0
    
    ##########################
    # change None to unknown #
    ##########################

    for k in restaurant.keys():
        if restaurant[k] is None:
            restaurant[k]="Unknown"

    # check categories
    if len(restaurant['categories'])==0:
        restaurant['categories']=None

    ############
    # bookmark #
    ############

    # check bookmark status
    restaurant['is_bookmark']=None
    if session.get('logged_in'):
        sql="SELECT rid FROM bookmarks WHERE uid='"+session['uid']+"' AND rid='"+restaurant['rid']+"'"
        # print(sql)
        try:
            
            cursor = g.conn.execute(sql)
            # reviews[i_review]['is_friend']='-star-empty'
            for result in cursor:
                # print(result)

                # reviews[i_review]['is_friend']='-star'
                restaurant['is_bookmark']=True

                # names.append(result['r_name'])  # can also be accessed using result[0]
            cursor.close()
            # print(reviews[i_review])
        except:
            flash('error in bookmark')

    ########
    # tips #
    ########
    tips=[]
    try:
        cursor = g.conn.execute('SELECT * FROM tip_writes WHERE rid=%(rid)s', restaurant)
        for result in cursor:
            tips.append(dict(result))
            # names.append(result['r_name'])  # can also be accessed using result[0]
        cursor.close()
    except:
        flash('error in reviews')
    

    for i_tip in range(len(tips)):
        # print("get friends info")
        try:
            # print(reviews[i_review])
            cursor = g.conn.execute('SELECT u_name FROM users WHERE uid=%(uid)s', tips[i_tip])
            for result in cursor:
                # print(result)
                tips[i_tip]['u_name']=result['u_name']

                # names.append(result['r_name'])  # can also be accessed using result[0]
            cursor.close()
            tips[i_tip]['is_friend']=None
            
            # print(session.get('logged_in'))
            # print(reviews[i_review])
            if session.get('logged_in'):
                # check friend status
                try:
                    # print(reviews[i_review])
                    sql="SELECT uid_b FROM friends WHERE uid_a='"+session['uid']+"' AND uid_b='"+tips[i_tip]['uid']+"'"
                    # print(sql)
                    cursor = g.conn.execute(sql)
                    # reviews[i_review]['is_friend']='-star-empty'
                    for result in cursor:
                        # print(result)

                        # reviews[i_review]['is_friend']='-star'
                        tips[i_tip]['is_friend']=True

                        # names.append(result['r_name'])  # can also be accessed using result[0]
                    cursor.close()
                    # print(reviews[i_review])
                except:
                    flash('error')
        except:
            flash('error')
    # print(tips)
    
    ###########
    # reviews #
    ###########

    reviews=[]
    try:
        cursor = g.conn.execute('SELECT * FROM reviews WHERE rid=%(rid)s', restaurant)
        for result in cursor:
            reviews.append(dict(result))
            # names.append(result['r_name'])  # can also be accessed using result[0]
        cursor.close()
    except:
        flash('error in reviews')
    

    for i_review in range(len(reviews)):
        # print("get friends info")
        try:
            # print(reviews[i_review])
            cursor = g.conn.execute('SELECT u_name FROM users WHERE uid=%(uid)s', reviews[i_review])
            for result in cursor:
                # print(result)
                reviews[i_review]['u_name']=result['u_name']

                # names.append(result['r_name'])  # can also be accessed using result[0]
            cursor.close()
            reviews[i_review]['is_friend']=None
            
            # print(session.get('logged_in'))
            # print(reviews[i_review])
            if session.get('logged_in'):
                # check friend status
                try:
                    # print(reviews[i_review])
                    sql="SELECT uid_b FROM friends WHERE uid_a='"+session['uid']+"' AND uid_b='"+reviews[i_review]['uid']+"'"
                    # print(sql)
                    cursor = g.conn.execute(sql)
                    # reviews[i_review]['is_friend']='-star-empty'
                    for result in cursor:
                        # print(result)

                        # reviews[i_review]['is_friend']='-star'
                        reviews[i_review]['is_friend']=True

                        # names.append(result['r_name'])  # can also be accessed using result[0]
                    cursor.close()
                    # print(reviews[i_review])
                except:
                    flash('error')
        except:
            flash('error')
    # print(reviews)
    context = dict(data = restaurant, username=username, reviews=reviews, tips=tips, rid=restaurant['rid'])

    return render_template("show_restaurant_detail.html", **context)
# write a review
@app.route('/write_review_act', methods=['POST'])
def write_review_act():
    # print(request.form['review_text'])
    restaurant={}
    # restaurant['rid']=request.args.get('rid')
    restaurant['rid']=request.form['rid']

    username="guest"
    if session.get('logged_in'):
        username=session['u_name']
    else:
        # you cannot write a review without login
        flash('you cannot write a review without login')
        # return render_template("show_restaurant_detail.html", messages={"rid":restaurant['rid']})
        return redirect(url_for('show_restaurant_details', rid=restaurant['rid']))
    review={}
    review['rating']=request.form['rating']
    # print(review)
    review['plaintext']=request.form['review_text']

    review['date']=datetime.datetime.now().strftime("%Y-%m-%d")
    for col in ['useful', 'funny', 'cool']:
        review[col]=0
    review['uid']=session['uid']
    review['rid']=restaurant['rid']
    # print(review)
    try:
        review_id=None
        cursor = g.conn.execute("SELECT COUNT(review_id) FROM reviews")
        for result in cursor:
            review_id=int(result[0])+1
        cursor.close()
        review['review_id']=str(review_id)
        print(review)
        try:
            g.conn.execute('INSERT INTO reviews(review_id, rating, plaintext, useful, funny, cool, date, uid, rid) VALUES (%(review_id)s, %(rating)s, %(plaintext)s, %(useful)s, %(funny)s, %(cool)s, %(date)s, %(uid)s, %(rid)s)', review)
            flash('insert a review successfully')
        except:
            flash('error')
    except:
        flash('error')
    # return render_template("show_restaurant_detail.html", messages={"rid":restaurant['rid']})
    return redirect(url_for('show_restaurant_details', rid=restaurant['rid']))
    # return render_template("show_restaurant_detail.html", messages={"rid":restaurant['rid']})

# write a tip
@app.route('/write_tip_act', methods=['POST'])
def write_tip_act():
    # print(request.form['review_text'])
    restaurant={}
    # restaurant['rid']=request.args.get('rid')
    restaurant['rid']=request.form['rid']

    username="guest"
    if session.get('logged_in'):
        username=session['u_name']
    else:
        # you cannot write a review without login
        flash('you cannot write a tip without login')
        # return render_template("show_restaurant_detail.html", messages={"rid":restaurant['rid']})
        return redirect(url_for('show_restaurant_details', rid=restaurant['rid']))
    tip={}
    
    # print(review)
    tip['t_text']=request.form['t_text']

    tip['t_date']=datetime.datetime.now().strftime("%Y-%m-%d")
    
    tip['uid']=session['uid']
    tip['rid']=restaurant['rid']
    # print(review)
    print(tip)
    try:
        tid=None
        cursor = g.conn.execute("SELECT COUNT(tid) FROM tip_writes")
        for result in cursor:
            tid=int(result[0])+1
        cursor.close()
        tip['tid']=str(tid)
        
        try:
            g.conn.execute('INSERT INTO tip_writes(tid, uid, rid, t_text,t_date) VALUES (%(tid)s, %(uid)s, %(rid)s, %(t_text)s, %(t_date)s)', tip)
            flash('insert a tip successfully')
        except:
            flash('error in getting tid (tips id)')
    except:
        flash('error in get tid')
    # return render_template("show_restaurant_detail.html", messages={"rid":restaurant['rid']})
    return redirect(url_for('show_restaurant_details', rid=restaurant['rid']))
    # return render_template("show_restaurant_detail.html", messages={"rid":restaurant['rid']})

# add bookmark
@app.route('/add_bookmark_act')
def add_bookmark_act():
    username="guest"
    if session.get('logged_in'):
        username=session['u_name']
    else:
        flash('you cannot add a bookmark without login')
        return redirect(url_for('show_restaurant_details', rid=info['rid']))
    info={}
    info['rid']=request.args.get('rid')
    info['uid']=session['uid']
    # print(info)
    try:
        g.conn.execute('INSERT INTO bookmarks(uid, rid) VALUES (%(uid)s, %(rid)s)', info)
        flash('add a bookmark successfully')
    except:
        flash('error')
    # return render_template("show_restaurant_detail.html", messages={"rid":restaurant['rid']})
    return redirect(url_for('show_restaurant_details', rid=info['rid']))
# delete bookmark
# add bookmark
@app.route('/del_bookmark_act')
def del_bookmark_act():
    username="guest"
    if session.get('logged_in'):
        username=session['u_name']
    else:
        flash('you cannot delete a bookmark without login')
        return redirect(url_for('show_restaurant_details', rid=info['rid']))
    info={}
    info['rid']=request.args.get('rid')
    info['uid']=session['uid']
    # print(info)
    try:
        g.conn.execute('DELETE FROM bookmarks WHERE uid=%(uid)s AND rid=%(rid)s)', info)
        flash('delete a bookmark successfully')
    except:
        flash('error')
    # return render_template("show_restaurant_detail.html", messages={"rid":restaurant['rid']})
    return redirect(url_for('show_restaurant_details', rid=info['rid']))
# review useful, funny, cool
@app.route('/review_vote_act')
def review_vote_act():
    # print(request.form['review_text'])
    info={}
    info['review_id']=request.args.get('review_id')
    info['rid']=request.args.get('rid')
    info['vote_type']=request.args.get('vote_type') # useful, funny, cool

    username="guest"
    if session.get('logged_in'):
        username=session['u_name']
    else:
        flash('you cannot add a vote without login')
        return redirect(url_for('show_restaurant_details', rid=info['rid']))
    sql="UPDATE reviews SET "+info['vote_type']+"="+info['vote_type']+"+1 WHERE review_id='"+info['review_id']+"'"
    print(sql)
    try:
        g.conn.execute(sql)
        flash('you add a vote successfully')
    except:
        flash('error')
    # return render_template("show_restaurant_detail.html", messages={"rid":restaurant['rid']})
    return redirect(url_for('show_restaurant_details', rid=info['rid']))

# friend
@app.route('/add_friend_act')
def add_friend_act():
    # print(request.form['review_text'])
    info={}
    info['rid']=request.args.get('rid')
    info['uid']=request.args.get('uid')

    username="guest"
    if session.get('logged_in'):
        username=session['u_name']
    else:
        # you cannot add a friend without login
        flash('you cannot add a friend without login')
        return redirect(url_for('show_restaurant_details', rid=info['rid']))
    friend={}
    friend['uid_a']=session['uid']
    friend['uid_b']=info['uid']
    try:
        g.conn.execute('INSERT INTO friends(uid_a, uid_b) VALUES (%(uid_a)s, %(uid_b)s)', friend)
        
    except:
        flash('error')
    # return render_template("show_restaurant_detail.html", messages={"rid":restaurant['rid']})
    return redirect(url_for('show_restaurant_details', rid=info['rid']))


@app.route('/del_friend_act')
def del_friend_act():
    # print(request.form['review_text'])
    info={}
    info['rid']=request.args.get('rid')
    info['uid']=request.args.get('uid')

    username="guest"
    if session.get('logged_in'):
        username=session['u_name']
    else:
        # you cannot add a friend without login
        flash('you cannot add a friend without login')
        return redirect(url_for('show_restaurant_details', rid=info['rid']))
    friend={}
    friend['uid_a']=session['uid']
    friend['uid_b']=info['uid']
    try:
        g.conn.execute('DELETE FROM friends WHERE uid_a=%(uid_a)s AND uid_b=%(uid_b)s', friend)
        
    except:
        flash('error')
    # return render_template("show_restaurant_detail.html", messages={"rid":restaurant['rid']})
    return redirect(url_for('show_restaurant_details', rid=info['rid']))

# show friend list
@app.route('/show_friend_list')
def show_friend_list():
    info={}
    

    username="guest"
    if session.get('logged_in'):
        username=session['u_name']
    else:
        flash('you should login to view friend list')
        return redirect('login_page')


    info['uid_a']=session['uid']

    friends_uid=[]
    try:
        cursor = g.conn.execute('SELECT uid_b FROM friends WHERE uid_a=%(uid_a)s', info)
        for result in cursor:
            friends_uid.append(dict(result))
            # names.append(result['r_name'])  # can also be accessed using result[0]
        cursor.close()
    except:
        flash('error in select friends')
    friends=[]
    for fuid in friends_uid:
        try:
            cursor = g.conn.execute('SELECT u_name, uid FROM users WHERE uid=%(uid_b)s', fuid)
            for result in cursor:
                friends.append(dict(result))
            cursor.close()
        except:
            flash('error in select user in friends')

    

    
    # print(reviews)
    context = dict(data = friends, username=username)

    return render_template("show_friend_list.html", **context)
# some TODOs

# write tip


if __name__ == "__main__":
    import click

    @click.command()
    @click.option('--debug', is_flag=True)
    @click.option('--threaded', is_flag=True)
    @click.argument('HOST', default='0.0.0.0')
    @click.argument('PORT', default=8111, type=int)
    def run(debug, threaded, host, port):
        """
        This function handles command line parameters.
        Run the server using:

            python server.py

        Show the help text using:

            python server.py --help

        """

        HOST, PORT = host, port
        print("running on %s:%d" % (HOST, PORT))
        app.secret_key = os.urandom(12) # added
        app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


    run()
