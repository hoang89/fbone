__author__ = 'hoangnn'
from flask.ext.restful import Resource, reqparse
from .service import ReaderService
from flask import jsonify
import json

class Reader(Resource):

    def __get_put_param(self):
        parser = reqparse.RequestParser()
        parser.add_argument('uuid', type=str, required=True, help='Need pass uuid')
        parser.add_argument('os', type=int, required=True, help='Need pass os')
        parser.add_argument('token', type=str, required=True, help='Need pass token')
        args = parser.parse_args()
        uuid = args['uuid']
        os = args['os']
        token = args['token']
        return uuid, os, token

    def post(self):
        uuid, os, token = self.__get_put_param()
        reader = ReaderService.getOrCreate(uuid=uuid, os=os, token=token)
        return json.loads(reader.to_json())