Feature: Todos

    Scenario: Displaying todos
        Given we use the config "todos.json"
        When we run "jrnl --todos"
        Then we should get no error
        and the output should be
            """
            =======
            Pending
            =======
            * ???
                Entry: 2015-04-09 15:39
                       I have so many things to do:
            * PROFIT!
                Entry: 2015-04-09 15:39
                       I have so many things to do:
            * Think about doing laundry.
                Entry: 2015-06-10 15:40
                       A few more things to do...
            * Become a world-famous circus juggler.
                Entry: 2015-06-10 15:40
                       A few more things to do...
                Due: 2015-06-02

            ========
            Complete
            ========
            * write a command line @journal software
                Entry: 2015-04-09 15:39
                       I have so many things to do:
            * Think about life (no deadline).
                Entry: 2015-06-10 15:40
                       A few more things to do...
            * Worry about the apocalypse.
                Entry: 2015-06-10 15:40
                       A few more things to do...
                Due: 2015-07-01
                Completed: 2015-06-28
            * Do something awesome!
                Entry: 2015-06-10 15:40
                       A few more things to do...
                Due: 2015-11-25
            """