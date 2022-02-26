import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pymongo
from global_vars import app, db

layout = html.Div([
    html.H1("How to use the Task App"),
    html.P(["You can always get back to this page by clicking on the \"Read Me\" tab in the top right of the web page."]),
    html.H2(["New Account"]),
    html.P(["Make an account in the ", html.A("Register", href="/register"), " page. Try not to forget your password, there is currently no password recovery tool. The passwords are not saved in plain text so there's no way to look up the password if it is lost. If you do forget your password a password recovery tool may be created to assist you."]),
    html.H2(["Preferences"]),
    html.P(["Go to the ", html.A("Preferences", href="/preferences"), " page and update your preferences to reflect how you feel about all of the tasks. Preference scores are linear units of effort. For example if starting the dishwasher has a score of 1 and you consider starting the dishwasher to be about one tenth the effort as taking out the trash you would set the score of taking out the trash to 10. If you see a new task, update your preference score for that task. New tasks are initialized with a default preference score of 1."]),
    html.H2(["To Do Page"]),
    html.P(["Once you're happy with your preferences go to the ", html.A("To Do", href="/todo"), " page and look at the available tasks."]),
    html.H4(["Task Points"]),
    html.P(["Notice each task has a number of points associated with it. When you mark a task as complete you will recieve that many points. The number of points a task is worth is based on all of the users' preference scores. A task that users deem to take more effort with be worth more points."]),
    html.H4("Assigments"),
    html.P(["Tasks are assigned to you based on ", html.B("your") ," preference score for a task, and the ", html.B("average") ," preference score for that task as well as your point history. The average number of points you have recived per day is compared to the average number of points recieved by everyone else. If you are lagging behind your peers you will be assigned more tasks. You do not need to wait to be assigned a task to complete it."]),
    html.H4(["Add Helpers"]),
    html.P(["If you click the ADD HELPER button you will be presented with a list of other users that may have hepled you with your task. When the task is completed the points will be split evenly between all helpers. You don't need to have yourself selected in the helper list. If you notice another user has completed a task you can select only them in the helper list and mark the task as completed for them."]),
    html.H2("Adding or Modifying a Task"),
    html.P(["To add a task go to the ", html.A("Tasks", href="/tasks"), " page. Give this page ~10 seconds to load before you attempt to click on things. To add a new task click the NEW TASK button and fill out the form. The 'Period in days' field is the number of days between task completions. For example, if taking out the trash needs to be done once a week the 'Period in days' would be 7. The 'Percent of period' is the percent the task is currently in in its life cycle. For example, if you were half way through the week and the trash needed to be taken out at the end of the week the percent of period could be set to '50' because 'take out the trash' is halfway through it's weekly life cycle."]),
    html.P(["To modify a task click on the task. The task will morph into a form pre-populated with that task's details. Edit the details and then click update. ", html.B("Don't update the name of a task lightly."), " Tasks of different names look different in the record keeping system. If you click delete the task will be deleted but records of that task will not be deleted."]),
    html.H2("Viewing Points"),
    html.P(["Go to the ", html.A("Points", href="/points"), " page to see a history of all the tasks done by all of the users."]),
    html.H2("Report Issues!"),
    html.P(["Use the ", html.A("Report Issue", href="/issues"), " page to mark down suggestions and issues. If you want, leave your name in the issue so I can follow up with you. I appriciate feedback and want to improve this app."])

])
