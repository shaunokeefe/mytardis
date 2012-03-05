====
Transfer App
====

The transfer app oversees the transfer and synchronisation of experiments between providers (e.g. The Synchrotron) and consumers (e.g. Home institutions such as Monash). The app has a provider component and a consumer component, to be deployed at the respective locations, that define a protocol allowing:

    * A provider to notify consumers of new experiments, and register them with the consumer
    * A consumer to request the transfer data files for experiments from a provider
    * A consumer to poll the provider for status of a transfer of data files

The consumer also manages the state of each experiment, so success or failure of the tranfser can easily be determined on the consumer side. Failed transfers log data about the cause of the failure and can be restarted with user intervention.

Quick Setup
===========

Add the sync application and dependancies to the INSTALLED_APPS list in your tardis projects settings file

    INSTALLED_APPS == (
        ...    
        TARDIS_APP_ROOT + '.sync',
        ...
        'djcelery',V
        'djkombu',
    )

Add the sync application and dependancies to the INSTALLED_APPS list in your tardis projects settings file

    INSTALLED_APPS == (
        ...    
        TARDIS_APP_ROOT + '.sync',
        ...
        'djcelery',V
        'djkombu',
    )

Next, if you are planning on running the code for the consumer side of the app, set up Celery. This will periodically check all of your experiments to see if they
    import djcelery

    INSTALLED_APPS == (
        ...
        'djcelery',
        'djkombu',
    )
    
    CELERYBEAT_SCHEDULE = {
                "tasks.clock": {
                "task": "tardis.apps.sync.tasks.clock_tick",
                "schedule": timedelta(seconds=6)
                                },
    }
    djcelery.setup_loader()

Last, set the manager that the sync manager will use. Set it to the default for now.

    SYNC_MANAGER = 'managers.default_manager'

Run syncdb to add the SyncedExperiment table to the database. The app does not alter any existing tables so there is no need to do a migrate.

If you are setting up a consumer, start celery by switching to your tardis checkout and running

    ./bin/django celeryd -b

This will start a clock which periodically checks your experiments and attemps to progress any that havn't been completely transferred to your home institution.

Settings
=====

Celery
------
Celery runs the tasks that periodically check to see if there are any experiments that havn't been properly transferred to the home institution it is running at, and attempts to progress those experiments down the transfer workflow.

The main setting you'll be interested in here is the "Schedule" value in the CELERYBEAT_SCHEDULE dictionary. Set this  to the frequency that you'd like celery to check for new experiments.

SYNC_MANAGER
------------

The transfer app comes with a number of default implementations of parts of its backend. These can be replaced in order to addapt the transfer app to work with the backends at your particular institution. 

The SynchManager class defines the interface for the backends at a provider that the rest of the ap (Read: the views) plugs into.

The app comes with a default implementation of a SynchManager, the DefaultManager. Specify this in your settings if you're happy to use the default implementation

    SYNC_MANAGER = 'managers.default_manager'

The default manager uses the following:

    * The default www.tardis.edu.au registry of sites to find sites to recieve information about experiments
    * A format of 'tardis.<EPN>' to generate the UIDs used by the synch manager to identify experiments across institutions
    * METS export to send experiment data
    * Has the file transfer method (to send files for experiments) stubbed and will need to be defined if oyu want to send files (i.e. if your deployment is a provider).
    * Has the status request method stubbed (will always return a failure message on being queried)

If this functionality is not as desired then see the 'Customizing' section belowe to see which you will need to change.

The TransferClient defines the interface to the backends of a consumer deployement. There is not likely any need to rewrite the TransferClient.


Architecture
============

The sync app consists of two components or sub-apps; The consumer sub-app and the provider sub-app. They are presented in the one app (rather than two separate apps) to aid understandability, and also as there is a considerable shared amount of code between the two. Each sub-app has an interface which defines how its counterpart can query it and post data to it. Each sub-app has a number of pluggable components which can be replaced (either through changing the settings file or subclassing the components) on a deployment by deployment basis, to reflect the different backends of each tardis employment (e.g. different site registries, different file transfer methods)

Consumer
--------

The consumer handles the registration of new experiments from a provider, initiates data transfer of datafiles from the providing institution, and keeps track of the progress of these transfers. Should a transfer fail, the consumer sets the state of a transfer to 'failed permanent' and the appropriate user is notified. 

Views
~~~~~
*register_experiment*

Models
~~~~~~
*SyncedExperiment* This is the only model added by the sync app. The model wraps the existing tardis.tardis_portal.Experiment model, and ads information about the state of the transfer of the experiment to the home institution. 
Experiments are only wrapped in SyncedExperiment wrappers at home institution instances of myTardis (i.e. deployments of tardis that recieve experiments from other deployments) and are only if they have been transferred (or are in the process of being transferred) to that home institution (Experiments created there will not be wrapped). 

# TODO when a syncedExperiment is isntantiated

The SyncedExperiment model tracks progress after the experiment is initially ingested into the home institution. This is done using a custom django field 'FSMField'. The field stores the state of a finite state machine (FSM), which tells us at any time what state the transfer is in. Each state in the FSM is defined as its own class, and defines a method *get_next_state* which can be called to progress to the next state. Each state defines a list operations to attempt to perform for that state, and conditions to progress to subsequent states. The app comes with a default FSM which reflects a regular transfer workflow, but can be changed or extended by adding classes that subclass the State class.

Also keeps track of TODO (url etc)

In the default deployment of the sync app uses Celery (specifically, celerybeat) to periodically get a list of all SyncedExperiments that are not in the COMPLETE state, and attempts to progress them to their next state. The steps for setting up Celery are outlined in the Setup section of this document.

Pluggable Components
~~~~~~~~~~~~~~~~~~~~

*TransferClient* Defines the consumer side of the communication protocol between the consumer and the provider. Generally, this component will be the same for most deployments and should not need to be altered.

    *request_file_transfer(synced_experiment)* makes a request to the provider to begin the transfer of the files for the SyncedExperiment synced_experiment. This starts a file transfer between the file server for the providers backend and _____ on the consumer end.

    *get_status(synced_experiment)* If the files for an experimmnet are in the process of being transferred to the home institution, this function may be used to query the progress of the transfer.
    
Provider
--------

Views
~~~~~
*get_exeperiment*

*handle_file_transfer_request*

*transfer_status*

Models
~~~~~~
None

Pluggable Components
~~~~~~~~~~~~~~~~~~~~

*TransferService*

Think of this as the counterpart to the TransferClient on the consumer side. This is a very shallow wrapper that defines an interface and basically loads a user specified instance of a SyncManager as the backend.

*SyncManager*

To override any of the implementation of the default SyncManager provided, a developer should inherit from SyncManager and re-implement each of the classes.

*SiteManager*

Manages the retrieval of information about home institutions that will need experiments. By default, this retrieves a list of sites, as well as their configurations from www.tardis.edu.au. Customizing

Customization
=============

File Transfer Method
--------------------
No file transfer method is 

Site Registration
-----------------

It is possible to change this through the settings in settings.py

TODO

Alternatively, a developer may provide their own implementation of SiteManager, and specify its use by sub-classin

Transfer Workflow
-----------------


Admin
=====

The app adds a 'transfer' command to the admin interface to which an experiment EPN can be passed. If the deployement is a provider, it will attempt to broadcast the experiment denoted by the EPN to all registered sites.
