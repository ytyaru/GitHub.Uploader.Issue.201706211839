import configparser
import os.path
class Setting:
    def __init__(self, path_dir_root):
        self.__path_dir_root = path_dir_root
        self.__config = configparser.ConfigParser()
        self.__config.read(os.path.join(path_dir_root, 'config.ini'))
        self.__LoadDbPath()
        self.__GithubUser()
        
    @property
    def DbPath(self): return self.__path_dir_db
    @property
    def GithubUsername(self): return self.__username

    def __GithubUser(self):
        if 'GitHub' not in self.__config or 'User' not in self.__config['GitHub']: self.__username = None
        else: self.__username = self.__config['GitHub']['User']
        
    def __LoadDbPath(self):
        if 'Path' not in self.__config or 'DB' not in self.__config['Path']: self.__path_dir_db = None
        else:
            self.__path_dir_db = self.__RelToAbs(self.__config['Path']['DB'])
            if not os.path.isdir(self.__path_dir_db):
                raise Exception(os.path.join(self.__path_dir_root, 'config.ini') + ' のPath.DBに指定されたパスは存在しないかディレクトリではありません。存在するディレクトリを指定してください。')
            
    def __RelToAbs(self, path):
        if not os.path.isabs(path):
            # ./
            if path.startswith('./'):
                return os.path.join(self.__path_dir_root, path[2:])
            # ../../../
            abs_path = self.__base_path
            rel_path = path
            while rel_path.startswith('../'):
                rel_path = rel_path[3:]
                abs_path = os.path.dirname(abs_path)
            return os.path.join(abs_path, rel_path)
        return path
