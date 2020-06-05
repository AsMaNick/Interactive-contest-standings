import json
import requests
from time import time


def is_letter(c):
    return c.lower() != c.upper() or c == "'"


class CodeforcesUser:
    def __init__(self, user_info):
        self.first_name = user_info['firstName'] if 'firstName' in user_info else ''
        self.last_name = user_info['lastName'] if 'last_name' in user_info else ''
        self.rating = int(user_info['rating'])
        self.handle = user_info['handle']
        self.country = user_info['country'] if 'country' in user_info else ''
        self.city = user_info['city'] if 'city' in user_info else ''
        self.organization = user_info['organization'] if 'organization' in user_info else ''
        
    def get_color_class(self):
        if self.rating == 0:
            return "user-black"
        elif self.rating < 1200:
            return "user-gray"
        elif self.rating < 1400:
            return "user-green"
        elif self.rating < 1600:
            return "user-cyan"
        elif self.rating < 1900:
            return "user-blue"
        elif self.rating < 2100:
            return "user-violet"
        elif self.rating < 2400:
            return "user-orange"
        elif self.rating < 3000:
            return "user-red"
        else:
            return "user-legendary"
        
    def get_html_name(self, name, handle):
        result = "<a href=http://www.codeforces.com/profile/" + self.handle + " title=\"" + name + "\" class=\"" + self.get_color_class() + "\">";
        if len(handle) > 17:
            handle = handle[:16] + "..." + handle[-1];
        if self.get_color_class() == "user-legendary":
            result += "<span class=\"legendary-user-first-letter\">" + handle[0] + "</span>";
            result += handle[1:]
        else:
            result += handle
        result += "</a>"
        return result
        
        
class CodeforcesUserIdentifier:
    def __init__(self, time_to_update):
        self.last_update = 0
        self.time_to_update = time_to_update
        self.load_users()
        
    def need_update(self):
        return time() > self.last_update + self.time_to_update
        
    def load_users(self):
        if True:
            j = json.load(fp=open('data/cf_users.json', 'r'))
        else:
            response = requests.get('https://codeforces.com/api/user.ratedList')
            j = response.json()
            json.dump(j, fp=open('data/cf_users.json', 'w'))
        if j['status'] != 'OK':
            return
        self.users = {}
        self.all_names = set()
        for user in j['result']:
            cf_user = CodeforcesUser(user)
            self.users[cf_user.handle.lower()] = cf_user
            if cf_user.last_name != '':
                self.all_names.add(cf_user.last_name.lower())
        self.last_update = time()
        
    def get_user(self, handle):
        handle = handle.lower()
        if handle not in self.users:
            return None
        return self.users[handle]
        
class TeamIdentifier:
    def __init__(self, time_to_update):
        self.link_to_teams = open('data/link_to_teams.txt', 'r').read()
        self.last_update = 0
        self.time_to_update = time_to_update
        self.cf = CodeforcesUserIdentifier(86400) # update data each 1 day
        self.load_teams()
        
    def load_teams(self):
        response = requests.get(self.link_to_teams)
        j = response.json()
        self.teams = []
        self.team_ids = {}
        Q = 0
        for entry in j['feed']['entry']:
            team = []
            team_names = []
            for i in range(1, 6):
                if entry[f'gsx$handle{i}']['$t'] == '':
                    break
                team.append((entry[f'gsx$name{i}']['$t'].lower(), entry[f'gsx$handle{i}']['$t']))
                team_names.append(entry[f'gsx$name{i}']['$t'].lower())
                self.cf.all_names.add(team[-1][0].lower())
            for p1 in range(len(team)):
                for p2 in range(p1 + 1, len(team)):
                    self.team_ids[TeamIdentifier.get_team_subset(team_names, p1, p2)] = len(self.teams)
                    for p3 in range(p2 + 1, len(team)):
                        self.team_ids[TeamIdentifier.get_team_subset(team_names, p1, p2, p3)] = len(self.teams)
                        for p4 in range(p3 + 1, len(team)):
                            self.team_ids[TeamIdentifier.get_team_subset(team_names, p1, p2, p3, p4)] = len(self.teams)
                            for p5 in range(p4 + 1, len(team)):
                                self.team_ids[TeamIdentifier.get_team_subset(team_names, p1, p2, p3, p4, p5)] = len(self.teams)
            self.teams.append(team)
        self.last_update = time()
        
    def get_team_subset(team, *members):
        res = [team[member].lower() for member in members]
        res.sort()
        return tuple(res)
        
    def need_update(self):
        return time() > self.last_update + self.time_to_update
        
    def get_team(self, team):
        res = []
        if len(team) >= 3 and TeamIdentifier.get_team_subset(team, 0, 1, 2) in self.team_ids:
            res = self.teams[self.team_ids[TeamIdentifier.get_team_subset(team, 0, 1, 2)]]
        else:
            for p1 in range(len(team)):
                for p2 in range(p1 + 1, len(team)):
                    team_subset = TeamIdentifier.get_team_subset(team, p1, p2)
                    if team_subset in self.team_ids:
                        res = self.teams[self.team_ids[team_subset]]
        return {member[0] : member[1] for member in res}
                    
    def update_last_name(self, last_name):
        if last_name.lower() in self.cf.all_names:
            return last_name
        space_index = last_name.rfind(' ');
        if space_index  != -1:
            name1 = last_name[:space_index]
            name2 = last_name[space_index + 1:]
            if name2.lower() in self.cf.all_names:
                last_name = name2
            if name1.lower() in self.cf.all_names:
                last_name = name1
        return last_name
    
    def identify(self, team_text, identification):
        if identification == 'none':
            return team_text
        show_handle = 'handle' in identification
        if self.need_update():
            self.load_teams()
        team_text += '<'
        position = 0
        last_name = ''
        team_members = []
        builder = []
        while position < len(team_text):
            if is_letter(team_text[position]) or \
               (team_text[position] == ' ' and last_name != '') or \
               (position + 1 < len(team_text) and team_text[position] == '-' and last_name != '' and is_letter(team_text[position + 1])):
               
                last_name += team_text[position]
            else:
                l = len(last_name)
                last_name = last_name.strip()
                last_name = self.update_last_name(last_name)
                if last_name.lower() in self.cf.all_names:
                    for i in range(l):
                        builder.pop()
                    builder.append((True, len(team_members)))
                    team_members.append(last_name)
                last_name = ''
                if team_text[position] == '<':
                    break
            builder.append((False, team_text[position]))
            position += 1
        res = ''
        team = self.get_team(team_members)
        for p in builder:
            if p[0]:
                if team_members[p[1]].lower() in team:
                    handle = team[team_members[p[1]].lower()]
                    cf_user = self.cf.get_user(handle)
                    if cf_user is None:
                        res += team_members[p[1]]
                    else:
                        if show_handle:
                            res += cf_user.get_html_name(team_members[p[1]], handle)
                        else:
                            res += cf_user.get_html_name(handle, team_members[p[1]])
                else:
                    res += team_members[p[1]]
            else:
                res += p[1]
        return res
        
        
team_identifier = TeamIdentifier(3600) # update data each 1 hour
