#!python3
#encoding:utf-8
import os.path
import subprocess
import shlex
import re
import datetime
import dataset
import database.src.Database
from web.service.github.api.v3.authentication.BasicAuthentication import BasicAuthentication
from web.service.github.api.v3.authentication.TwoFactorAuthentication import TwoFactorAuthentication
from web.service.github.api.v3.authentication.OAuthAuthentication import OAuthAuthentication
import web.service.github.api.v3.Client
import web.sqlite.Json2Sqlite
import cui.register.SshConfigurator
import cui.register.command.ASubCommand
import web.log.Log
import cui.register.SshKeyGen
class Inserter(cui.register.command.ASubCommand.ASubCommand):
    def __init__(self, path_dir_root):
        self.__path_dir_root = path_dir_root
        self.__j2s = web.sqlite.Json2Sqlite.Json2Sqlite()
        self.__db = None
        self.__sshkeygen = cui.register.SshKeyGen.SshKeyGen()

    def Run(self, args):
        web.log.Log.Log().Logger.debug('Account.Insert')
        web.log.Log.Log().Logger.debug(args)
        web.log.Log.Log().Logger.debug('-u: {0}'.format(args.username))
        web.log.Log.Log().Logger.debug('-p: {0}'.format(args.password))
        web.log.Log.Log().Logger.debug('-s: {0}'.format(args.ssh_host))
        web.log.Log.Log().Logger.debug('-t: {0}'.format(args.two_factor_secret_key))
        web.log.Log.Log().Logger.debug('-r: {0}'.format(args.two_factor_recovery_code_file_path))
        web.log.Log.Log().Logger.debug('--auto: {0}'.format(args.auto))

        self.__db = database.src.Database.Database(self.__path_dir_root)
        self.__db.Initialize()
        
        account = self.__db.Accounts['Accounts'].find_one(Username=args.username)
        web.log.Log.Log().Logger.debug(account)
        
        if None is account:
            authentications = []
            if None is not args.two_factor_secret_key:
                authentications.append(TwoFactorAuthentication(args.username, args.password, args.two_factor_secret_key))
            else:
                authentications.append(BasicAuthentication(args.username, args.password))
            client = web.service.github.api.v3.Client.Client(self.__db, authentications)
            # 1. Tokenの新規作成
            token = client.Authorizations.Create(scopes=['repo', 'delete_repo', 'user', 'admin:public_key'], note='GitHubUserRegister.py {0}'.format('{0:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())))
            # 2. APIでメールアドレスを習得する。https://developer.github.com/v3/users/emails/
            mailaddress = self.__GetPrimaryMail(client)
            # 3. SSHの生成と設定
            # 起動引数`-s`がないなら
            if None is args.ssh_host:
                # 3A-1. SSH鍵の新規作成
                ssh_key_gen_params = self.__SshKeyGen(args.username, mailaddress)
                sshconf = cui.register.SshConfigurator.SshConfigurator()
                sshconf.Load()
                host = sshconf.AppendHost(args.username, ssh_key_gen_params['path_file_key_private'])
                # 3A-2. SSH鍵をGitHubに登録してDBに挿入する
                j_ssh = client.SshKeys.Create(ssh_key_gen_params['public_key'], title=mailaddress)
                web.log.Log.Log().Logger.debug(j_ssh)                
                # 3A-3. SSH接続確認
                self.__sshkeygen.CheckSshConnect(host, args.username)
            else:
                # 3B-1. ~/.ssh/configから指定されたHostデータを取得する
                sshconf = cui.register.SshConfigurator.SshConfigurator()
                sshconf.Load()
                if not(args.ssh_host in sshconf.Hosts.keys()):
                    raise Exception('存在しないSSH Host名が指定されました。-s引数を指定しなければSSH鍵を新規作成して設定します。既存のSSH鍵を使用するなら~/.ssh/configファイルに設定すると自動で読み取ります。configファイルに設定済みのHost名は次の通りです。 {0}'.format(sshconf.Hosts.keys()))
                host = args.ssh_host
                ssh_key_gen_params = self.__LoadSshKeyFile(args, sshconf)                
                # 3B-2.GitHubのSSHにすでに設定されているか確認する
                j_ssh = self.__GetGitHubSsh(client, args.username, mailaddress, ssh_key_gen_params['public_key'])
            # 4. 全部成功したらDBにアカウントを登録する
            self.__db.Accounts['Accounts'].insert(self.__CreateRecordAccount(args, mailaddress))
            account = self.__db.Accounts['Accounts'].find_one(Username=args.username)
            web.log.Log.Log().Logger.debug(account)
            if None is not args.two_factor_secret_key:
                self.__db.Accounts['TwoFactors'].insert(self.__CreateRecordTwoFactor(account['Id'], args))
            self.__db.Accounts['AccessTokens'].insert(self.__CreateRecordToken(account['Id'], token, j_ssh['id']))
            self.__db.Accounts['SshConfigures'].insert(self.__CreateRecordSshConfigures(account['Id'], host, ssh_key_gen_params))
            self.__db.Accounts['SshKeys'].insert(self.__CreateRecordSshKeys(account['Id'], ssh_key_gen_params['private_key'], ssh_key_gen_params['public_key'], j_ssh))
        # 作成したアカウントのリポジトリDB作成や、作成にTokenが必要なライセンスDBの作成
        self.__db.Initialize()
        return self.__db

    def __GetPrimaryMail(self, client):
        mails = client.Emails.Gets()
        web.log.Log.Log().Logger.debug(mails)
        for mail in mails:
            if mail['primary']:
                return mail['email']
                
    def __LoadSshKeyFile(self, args, sshconf):
        ssh_key_gen_params = {
            'type': None,
            'bits': None,
            'passphrase': None,
            'path_file_key_private': None,
            'path_file_key_public': None,
            'private_key': None,
            'public_key': None,
        }
        path_file_key_private = sshconf.GetPrivateKeyFilePath(args.ssh_host)
        path_file_key_public = sshconf.GetPublicKeyFilePath(args.ssh_host)
        ssh_key_gen_params.update({'path_file_key_public': os.path.expanduser(path_file_key_public)})
        ssh_key_gen_params.update({'path_file_key_private': os.path.expanduser(path_file_key_private)})
        web.log.Log.Log().Logger.debug(ssh_key_gen_params['path_file_key_private'])
        web.log.Log.Log().Logger.debug(ssh_key_gen_params['path_file_key_public'])
        # キーファイルから内容を読み取る
        with open(ssh_key_gen_params['path_file_key_private']) as f:
            ssh_key_gen_params['private_key'] = f.read()
        with open(ssh_key_gen_params['path_file_key_public']) as f:
            # 公開鍵ファイルはスペース区切りで`{ssh-rsa} {公開鍵} {コメント}`の形式になっている。
            # GitHubではコメント値は保持しない。よって`{ssh-rsa} {公開鍵}`の部分だけ渡す
            pub_keys = f.read().split()
            ssh_key_gen_params['public_key'] = pub_keys[0] + ' ' + pub_keys[1]
        
        # 暗号化強度の情報を取得する
        ssh_key_gen_params.update(self.__sshkeygen.GetTypeAndBit(ssh_key_gen_params['path_file_key_private']))
        web.log.Log.Log().Logger.debug(ssh_key_gen_params)
        return ssh_key_gen_params
    
    """
    GitHubにしたSSH設定を取得する。まだ無いなら設定する。
    """
    def __GetGitHubSsh(self, client, username, mailaddress, public_key):
        j_sshs = client.SshKeys.Gets(username)
        web.log.Log.Log().Logger.debug(j_sshs)
        j_sshkey = None
        for j in j_sshs:
            if j['key'] == public_key:
                j_sshkey = j
                web.log.Log.Log().Logger.debug('一致一致一致一致一致一致一致一致一致一致一致一致一致')
                break
        j_ssh = None
        if None is j_sshkey:
            # 新規作成
            web.log.Log.Log().Logger.debug('新規作成新規作成新規作成新規作成新規作成新規作成新規作成新規作成新規作成新規作成')
            j_ssh = client.SshKeys.Create(public_key, title=mailaddress)
        else:
            # 詳細情報取得
            web.log.Log.Log().Logger.debug('詳細情報取得詳細情報取得詳細情報取得詳細情報取得詳細情報取得詳細情報取得')
            j_ssh = client.SshKeys.Get(j_sshkey['id'])
        return j_ssh

    def __SshKeyGen(self, username, mailaddress):
        # SSH鍵の生成
        path_dir_ssh = os.path.join(os.path.expanduser('~'), '.ssh/')
#        path_dir_ssh = "/tmp/.ssh/" # テスト用
        path_dir_ssh_keys = os.path.join(path_dir_ssh, 'github/')
        if not(os.path.isdir(path_dir_ssh_keys)):
            os.makedirs(path_dir_ssh_keys)
        protocol_type = "rsa" # ["rsa", "dsa", "ecdsa", "ed25519"]
        bits = 4096 # 2048以上推奨
        passphrase = '' # パスフレーズはあったほうが安全らしい。忘れるだろうから今回はパスフレーズなし。
        path_file_key_private = os.path.join(path_dir_ssh_keys, 'rsa_{0}_{1}'.format(bits, username))
        web.log.Log.Log().Logger.debug(path_dir_ssh)
        web.log.Log.Log().Logger.debug(path_dir_ssh_keys)
        web.log.Log.Log().Logger.debug(path_file_key_private)
        self.__sshkeygen.Generate(type="rsa", bits=4096, passphrase='', comment=mailaddress, file_path=path_file_key_private)
        private_key = None
        with open(os.path.expanduser(path_file_key_private), 'r') as f:
            private_key = f.read()
        public_key = None
        with open(os.path.expanduser(path_file_key_private) + '.pub', 'r') as f:
            public_key = f.read()
        
        ssh_key_gen_params = {
            'type': protocol_type,
            'bits': bits,
            'passphrase': passphrase,
            'path_file_key_private': path_file_key_private,
            'path_file_key_public': path_file_key_private + '.pub',
            'private_key': private_key,
            'public_key': public_key,
        }
        return ssh_key_gen_params

    def __CreateRecordAccount(self, args, mailaddress):
        return dict(
            Username=args.username,
            MailAddress=mailaddress,
            Password=args.password,
            CreatedAt="1970-01-01T00:00:00Z",
            UpdatedAt="1970-01-01T00:00:00Z"
        )
        # 作成日時はAPIのuser情報取得によって得られる。
        
    def __CreateRecordToken(self, account_id, j, ssh_key_id):
        return dict(
            AccountId=account_id,
            IdOnGitHub=j['id'],
            Note=j['note'],
            AccessToken=j['token'],
            Scopes=self.__j2s.ArrayToString(j['scopes']),
            SshKeyId=ssh_key_id
        )

    def __CreateRecordTwoFactor(self, account_id, args):
        return dict(
            AccountId=account_id,
            Secret=args.two_factor_secret_key
        )        

    def __CreateRecordSshConfigures(self, account_id, host, ssh_key_gen_params):
        return dict(
            AccountId=account_id,
            HostName=host,
            PrivateKeyFilePath=ssh_key_gen_params['path_file_key_private'],
            PublicKeyFilePath=ssh_key_gen_params['path_file_key_public'],
            Type=ssh_key_gen_params['type'],
            Bits=ssh_key_gen_params['bits'],
            Passphrase=ssh_key_gen_params['passphrase'],
        )

    def __CreateRecordSshKeys(self, account_id, private_key, public_key, j):
        return dict(
            AccountId=account_id,
            IdOnGitHub=j['id'],
            Title=j['title'],
            Key=j['key'],
            PrivateKey=private_key,
            PublicKey=public_key,
            Verified=self.__j2s.BoolToInt(j['verified']),
            ReadOnly=self.__j2s.BoolToInt(j['read_only']),
            CreatedAt=j['created_at'],
        )
