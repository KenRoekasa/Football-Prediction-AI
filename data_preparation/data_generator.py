import glob
import os
import random

import numpy as np
import pandas as pd
from tqdm import tqdm


class DataGenerator:
    def __init__(self, settings):
        self.settings = settings

    def get_team_home_games(self, table, team):
        return table[table["home team"].str.contains(team)]

    def get_team_away_games(self, table, team):
        return table[table["away team"].str.contains(team)]

    def get_all_team_games(self, table, team):
        return pd.concat([self.get_team_home_games(table, team), self.get_team_away_games(table, team)]).sort_values(
            by=['date'])

    def select_random_consecutive_games(self, table, team, n):  # select random n consecutive games
        all_games = self.get_all_team_games(table, team)

        first_index = random.randrange(0, len(all_games) - n)
        return all_games.iloc[first_index:first_index + n]

    def get_previous_n_games(self, table, team, n, game):
        all_games = self.get_all_team_games(table, team)
        all_games.reset_index(drop=True, inplace=True)

        gamelink = str(game['link'])
        the_game = all_games[all_games['link'] == gamelink]
        index = the_game.index[0]

        if index > n:
            previous = index - n

        else:
            previous = 0

        previous_games = all_games.iloc[previous:index]
        return previous_games

    def format_data(self, data):
        # Change date to date format
        data['date'] = pd.to_datetime(data["date"], dayfirst=True, format="%Y-%m-%d")

        # Make a subset of the table to include the fields we need
        data_subset = data[
            ['date', 'link', 'home team', 'away team', 'home score', 'away score', 'league', 'season',
            'home total shots', 'away total shots', 'home total conversion rate',
            'away total conversion rate', 'home open play shots',
            'away open play shots',
            'home open play goals', 'away open play goals',
            'home open play conversion rate', 'away open play conversion rate',
            'home set piece shots', 'away set piece shots', 'home set piece goals',
            'away set piece goals', 'home set piece conversion',
            'away set piece conversion', 'home counter attack shots',
            'away counter attack shots', 'home counter attack goals',
            'away counter attack goals', 'home counter attack conversion',
            'away counter attack conversion', 'home penalty shots',
            'away penalty shots',
            'home penalty goals', 'away penalty goals', 'home penalty conversion',
            'away penalty conversion', 'home own goals shots',
            'away own goals shots',
            'home own goals goals', 'away own goals goals',
            'home own goals conversion',
            'away own goals conversion', 'home total passes', 'away total passes',
            'home total average pass streak', 'away total average pass streak',
            'home crosses', 'away crosses', 'home crosses average pass streak',
            'away crosses average pass streak', 'home through balls',
            'away through balls', 'home through balls average streak',
            'away through balls average streak', 'home long balls',
            'away long balls',
            'home long balls average streak', 'away long balls average streak',
            'home short  passes', 'away short  passes',
            'home short passes average streak', 'away short passes average streak',
            'home cards', 'away cards', 'home fouls', 'away fouls',
            'home unprofessional',
            'away unprofessional', 'home dive', 'away dive', 'home other',
            'away other',
            'home red cards', 'away red cards', 'home yellow cards',
            'away yellow cards',
            'home cards per foul', 'away cards per foul',
            'home woodwork', 'away woodwork', 'home shots on target',
            'away shots on target', 'home shots off target',
            'away shots off target',
            'home shots blocked', 'away shots blocked', 'home possession',
            'away possession', 'home touches', 'away touches',
            'home passes success',
            'away passes success',
            'home accurate passes', 'away accurate passes', 'home key passes',
            'away key passes', 'home dribbles won', 'away dribbles won',
            'home dribbles attempted', 'away dribbles attempted',
            'home dribbled past',
            'away dribbled past', 'home dribble success', 'away dribble success',
            'home aerials won', 'away aerials won', 'home aerials won%',
            'away aerials won%', 'home offensive aerials',
            'away offensive aerials',
            'home defensive aerials', 'away defensive aerials',
            'home successful tackles',
            'away successful tackles', 'home tackles attempted',
            'away tackles attempted',
            'home was dribbled', 'away was dribbled', 'home tackles success %',
            'away tackles success %', 'home clearances', 'away clearances',
            'home interceptions', 'away interceptions', 'home corners',
            'away corners',
            'home corner accuracy', 'away corner accuracy', 'home dispossessed',
            'away dispossessed', 'home errors', 'away errors', 'home offsides',
            'away offsides', 'home elo', 'away elo',
            'home pi rating',
            'away pi rating']].copy()

        data_subset = data_subset.loc[:, ~data_subset.columns.duplicated()]  # removes duplicates

        # remove % sign from certain columns
        data_object = data_subset.select_dtypes(['object'])
        data_object = data_object.iloc[:, 5:]
        data_subset[data_object.columns] = data_object.apply(lambda x: x.str.rstrip('%').astype(float))

        data_subset.dropna(inplace=True)
        data_subset = data_subset.sort_values(by=['date'])
        data_subset = data_subset.reset_index(drop=True)
        return data_subset

    def get_winstreak(self, previous_games, team):
        counter = 0

        n = len(previous_games)
        if n == 0:
            return 0
        for i in range(0, n):
            game = previous_games.iloc[i]
            home_goals = game['home score']
            away_goals = game['away score']

            if (home_goals > away_goals and game['home team'] == team) or (
                    away_goals > home_goals and game['away team'] == team):  # If team the team wins
                counter += 1
            else:  # team loses or draw
                counter = 0

        return counter

    def get_losestreak(self, previous_games, team):
        counter = 0

        n = len(previous_games)
        if n == 0:
            return 0
        for i in range(0, n):
            game = previous_games.iloc[i]
            home_goals = game['home score']
            away_goals = game['away score']

            if (home_goals < away_goals and game['home team'] == team) or (
                    away_goals < home_goals and game['away team'] == team):  # If team the team wins
                counter += 1
            else:  # team loses or draw
                counter = 0

        return counter

    def create_training_data(self, data):  # TODO comment functions
        n = self.settings['n']
        # Split into leagues and seasons
        leagues = data['league'].unique()  # change this to the league i want

        training_data = []
        pbar = tqdm(total=len(data.index))
        for league in leagues:

            data_league = data[data['league'] == league]

            seasons = data_league['season'].unique()

            for season in seasons:  # get training data for each season
                data_season = data_league[data_league['season'] == season]
                data_season.reset_index(drop=True, inplace=True)
                for i in range(0, len(data_season)):  # remove the first game with no previous data

                    random_game = data_season.iloc[i]

                    teama = random_game['home team']
                    teamb = random_game['away team']

                    home_goals = random_game['home score']
                    away_goals = random_game['away score']

                    if home_goals > away_goals:
                        classification_label = 0  # win
                    elif home_goals == away_goals:
                        classification_label = 1  # draw
                    else:
                        classification_label = 2  # lose

                    teama_previous_games = self.get_previous_n_games(data_season, teama, n, random_game)
                    teamb_previous_games = self.get_previous_n_games(data_season, teamb, n, random_game)

                    if teama_previous_games.size == 0 or teamb_previous_games.size == 0:  # if no previous games are found skip
                        continue

                    away_rating, home_rating = self.normalise_ratings(data_league, teama, teamb, teama_previous_games,
                                                                      teamb_previous_games)

                    teama_mean_array = self.get_mean_array(teama, teama_previous_games)
                    teamb_mean_array = self.get_mean_array(teamb, teamb_previous_games)

                    # append the ratings
                    teama_mean_array = np.append(teama_mean_array, home_rating)
                    teamb_mean_array = np.append(teamb_mean_array, away_rating)

                    if self.settings['combination'] == 'append':
                        mean_data_array = np.append(teama_mean_array, teamb_mean_array)
                    if self.settings['combination'] == 'diff':
                        mean_data_array = teama_mean_array - teamb_mean_array

                    final = np.insert(mean_data_array, 0, classification_label)
                    final = np.append(final, league)
                    training_data.append(final)
                    pbar.update(1)
        pbar.close()
        return training_data

    def normalise_ratings(self, data_league, teama, teamb, teama_previous, teamb_previous):
        if self.settings['rating normalisation'] == 'min-max':
            home_rating, away_rating = self.get_ratings(teama, teamb, 'pi rating', teama_previous, teamb_previous)

            # Get the minimum value for that league
            pi_rating_min_rating = data_league[['home pi rating', 'away pi rating']].min().min()
            # Get the maximum value for that league
            pi_rating_max_rating = data_league[['home pi rating', 'away pi rating']].max().max()

            pi_rating_away_rating, pi_rating_home_rating = self.min_max_normalisation(away_rating,
                                                                                      home_rating,
                                                                                      pi_rating_max_rating,
                                                                                      pi_rating_min_rating)

            elo_min_rating = data_league[['home elo', 'away elo']].min().min()
            elo_max_rating = data_league[['home elo', 'away elo']].max().max()

            # find max to normalise the values
            home_rating, away_rating = self.get_ratings(teama, teamb, 'elo', teama_previous, teamb_previous)
            elo_away_rating, elo_home_rating = self.min_max_normalisation(away_rating, home_rating,
                                                                          elo_max_rating, elo_min_rating)

            away_rating, home_rating = [elo_away_rating, pi_rating_away_rating], [elo_home_rating,
                                                                                  pi_rating_home_rating]

        if self.settings['rating normalisation'] == 'ratio':




            home_rating, away_rating = self.get_ratings(teama, teamb, 'pi rating', teama_previous, teamb_previous)
            pi_rating_away_rating, pi_rating_home_rating = self.ratio_normalisation(away_rating, home_rating)

            home_rating, away_rating = self.get_ratings(teama, teamb, 'elo', teama_previous, teamb_previous)
            elo_away_rating, elo_home_rating = self.ratio_normalisation(away_rating, home_rating)

            away_rating, home_rating = [elo_away_rating, pi_rating_away_rating], [elo_home_rating,
                                                                                  pi_rating_home_rating]

        if self.settings['rating normalisation'] == 'none':

            # ratio normalisation
            if 'pi-rating' in self.settings['columns']:
                home_rating, away_rating = self.get_ratings(teama, teamb, 'pi rating', teama_previous, teamb_previous)

            elif 'elo' in self.settings['columns']:  # same for elo

                # find max to normalise the values
                home_rating, away_rating = self.get_ratings(teama, teamb, 'elo', teama_previous, teamb_previous)

        return away_rating, home_rating

    def get_ratings(self, home_team, away_team, rating, teama_previous, teamb_previous):
        if rating == 'pi rating':
            # get the previous game
            home_previous = teama_previous.iloc[-1]

            # if rating team is home team get home rating
            if home_previous['home team'] == home_team:
                home_rating = home_previous['home pi rating']
            # if rating team is away team get away rating
            elif home_previous['away team'] == home_team:
                home_rating = home_previous['away pi rating']

            # get the previous game
            away_previous = teamb_previous.iloc[-1]

            # if rating team is home team get home rating
            if away_previous['home team'] == away_team:
                away_rating = away_previous['home pi rating']
            # if rating team is away team get away rating
            elif away_previous['away team'] == away_team:
                away_rating = away_previous['away pi rating']


        elif rating == 'elo':
            # get the previous game
            home_previous = teama_previous.iloc[-1]

            # if rating team is home team get home rating
            if home_previous['home team'] == home_team:
                home_rating = home_previous['home elo']
            # if rating team is away team get away rating
            elif home_previous['away team'] == home_team:
                home_rating = home_previous['away elo']

            # get the previous game
            away_previous = teamb_previous.iloc[-1]

            # if rating team is home team get home rating
            if away_previous['home team'] == away_team:
                away_rating = away_previous['home elo']
            # if rating team is away team get away rating
            elif away_previous['away team'] == away_team:
                away_rating = away_previous['away elo']

        return float(home_rating), float(away_rating)

    def min_max_normalisation(self, away_rating, home_rating, max_rating, min_rating):
        home_rating = (home_rating - min_rating) / (max_rating - min_rating)
        away_rating = (away_rating - min_rating) / (max_rating - min_rating)
        return away_rating, home_rating

    def ratio_normalisation(self, away_rating, home_rating):
        # find max to normalise the values

        sum_rating = home_rating + away_rating
        home_rating = home_rating / sum_rating
        away_rating = away_rating / sum_rating

        return away_rating, home_rating

    def get_mean_array(self, team, previous_games):
        winstreak = self.get_winstreak(previous_games, team)
        losestreak = self.get_losestreak(previous_games, team)
        mean = self.get_mean_stats(previous_games, team)
        mean_array = np.append(mean, winstreak)
        mean_array = np.append(mean_array, losestreak)
        return mean_array

    def get_mean_stats(self, previous_games, team):
        # Get home statistics
        # Get all home games
        home_games = self.get_team_home_games(previous_games, team)
        home_goals_conceded = home_games['away score'].to_numpy(dtype=float)
        home_games = home_games.filter(regex='home', axis=1)

        try:
            home_games.drop('home pi rating', axis=1, inplace=True)
        except KeyError:
            pass
        try:
            home_games.drop('home elo', axis=1, inplace=True)
        except KeyError:
            pass

        home_games.drop('home team', axis=1, inplace=True)
        # print(home_games.columns)
        home_mean = home_games.to_numpy(dtype=float)
        home_mean = np.insert(home_mean, np.shape(home_mean)[1], home_goals_conceded, axis=1)

        # print(home_mean)
        # Get away statistics
        away_games = self.get_team_away_games(previous_games, team)
        away_goals_conceded = away_games['home score'].to_numpy(dtype=float)
        away_games = away_games.filter(regex='away', axis=1)

        try:
            away_games.drop('away pi rating', axis=1, inplace=True)
        except KeyError:
            pass
        try:
            away_games.drop('away elo', axis=1, inplace=True)
        except KeyError:
            pass

        away_games.drop('away team', axis=1, inplace=True)
        away_mean = away_games.to_numpy(dtype=float)

        away_mean = np.insert(away_mean, np.shape(away_mean)[1], away_goals_conceded, axis=1)

        # Combine away and home statistics to get the final
        combined_mean = np.append(home_mean, away_mean, axis=0)
        combined_mean = np.mean(combined_mean, axis=0)

        # [columns] + goals conceded

        return combined_mean

    def generate_training_data(self, csv, path):
        data = pd.read_csv(csv)
        data = self.format_data(data)
        training_data = self.create_training_data(data)

        df = pd.DataFrame(data=training_data, dtype=float,
                          columns=['Outcome', 'home score', 'home total shots', 'home total conversion rate',
                                   'home open play shots', 'home open play goals',
                                   'home open play conversion rate', 'home set piece shots',
                                   'home set piece goals', 'home set piece conversion',
                                   'home counter attack shots', 'home counter attack goals',
                                   'home counter attack conversion', 'home penalty shots',
                                   'home penalty goals', 'home penalty conversion', 'home own goals shots',
                                   'home own goals goals', 'home own goals conversion',
                                   'home total passes', 'home total average pass streak', 'home crosses',
                                   'home crosses average pass streak', 'home through balls',
                                   'home through balls average streak', 'home long balls',
                                   'home long balls average streak', 'home short passes',
                                   'home short passes average streak', 'home cards', 'home fouls',
                                   'home unprofessional', 'home dive', 'home other', 'home red cards',
                                   'home yellow cards', 'home cards per foul', 'home woodwork',
                                   'home shots on target', 'home shots off target', 'home shots blocked',
                                   'home possession', 'home touches', 'home passes success',
                                   'home accurate passes', 'home key passes', 'home dribbles won',
                                   'home dribbles attempted', 'home dribbled past', 'home dribble success',
                                   'home aerials won', 'home aerials won%', 'home offensive aerials',
                                   'home defensive aerials', 'home successful tackles',
                                   'home tackles attempted', 'home was dribbled', 'home tackles success %',
                                   'home clearances', 'home interceptions', 'home corners',
                                   'home corner accuracy', 'home dispossessed', 'home errors',
                                   'home offsides',
                                   'home goals conceded', 'home win streak', 'home lose streak', 'home elo',
                                   'home pi rating', 'away score', 'away total shots', 'away total conversion rate',
                                   'away open play shots', 'away open play goals',
                                   'away open play conversion rate', 'away set piece shots',
                                   'away set piece goals', 'away set piece conversion',
                                   'away counter attack shots', 'away counter attack goals',
                                   'away counter attack conversion', 'away penalty shots',
                                   'away penalty goals', 'away penalty conversion', 'away own goals shots',
                                   'away own goals goals', 'away own goals conversion',
                                   'away total passes', 'away total average pass streak', 'away crosses',
                                   'away crosses average pass streak', 'away through balls',
                                   'away through balls average streak', 'away long balls',
                                   'away long balls average streak', 'away short passes',
                                   'away short passes average streak', 'away cards', 'away fouls',
                                   'away unprofessional', 'away dive', 'away other', 'away red cards',
                                   'away yellow cards', 'away cards per foul', 'away woodwork',
                                   'away shots on target', 'away shots off target', 'away shots blocked',
                                   'away possession', 'away touches', 'away passes success',
                                   'away accurate passes', 'away key passes', 'away dribbles won',
                                   'away dribbles attempted', 'away dribbled past', 'away dribble success',
                                   'away aerials won', 'away aerials won%', 'away offensive aerials',
                                   'away defensive aerials', 'away successful tackles',
                                   'away tackles attempted', 'away was dribbled', 'away tackles success %',
                                   'away clearances', 'away interceptions', 'away corners',
                                   'away corner accuracy', 'away dispossessed', 'away errors',
                                   'away offsides',
                                   'away goals conceded', 'away win streak', 'away lose streak', 'away elo',
                                   'away pi rating', 'league'])

        df.to_csv(path, index=False)


def merge_seasons(path, csv):
    owd = os.getcwd()
    extension = 'csv'
    os.chdir(path)
    result = glob.glob('*.{}'.format(extension))
    data = pd.read_csv(result[0])
    for i, r in enumerate(result):
        if i > 0:
            print()
            read_csv = pd.read_csv(r)
            print(str(r) + " " + str(len(read_csv)))
            data = data.append(read_csv)

    data['date'] = pd.to_datetime(data["date"], dayfirst=True, format="%a, %d-%b-%y")
    data.sort_values(by=['date'], inplace=True)
    data.reset_index(drop=True, inplace=True)
    data.to_csv(csv, index=False)
    os.chdir(owd)


def merge_leagues():
    data = pd.read_csv('../data/whoscored/premierleague/all-premierleague.csv')
    laliga = pd.read_csv('../data/whoscored/laliga/all-laliga.csv')
    bundesliga = pd.read_csv('../data/whoscored/bundesliga/all-bundesliga.csv')
    seriea = pd.read_csv('../data/whoscored/seriea/all-seriea.csv')
    ligue1 = pd.read_csv('../data/whoscored/ligue1/all-ligue1.csv')

    data = data.append(laliga)
    data = data.append(bundesliga)
    data = data.append(seriea)
    data = data.append(ligue1)

    data['date'] = pd.to_datetime(data["date"], dayfirst=True, format="%Y-%m-%d")
    data.sort_values(by=['date'], inplace=True)
    data.reset_index(drop=True, inplace=True)
    data.to_csv('../data/whoscored/all-leagues.csv', index=False)


if __name__ == '__main__':
    for combination in ['append']:
        for column in ['everything both']:
            for i in range(10, 0, -1):
                settings = {'n': i, 'rating normalisation': 'min-max',
                            'combination': combination}

                data_gen = DataGenerator(settings)

                data_gen.generate_training_data('../data/whoscored/all-leagues.csv',
                                                '../data/whoscored/trainingdata/mean/alltrainingdata-%d.csv' % settings[
                                                    'n'],
                                                settings)
