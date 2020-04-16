# Fantasy Football Dashboard

A simple fantasy football dashboard.  Allows you to implement custom league scoring, visualize the weekly and seasonal stats, and share it with your league.

### Installing

1. [Download Anaconda](https://www.anaconda.com/distribution/).
2. Create a new environment with `conda create -n fantasy dash pandas plotly pytest`
3. Run `conda activate fantasy`
4. Clone the repo `git clone https://github.com/jeremyrcouch/fantasy_dashboard.git`
5. Test out the app locally with `python ./app/app.py`

## Running the Tests

From the `fantasy_dashboard` folder, run `pytest tests/test_app.py` to run all tests.

## Data

The dashboard requires two inputs: the weekly matchup schedule for the season and the weekly points for each player.  The schedule data is expected to be in the format:

| Week  | Bob   | Tom   | Jerry | Phil  | ...   |
|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|
| 1     | Tom   | Bob   | Phil  | Jerry | ...   |
| 2     | Jerry | Phil  | Bob   | Tom   | ...   |
| 3     | Phil  | Jerry | Tom   | Bob   | ...   |
| ...   | ...   | ...   | ...   | ...   | ...   |

There should be a column for `Week` and a column for each player's name.  The schedule should be for the whole season.  For weekly points data, it should look like:

| Week  | Bob   | Tom   | Jerry | Phil  | ...   |
|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|
| 1     | 90.21 | 80.73 | 89.26 | 98.88 | ...   |
| 2     | 80.74 | 99.27 | 90.45 | 87.34 | ...   |
| 3     | 96.30 | 78.08 | 87.65 | 90.56 | ...   |
| 4     | ...   | ...   | ...   | ...   | ...   |

There should be a column for `Week` and a column for each player's name.  Only the rows for weeks that have already finished should be filled in with point values for each player - leave the rest blank.  The dashboard interprets this to determine the current week.

## Pointing the Dashboard to Your Data

There are several ways you can point the dashboard to your league's data.

#### Google Sheets

Stuff.

#### Local to App

Things.

## Deploying with Heroku

You can use Heroku to deploy your app, making it available for your league to see and interact with.  Every Heroku account gets a number of [free dyno hours](https://devcenter.heroku.com/articles/free-dyno-hours).  See Heroku's [Getting Started Guide for Python](https://devcenter.heroku.com/articles/getting-started-with-python?singlepage=true) for the steps to get setup.

1. open powershell
2. cd to the `fantasy_dashboard` folder
3. run `heroku login` and you'll be prompted to login to your account via your browser
4. if this is your first time deploying this app's code, run `heroku create` to create an app
5. run `git push heroku master` to deploy your code to Heroku
6. run `heroku ps:scale web=1` to have an instance of the app running
7. run `heroku open` as a quick way to visit the app in your browser

## License

This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details.

