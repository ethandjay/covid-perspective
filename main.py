import config
import sys, json, math, os
from datetime import datetime
import shelve, requests, tweepy
from num2words import num2words

def main():
    
    try:
        covidData = requests.get('https://api.covidtracking.com/v1/us/current.json').json()[0]
    except (requests.exceptions.ConnectionError, json.decoder.JSONDecodeError) as e:
        print('Error retrieving COVID data: ' + str(e))
        sys.exit()

    try:
        auth = tweepy.OAuthHandler(config.consumer_key, config.consumer_secret)
        auth.set_access_token(config.access_token, config.access_token_secret)

        api = tweepy.API(auth)

        # Test a method
        api.home_timeline()
    except tweepy.TweepError as e:
        print("Error authenticating to Twitter: " + str(e.response.text))
        sys.exit()

    NE_DEATH_COUNT = 2977
    with shelve.open(os.path.dirname(os.path.abspath(__file__)) + '/store') as db:

        new_deaths_divided = math.floor(covidData['death'] / NE_DEATH_COUNT)

        if ('deaths_divided' not in db):
            # Save fresh data
            print("Previous COVID tweet data unavailable. Saving new data...")
            db['deaths_divided'] = new_deaths_divided
            db['last_updated_ts'] = datetime.now()

            status = num2words(new_deaths_divided).capitalize() + " 9/11s worth of Americans have died from COVID-19 since the start of the pandemic."
            print("Tweeting...")
            api.update_status(status=status)
        else:

            prev_deaths_divided = db['deaths_divided']

            if (new_deaths_divided != prev_deaths_divided):

                # Tweet out the new thing
                last_updated = db['last_updated_ts']
                time_diff = abs(datetime.now() - last_updated)
                time_diff_hours = round(time_diff.total_seconds() / 3600)
                print("Generating COVID tweet based on saved data...")
                ne_change = new_deaths_divided - prev_deaths_divided
                status = (num2words(ne_change).capitalize() + " 9/11" + ("s" if ne_change > 1 else "") + " worth of Americans have died from COVID-19 in the last " + str(time_diff_hours) + " hours. "
                            "" + num2words(new_deaths_divided).capitalize() + " 9/11s worth of Americans have died from COVID-19 since the start of the pandemic." )
                print("Tweeting...")
                api.update_status(status=status)

                # Save the new info
                db['deaths_divided'] = new_deaths_divided
                db['last_updated_ts'] = datetime.now()

            else:

                # If death data has not changed enough, do nothing
                print("No new data since last run. Doing nothing...")
                pass


if __name__ == "__main__":
    main()