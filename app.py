# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#
from datetime import datetime

import dateutil.parser
import babel
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from forms import *
# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#
venue_genres = db.Table('venue_genres', db.Column('genre_id', db.Integer, db.ForeignKey('Genre.id'), primary_key=True),
                        db.Column('venue_id', db.Integer, db.ForeignKey('Venue.id'), primary_key=True))


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean(), default=True)
    seeking_description = db.Column(db.String(500), nullable=True)
    genres = db.relationship('Genre', secondary=venue_genres, backref=db.backref('venue_genres', lazy=True))
    show = db.relationship('Show', backref='venue', cascade="all, delete-orphan")

    def __repr__(self):
        return self.name


artist_genres = db.Table('artist_genres',
                         db.Column('genre_id', db.Integer, db.ForeignKey('Genre.id'), primary_key=True),
                         db.Column('artist_id', db.Integer, db.ForeignKey('Artist.id'), primary_key=True))


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean(), default=True)
    seeking_description = db.Column(db.String(500), nullable=True)
    genres = db.relationship('Genre', secondary=artist_genres, backref=db.backref('genres', lazy=True))
    show = db.relationship('Show', backref='artist', cascade="all, delete-orphan")

    def __repr__(self):
        return self.name


class Genre(db.Model):
    __tablename__ = 'Genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    def __repr__(self):
        return self.name


class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.String, nullable=False)


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#
def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#
@app.route('/')
def index():
    return render_template('pages/home.html')


def set_shows(obj):
    """This function takes an object as input and update it by adding extra fields to it"""
    past_shows = []
    upcoming_shows = []
    past_shows_count = 0
    upcoming_shows_count = 0
    for show in obj.show:
        show_time = datetime.strptime(show.start_time, '%Y-%m-%d %H:%M:%S')
        if show_time < datetime.now():
            past_shows_count += 1
            past_shows.append(show)
        else:
            upcoming_shows_count += 1
            upcoming_shows.append(show)
    obj.past_shows = past_shows
    obj.upcoming_shows = upcoming_shows
    obj.past_shows_count = past_shows_count
    obj.upcoming_shows_count = upcoming_shows_count
    return obj


#  Venues
#  ----------------------------------------------------------------
@app.route('/venues')
def venues():
    data = []
    for area in db.session.query(Venue.city, Venue.state).distinct():
        data.append({
            'city': area.city,
            'state': area.state,
            'venues': Venue.query.filter(Venue.city == area.city, Venue.state == area.state)
        })
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term')
    venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%'))
    response = {
        "count": venues.count(),
        "data": [{'id': venue.id, 'name': venue.name} for venue in venues]
    }
    return render_template('pages/search_venues.html', results=response, search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.get(venue_id)
    venue = set_shows(venue)
    return render_template('pages/show_venue.html', venue=venue)


#  Create Venue
#  ----------------------------------------------------------------
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    address = request.form.get('address')
    phone = request.form.get('phone')
    image_link = request.form.get('image_link')
    genres = request.form.getlist('genres')
    website = request.form.get('website')
    facebook_link = request.form.get('facebook_link')
    try:
        venue = Venue(name=name, city=city, state=state, address=address, phone=phone, image_link=image_link,
                      website=website, facebook_link=facebook_link)
        # Loop through every genre in the posted genre list and inserted to the venue genres
        venue.genres = [Genre.query.filter(Genre.name == g).first() for g in genres]
        db.session.add(venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    finally:
        db.session.close()
        return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
        return {}


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    artists = Artist.query.all()
    return render_template('pages/artists.html', artists=artists)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term')
    artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%'))
    response = {
        "count": artists.count(),
        "data": [{'id': artist.id, 'name': artist.name, "num_upcoming_shows": 0} for artist in artists]
    }
    return render_template('pages/search_artists.html', results=response, search_term=search_term)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.get(artist_id)
    artist = set_shows(artist)
    return render_template('pages/show_artist.html', artist=artist)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.get(artist_id)
    form = ArtistForm(obj=artist)
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    artist = Artist.query.get(artist_id)
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    phone = request.form.get('phone')
    genres = request.form.getlist('genres')
    image_link = request.form.get('image_link')
    facebook_link = request.form.get('facebook_link')
    website = request.form.get('website')
    try:
        artist.name = name
        artist.city = city
        artist.state = state
        artist.phone = phone
        # Loop through every genre in the posted genre list and inserted to the artist genres
        artist.genres = [Genre.query.filter(Genre.name == g).first() for g in genres]
        artist.image_link = image_link
        artist.website = website
        artist.facebook_link = facebook_link
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.get(venue_id)
    form = VenueForm(obj=venue)
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    venue = Venue.query.get(venue_id)
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    phone = request.form.get('phone')
    genres = request.form.getlist('genres')
    image_link = request.form.get('image_link')
    facebook_link = request.form.get('facebook_link')
    website = request.form.get('website')
    try:
        venue.name = name
        venue.city = city
        venue.state = state
        venue.phone = phone
        # Loop through every genre in the posted genre list and inserted to the venue genres
        venue.genres = [Genre.query.filter(Genre.name == g).first() for g in genres]
        venue.image_link = image_link
        venue.website = website
        venue.facebook_link = facebook_link
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    phone = request.form.get('phone')
    genres = request.form.getlist('genres')
    facebook_link = request.form.get('facebook_link')
    try:
        artist = Artist(name=name, city=city, state=state, phone=phone, facebook_link=facebook_link)
        # Loop through every genre in the posted genre list and inserted to the artist genres
        artist.genres = [Genre.query.filter(Genre.name == g).first() for g in genres]
        db.session.add(artist)
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        flash('An error occurred. Artist ' + name + ' could not be listed.')
    finally:
        db.session.close()
        return render_template('pages/home.html')


@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
    try:
        artist = Artist.query.get(artist_id)
        db.session.delete(artist)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
        return {}


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    shows = Show.query.all()
    return render_template('pages/shows.html', shows=shows)


@app.route('/shows/create')
def create_shows():
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    artist_id = request.form.get('artist_id')
    venue_id = request.form.get('venue_id')
    start_time = request.form.get('start_time')
    try:
        show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
        db.session.add(show)
        db.session.commit()
        flash('Show was successfully listed!')
    except:
        db.session.rollback()
        flash('An error occurred. Show could not be listed.')
    finally:
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
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
