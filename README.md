# OVH DynHost Updater

This Python script updates the DynHost IP, using the OVH API.

## Requirements

* ovh - https://github.com/ovh/python-ovh
* ipgetter - https://github.com/phoemur/ipgetter

## Installation

It is recommended to install the script in a virtualenv.

    git clone <>
    virtualenv venv
    . venv/bin/activate

    pip install ovh ipgetter


## Configuration

### Subdomain
The two scripts `ck.py` and `updater.py` require subdomain data.

    cp subdomain.conf.sample subdomain.conf
    nano subdomain.conf

You need to change :
* the zone name
* the subdomain name
* the subdomain id

> This last can be retreived from the OVH API console :
> https://api.ovh.com/console/

> `GET /domain/zone/{zoneName}/dynHost/record`

### Access
The `ovh` module uses the file `ovh.conf` to get the access tokens.

    cp ovh.conf.sample ovh.conf
    nano ovh.conf

Fill the fields `application_key` and `application_secret` with the values
obtained here: https://eu.api.ovh.com/createApp/

You need to generate the `consumer_key`.

    python ck.py

> The python script asks OVH server `GET` and `PUT` access to the path
`/domain/zone/{zonename}/dynHost/record/{id}`

Follow then the instructions of the console output.

Copy the Consumer Key into the file `ovh.conf`.

## Automatization with cron

The script will run with current user privileges.

    crontab -e

Add the following line to launch the `updater.py` script **every five minutes**.

    # m   h   dom   mon   dow   command
    */5   *   *     *     *     /my_path_to/updater.sh
