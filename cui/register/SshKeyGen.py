import subprocess
import os.path
#import web.log.Log
"""
* ssh-keygenコマンド文字列を作成する
* ssh-keygen -l コマンドにて暗号化情報を取得する
* sshコマンドにて接続確認する
"""
class SshKeyGen(object):
    def __init__(self):
        pass
    
    """
    SSH鍵を生成するコマンドを実行する。
    @params {string} typeは次のいずれか。["rsa", "dsa", "ecdsa", "ed25519"]
    @params {integer} bitは2048以上を推奨。セキュリティのために。
    @params {passphrase} passphraseは空文字列(パスフレーズなし)でもOK。SSH接続のたびに毎回入力が面倒なので。
    @params {comment} commentはGitHubでは登録したメールアカウントを設定する。
    @params {string} file_pathは生成したい秘密鍵ファイルのフルパス。
    @return {string} ssh-keygenの標準出力値。    
    """
    def Generate(self, type='rsa', bits='4096', passphrase='', comment=None, file_path=None):
        if os.path.isfile(file_path):
            raise Exception('{0} は既に存在します。パスを変えてから再度実行してください。'.format(file_path))
        command = self.__GetGenerateCommand(type=type, bits=bits, passphrase=passphrase, comment=comment, file_path=file_path)
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout_data, stderr_data = p.communicate()
        stdout_utf8 = stdout_data.decode('utf-8').strip()
        stderr_utf8 = stderr_data.decode('utf-8').strip()
        if 0 < len(stderr_utf8):
            raise Exception('ssh-keygenコマンドでエラーが発生しました。: {0}'.format(stderr_utf8))
#        web.log.Log.Log().Logger.debug(stdout_utf8)
        return stdout_utf8
    
    """
    指定したSSH鍵ファイルの暗号化における情報を取得する。
    @params {string} file_pathはSSH鍵ファイルパス。
    @return {dict} type=暗号化方式, bit=暗号化強度。
    """
    def GetTypeAndBit(self, file_path):
        # 暗号化の情報を取得する
        command = self.__GetListCommand(file_path)
#        web.log.Log.Log().Logger.debug(command)
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout_data, stderr_data = p.communicate()
        stdout_utf8 = stdout_data.decode('utf-8')
#        web.log.Log.Log().Logger.debug(stdout_utf8)
        elements = stdout_utf8.split()
#        web.log.Log.Log().Logger.debug(elements)
        # 出力文字列から不要箇所を削除して返す
        ssh_key_gen_params = {}
        ssh_key_gen_params['bits'] = elements[0]
        elements[3] = elements[3][1:] # '(' 削除
        elements[3] = elements[3][:-1] # ')' 削除
        ssh_key_gen_params['type'] = elements[3].lower()
        return ssh_key_gen_params

    """
    sshコマンドで指定したホストのSSH接続を確認する。
    正常に接続できたら以下のようなメッセージが表示されるはず。
    Hi {user}! You've successfully authenticated, but GitHub does not provide shell access.
    """
    def CheckSshConnect(self, host, github_username, config_user='git'):
        # なぜかStdOutでなくStdErrのほうに出力される
        command = "ssh -T {config_user}@{host}".format(config_user=config_user, host=host)
#        command = "ssh -T git@{host}".format(host=host)
#        web.log.Log.Log().Logger.debug(command)
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout_data, stderr_data = p.communicate()
        res = stdout_data.decode('utf-8').strip()
        if 0 == len(res):
            res = stderr_data.decode('utf-8').strip()
#        web.log.Log.Log().Logger.debug(res)
        if "Hi {0}! You've successfully authenticated, but GitHub does not provide shell access.".format(github_username) != res:
            raise Exception('SSH接続に失敗しました。接続できているのに失敗と判断する場合があります。このSSH接続確認はsshコマンドの標準出力値で行っているため、その出力値が開発した時点から変更されていると誤って失敗と判断してしまいます。sshコマンド出力値(英語)から目視で判断してください。出力値: {0}'.format(res))
        return True    
    """
    SSH鍵を生成するコマンド文字列を返す。
    @params {string} typeは次のいずれか。["rsa", "dsa", "ecdsa", "ed25519"]
    @params {integer} bitは2048以上を推奨。セキュリティのために。
    @params {passphrase} passphraseは空文字列(パスフレーズなし)でもOK。SSH接続のたびに毎回入力が面倒なので。
    @params {comment} commentはGitHubでは登録したメールアカウントを設定する。
    @params {string} file_pathは生成したい秘密鍵ファイルのフルパス。
    @return {string} ssh-keygen -t {type} -b {bits} -P "{passphrase}" -C "{comment}" -f "{file_path}"
    """
    def __GetGenerateCommand(self, type='rsa', bits='4096', passphrase='', comment=None, file_path=None):
        command = 'ssh-keygen -t {type} -b {bits}'.format(type=type, bits=bits)
        command += ' -P "{passphrase}"'.format(passphrase=passphrase)
        if None is not comment:
            command += ' -C "{comment}"'.format(comment=comment)
        if None is not file_path:
            command += ' -f "{file_path}"'.format(file_path=file_path)
#        web.log.Log.Log().Logger.debug(command)
        return command

    """
    指定したSSH鍵ファイルの暗号化における情報を取得するコマンド文字列を返す。
    @params {string} file_pathはSSH鍵ファイルパス。
    @return {string} ssh-keygen -l -f {file_path}
    """
    def __GetListCommand(self, file_path):
        command = 'ssh-keygen -l -f "{file_path}"'.format(file_path=file_path)
        if not(os.path.isfile(file_path)):
            raise Exception('ファイルが存在しません。: {0}'.format(file_path))
        return command

