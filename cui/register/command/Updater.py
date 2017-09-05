#!python3
#encoding:utf-8
import os.path
import subprocess
import shlex
import re
import datetime
import traceback
import copy
import dataset
import database.src.Database
from web.service.github.api.v3.authentication.BasicAuthentication import BasicAuthentication
from web.service.github.api.v3.authentication.TwoFactorAuthentication import TwoFactorAuthentication
from web.service.github.api.v3.authentication.OAuthAuthentication import OAuthAuthentication
import web.service.github.api.v3.Client
import web.service.github.api.v3.AuthenticationsCreator
import web.sqlite.Json2Sqlite
import cui.register.SshConfigurator
import cui.register.command.ASubCommand
import web.log.Log
class Updater(cui.register.command.ASubCommand.ASubCommand):
    def __init__(self, path_dir_root):
        self.__path_dir_root = path_dir_root
        self.__j2s = web.sqlite.Json2Sqlite.Json2Sqlite()
        self.__db = None
        self.__sshkeygen = cui.register.SshKeyGen.SshKeyGen()

    def Run(self, args):
        web.log.Log.Log().Logger.debug('Account.Update')
        web.log.Log.Log().Logger.debug(args)
        web.log.Log.Log().Logger.debug('-u: {0}'.format(args.username))
        web.log.Log.Log().Logger.debug('-rn: {0}'.format(args.rename))
        web.log.Log.Log().Logger.debug('-p: {0}'.format(args.password))
        web.log.Log.Log().Logger.debug('-m: {0}'.format(args.mailaddress))
        web.log.Log.Log().Logger.debug('-s: {0}'.format(args.ssh_host))
        web.log.Log.Log().Logger.debug('-t: {0}'.format(args.two_factor_secret_key))
        web.log.Log.Log().Logger.debug('-r: {0}'.format(args.two_factor_recovery_code_file_path))
        web.log.Log.Log().Logger.debug('--auto: {0}'.format(args.auto))

        self.__db = database.src.Database.Database(self.__path_dir_root)
        self.__db.Initialize()
        
        account = self.__db.Accounts['Accounts'].find_one(Username=args.username)
        web.log.Log.Log().Logger.debug(account)
        
        if None is account:
            web.log.Log.Log().Logger.warning('指定したユーザ {0} がDBに存在しません。更新を中止します。'.format(args.username))
            return

        creator = web.service.github.api.v3.AuthenticationsCreator.AuthenticationsCreator(self.__db, args.username)
        authentications = creator.Create()
        client = web.service.github.api.v3.Client.Client(self.__db, authentications)

        # Accountsテーブルを更新する（ユーザ名、パスワード、メールアドレス）
        self.__UpdateAccounts(args, account, client)
        
        # SSH鍵を更新する(APIの削除と新規作成で。ローカルで更新し~/.ssh/configで設定済みとする)
        self.__UpdateSsh(args, account, client)
        
        # 未実装は以下。
        # E. 2FA-Secret
        # F. 2FA-Recovery-Code
        
        # 作成したアカウントのリポジトリDB作成や、作成にTokenが必要なライセンスDBの作成
        self.__db.Initialize()
        return self.__db

    def __UpdateAccounts(self, args, account, client):
        new_account = copy.deepcopy(account)
        # ユーザ名とパスワードを変更する
        if None is not args.rename or None is not args.password:
            j_user = self.__IsValidUsernameAndPassword(args, account, client)
            if None is not args.rename:
                new_account['Username'] = args.rename
            if None is not args.password:
                new_account['Password'] = args.password
            new_account['CreatedAt'] = j_user['created_at']
            new_account['UpdatedAt'] = j_user['updated_at']
        # メールアドレスを更新する
        if args.mailaddress:
            mail = self.__GetPrimaryMail(client)
            if mail != account['MailAddress']:
                new_account['MailAddress'] = mail
            else:
                web.log.Log.Log().Logger.warning('MailAddressはDBと同一でした。: {0}'.format(mail))
        # DBを更新する
        self.__db.Accounts['Accounts'].update(new_account, ['Id'])
    
    def __IsValidUsernameAndPassword(self, args, account, client):
        if None is args.password:
            password = account['Password']
        else:
            password = args.password
        web.log.Log.Log().Logger.debug('password: ' + password)
        try:
            j = client.Users.Get()
            account['CreatedAt'] = j['created_at']
            account['UpdatedAt'] = j['updated_at']
        except:
            raise Exception('指定したユーザ名とパスワードでAPI実行しましたがエラーです。有効なユーザ名とパスワードではない可能性があります。')
            return None
        return j

    def __GetPrimaryMail(self, client):
        mails = client.Emails.Gets()
        web.log.Log.Log().Logger.debug(mails)
        for mail in mails:
            if mail['primary']:
                return mail['email']

    def __UpdateSsh(self, args, account, client):
        if None is args.ssh_host:
            return
        sshconf = cui.register.SshConfigurator.SshConfigurator()
        sshconf.Load()
        if not(args.ssh_host in sshconf.Hosts):
            raise Exception('指定したSSHホスト名 {0} は~/.ssh/config内に未定義です。定義してから再度実行してください。'.format(args.ssh_host))
        if 1 < self.__db.Accounts['AccessTokens'].count(Username=account['Username']):
            raise Exception('プログラムエラー。1ユーザ1Tokenのはずですが、Tokenが2つ以上あります。')
        
        # GitHubAPIでSSH鍵を削除する
        token = self.__db.Accounts['AccessTokens'].find_one(AccountId=account['Id'])
        web.log.Log.Log().Logger.debug(token)
        
        if None is args.password:
            password = account['Password']
        else:
            password = args.password
        client.SshKeys.Delete(token['SshKeyId'])
        
        # GitHubAPIでSSH鍵を生成する
        ssh_key_gen_params = self.__LoadSshKeyFile(args, sshconf)
        j_ssh = client.SshKeys.Create(ssh_key_gen_params['public_key'], title=account['MailAddress'])
        web.log.Log.Log().Logger.debug(j_ssh)
        
        # SSH接続確認
        self.__sshkeygen.CheckSshConnect(args.ssh_host, args.username)
        
        # DB更新
        if 1 < self.__db.Accounts['AccessTokens'].count(AccountId=account['Id']):
            raise Exception('プログラムエラー。1ユーザ1Tokenのはずですが、Tokenが2つ以上あります。')
        if 1 < self.__db.Accounts['SshConfigures'].count(AccountId=account['Id']):
            raise Exception('プログラムエラー。1ユーザ1SshConfiguresレコードのはずですが、レコードが2つ以上あります。')
        if 1 < self.__db.Accounts['SshKeys'].count(AccountId=account['Id']):
            raise Exception('プログラムエラー。1ユーザ1SshKeysレコードのはずですが、レコードが2つ以上あります。')
        rec_token = self.__db.Accounts['AccessTokens'].find_one(AccountId=account['Id'])
        rec_token['SshKeyId'] = j_ssh['id']
        self.__db.Accounts['AccessTokens'].update(rec_token, ['Id'])
            
        sshconfigures = self.__db.Accounts['SshConfigures'].find_one(AccountId=account['Id'])
        sshconfigures['HostName'] = args.ssh_host
        sshconfigures['PrivateKeyFilePath'] = ssh_key_gen_params['path_file_key_private']
        sshconfigures['PublicKeyFilePath'] = ssh_key_gen_params['path_file_key_public']
        sshconfigures['Type'] = ssh_key_gen_params['type']
        sshconfigures['Bits'] = ssh_key_gen_params['bits']
        sshconfigures['Passphrase'] = ssh_key_gen_params['passphrase']
        self.__db.Accounts['SshConfigures'].update(sshconfigures, ['Id'])
        
        sshkeys = self.__db.Accounts['SshConfigures'].find_one(AccountId=account['Id'])
        sshkeys['IdOnGitHub'] = j_ssh['id']
        sshkeys['Title'] = j_ssh['title']
        sshkeys['Key'] = j_ssh['key']
        sshkeys['PrivateKey'] = ssh_key_gen_params['private_key']
        sshkeys['PublicKey'] = ssh_key_gen_params['public_key']
        sshkeys['Verified'] = self.__j2s.BoolToInt(j_ssh['verified'])
        sshkeys['ReadOnly'] = self.__j2s.BoolToInt(j_ssh['read_only'])
        sshkeys['CreatedAt'] = j_ssh['created_at']
        self.__db.Accounts['SshKeys'].update(sshkeys, ['Id'])

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
        ssh_key_gen_params.update({'path_file_key_public': path_file_key_public})
        ssh_key_gen_params.update({'path_file_key_private': path_file_key_private})
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
