#!python3
#encoding:utf-8
import os
import os.path
import subprocess
import shlex
import shutil
import time
import pytz
import requests
import json
import datetime
import web.log.Log

class Deleter:
    def __init__(self, db, client, args):
        self.__db = db
        self.__client = client
        self.__args = args
        self.__userRepo = self.__db.Repositories[self.__args.username]
        self.__repo_name = os.path.basename(self.__args.path_dir_pj)

    def ShowDeleteRecords(self):
        repo = self.__userRepo['Repositories'].find_one(Name=self.__repo_name)
        web.log.Log.Log().Logger.info(repo)
        web.log.Log.Log().Logger.info(self.__userRepo['Counts'].find_one(RepositoryId=repo['Id']))
        for record in self.__userRepo['Languages'].find(RepositoryId=repo['Id']):
            web.log.Log.Log().Logger.info(record)

    def Delete(self):
        self.__DeleteLocalRepository()
        self.__client.Repositories.delete()
        self.__DeleteDb()

    def __DeleteLocalRepository(self):
        shutil.rmtree('.git')

    def __DeleteDb(self):
        repo = self.__userRepo['Repositories'].find_one(Name=self.__repo_name)
        self.__userRepo.begin()
        self.__userRepo['Repositories'].delete(Id=repo['Id'])
        self.__userRepo['Counts'].delete(RepositoryId=repo['Id'])
        self.__userRepo['Languages'].delete(RepositoryId=repo['Id'])
        self.__userRepo.commit()

