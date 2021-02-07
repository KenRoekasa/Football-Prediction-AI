import urllib.request, json


def json_parser(id):
    # print(id)
    api_link = "https://api.sofascore.com/api/v1/event/%d/statistics" % id
    with urllib.request.urlopen(api_link) as url:
        data = json.loads(url.read().decode())
        data = data['statistics'][0]['groups']
        possession = data[0]['statisticsItems']
        possession_arr = []
        for p in possession:
            possession_arr.append(p['home'])
            possession_arr.append(p['away'])
        # print("possession_arr " + str(possession_arr))
        shots = data[1]['statisticsItems']
        shot_data = []
        for s in shots:
            shot_data.append(s['home'])
            shot_data.append(s['away'])
        # print("shot data " + str(shot_data))
        tvdata = data[2]['statisticsItems']
        tv_data_arr = []
        for tv in tvdata:
            tv_data_arr.append(tv['home'])
            tv_data_arr.append(tv['away'])
        while len(tv_data_arr) < 10:
            tv_data_arr.append(0)
        # print("tv_data_arr data " + str(tv_data_arr))
        shots_extra = data[3]['statisticsItems']
        shots_extra_arr = []
        shots_categories = ['Big chances', 'Big chances missed', 'Hit woodwork', 'Shots inside box',
                            'Shots outside box', 'Goalkeeper saves']

        for n in shots_categories:
            stat1 = 0
            stat2 = 0
            for s in shots_extra:
                name = s['name']
                if n == name:
                    stat1 = s['home']
                    stat2 = s['away']
                    break
            shots_extra_arr.append(stat1)
            shots_extra_arr.append(stat2)

        # print("shots_extra_arr data " + str(shots_extra_arr))
        try:
            passes = data[4]['statisticsItems']
            passes_data = []
            pass_categories = ['Passes', 'Accurate passes', 'Long balls', 'Crosses']
            for n in pass_categories:
                stat1 = 'N/A'
                stat2 = 'N/A'
                for s in passes:
                    name = s['name']
                    if n == name:
                        stat1 = s['home']
                        stat2 = s['away']
                        break
                passes_data.append(stat1)
                passes_data.append(stat2)
        except IndexError:
            passes_data.append('N/A')
            passes_data.append('N/A')
            passes_data.append('N/A')
            passes_data.append('N/A')
            passes_data.append('N/A')
            passes_data.append('N/A')
            passes_data.append('N/A')
            passes_data.append('N/A')
        # print("passes_data data " + str(passes_data))

        duels = data[5]['statisticsItems']
        duel_categories = ['Dribbles', 'Possession lost', 'Duels won', 'Aerials won']
        duels_data = []
        for n in duel_categories:
            stat1 = 'N/A'
            stat2 = 'N/A'
            for s in duels:
                name = s['name']
                if n == name:
                    stat1 = s['home']
                    stat2 = s['away']
                    break
            duels_data.append(stat1)
            duels_data.append(stat2)
        # print("duels_data data " + str(duels_data))

        defending_arr = []
        defending_categories = ['Tackles', 'Interceptions', 'Clearances']
        try:
            defending = data[6]['statisticsItems']
            for n in defending_categories:
                stat1 = 'N/A'
                stat2 = 'N/A'
                for s in defending:
                    name = s['name']
                    if n == name:
                        stat1 = s['home']
                        stat2 = s['away']
                        break
                duels_data.append(stat1)
                duels_data.append(stat2)
        except IndexError:
            defending_arr.append('N/A')
            defending_arr.append('N/A')
            defending_arr.append('N/A')
            defending_arr.append('N/A')
            defending_arr.append('N/A')
            defending_arr.append('N/A')

        # print("defending_arr data " + str(defending_arr))
        # print("possession arr " + str(len(possession_arr)))
        # print("shot_data arr " + str(len(shot_data)))
        # print("tv_data_arr arr " + str(len(tv_data_arr)))
        # print("shots_extra_arr arr " + str(len(shots_extra_arr)))
        # print("passes_data arr " + str(len(passes_data)))
        # print("duels_data arr " + str(len(duels_data)))
        # print("defending_arr arr " + str(len(defending_arr)))

        csv_data = possession_arr + shot_data + tv_data_arr + shots_extra_arr + passes_data + duels_data + defending_arr
        return csv_data


if __name__ == "__main__":
    # execute only if run as a script
    json_parser(7828251)