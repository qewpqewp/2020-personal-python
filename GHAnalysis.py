import json
import os
import argparse
class DataProcessing:
    def __init__(self,Firsttime: bool , Address: str = None ):
        if(Firsttime):
            self.Pretreatment(Address)
        else:
            self.LoadData()


    def Pretreatment(self,Address: str):
        self.__User = {}
        self.__Repo = {}
        self.__UserAndRepo = {}
        for root, dic, files in os.walk(Address):
            for file in files:
                if file[-5:] == '.json':

                    json_path = file
                    filedir = open(Address+'\\'+json_path,
                             'r', encoding='utf-8')
                    line = filedir.readline()
                    while line:
                        line = filedir.readline()
                        if line.strip() == '':  # 如果读到的是空行
                            continue  # 跳过该行
                        jsondata=json.loads(line)
                        if not self.__User.get(jsondata['actor']['login'], 0):
                            self.__User.update({jsondata['actor']['login']: {}})
                            self.__UserAndRepo.update({jsondata['actor']['login']: {}})
                        self.__User[jsondata['actor']['login']][jsondata['type']
                        ] = self.__User[jsondata['actor']['login']].get(jsondata['type'], 0) + 1
                        if not self.__Repo.get(jsondata['repo']['name'], 0):
                            self.__Repo.update({jsondata['repo']['name']: {}})
                        self.__Repo[jsondata['repo']['name']][jsondata['type']
                        ] = self.__Repo[jsondata['repo']['name']].get(jsondata['type'], 0) + 1
                        if not self.__UserAndRepo[jsondata['actor']['login']].get(jsondata['repo']['name'], 0):
                            self.__UserAndRepo[jsondata['actor']['login']].update({jsondata['repo']['name']: {}})
                        self.__UserAndRepo[jsondata['actor']['login']][jsondata['repo']['name']][jsondata['type']
                        ] = self.__UserAndRepo[jsondata['actor']['login']][jsondata['repo']['name']].get(jsondata['type'], 0) + 1
        with open('user.json', 'w', encoding='utf-8') as f:
            json.dump(self.__User, f)
        with open('repo.json', 'w', encoding='utf-8') as f:
            json.dump(self.__Repo, f)
        with open('userandrepo.json', 'w', encoding='utf-8') as f:
            json.dump(self.__UserAndRepo, f)


    def LoadData(self):
        if  not os.path.exists('user.json') and not os.path.exists(
                'repo.json') and not os.path.exists('userandrepo.json'):
            raise RuntimeError('error: init failed')
        temp = open('user.json', 'r', encoding='utf-8').read()
        self.__User = json.loads(temp)
        temp = open('repo.json', 'r', encoding='utf-8').read()
        self.__Repo = json.loads(temp)
        temp = open('userandrepo.json', 'r', encoding='utf-8').read()
        self.__UserAndRepo = json.loads(temp)
    def getEventsByUsers(self, username: str, event: str) -> int:
        if not self.__User.get(username,0):
            return 0
        else:
            return self.__User[username].get(event,0)

    def getEventsByRepos(self, reponame: str, event: str) -> int:
        if not self.__Repo.get(reponame,0):
            return 0
        else:
            return self.__Repo[reponame].get(event,0)

    def getEventsByUsersAndRepos(self, username: str, reponame: str, event: str) -> int:
        if not self.__User.get(username,0):
            return 0
        elif not self.__UserAndRepo[username].get(reponame,0):
            return 0
        else:
            return self.__UserAndRepo[username][reponame].get(event,0)


class GHAnalysis:
    def __init__(self):
        self.InitArgparse()
        print(self.DataResult())

    def InitArgparse(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('-i', '--init')
        self.parser.add_argument('-u', '--user')
        self.parser.add_argument('-r', '--repo')
        self.parser.add_argument('-e', '--event')

    def DataResult(self):
        if self.parser.parse_args().init:
            self.data = DataProcessing( True,self.parser.parse_args().init)
            return 0
        else:
            self.data = DataProcessing(False)
            if self.parser.parse_args().event:
                if self.parser.parse_args().user:
                    if self.parser.parse_args().repo:
                        result = self.data.getEventsByUsersAndRepos(
                            self.parser.parse_args().user, self.parser.parse_args().repo,
                            self.parser.parse_args().event)
                    else:
                        result = self.data.getEventsByUsers(
                            self.parser.parse_args().user, self.parser.parse_args().event)
                elif self.parser.parse_args().repo:
                    result = self.data.getEventsByRepos(
                        self.parser.parse_args().reop, self.parser.parse_args().event)
                else:
                    raise RuntimeError('error: argument -u or -r is required')
            else:
                raise RuntimeError('error: argument -e is required')
        return result






if __name__ == '__main__':
    GHAnalysis();