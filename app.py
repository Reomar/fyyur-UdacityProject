#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import sys
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy.sql.schema import ForeignKey
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)
migrate = Migrate(compare_type=True)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)))
    image_link = db.Column(db.String(500), server_default='https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/600px-No_image_available.svg.png')
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String())
    seeking_talent = db.Column(db.Boolean, nullable=False, default=True)
    seeking_description = db.Column(db.String())

    # TODO: implement any missing fields, as a database migration using Flask-Migrate ✅


class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)))
    image_link = db.Column(db.String(500), server_default='https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/600px-No_image_available.svg.png')
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String())
    seeking_venues = db.Column(db.Boolean, nullable=False, default=True)
    seeking_description = db.Column(db.String())

    # TODO: implement any missing fields, as a database migration using Flask-Migrate ✅

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.✅


class Shows(db.Model):
    __tablename__ = 'shows'

    # Set columns for Artist id, Venue Id & the start time
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'artists.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey(
        'venues.id'), nullable=False)
    start_time = db.Column(db.DateTime(), nullable=False)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')

#  ----------------------------------------------------------------#
#  Venues
#  ----------------------------------------------------------------#

# Done ✅
@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.

    # query the venues data from the db
    venuesQuery = Venue.query.group_by(Venue.id, Venue.state, Venue.city).all()

    adress = ''
    venuesData = []

    for venue in venuesQuery:

        num_shows = Shows.query.filter(
            Shows.venue_id == venue.id, Shows.start_time > datetime.now()).count()

        dataObject = {
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": num_shows,
        }

        if adress == venue.city + venue.state:
            venuesData[len(venuesData) - 1]['venues'].append(dataObject)
        else:
            adress = venue.city + venue.state
            venueObject = {
                "city": venue.city,
                "state": venue.state,
                "venues": [dataObject]
            }
            venuesData.append(venueObject)

    return render_template('pages/venues.html', areas=venuesData)


# Done ✅
@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

    search_term = request.form.get('search_term')

    # Query the searched term
    venuesSearched = Venue.query.filter(
        Venue.name.ilike(f'%{search_term}%')).all()

    data = {
        'count': len(venuesSearched),
        'data': []
    }
    # Loop through the venues and sepertae its values to dataobject
    for venue in venuesSearched:
        # Get the data of the upcomming shows
        num_shows = Shows.query.filter(
            Shows.venue_id == venue.id, Shows.start_time > datetime.now()).count()

        dataObject = {
            'id': venue.id,
            'name': venue.name,
            'num_upcoming_shows': num_shows
        }
        data['data'].append(dataObject)

    return render_template('pages/search_venues.html', results=data, search_term=request.form.get('search_term'))


# Done ✅
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id✅

    venue = Venue.query.get(venue_id)

    # query the upcomming shows
    futureShows = Shows.query.filter(
        Shows.venue_id == venue_id, Shows.start_time > datetime.now()).all()
    upcommingShows = []
    # Loop through futureShows, & sperate its data to objects
    for show in futureShows:
        # Get the show artist
        showArtist = Artist.query.get(show.artist_id)
        dataObject = {
            "artist_id": show.artist_id,
            "artist_name": showArtist.name,
            "artist_image_link": showArtist.image_link,
            "start_time": str(show.start_time)
        }
        # Add the object to upcomming shows list
        upcommingShows.append(dataObject)

    # query the past shows
    futureShows = Shows.query.filter(
        Shows.venue_id == venue_id, Shows.start_time < datetime.now()).all()
    pastShows = []

    # Loop through futureShows, & sperate its data to objects
    for show in futureShows:
        # Get the show artist
        showArtist = Artist.query.get(show.artist_id)
        dataObject = {
            "artist_id": show.artist_id,
            "artist_name": showArtist.name,
            "artist_image_link": showArtist.image_link,
            "start_time": str(show.start_time)
        }
        # Add the object to past shows list
        pastShows.append(dataObject)

    data = {
        'id': venue.id,
        'name': venue.name,
        'genres': venue.genres,
        'address': venue.address,
        'city': venue.city,
        'state': venue.state,
        'phone': venue.phone,
        'facebook_link': venue.facebook_link,
        'seeking_talent': venue.seeking_talent,
        'seeking_description': venue.seeking_description,
        'image_link': venue.image_link,
        'website': venue.website,
        "past_shows": pastShows,
        "upcoming_shows": upcommingShows,
        "past_shows_count": len(pastShows),
        "upcoming_shows_count": len(upcommingShows),
    }

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
# ---------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


# Done ✅
@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead ✅
    # TODO: modify data to be the data object returned from db insertion✅

    # Extract data from the form
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    genres = request.form.getlist('genres')
    facebook_link = request.form['facebook_link']
    website = request.form['website']
    image_link = request.form['image_link']
    seeking_talent = True if 'seeking_talent' in request.form else False
    seeking_description = request.form['seeking_description']

    # Add the Extracted data the an new venue object
    # and send it to the database
    try:
        newVenue = Venue(name=name,
                         city=city,
                         state=state,
                         address=address,
                         phone=phone,
                         genres=genres,
                         facebook_link=facebook_link,
                         website=website,
                         image_link=image_link,
                         seeking_talent=seeking_talent,
                         seeking_description=seeking_description
                         )
        db.session.add(newVenue)
        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + name + ' was successfully listed!')

    except:
        # Rollback in case of any error occured
        db.session.rollback()
        print(sys.exc_info())

        # TODO: on unsuccessful db insert, flash an error instead.✅
        flash('An error occurred. Venue ' + name + ' could not be listed.')

    finally:
        # End the session
        db.session.close()

    return render_template('pages/home.html')


# Done ✅
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    venue = Venue.query.get(venue_id)

    # Render 404 page if venue not found
    if not venue:
        return render_template('errors/404.html')

    venueName = venue.name

    try:
        db.session.delete(venue)
        db.session.commit()

        # on successful db dellte, flash success
        flash(f'{venueName} was successfully Deleted!')
    except:
        db.session.rollback()
        print(sys.exc_info())

        # on unsuccessful db insert, flash an error instead.
        flash(f'An error occurred. {venueName} could not be deleted.')
    finally:
        db.session.close()

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return render_template('pages/home.html')

# Update venue
# -------------

# Done ✅
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()

    # Query the artist using ID
    venue = Venue.query.get(venue_id)

    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.address.data = venue.address
    form.phone.data = venue.phone
    form.genres.data = venue.genres
    form.facebook_link.data = venue.facebook_link
    form.image_link.data = venue.image_link
    form.website.data = venue.website
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


# Done ✅
@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes

    venue = Venue.query.get(venue_id)

    try:
        venue.name = request.form['name']
        venue.city = request.form['city']
        venue.state = request.form['state']
        venue.address = request.form['address']
        venue.phone = request.form['phone']
        venue.genres = request.form.getlist('genres')
        venue.facebook_link = request.form['facebook_link']
        venue.website = request.form['website']
        venue.image_link = request.form['image_link']
        venue.seeking_talent = True if 'seeking_talent' in request.form else False
        venue.seeking_description = request.form['seeking_description']

        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()

    return redirect(url_for('show_venue', venue_id=venue_id))

# _________________________________________________________________
#  Artists
#  ----------------------------------------------------------------

# Done ✅
@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database

    # Extract Artist data form db
    dbData = Artist.query.all()

    # List that hold Artists objects that will be sent to the front
    artistData = []

    # Loop through the artists , then add the id and name to an object
    for artist in dbData:

        # Object that holds artist's id and name
        dataObject = {}

        dataObject['id'] = artist.id
        dataObject['name'] = artist.name

        # Apend the object to the data list
        artistData.append(dataObject)

    return render_template('pages/artists.html', artists=artistData)


# Done ✅
@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".

    search_term = request.form.get('search_term')

    # Query the searched term
    artistsSearched = Artist.query.filter(
        Artist.name.ilike(f'%{search_term}%')).all()

    data = {
        'count': len(artistsSearched),
        'data': []
    }
    # Loop through the venues and sepertae its values to dataobject
    for artist in artistsSearched:
        # Get the data of the upcomming shows
        num_shows = Shows.query.filter(
            Shows.artist_id == artist.id, Shows.start_time > datetime.now()).count()

        dataObject = {
            'id': artist.id,
            'name': artist.name,
            'num_upcoming_shows': num_shows
        }
        data['data'].append(dataObject)

    return render_template('pages/search_artists.html', results=data, search_term=request.form.get('search_term', ''))


# Done ✅
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id

    artist = Artist.query.get(artist_id)

    # Render 404 Error if artist is not founf
    if not artist:
        return render_template('errors/404.html')

    # query and sperate upccoming shows and past shows
    pastShows = []
    uppcommingShows = []
    shows = Shows.query.filter(Shows.artist_id == artist_id)

    for show in shows:
        venue = Venue.query.get(show.venue_id)
        showsobject = {
            "venue_id": venue.id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": str(show.start_time)
        }
        if show.start_time > datetime.now():
            uppcommingShows.append(showsobject)
        else:
            pastShows.append(showsobject)

    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venues,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": pastShows,
        "upcoming_shows": uppcommingShows,
        "past_shows_count": len(pastShows),
        "upcoming_shows_count": len(uppcommingShows),
    }

    return render_template('pages/show_artist.html', artist=data)

#  Update Artist
#  --------------

# Done ✅
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()

    # Query the artist using ID
    artist = Artist.query.get(artist_id)

    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.genres.data = artist.genres
    form.facebook_link.data = artist.facebook_link
    form.image_link.data = artist.image_link
    form.website.data = artist.website
    form.seeking_venues.data = artist.seeking_venues
    form.seeking_description.data = artist.seeking_description

    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)

# Done ✅
@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    artist = Artist.query.get(artist_id)

    try:
        artist.name = request.form['name']
        artist.city = request.form['city']
        artist.state = request.form['state']
        artist.phone = request.form['phone']
        artist.genres = request.form.getlist('genres')
        artist.facebook_link = request.form['facebook_link']
        artist.image_link = request.form['image_link']
        artist.website = request.form['website']
        artist.seeking_venues = True if 'seeking_venues' in request.form else False
        artist.seeking_description = request.form['seeking_description']

        db.session.commit()
    except:
        db.session.rollback()

    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))

#  Create Artist
#  --------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


# Done ✅
@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead✅
    # TODO: modify data to be the data object returned from db insertion✅

    # Extract data from the form
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    genres = request.form.getlist('genres')
    facebook_link = request.form['facebook_link']
    image_link = request.form['image_link']
    website = request.form['website']
    seeking_venues = True if 'seeking_venues' in request.form else False
    seeking_description = request.form['seeking_description']

    # Add the Extracted data the an new venue object
    # and send it to the database
    try:
        newArtist = Artist(name=name,
                           city=city,
                           state=state,
                           phone=phone,
                           genres=genres,
                           facebook_link=facebook_link,
                           image_link=image_link,
                           website=website,
                           seeking_venues=seeking_venues,
                           seeking_description=seeking_description
                           )
        db.session.add(newArtist)
        db.session.commit()
        # on successful db insert, flash success
        flash(name + ' was successfully Added! 🎉')

    except:
        # Rollback in case of any error occured
        db.session.rollback()
        print(sys.exc_info())

        # TODO: on unsuccessful db insert, flash an error instead.✅
        flash('An error occurred. ' + name + ' could not be Added. 🤷‍♂️')

    finally:
        # End the session
        db.session.close()

    return render_template('pages/home.html')

# ----------------------------------------------------------------
#  Shows
#  ----------------------------------------------------------------

# Done ✅
@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
  
    # List of shows objects that will be sent to the view
    showsList = []

    # Search for all the shows
    shows = Shows.query.order_by('id').all()

    # loop through the shows list to get other data
    for show in shows:
        # Get artist and venues using the IDs that are in the show
        artist = Artist.query.get(show.artist_id)
        venue = Venue.query.get(show.venue_id)

        # Create a new dict to populate the card in the view
        dataObject = {
            'venue_id': show.venue_id,
            'venue_name': venue.name,
            'artist_id': show.artist_id,
            'artist_name': artist.name,
            'artist_image_link': artist.image_link,
            'start_time': str(show.start_time)
        }

        # Add the dataObject to the shows list
        showsList.append(dataObject)

    return render_template('pages/shows.html', shows=showsList)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead✅

    # Extract data from the form
    artist_id = request.form['artist_id']
    venue_id = request.form['venue_id']
    start_time = request.form['start_time']

    try:
        newShow = Shows(artist_id=artist_id,
                        venue_id=venue_id,
                        start_time=start_time
                        )
        db.session.add(newShow)
        db.session.commit()

        # on successful db insert, flash success
        flash('Show was successfully listed! 🎉')

    except:
        # Rollback in case of any error occured
        db.session.rollback()
        print(sys.exc_info())

        # TODO: on unsuccessful db insert, flash an error instead.✅
        flash('An error occurred. Show could not be listed. 😥')

    finally:
        # End the session
        db.session.close()

    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
