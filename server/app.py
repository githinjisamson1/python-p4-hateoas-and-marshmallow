#!/usr/bin/env python3

from flask_marshmallow import Schema as ma
from flask import Flask, request, make_response
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Newsletter

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///newsletters.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

# A Marshmallow instance must be instantiated after our database. The interpreter will throw all sorts of errors if we do it before!
ma = Marshmallow(app)

# Import the necessary components from Flask-Marshmallow

# Define a schema for serializing and deserializing Newsletter model objects


class NewsletterSchema(ma.SQLAlchemySchema):
    # Meta class to associate the schema with the Newsletter model
    class Meta:
        model = Newsletter

    # Fields for serialization and deserialization
    title = ma.auto_field()
    published_at = ma.auto_field()

    # Hyperlinks field for including navigation links in the serialized output
    url = ma.Hyperlinks(
        {
            # "self" link pointing to the route for a specific newsletter by ID
            "self": ma.URLFor("newsletterbyid", values=dict(id="<id>")),
            # "collection" link pointing to the route for all newsletters
            "collection": ma.URLFor("newsletters"),
        }
    )


# Create instances of the schema for single and multiple Newsletter objects
newsletter_schema = NewsletterSchema()
newsletters_schema = NewsletterSchema(many=True)


api = Api(app)


class Index(Resource):

    def get(self):

        response_dict = {
            "index": "Welcome to the Newsletter RESTful API",
        }

        response = make_response(
            response_dict,
            200,
        )

        return response


api.add_resource(Index, '/')


class Newsletters(Resource):

    def get(self):

        # response_dict_list = [n.to_dict() for n in Newsletter.query.all()]
        newsletters = Newsletter.query.all()

        response = make_response(
            # response_dict_list,
            newsletters_schema.dump(newsletters),
            200,
        )

        return response

    def post(self):

        new_record = Newsletter(
            title=request.form['title'],
            body=request.form['body'],
        )

        db.session.add(new_record)
        db.session.commit()

        # response_dict = new_record.to_dict()

        response = make_response(
            # response_dict,
            newsletter_schema.dump(new_record),
            201,
        )

        return response


api.add_resource(Newsletters, '/newsletters')


class NewsletterByID(Resource):

    def get(self, id):

        # response_dict = Newsletter.query.filter_by(id=id).first().to_dict()
        newsletter = Newsletter.query.filter_by(id=id).first()

        response = make_response(
            # response_dict,
            newsletter_schema.dump(newsletter),
            200,
        )

        return response

    def patch(self, id):

        record = Newsletter.query.filter_by(id=id).first()
        for attr in request.form:
            setattr(record, attr, request.form[attr])

        db.session.add(record)
        db.session.commit()

        # response_dict = record.to_dict()

        response = make_response(
            # response_dict,
            newsletter_schema.dump(record),
            200
        )

        return response

    def delete(self, id):

        record = Newsletter.query.filter_by(id=id).first()

        db.session.delete(record)
        db.session.commit()

        response_dict = {"message": "record successfully deleted"}

        response = make_response(
            response_dict,
            200
        )

        return response


api.add_resource(NewsletterByID, '/newsletters/<int:id>')


if __name__ == '__main__':
    app.run(port=5555, debug=True)


'''
In simpler terms, when a client interacts with a RESTful API, the server includes hypermedia links in the response, providing information about other related resources or actions that the client can take. These links enable the client to navigate the application's state without having prior knowledge of the entire API.

Using Marshmallow, our models are serialized after they've been generated. This means that we can remove all of the SQLAlchemy-Serializer code from models.py:

That's it! Marshmallow will require us to modify some code in our app in addition to writing a schema for serialization, but it stays out of our models entirely.

Marshmallow decides how to present the data from your database according to a schema, or blueprint. This is a similar idea to a schema in SQL, but make sure you don't get them confused: a serializer's schema informs a server how to present data. A database schema informs a server how to store data.

A Marshmallow instance must be instantiated after our database. The interpreter will throw all sorts of errors if we do it before!

Instances of this schema can be used to convert Newsletter objects to JSON and vice versa in a Flask application. The hyperlinks provide additional navigation information, following the principles of HATEOAS (Hypermedia as the Engine of Application State).
'''
