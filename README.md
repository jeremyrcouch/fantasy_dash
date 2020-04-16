# Fantasy Football Dashboard

Simple fantasy football dashboard.  Allows you to implement custom league scoring, visualize the weekly and seasonal stats, and share it with your league.

### Installing

1. [Download Anaconda](https://www.anaconda.com/distribution/).
2. Create a new environment with `conda create -n fantasy dash pandas plotly pytest`
3. Run `conda activate fantasy`
4. Clone the repo `git clone https://github.com/jeremyrcouch/fantasy_dashboard.git`
5. Test out the app locally with `python ./app/app.py`

## Running the tests

From the `fantasy_dashboard` folder, run `pytest tests/test_app.py` to run all tests.

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

