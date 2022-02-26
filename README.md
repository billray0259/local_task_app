## Problem Description

Assume people seek happiness

### Goal: Ensure useful tasks are completed while maximizing happiness

-   A task is useful if

    -   The people agree the task is useful
-   Tasks are completed by people with the requirements

    -   Are physically capable of doing the task
    -   Know how to do the task
    -   Know to do task
    -   Anticipate experiencing a reward after completing the task greater than opportunity cost of doing something else

        -   *Define* “reward” to be anything that makes the person happy, likely a psychological sense of accomplishment but could be some prize or points

*Assume* tasks are repetitive and become useful again after some time has elapsed

-   Usefulness delay may not be constant
-   *Define* “frequency” to refer to the usefulness delay

Determine if a task is useful

-   Users can add tasks they agree are useful
-   Users can add an estimated frequency for every new task

Estimating task usefulness

-   Assume all potentially useful tasks are added by users
-   Re-define “useful tasks” to be tasks that have not been completed since their usefulness delay
-   Estimating usefulness delay

    -   Initial manual estimate
    -   Refining initial manual estimate

        -   Periodically ask users to estimate how much longer until a given task needs to be done
        -   Use these estimates as well as how much time has elapsed since the task was last completed to update the task frequency

Assume all users are physically capable of doing all tasks

Assume all users know how to do all tasks

-   It might be fun to have a little how-to guide for every task though

Ensure users know to do every useful task

-   When a task becomes useful the optimal user is notified to do the task

Optimal user is the user that would experience the greatest relative reward to opportunity cost of doing something else

Assume opportunity cost is constant for all users

Assume all users at least very mildly dislike doing all tasks

Estimating reward given a user and a task

-   How much the user dislikes doing the task

    -   Define “preference spectrum” as a number line from -infinity to 0 indicating how much a user dislikes doing a task
    -   Ask every user to place every task relative to every other task on a preference spectrum
-   The time elapsed since this task was last completed relative to this task’s usefulness delay

    -   Assume that tasks that are near / over their usefulness delay will add to **all** users’ reward when completed
    -   Define “timely reward” to be this reward felt by all users’ upon completing a task
    -   Assume the timely reward for a task is the same for every user
-   How much accomplishment the user would feel for completing the task

    -   Assume users who have contributed less so far in recent history will feel a greater amount of accomplishment from completing this task than users who have contributed more
    -   Define “point reward” as this sense of accomplishments from doing a task proportional to the relative positioning of users’ contributions
    -   Keep track of users’ contributions
    -   Use simple moving average of users’ contributions to calculate point reward
-   Estimate reward for every user based on the position of this task on their preference spectrum and the amount of their recent contributions

    -   Timely reward does not affect the relative reward between users, making it unnecessary to factor into the determination of the optimal user

Keeping track of users’ contributions

-   When a user completes a task assign them points
-   Point value of task is based on the average reward felt by every other user for completing that task

    -   *Define* “reward felt by other users” as the negative preference spectrum value of the task plus the timely reward for completing this task

Meta-feedback

-   How are things weighted?

    -   Weight types

        -   Timely reward
        -   Preference spectrum
        -   Point reward
    -   Estimate initial weights
    -   Periodically ask users if weights should be adjusted

        -   “Are tasks generally getting completed on time?” → Timely reward

            -   This can be determined automatically
        -   “Are you frequently getting assigned to tasks you dislike?” → preference spectrum
        -   “Would you care if you had fewer points than your peers?” → point reward

    -   Allow users to answer on a spectrum form -1 to 1 to adjust the weights more continuously

## App functionality

-   Users can create profiles

    -   User’s name
    -   Preference spectrum

        -   (-100, 0) for every task
        -   Relative task position on spectrum should be easy to see
    -   Points
    -   Update preference spectrum

-   Users can add tasks

    -   Task name
    -   Description (maybe this is where a possible how-to guide is)
    -   Created by
    -   Created date
    -   Estimated frequency
    -   Trigger

        -   If the task pertains to something in the app, what the app should do to when a user begins this task. Example: Task is asking how long until a task needs to be completed
    -   When a new task is added users are asked to place it on their preference spectrum

-   User can view which tasks are available

    -   Task name
    -   Task point value
    -   Time since last completion

        -   Progress bar

-   Ask user’s questions regarding the weights of the different reward types

    -   Log user input

        -   User ID
        -   Answer values
    -   Update reward weights

-   Ask users how much longer until a given task needs to be completed

    -   Log user input

        -   Task ID
        -   User ID
        -   Timestamp
        -   Time since last completion
        -   Time estimated
    -   Adjust task frequency as a function of how much time has passed since the task was last completed and the estimated time until the task needs to be completed again.

        -   New period is time passed plus estimated time remaining
        -   Update period as exponential moving average with this new period

-   Users can report a task they completed

    -   Log user input

        -   Task ID
        -   User Ids
        -   Timestamp
        -   Time since last completion
        -   Total points awarded
    -   Select task
    -   Add collaborators

        -   Points get split between collaborators
    -   Adjust task period based on current time and the last completed task time

-   Users can view their points relative to other users

    -   Select users to view
    -   Select a short time period
    -   Select a long time period
    -   View all points collected by every user in the last short time period
    -   Go to long time period view
    -   See bar graph

        -   X-axis = dates from the last long time period
        -   Y-axis = Points received in every short time period
        -   Ex:

            -   Short time period = 1 day
            -   Long time period = 1 month
            -   Long time period view shows how many points each user got every day over the last month

## Database Tables / Django Models

User

-   username – string

    -   User’s username
-   points – int

    -   Number of points user has

Task

-   name – string

    -   Name of task
-   description – string

    -   Description of task
-   author – User

    -   User that created the task
-   time\_created – timestamp

    -   timestamp marking when the task was created
-   period – int

    -   Usefulness delay in seconds
-   last\_completed – timestamp

    -   Time the task was last completed

Record

-   task – Task

    -   Task associated with this record
-   time\_taken – int

    -   Number of seconds between time\_completed and the task’s last\_completed time
-   time\_completed – timestamp

    -   Time when the task was completed
-   points\_awarded – int

    -   Total number of points awarded to all users
-   num\_users – int

    -   Number of users that split the points for doing the task

RecordToUser

-   record – Record

    -   A record
-   user – User

    -   One user associated with the record

UserToPreference

-   user – User

    -   User whose preference is documented by this entry
-   task – Task

    -   The Task
-   preference – int

    -   Preference score

## Pages

Create profile

-   First / Last name

<!-- -->

-   username
-   password
-   verify password
-   submit button

Sign In

-   username
-   password
-   submit button

View / edit preference spectrum

-   Description of the preference spectrum and a statement explaining how the preference score should be linear. Eg if you would rather do task X 5 times than task Y once, task X should have a score 1/5th that of task Y

<!-- -->

-   List of tasks sorted by preference descending from 0 to -100
-   Click and drag tasks below and above other ones

    -   Updates preference score if task is moved relative to other tasks
-   Manually updating preference score reorders tasks

View / edit tasks

-   List of tasks
-   Clicking on task enlarges the task and makes the fields editable

    -   Save task
    -   Delete task
-   Add task button

    -   Creates blank enlarged, editable task

View / complete records

-   To Do

    -   List of uncompleted records

        -   Name of task

            -   Optionally name of “optimal user” to complete task
        -   Current point value of task
        -   Progress bar with percentage from time since last completion out of task period

            -   Optionally changes color from green to red

-   Done

    -   Perhaps hidden behind a “Show past records” button
    -   List of completed tasks

        -   Name of task
        -   Name of users who completed the task
        -   Total points awarded

Report time status

-   Name of task
-   Time selector
-   Submit button

Answer weight questions

-   Question text
-   Answer slider form -1 to 1
-   Submit button

View point histories

-   Long time selector
-   Short time selector
-   Bar graph of all active users
