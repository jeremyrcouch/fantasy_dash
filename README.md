# Fantasy Football Dashboard

A simple fantasy football dashboard.
- Implement custom scoring for your league
- Visualize weekly and seasonal stats
- Share it with your league

## Installing

1. [Download Anaconda](https://www.anaconda.com/distribution/).
2. From your terminal, create a new environment

   To create an environment with the latest and greatest versions of each package, run:
   ```
   conda create -n fantasy dash pandas plotly pytest
   ```
   To create an environment that mirrors mine (making sure everything works right out of the box), run:
   ```
   conda create -n fantasy dash=1.4.1 pandas=1.0.3 plotly=4.6.0 pytest=5.4.1
   ```

3. Active the environment:
   ```
   conda activate fantasy
   ```

4. Use `cd` to the navigate to the directory where you want the repo
5. Clone the repo:
   ```
   git clone https://github.com/jeremyrcouch/fantasy_dashboard.git
   ```

6. Test out the app locally:
   ```
   python ./app/app.py
   ```

## Running the Tests

From the `fantasy_dashboard` folder, run all tests with:
```
pytest tests/test_app.py
```

## Modifying Scoring

Scoring can be modified in any number of ways by adjusting the code.  Some options:
- Change the number of points awarded for winning
- Adjust how points are awared for weekly ranking
- Add your own scoring logic

As an example, to change how points are awarded based on each player's weekly ranking, you can change the `rank_scoring` function.  If you do, you'll want to update or remove the corresponding test for the function in `./tests/test_app.py`.

## Data

The dashboard requires two input datasets: the weekly matchup schedule for the season and the weekly points for each player.  See the `points.csv` and `schedule.csv` in `./tests/data/` for examples of these in CSV form.

#### Schedule

The schedule data is expected to be in the format:

| Week   | Jim    | Dwight | Michael| Pam    | ...    |
|:------:|:------:|:------:|:------:|:------:|:------:|
| 1      | Dwight | Jim    | Pam    | Michael| ...    |
| 2      | Michael| Pam    | Jim    | Dwight | ...    |
| 3      | Pam    | Michael| Dwight | Jim    | ...    |
| ...    | ...    | ...    | ...    | ...    | ...    |

There should be a column for `Week` and a column for each player's name.  The schedule should be for the whole season.

#### Points

The weekly points data should look like:

| Week   | Jim    | Dwight | Michael| Pam    | ...    |
|:------:|:------:|:------:|:------:|:------:|:------:|
| 1      | 90.21  | 80.73  | 89.26  | 98.88  | ...    |
| 2      | 80.74  | 99.27  | 90.45  | 87.34  | ...    |
| 3      | 96.30  | 78.08  | 87.65  | 90.56  | ...    |
| 4      | ...    | ...    | ...    | ...    | ...    |

There should be a column for `Week` and a column for each player's name.  Only the rows for weeks that have already finished should be filled in with point values for each player - leave the rest blank.  The dashboard interprets this to determine the current week.

## Pointing the Dashboard to Your Data

There are several ways you can point the dashboard to your league's data.

#### Google Sheets

You can store your league's data in a Google sheet.  For both the schedule and points data, follow these steps:

1. Create a new sheet (or tab) by clicking the + button on the bottom left
2. Starting in the top left cell (with the `Week` header in that cell) enter your data
3. Click `File > Publish to the web`
4. Under `Link`, select the correct tab name and `Comma separated values (.csv)` option in the dropdowns
5. Click `Publish`
6. Copy the URL for the published CSV

You can then use `pd.read_csv(URL)` to read in the data.  Make sure you have the two lines under `### Google Sheets ###` in app.py uncommented (and comment out the two lines under `### Local Data ###`) and pass in your correct URLs.  You can see I specified my URLs for both pieces of data at the top of app.py.

#### Local to App

Alternatively, you can store your data locally in the project.  Put your `schedule.csv` and `points.csv` in the `data` folder at the top level (replacing the example files in there).  Make sure you uncomment the two lines under `### Local Data ###` in app.py (and comment out the two lines under `### Google Sheets ###`).  With this setup, however, you'll have to deploy your app to Heroku each time you want to reflect updated points or schedule info on your dashboard.

## Deploying with Heroku

You can use Heroku to deploy your app, making it available for your league to see and interact with.  There are other options for deploying your app, but I chose to use Heroku because each account gets a number of [free dyno hours](https://devcenter.heroku.com/articles/free-dyno-hours).  See Heroku's [Getting Started Guide for Python](https://devcenter.heroku.com/articles/getting-started-with-python?singlepage=true) for the steps to get setup.

1. Open powershell or your terminal
2. Use `cd` to the navigate to the `fantasy_dashboard` directory
3. Run
   ```
   heroku login
   ```

4. You'll be prompted to login to your account via your browser
5. If this is your first time deploying this app's code, create an app:
   ```
   heroku create
   ```

6. Deploy your code to Heroku
   ```
   git push heroku master
   ```
   
7. Scale your app to have 1 instance running
   ```
   heroku ps:scale web=1
   ```

8. Visit the app in your browser:
   ```
   heroku open
   ```

## License

This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details.

