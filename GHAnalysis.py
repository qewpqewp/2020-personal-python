import json
import os
import argparse
class DataProcessing:
    def __init__(self,FirstTime: bool , Address: str = None ):
        if(FirstTime):#第一次执行初始化
            if(self.pretreatment(Address)==False):
                raise RuntimeError('error: Files not Found')
        else:#读取预制文件
            if(self.loadData() == False):
                raise RuntimeError('error: please -i before using ')


    def pretreatment(self,Address: str) -> bool:
        self.__User = {}
        self.__Repo = {}
        self.__UserAndRepo ={}
        findFile=False
        for root, dic, files in os.walk(Address): #获取文件夹内所有文件
            for file in files:
                if file[-5:] == '.json': #筛选后缀为.json的文件
                    findFile=True
                    json_path = file
                    filedir = open(Address+'\\'+json_path,
                             'r', encoding='utf-8')

                    while True:  #对单个文件逐行读取
                        line = filedir.readline()
                        if line :
                            if line.strip() == '':  # 如果读到的是空行
                                continue  # 跳过该行
                            jsondata=json.loads(line)
                            if not jsondata["type"] in ['PushEvent', 'IssueCommentEvent', 'IssuesEvent', 'PullRequestEvent']: #筛选事件
                                continue # 跳过无关事件
                            self.addEvent(jsondata)# 统计事件数量
                        else:
                            break

                    filedir.close()
        self.saveToFile()  # 循环读取结束后保存到文件
        return  findFile

    def saveToFile(self):#保存到文件
        with open('user.json', 'w', encoding='utf-8') as f:
            json.dump(self.__User, f)
            f.close()
        with open('repo.json', 'w', encoding='utf-8') as f:
            json.dump(self.__Repo, f)
            f.close()
        with open('userandrepo.json', 'w', encoding='utf-8') as f:
            json.dump(self.__UserAndRepo, f)
            f.close()

    def addEvent(self,jsondata):#事件统计
        #emptyevent = {'PushEvent': 0, 'IssueCommentEvent': 0, 'IssuesEvent': 0,'PullRequestEvent': 0}
        if not jsondata["actor"]["login"] in self.__User.keys():
            self.__User[jsondata["actor"]["login"]] = {'PushEvent': 0, 'IssueCommentEvent': 0, 'IssuesEvent': 0,
                      'PullRequestEvent': 0}
        if not jsondata["repo"]["name"] in self.__Repo.keys():
            self.__Repo[jsondata["repo"]["name"]] = {'PushEvent': 0, 'IssueCommentEvent': 0, 'IssuesEvent': 0,
                      'PullRequestEvent': 0}

        if not jsondata["actor"]["login"] in self.__UserAndRepo.keys():
            self.__UserAndRepo[jsondata["actor"]["login"]] = {}
            self.__UserAndRepo[jsondata["actor"]["login"]][jsondata["repo"]["name"]] ={'PushEvent': 0, 'IssueCommentEvent': 0, 'IssuesEvent': 0,
                      'PullRequestEvent': 0}
        elif not jsondata["repo"]["name"] in self.__UserAndRepo[jsondata["actor"]["login"]].keys():
            self.__UserAndRepo[jsondata["actor"]["login"]][jsondata["repo"]["name"]] = {'PushEvent': 0, 'IssueCommentEvent': 0, 'IssuesEvent': 0,
                      'PullRequestEvent': 0}
        self.__User[jsondata["actor"]["login"]][jsondata['type']] += 1
        self.__Repo[jsondata["repo"]["name"]][jsondata['type']] += 1
        self.__UserAndRepo[jsondata["actor"]["login"]][jsondata["repo"]["name"]][jsondata['type']] += 1



    def loadData(self) -> bool:
        #读取预制文件
        if  not os.path.exists('user.json') and not os.path.exists(
                'repo.json') and not os.path.exists('userandrepo.json'):
            return False
        with open('user.json', 'r', encoding='utf-8') as f:
            temp = f.read()
            self.__User = json.loads(temp)
        with open('repo.json', 'r', encoding='utf-8') as f:
            temp = f.read()
            self.__Repo = json.loads(temp)
        with open('userandrepo.json', 'r', encoding='utf-8') as f:
            temp = f.read()
            self.__UserAndRepo = json.loads(temp)
        return True

    def getEventsByUsers(self, username: str, event: str) -> int:
        #通过用户名获取事件数量
        if not self.__User.get(username,0):
            return 0
        else:
            return self.__User[username].get(event,0)

    def getEventsByRepos(self, reponame: str, event: str) -> int:
        #通过仓库名获取事件数量
        if not self.__Repo.get(reponame,0):
            return 0
        else:
            return self.__Repo[reponame].get(event,0)

    def getEventsByUsersAndRepos(self, username: str, reponame: str, event: str) -> int:
        #通过用户名和仓库名获取事件数量
        if not self.__User.get(username,0):
            return 0
        elif not self.__UserAndRepo[username].get(reponame,0):
            return 0
        else:
            return self.__UserAndRepo[username][reponame].get(event,0)


class GHAnalysis:
    def __init__(self):
        self.initArgparse()#初始化Arg
        print(self.dataResult())#输出结果

    def initArgparse(self):
        # 初始化Arg
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('-i', '--init')
        self.parser.add_argument('-u', '--user')
        self.parser.add_argument('-r', '--repo')
        self.parser.add_argument('-e', '--event')

    def dataResult(self):
        #根据参数执行
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
                        self.parser.parse_args().repo, self.parser.parse_args().event)
                else:
                    raise RuntimeError('error: argument -u or -r is required')
            else:
                raise RuntimeError('error: argument -e is required')
        return result

if __name__ == '__main__':
    GHAnalysis()