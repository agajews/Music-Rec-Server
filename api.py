from flask import Flask
from flask_restful import Resource, Api
from flask_restful import fields, marshal
from flask_restful.reqparse import RequestParser

from neural_models.data.music_recommendator.lib import User, Song
from neural_models.music_recommendator.test_audio_model import \
    setup_test_model, get_user_recs

app = Flask(__name__)
api = Api(app)

user_parser = RequestParser()
user_parser.add_argument('user_id', type=str)
user_parser.add_argument('song_name', type=str, action='append')
user_parser.add_argument('song_artist', type=str, action='append')
user_parser.add_argument('song_id', type=str, action='append')
user_parser.add_argument('play_count', type=str, action='append')

users = {}

model = setup_test_model()


class AddUser(Resource):

    def post(self):

        args = user_parser.parse_args()

        user_id = args['user_id']

        user_songs = []

        for name, artist, song_id, play_count in zip(
                args['song_name'],
                args['song_artist'],
                args['song_id'],
                args['play_count']):

            song = Song(
                name=name,
                artist=artist,
                play_count=play_count,
                song_id=song_id)

            user_songs.append(song)

        user = User(user_id, user_songs)
        users[user_id] = user

        user.add_filenames()
        user.add_wavs()
        user.add_embeddings(model)

        user.recs = get_user_recs(user, model)

        return {'message': 'success'}


song_fields = {
    'song_name': fields.String(),
    'song_artist': fields.String(),
    'exp_play_count': fields.Integer()
}

recs_fields = {
    'recs': fields.List(fields.Nested(song_fields)),
    'message': fields.String()
}


class UserRecs(Resource):

    def get(self, user_id):

        try:
            recs = []
            for song in users[user_id].recs:

                song_data = {}
                song_data['song_name'] = song.name
                song_data['song_artist'] = song.artist
                song_data['exp_play_count'] = song.exp_play_count

                recs.append(song_data)

            res = {}
            res['message'] = 'success'
            res['recs'] = recs

            return marshal(res, recs_fields), 200

        except Exception as e:
            print(e)
            return {'message': 'no user recs yet'}


users_fields = {
    'all_users': fields.List(fields.String())
}


class Users(Resource):

    def get(self):

        try:
            print(users.keys())
            res = {'all_users': list(users.keys())}
            print(res)
            return marshal(res, users_fields), 200
        except Exception as e:
            print(e)

api.add_resource(AddUser, '/adduser')
api.add_resource(Users, '/users')
api.add_resource(UserRecs, '/recs/<string:user_id>')

if __name__ == '__main__':
    app.run(debug=True)
